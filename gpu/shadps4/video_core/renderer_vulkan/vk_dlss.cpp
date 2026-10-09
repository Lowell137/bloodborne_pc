// SPDX-FileCopyrightText: Copyright 2026 IFreemz, bbport contributors
// SPDX-License-Identifier: GPL-2.0-or-later

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <mutex>
#include <optional>
#include <string_view>

#include "video_core/renderer_vulkan/vk_dlss.h"

#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#else
#include <dlfcn.h>
#include <unistd.h>
using HMODULE = void*;
#endif
#include "../../../dlss_bridge/bbport_dlss_bridge.h"

namespace Vulkan {

int Dlss::QualityForScale(float scale) {
    // DLAA only for equal sizes: any real upscale needs at least the Quality mode.
    return scale >= 2.9f ? 4 : scale >= 1.95f ? 3 : scale >= 1.65f ? 2 : scale > 1.01f ? 1 : 0;
}

namespace {
#ifdef _WIN32
constexpr wchar_t BridgeName[] = L"bbport_dlss.dll";
constexpr wchar_t NgxName[] = L"nvngx_dlss.dll";
#else
constexpr char BridgeName[] = "libbbport_dlss.so";
constexpr char NgxName[] = "libnvidia-ngx-dlss.so";
#endif

std::filesystem::path ExecutableDirectory() {
#ifdef _WIN32
    std::wstring path(MAX_PATH, L'\0');
    const DWORD length = GetModuleFileNameW(nullptr, path.data(), DWORD(path.size()));
    path.resize(length);
    return std::filesystem::path{path}.parent_path();
#else
    char buf[1024];
    ssize_t len = readlink("/proc/self/exe", buf, sizeof(buf) - 1);
    if (len > 0) {
        buf[len] = '\0';
        return std::filesystem::path{buf}.parent_path();
    }
    return std::filesystem::current_path();
#endif
}

void BridgeLog(int warning, const char* message) {
    std::printf("DLSS: %s%s\n", warning ? "warning: " : "", message);
}

bool CollectExtensions(const VkExtensionProperties* required, u32 count,
                       const std::vector<vk::ExtensionProperties>& available,
                       std::vector<std::string>& storage, std::vector<const char*>& enabled) {
    storage.clear();
    for (u32 i = 0; i < count; ++i) {
        const auto& request = required[i];
        const auto match = std::ranges::find_if(available, [&](const auto& extension) {
            return std::strcmp(extension.extensionName.data(), request.extensionName) == 0 &&
                   extension.specVersion >= request.specVersion;
        });
        if (match == available.end()) {
            std::printf("DLSS: missing Vulkan extension %s\n", request.extensionName);
            return false;
        }
        storage.emplace_back(request.extensionName);
    }
    for (const auto& name : storage) {
        if (std::ranges::none_of(enabled, [&](const char* current) { return name == current; })) {
            enabled.push_back(name.c_str());
        }
    }
    return true;
}
} // namespace

struct Dlss::Impl {
    HMODULE module{};
    const BbDlssApi* api{};
    std::vector<std::string> instance_extensions, device_extensions;
    std::optional<FeatureDesc> feature;
    std::string problem;
    bool eligible{true}, instance_ready{}, device_ready{}, initialized{}, available{};

