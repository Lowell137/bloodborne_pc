// bbport: SDL3 window for the Vulkan swapchain (X11 or Wayland).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <SDL3/SDL.h>
#include "common/assert.h"
#include "common/logging/log.h"
#include "sdl_window.h"
#include "bbport_overlay.h"
#include "bbport_mouse.h"
#include "bbport_settings.h"
#include "../../src/host_input.h"

namespace Frontend {

namespace {

// Issue #69: the monitor the window (and fullscreen) goes to. BB_DISPLAY: its number in SDL's
// order (1, 2, ...; bb-gpu-capabilities --displays lists them) or a part of its name; without it
// SDL's primary display. The monitors are logged so a report says which one was taken.
SDL_DisplayID ChooseDisplay() {
    const SDL_DisplayID primary = SDL_GetPrimaryDisplay();
    const char* wanted = std::getenv("BB_DISPLAY");
    int count = 0;
    SDL_DisplayID* ids = SDL_GetDisplays(&count);
    SDL_DisplayID chosen = 0;
    if (wanted && *wanted) {
        char* end = nullptr;
        const long number = std::strtol(wanted, &end, 10);
        if (end && *end == '\0') {
            if (number >= 1 && number <= count) {
                chosen = ids[number - 1];
            }
        } else {
            for (int i = 0; i < count && !chosen; ++i) {
                const char* name = SDL_GetDisplayName(ids[i]);
                if (name && strcasestr(name, wanted)) {
                    chosen = ids[i];
                }
            }
        }
    }
    const SDL_DisplayID display = chosen ? chosen : primary;
    for (int i = 0; i < count; ++i) {
        const char* name = SDL_GetDisplayName(ids[i]);
        const SDL_DisplayMode* mode = SDL_GetDesktopDisplayMode(ids[i]);
        std::printf("Display %d: %s %dx%d%s%s\n", i + 1, name ? name : "?", mode ? mode->w : 0,
                    mode ? mode->h : 0, ids[i] == primary ? " (primary)" : "",
                    ids[i] == display ? " <- the game's (BB_DISPLAY)" : "");
    }
    if (wanted && *wanted && !chosen) {
        std::printf("Display: BB_DISPLAY=%s matches none, the primary one is used\n", wanted);
    }
    SDL_free(ids);
    return display;
}

} // namespace

WindowSDL::WindowSDL(s32 width_, s32 height_, const char* title) : width{width_}, height{height_} {
    // Windows SDL relative mode uses native Raw Input. Keep its device counts
    // unscaled even if inherited SDL environment hints enable pointer acceleration.
    SDL_SetHintWithPriority(SDL_HINT_MOUSE_RELATIVE_SYSTEM_SCALE, "0", SDL_HINT_OVERRIDE);
    SDL_SetHintWithPriority(SDL_HINT_MOUSE_RELATIVE_SPEED_SCALE, "1", SDL_HINT_OVERRIDE);
    SDL_SetHintWithPriority(SDL_HINT_MOUSE_RELATIVE_WARP_MOTION, "0", SDL_HINT_OVERRIDE);
    SDL_SetHintWithPriority(SDL_HINT_MOUSE_EMULATE_WARP_WITH_RELATIVE, "0", SDL_HINT_OVERRIDE);
    // Gamepads are sampled by runtime_pad.c; their events are pumped here with the window's.
    if (!SDL_InitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMEPAD)) {
        UNREACHABLE_MSG("Failed to initialize SDL video: {}", SDL_GetError());
    }
    SDL_PropertiesID props = SDL_CreateProperties();
    SDL_SetStringProperty(props, SDL_PROP_WINDOW_CREATE_TITLE_STRING, title);
    const SDL_DisplayID display = ChooseDisplay();
    SDL_SetNumberProperty(props, SDL_PROP_WINDOW_CREATE_X_NUMBER, SDL_WINDOWPOS_CENTERED_DISPLAY(display));
    SDL_SetNumberProperty(props, SDL_PROP_WINDOW_CREATE_Y_NUMBER, SDL_WINDOWPOS_CENTERED_DISPLAY(display));
    SDL_SetNumberProperty(props, SDL_PROP_WINDOW_CREATE_WIDTH_NUMBER, width_);
    SDL_SetNumberProperty(props, SDL_PROP_WINDOW_CREATE_HEIGHT_NUMBER, height_);
    SDL_SetBooleanProperty(props, SDL_PROP_WINDOW_CREATE_RESIZABLE_BOOLEAN, true);
    SDL_SetBooleanProperty(props, SDL_PROP_WINDOW_CREATE_VULKAN_BOOLEAN, true);
    // Native startup smoke tests create a real Win32 surface without showing a window.
    const char* hidden = std::getenv("BB_HIDDEN_WINDOW");
    SDL_SetBooleanProperty(props, SDL_PROP_WINDOW_CREATE_HIDDEN_BOOLEAN, hidden && hidden[0] == '1');
    const char* fullscreen = std::getenv("BB_FULLSCREEN");
    SDL_SetBooleanProperty(props, SDL_PROP_WINDOW_CREATE_FULLSCREEN_BOOLEAN, fullscreen && fullscreen[0] == '1');
    base_title = title;
    window = SDL_CreateWindowWithProperties(props);
    SDL_DestroyProperties(props);
    ASSERT_MSG(window, "Failed to create window: {}", SDL_GetError());