    void Disable(std::string_view reason) {
        eligible = available = false;
        problem = reason;
        std::printf("DLSS: unavailable (%.*s)\n", int(reason.size()), reason.data());
    }
};

Dlss* Dlss::Get() {
    static Dlss* const dlss = []() -> Dlss* {
        const char* setting = std::getenv("BB_DLSS");
        if (setting && setting[0] == '0') {
            return nullptr;
        }
        const auto directory = ExecutableDirectory();
        bool found = false;
        for (const auto& dir : {directory, directory / "gpu", std::filesystem::current_path(),
                                std::filesystem::current_path() / "out",
                                std::filesystem::current_path() / "out/gpu",
                                std::filesystem::current_path() / "bin/gpu"}) {
            if (std::filesystem::is_regular_file(dir / BridgeName)) {
                found = true;
                break;
            }
        }
        if (!found) {
            return nullptr;
        }
        auto* created = new Dlss;
        // The process may end through quick_exit/_exit paths: release NGX first when it can.
        std::atexit([] {
            if (Dlss* live = Get()) {
                live->Shutdown();
            }
        });
        return created;
    }();
    return dlss;
}

Dlss::Dlss() : impl{std::make_unique<Impl>()} {
    const auto directory = ExecutableDirectory();
    std::filesystem::path bridge_path = directory / BridgeName;
    std::filesystem::path search_dir = directory;
    for (const auto& dir : {directory, directory / "gpu", std::filesystem::current_path(),
                            std::filesystem::current_path() / "out",
                            std::filesystem::current_path() / "out/gpu",
                            std::filesystem::current_path() / "bin/gpu"}) {
        if (std::filesystem::is_regular_file(dir / BridgeName)) {
            bridge_path = dir / BridgeName;
            search_dir = dir;
            break;
        }
    }
#ifdef _WIN32
    impl->module = LoadLibraryW(bridge_path.c_str());
    const auto get_api =
        impl->module ? reinterpret_cast<BbDlssGetApiFn>(GetProcAddress(impl->module, "BbDlssGetApi"))
                     : nullptr;
#else
    impl->module = dlopen(bridge_path.c_str(), RTLD_NOW | RTLD_LOCAL);
    const auto get_api =
        impl->module ? reinterpret_cast<BbDlssGetApiFn>(dlsym(impl->module, "BbDlssGetApi"))
                     : nullptr;
#endif
    impl->api = get_api ? get_api() : nullptr;
    if (!impl->api || impl->api->abi != BBPORT_DLSS_BRIDGE_ABI) {
        impl->Disable("bbport_dlss is missing or from another version");
        return;
    }
    // NGX writes its logs and model updates here: beside the saves and shader caches.
    std::filesystem::path data = search_dir / "dlss";
    if (const char* user = std::getenv("BB_GPU_USER_DIR"); user && user[0]) {
        data = std::filesystem::path{user} / "dlss";
    }
    std::error_code error;
    std::filesystem::create_directories(data, error);
    std::wstring wsearch = search_dir.wstring();
    std::wstring wdata = data.wstring();
    if (!impl->api->Configure(wsearch.c_str(), wdata.c_str(), BridgeLog)) {
        impl->Disable("bridge configuration failed");
    }
}

Dlss::~Dlss() {
    Shutdown();
}

void Dlss::AppendInstanceExtensions(std::vector<const char*>& enabled) {
    if (!impl->eligible) {
        return;
    }
    u32 count{};
    const VkExtensionProperties* required{};
    if (!impl->api->InstanceExtensions(&count, &required)) {
        return impl->Disable("instance extension query failed");
    }
    const auto [result, extensions] = vk::enumerateInstanceExtensionProperties();
    if (result != vk::Result::eSuccess ||
        !CollectExtensions(required, count, extensions, impl->instance_extensions, enabled)) {
        return impl->Disable("required Vulkan instance extensions are missing");
    }
    impl->instance_ready = true;
}

void Dlss::AppendDeviceExtensions(vk::Instance instance, vk::PhysicalDevice physical,
                                  std::vector<const char*>& enabled) {
    if (!impl->eligible || !impl->instance_ready) {
        return;
    }
    const auto properties = physical.getProperties();
    if (properties.vendorID != 0x10de) {
        return impl->Disable("not an NVIDIA GPU");
    }
    u32 count{};
    const VkExtensionProperties* required{};
    if (!impl->api->DeviceExtensions(instance, physical, &count, &required)) {
        return impl->Disable("this GPU or driver does not support DLSS (GeForce RTX needed)");
    }
    const auto [result, extensions] = physical.enumerateDeviceExtensionProperties();
    if (result != vk::Result::eSuccess ||
        !CollectExtensions(required, count, extensions, impl->device_extensions, enabled)) {
        return impl->Disable("required Vulkan device extensions are missing");
    }
    impl->device_ready = true;
}

void Dlss::Initialize(vk::Instance instance, vk::PhysicalDevice physical, vk::Device device) {
    if (!impl->eligible || !impl->device_ready || impl->initialized) {
        return;
    }
    impl->initialized = true;
    if (!impl->api->Initialize(instance, physical, device,
                               VULKAN_HPP_DEFAULT_DISPATCHER.vkGetInstanceProcAddr,
                               VULKAN_HPP_DEFAULT_DISPATCHER.vkGetDeviceProcAddr)) {
        return impl->Disable("NVIDIA NGX initialization failed (update the GPU driver)");
    }
    impl->available = true;
    std::printf("DLSS: ready\n");
}

bool Dlss::Available() const {
    return impl->available;
}

std::string Dlss::Problem() const {
    return impl->problem;
}

bool Dlss::HasFeature(const FeatureDesc& desc) const {
    return impl->feature && *impl->feature == desc;
}

bool Dlss::CreateFeature(vk::CommandBuffer command, const FeatureDesc& desc) {
    if (!impl->available) {
        return false;
    }
    impl->feature.reset();
    const BbDlssFeature feature{desc.input_width,  desc.input_height, desc.output_width,
                                desc.output_height, desc.quality,      0,
                                desc.preset,        desc.hdr ? 1 : 0};
    if (!impl->api->CreateFeature(command, &feature)) {
        return false;
    }
    impl->feature = desc;
    return true;
}

bool Dlss::Evaluate(vk::CommandBuffer command, const Frame& frame) {
    if (!impl->available || !impl->feature) {
        return false;
    }
    const auto image = [](const Resource& r) {
        const vk::ImageSubresourceRange range{r.aspect, 0, 1, 0, 1};
        return BbDlssImage{r.image,
                           r.view,
                           static_cast<VkImageSubresourceRange>(range),
                           static_cast<VkFormat>(r.format),
                           r.width,
                           r.height};
    };
    const BbDlssEvaluate parameters{image(frame.color),  image(frame.depth), image(frame.motion),
                                    image(frame.output), frame.jitter_x,     frame.jitter_y,
                                    frame.reset ? 1 : 0, frame.frame_ms,     frame.sharpness};
    return impl->api->Evaluate(command, &parameters) != 0;
}

void Dlss::ReleaseFeature() {
    impl->feature.reset();
    if (impl->api) {
        impl->api->ReleaseFeature();
    }
}

bool Dlss::FrameGenerationAvailable() const {
    return impl->available && impl->api->FrameGenerationAvailable();
}
bool Dlss::CreateFrameGeneration(vk::CommandBuffer command, u32 w, u32 h, vk::Format format) {
    return FrameGenerationAvailable() &&
           impl->api->CreateFrameGeneration(command, w, h, VkFormat(format));
}
bool Dlss::GenerateFrame(vk::CommandBuffer command, const BbDlssGenerate &frame) {
    return FrameGenerationAvailable() && impl->api->GenerateFrame(command, &frame);
}
void Dlss::ReleaseFrameGeneration() {
    if (impl->api)
        impl->api->ReleaseFrameGeneration();
}

void Dlss::Shutdown() {
    impl->available = false;
    impl->feature.reset();
    if (impl->api && impl->initialized) {
        impl->api->Shutdown();
        impl->initialized = false;
    }
    if (impl->module) {
#ifdef _WIN32
        FreeLibrary(impl->module);
#else
        dlclose(impl->module);
#endif
        impl->module = nullptr;
    }
}

} // namespace Vulkan