    const char* driver = SDL_GetCurrentVideoDriver();
    const SDL_PropertiesID wp = SDL_GetWindowProperties(window);
#ifdef _WIN32
    if (driver && !std::strcmp(driver, "windows")) {
        window_info.type = WindowSystemType::Windows;
        window_info.render_surface = SDL_GetPointerProperty(wp, SDL_PROP_WINDOW_WIN32_HWND_POINTER, nullptr);
    } else
#endif
    if (driver && !std::strcmp(driver, "x11")) {
        window_info.type = WindowSystemType::X11;
        window_info.display_connection = SDL_GetPointerProperty(wp, SDL_PROP_WINDOW_X11_DISPLAY_POINTER, nullptr);
        window_info.render_surface = reinterpret_cast<void*>(SDL_GetNumberProperty(wp, SDL_PROP_WINDOW_X11_WINDOW_NUMBER, 0));
    } else if (driver && !std::strcmp(driver, "wayland")) {
        window_info.type = WindowSystemType::Wayland;
        window_info.display_connection = SDL_GetPointerProperty(wp, SDL_PROP_WINDOW_WAYLAND_DISPLAY_POINTER, nullptr);
        window_info.render_surface = SDL_GetPointerProperty(wp, SDL_PROP_WINDOW_WAYLAND_SURFACE_POINTER, nullptr);
    } else {
        UNREACHABLE_MSG("Unsupported SDL video driver {}", driver ? driver : "(none)");
    }
    int w = 0, h = 0;
    SDL_GetWindowSizeInPixels(window, &w, &h);
    width = w;
    height = h;
    LOG_INFO(Frontend, "Window {}x{} on {}", w, h, driver);
}

WindowSDL::~WindowSDL() {
    BbMouse::SetActive(false);
    SDL_SetWindowRelativeMouseMode(window, false);
    SDL_DestroyWindow(window);
}

void WindowSDL::BeginTextInput(const std::string& initial, const std::string& prompt) {
    std::scoped_lock lock{text_mutex};
    text = initial;
    text_prompt = prompt;
    text_state = 0;
    text_requested = true;
}

int WindowSDL::PollTextInput(std::string& out) {
    std::scoped_lock lock{text_mutex};
    out = text;
    return text_state;
}

void WindowSDL::TakeMouse(double& dx, double& dy, int& up, int& down) {
    std::scoped_lock lock{mouse_mutex};
    dx = mouse_dx;
    dy = mouse_dy;
    up = wheel_up;
    down = wheel_down;
    mouse_dx = mouse_dy = 0;
    wheel_up = wheel_down = 0;
}

// Mouse look: relative mode while the window holds the mouse (runtime_pad.c turns its motion into
// the right stick). Motion from before is dropped, so taking the mouse does not turn the camera.
void WindowSDL::CaptureMouse(bool capture) {
    if (capture == mouse_captured.load(std::memory_order_relaxed)) {
        return;
    }
    if (!SDL_SetWindowRelativeMouseMode(window, capture) && capture) {
        std::printf("Mouse look: relative mouse mode failed: %s\n", SDL_GetError());
        return;
    }
    {
        std::scoped_lock lock{mouse_mutex};
        mouse_dx = mouse_dy = 0;
        wheel_up = wheel_down = 0;
    }
    mouse_captured.store(capture, std::memory_order_relaxed);
    static bool told;
    if (capture && !told) {
        told = true;
        std::printf("Mouse look: on (F1 releases the mouse, a click takes it again)\n");
    }
}

void WindowSDL::UpdateTextTitle() {
    const std::string title = text_active ? base_title + " \u2014 " + text_prompt + ": " + text + "_  (Enter = OK, Esc = cancel)"
                                          : base_title;
    SDL_SetWindowTitle(window, title.c_str());
    BbOverlay::SetTextEntry(text_active, text_prompt, text);
}

bool WindowSDL::PollEvents() {
    UpdateMouseCapture();
    {
        std::scoped_lock lock{text_mutex};
        if (text_requested) { // SDL text input must be toggled from the window thread
            text_requested = false;
            text_active = true;
            SDL_StartTextInput(window);
            UpdateTextTitle();
        }
    }
    if (!text_active) {
        BbOverlay::UpdateTextInput(window);
    }
    UpdateMouseCapture(); // a requested game text dialog releases capture before draining input
    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        if (event.type == SDL_EVENT_MOUSE_MOTION) {
            last_mouse_motion_ms = SDL_GetTicks();
            if (mouse_captured.load(std::memory_order_relaxed)) {
                std::scoped_lock lock{mouse_mutex};
                mouse_dx += event.motion.xrel;
                mouse_dy += event.motion.yrel;
            }
        }
        if (text_active && (event.type == SDL_EVENT_TEXT_INPUT || event.type == SDL_EVENT_KEY_DOWN)) {
            std::scoped_lock lock{text_mutex};
            if (event.type == SDL_EVENT_TEXT_INPUT) {
                text += event.text.text;
            } else if (event.key.key == SDLK_BACKSPACE && !text.empty()) {
                size_t cut = text.size() - 1; // drop one UTF-8 code point
                while (cut > 0 && (static_cast<unsigned char>(text[cut]) & 0xC0) == 0x80) --cut;
                text.erase(cut);
            } else if (event.key.key == SDLK_RETURN || event.key.key == SDLK_KP_ENTER || event.key.key == SDLK_ESCAPE) {
                text_state = event.key.key == SDLK_ESCAPE ? 2 : 1;
                text_active = false;
                SDL_StopTextInput(window);
            }
            UpdateTextTitle();
            continue;
        }
        // The controller finishes the text dialog too: Cross (A) accepts, Circle (B) cancels.
        if (text_active && event.type == SDL_EVENT_GAMEPAD_BUTTON_DOWN &&
            (event.gbutton.button == SDL_GAMEPAD_BUTTON_SOUTH ||
             event.gbutton.button == SDL_GAMEPAD_BUTTON_EAST)) {
            std::scoped_lock lock{text_mutex};
            text_state = event.gbutton.button == SDL_GAMEPAD_BUTTON_SOUTH ? 1 : 2;
            text_active = false;
            SDL_StopTextInput(window);
            UpdateTextTitle();
            continue;
        }
        if (BbOverlay::HandleEvent(event)) {
            UpdateMouseCapture();
            continue;
        }
        // Mouse look: a click in the game takes the mouse (that click is not passed on as a
        // button: runtime_pad.c reads the buttons only while it is held); F1 and leaving the
        // window let it go.
        if (event.type == SDL_EVENT_MOUSE_BUTTON_DOWN && !mouse_captured.load(std::memory_order_relaxed) &&
            mouse_look.load(std::memory_order_relaxed) && !BbOverlay::MenuOpen()) {
            CaptureMouse(true);
            continue;
        }
        if (event.type == SDL_EVENT_KEY_DOWN && !event.key.repeat && event.key.key == SDLK_F1 &&
            mouse_captured.load(std::memory_order_relaxed)) {
            CaptureMouse(false);
            continue;
        }
        if (event.type == SDL_EVENT_WINDOW_FOCUS_LOST) {
            CaptureMouse(false);
        }
        // F4 turns mouse look on and off (the same mouse_look setting as the launcher's).
        if (!text_active && event.type == SDL_EVENT_KEY_DOWN && event.key.key == SDLK_F4 &&
            !event.key.repeat && !(event.key.mod & (SDL_KMOD_CTRL | SDL_KMOD_ALT | SDL_KMOD_GUI))) {
            const bool on = !mouse_look.load(std::memory_order_relaxed);
            EnableMouseLook(on);
            if (!on) CaptureMouse(false);
            BbOverlay::ShowMouseCamera(on);
        }
        if (event.type == SDL_EVENT_MOUSE_MOTION && event.motion.windowID == SDL_GetWindowID(window) &&
            event.motion.which != SDL_TOUCH_MOUSEID && event.motion.which != SDL_PEN_MOUSEID &&
            mouse_captured && !text_active &&
            !BbOverlay::CapturesInput()) {
            BbMouse::Motion(event.motion.xrel, event.motion.yrel);
        }
        if (event.type == SDL_EVENT_MOUSE_WHEEL && !text_active && !BbOverlay::CapturesInput()) {
            const float sign = event.wheel.direction == SDL_MOUSEWHEEL_FLIPPED ? -1.f : 1.f;
            const float x = event.wheel.x * sign, y = event.wheel.y * sign;
            const auto until = SDL_GetTicks() + 80; // one short press, visible to guest pad sampling
            if (y > 0) wheel_until[0] = until;
            if (y < 0) wheel_until[1] = until;
            if (x < 0) wheel_until[2] = until;
            if (x > 0) wheel_until[3] = until;
        }
        if (event.type == SDL_EVENT_MOUSE_WHEEL && mouse_captured.load(std::memory_order_relaxed)) {
            const float notches = event.wheel.direction == SDL_MOUSEWHEEL_FLIPPED ? -event.wheel.y : event.wheel.y;
            std::scoped_lock lock{mouse_mutex};
            (notches > 0 ? wheel_up : wheel_down) += notches != 0 ? 1 : 0;
        }
        switch (event.type) {
        case SDL_EVENT_WINDOW_PIXEL_SIZE_CHANGED:
        case SDL_EVENT_WINDOW_RESIZED: {
            int w = 0, h = 0;
            SDL_GetWindowSizeInPixels(window, &w, &h);
            width = w;
            height = h;
            break;
        }
        case SDL_EVENT_QUIT:
        case SDL_EVENT_WINDOW_CLOSE_REQUESTED:
            is_open = false;
            break;
        default:
            break;
        }
    }
    UpdateMouseCapture();
    UpdateMouseButtons();
    UpdateCursor();
    return is_open;
}

void WindowSDL::UpdateMouseButtons() {
    u32 buttons = 0;
    if (!text_active && !BbOverlay::CapturesInput() &&
        (SDL_GetWindowFlags(window) & SDL_WINDOW_INPUT_FOCUS)) {
        // SDL mouse APIs belong to the window thread; guest threads read only this snapshot.
        buttons = SDL_GetMouseState(nullptr, nullptr);
        const auto now = SDL_GetTicks();
        for (unsigned i = 0; i < 4; ++i) if (now < wheel_until[i]) buttons |= BB_WHEEL_UP << i;
    } else {
        for (auto& until : wheel_until) until = 0;
    }
    mouse_buttons.store(buttons, std::memory_order_relaxed);
}

void WindowSDL::UpdateMouseCapture() {
    // The menu, the name dialog and mouse_look=0 want the cursor.
    if (mouse_captured.load(std::memory_order_relaxed) &&
        (BbOverlay::MenuOpen() || text_active || !mouse_look.load(std::memory_order_relaxed))) {
        CaptureMouse(false);
    }
    BbMouse::SetActive(mouse_captured.load(std::memory_order_relaxed));
}

// Issue #3: the OS cursor over the game. Hidden in fullscreen, and in a window after 3 s without
// moving the mouse; always shown while the settings menu is open.
void WindowSDL::UpdateCursor() {
    const bool fullscreen = (SDL_GetWindowFlags(window) & SDL_WINDOW_FULLSCREEN) != 0;
    const bool hide = mouse_captured || (!BbOverlay::CapturesInput() &&
                      (fullscreen || SDL_GetTicks() - last_mouse_motion_ms > 3000));
    if (hide != cursor_hidden) {
        cursor_hidden = hide;
        hide ? SDL_HideCursor() : SDL_ShowCursor();
    }
}

} // namespace Frontend
