#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Bloodborne launcher for the native port (GTK4 / libadwaita).

Picks the game folder, edits the port's settings (bbport.ini: upscaler, preset, ...) and the
start-up tweaks passed as environment variables to run.sh, starts and stops the game and shows
its output. Launcher settings live in ~/.config/bbport-launcher/settings.json.
Russian, English and Brazilian Portuguese (bbport_i18n: the Russian text is the key).
"""

import glob
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import time
import zipfile
from datetime import datetime
from pathlib import Path
from bbport_assets import fsr411_problem
from bbport_achievements import AchievementBox
from bbport_i18n import language, set_language, tr
from bbport_vulkan import amd_gpu

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk  # noqa: E402

PORT_DIR = Path(__file__).resolve().parent.parent  # native_probe (or the package's copy)
sys.path.insert(0, str(PORT_DIR / 'scripts'))
from mods import discover as discover_mods  # noqa: E402
import game_check  # noqa: E402
from patches import external_patches  # noqa: E402
# Packaged (AppImage): generated files, saves and bbport.ini live in BB_DATA_DIR.
PACKAGED = bool(os.environ.get("BB_PREBUILT"))
DATA_DIR = Path(os.environ.get("BB_DATA_DIR", PORT_DIR))
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "bbport-launcher"
CONFIG_FILE = CONFIG_DIR / "settings.json"
MAX_LOG_LINES = 5000
# The new memory and translation model runs on AMD GPUs only for now (None: unknown).
AMD_GPU = amd_gpu()
PC_MODEL_SUBTITLE = ("Эксперимент, только видеокарты AMD. Видеокарта работает с памятью игры "
                     "напрямую, как в игре для ПК, а команды графики переводятся, а не "
                     "эмулируются; возможны ошибки. Выключено — старая модель памяти, как в 0.3, "
                     "со всеми исправлениями")
PC_MODEL_NO_AMD = ("Только для видеокарт AMD, а на этом компьютере её нет. Используется старая "
                   "модель памяти, как в 0.3, со всеми исправлениями")
# FSR 4.1.1 assets built from the user's AMD DLL (tools/fsr4cap, also in the package).
FSR4CAP_DIR = PORT_DIR / "tools" / "fsr4cap"
sys.path.insert(0, str(FSR4CAP_DIR))
# PKG extractor (ShadPs4Plus PKG Extractor)
PKG_EXTRACTOR_PATH = PORT_DIR / "tools" / "ShadPs4Plus-PkgExtractor-1.1-linux" / "pkg_extractor.AppImage"
if not PKG_EXTRACTOR_PATH.is_file():
    _alt_extractor = PORT_DIR.parent / "src" / "tools" / "ShadPs4Plus-PkgExtractor-1.1-linux" / "pkg_extractor.AppImage"
    if _alt_extractor.is_file():
        PKG_EXTRACTOR_PATH = _alt_extractor
# The package's own environment (its Mesa, libraries, GTK modules) must not reach Proton's
# container: Proton runs the DLL on the system's drivers.
PACKAGE_ONLY_ENV = (
    "LD_LIBRARY_PATH", "VK_DRIVER_FILES", "VK_ICD_FILENAMES", "VK_ADD_DRIVER_FILES",
    "VK_LAYER_PATH", "VK_ADD_LAYER_PATH", "__EGL_VENDOR_LIBRARY_DIRS", "GDK_PIXBUF_MODULE_FILE",
    "GIO_EXTRA_MODULES", "GI_TYPELIB_PATH", "FONTCONFIG_FILE", "GSETTINGS_SCHEMA_DIR", "PYTHONPATH",
    "PYTHONHOME",
)
# build_assets.sh exit statuses (see there).
FSR411_BUILD_ERRORS = {
    2: "DLL не подходит: подробности в журнале",
    3: ("Не найден подходящий Proton: установите GE-Proton 10 или новее (ProtonUp-Qt) или Proton "
        "Experimental / Proton-CachyOS в Steam. Если они есть — запустите в Steam любую игру с "
        "этим Proton, чтобы Steam поставил его рантайм"),
    4: "Не хватает программ для сборки: список в журнале",
    5: ("Ни один Proton не запустил FSR 4.1 из этой DLL. Либо они слишком старые (подходят "
        "GE-Proton 10+, Proton Experimental, Proton-CachyOS 11), либо DLL не включает FSR 4.1 на "
        "этой видеокарте (Steam Deck?): тогда соберите на ПК с Radeon RX 7000/9000 и скопируйте "
        "папку fsr4_411. Подробности в журнале"),
    6: ("Записанные проходы не совпали с тем, что повторяет bbport (другая версия DLL или "
        "новая видеокарта?): подробности в журнале"),
    7: "Не найден загрузчик FidelityFX 2.x",
    8: ("На NixOS запись идёт на самой системе (systemd --user) через umu-launcher из nix-shell, "
        "а здесь их не нашлось: установите umu-launcher или Nix. Подробности в журнале"),
}

# Choices: (label, value). The first entry is the default. Labels are translated when shown.
UI_LANGUAGES = [("Как в системе", ""), ("English", "en"), ("Türkçe", "tr"), ("Русский", "ru"), ("Português (Brasil)", "pt_BR")]
UPSCALERS = [("NVIDIA DLSS", "dlss"), ("FSR 4", "fsr4"), ("FSR 4.1.1", "fsr411"), ("FSR 3", "fsr3"),
             ("TAA (нативное сглаживание)", "taa"), ("Выключен", "off")]
FRAME_GENERATION = [
    ("Выключена", "off"),
    ("DLSS Frame Generation ×2", "dlss"),
    ("FSR 3.1.6 Frame Generation ×2", "fsr"),
]
DLSS_PRESETS = [
    ("Авто", "auto"),
    ("K (Transformer)", "K"),
    ("L (Transformer v2)", "L"),
    ("M (Transformer v2)", "M"),
    ("J (Transformer)", "J"),
    ("E (CNN)", "E"),
    ("F (CNN)", "F"),
]
PRESETS = [("Native AA", 0), ("Quality (x1.5)", 1), ("Balanced (x1.7)", 2),
           ("Performance (x2)", 3), ("Ultra Performance (x3)", 4)]
OUTPUT_RES = [("1280×720 (Steam Deck)", "1280x720"), ("1920×1080", "1920x1080"), ("2560×1440", "2560x1440"), ("3840×2160", "3840x2160")]
# Game effects (patches applied at start): bbport.ini key, title, default.
EFFECTS = [
    ("effect_chromatic_aberration", "Хроматическая аберрация", True),
    ("effect_dof", "Глубина резкости (DoF)", True),
    ("effect_motion_blur", "Размытие в движении", True),
    ("effect_ssao", "Затенение SSAO", True),
    ("effect_game_aa", "Собственное сглаживание игры", True),
    ("effect_dynamic_shadows", "Тени от динамических источников", True),
    ("effect_ssr", "Отражения SSR (не было в игре)", False),
    ("skip_intro", "Пропуск заставок при запуске", False),
    ("debug_camera", "Свободная камера (Cross + L3 / Space + Z)", False),
    ("debug_menu", "Debug menu (левый touchpad / Tab; нужны шрифты)", False),
]
MODEL_LOD = [("Как в игре", "0"), ("Максимальная (-2)", "-2"), ("Ниже (1)", "1"),
             ("Минимальная (2)", "2")]
FPS_MODES = [("Без ограничения (патч)", "uncap"), ("60", "60"), ("90", "90"),
             ("30 (как на PS4)", "30")]
PRESENT_MODES = [("Mailbox", "Mailbox"), ("FIFO (VSync)", "Fifo"),
                 ("FIFO Relaxed", "FifoRelaxed"), ("Immediate", "Immediate")]
# A third element is a note shown under the row's title while that choice is selected: the
# choice labels stay short, so the selected one is shown in full.
DRAW_PIPE = [("Авто", "", "Включён при 8 и более потоках процессора"), ("Включён", "1"),
             ("Выключен", "0", "Стабильнее, но медленнее")]
LANGUAGES = [("Английский", "1"), ("Русский", "8"), ("Японский", "0"), ("Французский", "2"),
             ("Испанский", "3"), ("Немецкий", "4"), ("Итальянский", "5")]
LIVE_RESOLUTION = [("Авто (по видеокарте)", "auto"), ("Выключена (быстрее)", "0"), ("Включена", "1")]
READBACKS = [("Relaxed", "", "По умолчанию"), ("Выключены", "0"), ("Precise", "2")]
# Background pre-upload of the game's GPU memory into VRAM (BB_PREUPLOAD): auto = on with a discrete GPU.
PREUPLOAD = [("Обычная", "", "Без лишней видеопамяти"), ("Полная", "2", "Около 3 ГБ видеопамяти сверху"),
             ("Выключена", "0")]

DEFAULTS = {
    "ui_language": "",
    "game_dir": "" if PACKAGED else str(PORT_DIR.parent / "CUSA03173"),
    "user_dir": "",
    "mods_dir": "",
    "mods_enabled": True,
    "patches_dir": "",
    "language": "1",
    "fullscreen": False,
    "hdr": False,
    "present_mode": "Mailbox",
    "gamepad": "",
    "gamepad_name": "",
    "fps_mode": "uncap",
    "fps_limit": 0,
    "draw_pipe": "",
    "readbacks": "",
    "preupload": "",
    "mangohud": False,
    "frame_stats": False,
    "save_log": False,
    "crash_diag": False,
    "pc_model": False,
    "as_0_3": False,
    "gpu_profile": False,
    "vk_validation": False,
    "extra_env": "",
    "playtime_seconds": 0,
    "play_count": 0,
    "last_played": "",
}

# bbport.ini keys the launcher edits; the rest of the file is kept.
INI_DEFAULTS = {
    "upscaler": "fsr4",
    "preset": "4",
    "frame_generation": "off",
    "dlss_preset": "Auto",
    "sharpen": "1",
    "sharpness": "0.50",
    "object_motion": "1",
    "show_fps": "1",
    "output_res": "1920x1080",
    "model_lod": "0",
    "live_resolution": "0",
    **{key: "1" if default else "0" for key, _, default in EFFECTS},
}


def load_settings():
    settings = dict(DEFAULTS)
    try:
        settings.update(json.loads(CONFIG_FILE.read_text()))
    except (OSError, ValueError):
        pass
    return settings


def save_settings(settings):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(settings, indent=2, ensure_ascii=False))


def ini_path():
    return Path(os.environ.get("BB_CONFIG", DATA_DIR / "bbport.ini"))


def load_ini():
    values = dict(INI_DEFAULTS)
    lines = []
    try:
        lines = ini_path().read_text().splitlines()
    except OSError:
        pass
    for line in lines:
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values, lines


def save_ini(values, lines):
    """Rewrites the edited keys in place, appends missing ones, keeps comments and others; a key
    whose value is None is removed (a control binding back to its default)."""
    written = set()
    out = []
    for line in lines:
        if "=" in line and not line.lstrip().startswith("#"):
            key = line.split("=", 1)[0].strip()
            if key in values:
                if values[key] is not None:
                    out.append(f"{key}={values[key]}")
                written.add(key)
                continue
        out.append(line)
    if not lines:
        out.append("# bbport settings (in-game menu: Insert / L3+R3)")
    for key, value in values.items():
        if key not in written and value is not None:
            out.append(f"{key}={value}")
    ini_path().write_text("\n".join(out) + "\n")


def patches_dir(settings):
    return Path(settings.get("patches_dir") or DATA_DIR / "patches").expanduser()


def fsr411_dir():
    """Where the FSR 4.1.1 assets are looked up, as run.sh does."""
    if os.environ.get("BB_FSR411_DIR"):
        return Path(os.environ["BB_FSR411_DIR"])
    return PORT_DIR / "fsr4_411" if (PORT_DIR / "fsr4_411").is_dir() else DATA_DIR / "fsr4_411"


def fsr411_build_command(upscaler, loader=None):
    """tools/fsr4cap/build_assets.sh for the user's DLL: command and environment. The package
    writes into the data directory (it is read-only itself) and removes the work folder after."""
    env = dict(os.environ)
    if PACKAGED:
        for key in PACKAGE_ONLY_ENV:
            env.pop(key, None)
        env["BB_FSR4CAP_WORK"] = str(DATA_DIR / "fsr4cap")
        env["BB_FSR4CAP_CLEAN"] = "1"
    tools = FSR4CAP_DIR / "bin"
    if (tools / "dxil-spirv").is_file() and (tools / "fsr4cap.exe").is_file():
        env["BB_FSR4CAP_TOOLS"] = str(tools)
    env["BB_FSR411_OUT"] = os.environ.get("BB_FSR411_DIR") or str(
        (DATA_DIR if PACKAGED else PORT_DIR) / "fsr4_411")
    command = ["bash", str(FSR4CAP_DIR / "build_assets.sh"), str(upscaler)]
    return command + ([str(loader)] if loader else []), env


def game_environment(s):
    """Environment for run.sh from the launcher settings."""
    env = dict(os.environ)
    env["BB_GAME_DIR"] = str(Path(s["game_dir"]).expanduser())
    if s["user_dir"]:
        env["BB_USER_DIR"] = s["user_dir"]
    env["BB_MODS_DIR"] = str(Path(s.get("mods_dir") or DATA_DIR / "mods").expanduser())
    env["BB_MODS_CONFIG"] = str(DATA_DIR / "mods.json")
    env["BB_MODS_ENABLED"] = "1" if s.get("mods_enabled", True) else "0"
    env["BB_PATCHES_DIR"] = str(patches_dir(s))
    env["BB_PATCHES_CONFIG"] = str(DATA_DIR / "patches.json")
    env["BB_LANGUAGE"] = s["language"]
    # The in-game menu speaks the launcher's language until one is chosen in it (menu_language).
    env["BB_MENU_LANGUAGE"] = language()
    env["BB_FULLSCREEN"] = "1" if s["fullscreen"] else "0"
    env["BB_PRESENT_MODE"] = s["present_mode"]
    env["BB_PREBUILT"] = "1"
    if "SDL_VIDEODRIVER" not in env:
        env["SDL_VIDEODRIVER"] = "x11"
    if s.get("gamepad"):
        env["BB_GAMEPAD"] = s["gamepad"]
    if s["hdr"]:
        env["BB_HDR"] = "1"
    env["BB_FPS"] = s["fps_mode"]
    if s["fps_limit"] > 0:
        env["BB_FPS_LIMIT"] = str(s["fps_limit"])
    if s["draw_pipe"]:
        env["BB_DRAW_PIPE"] = s["draw_pipe"]
    if s["readbacks"]:
        env["BB_READBACKS"] = s["readbacks"]
    if s.get("preupload"):
        env["BB_PREUPLOAD"] = s["preupload"]
    if s["mangohud"]:
        env["MANGOHUD"] = "1"
    if s["frame_stats"]:
        env["BB_FRAME_STATS"] = "1"
    if s.get("save_log"):
        env["BB_SAVE_LOG"] = "1"
    # The new memory and translation model (experimental, AMD GPUs only, off by default); the
    # model of 0.3 with the fixes made since otherwise. "pc_memory", "old_memory_model",
    # "new_memory_model" and "legacy_memory_model" of older settings are ignored.
    env["BB_PC_MODEL"] = "1" if s.get("pc_model") and AMD_GPU is not False else "0"
    # Synchronisation and memory as released in 0.3 (run.sh: BB_AS_0_3), for comparisons.
    if s.get("as_0_3"):
        env["BB_AS_0_3"] = "1"
    if s.get("crash_diag"):
        env["BB_FREE_CHECK"] = "1"
        env["BB_WRITE_LOG"] = "1"
        env["BB_PRODUCER_CHECK"] = "1"
    if s["gpu_profile"]:
        env["BB_GPU_PROFILE"] = "1"
    if s["vk_validation"]:
        env["BB_VK_VALIDATION"] = "1"
    for item in s["extra_env"].split():
        if "=" in item:
            key, value = item.split("=", 1)
            env[key] = value
    return env


def flat_button(icon, tooltip, handler):
    button = Gtk.Button(icon_name=icon, valign=Gtk.Align.CENTER, tooltip_text=tooltip)
    button.add_css_class("flat")
    button.connect("clicked", handler)
    return button


def open_folder(window, path):
    """Opens `path` in the file manager (created first, so that a new saves folder opens)."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
    except OSError:
        return
    Gtk.FileLauncher.new(Gio.File.new_for_path(str(path))).launch(window, None, None)


def combo_row(title, subtitle, choices, current):
    model = Gtk.StringList.new([tr(choice[0]) for choice in choices])
    row = Adw.ComboRow(title=title, model=model)
    values = [choice[1] for choice in choices]
    notes = [tr(choice[2]) if len(choice) > 2 else None for choice in choices]

    def show_note(*_):
        lines = [line for line in (subtitle, notes[row.get_selected()]) if line]
        row.set_subtitle("\n".join(lines))

    row.set_selected(values.index(current) if current in values else 0)
    show_note()
    row.connect("notify::selected", show_note)
    row.values = values
    return row


def combo_value(row):
    return row.values[row.get_selected()]


# Controls (runtime_pad.c): input, label, default keyboard keys, default gamepad buttons (SDL names).
# bbport.ini key.<input>= / pad.<input>= replace a default; no line keeps it.
CONTROLS = [
    ("cross", "Крест", "Space", "a"),
    ("circle", "Круг", "Left Shift", "b"),
    ("square", "Квадрат", "E", "x"),
    ("triangle", "Треугольник", "Q", "y"),
    ("l1", "L1", "1", "leftshoulder"),
    ("r1", "R1", "3", "rightshoulder"),
    ("l2", "L2", "R", "lefttrigger"),
    ("r2", "R2", "F", "righttrigger"),
    ("l3", "L3", "Z", "leftstick"),
    ("r3", "R3", "C", "rightstick"),
    ("options", "Options", "Return", "start"),
    ("touchpad", "Тачпад, левая половина (жесты)", "Tab", "back, touchpad"),
    ("touchpad_right", "Тачпад, правая половина (личные вещи)", "Backspace", ""),
    ("up", "Крестовина вверх", "I", "dpup"),
    ("down", "Крестовина вниз", "K", "dpdown"),
    ("left", "Крестовина влево", "J", "dpleft"),
    ("right", "Крестовина вправо", "L", "dpright"),
    ("move_up", "Движение вперёд", "W", None),
    ("move_down", "Движение назад", "S", None),
    ("move_left", "Движение влево", "A", None),
    ("move_right", "Движение вправо", "D", None),
    ("look_up", "Камера вверх", "Up", None),
    ("look_down", "Камера вниз", "Down", None),
    ("look_left", "Камера влево", "Left", None),
    ("look_right", "Камера вправо", "Right", None),
]


def connected_gamepads():
    """(GUID, name) of the connected gamepads (bb-gpu-capabilities --gamepads), [] if unknown."""
    tool = PORT_DIR / ("bin" if PACKAGED else "out") / "bb-gpu-capabilities"
    try:
        run = subprocess.run([str(tool), "--gamepads"], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return []
    return [tuple(line.split("\t", 1)) for line in run.stdout.splitlines() if "\t" in line]


class FolderList:
    """A preferences group with a folder row and one switch row per item below it."""

    def __init__(self, group):
        self.group = group
        self.rows = []

    def clear(self):
        for _, row in self.rows:
            self.group.remove(row)
        self.rows = []

    def add(self, key, row):
        self.group.add(row)
        self.rows.append((key, row))


class LauncherWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Bloodborne")
        self.set_default_size(1020, 640)
        self._load_custom_css()
        self.settings = load_settings()
        set_language(self.settings.get("ui_language", ""))
        self.ini, self.ini_lines = load_ini()
        self.process = None
        self.stream = None
        self.fsr411_build = None  # tools/fsr4cap/build_assets.sh while it runs
        self.pkg_process = None
        self.pkg_stream = None
        self.pkg_target_dir = None
        self.pkg_total_files = 0
        self.pkg_done_files = 0
        self.session_start = None
        self.playtime_timer_id = None

        act_extract = Gio.SimpleAction.new("extract_pkg", None)
        act_extract.connect("activate", lambda _a, _p: self.start_extract_pkg_dialog())
        self.add_action(act_extract)

        act_folder = Gio.SimpleAction.new("choose_game_folder", None)
        act_folder.connect("activate", lambda _a, _p: self.on_choose_game(None))
        self.add_action(act_folder)

        self.build()
        GLib.timeout_add_seconds(4, self.update_gamepad_indicator)
        self.connect("close-request", self.on_close)

    def _load_custom_css(self):
        css = b"""
        .transparent-header {
            background-color: transparent;
            background-image: none;
            border-bottom: 1px solid alpha(@window_fg_color, 0.08);
            box-shadow: none;
        }
        .transparent-toolbar {
            background-color: transparent;
            background-image: none;
        }
        .game-backdrop-scroller {
            background: transparent;
        }
        .hero-banner-card {
            background-color: alpha(@card_bg_color, 0.78);
            border: 1px solid alpha(@window_fg_color, 0.12);
            border-radius: 14px;
            padding: 20px 22px;
        }
        .clean-card-group > list,
        .quick-access-group > list {
            background-color: alpha(@card_bg_color, 0.78);
            border: 1px solid alpha(@window_fg_color, 0.10);
            border-radius: 12px;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def build(self):
        """(Re)creates the window's content in authentic GNOME HIG layout with full-window background."""
        root_overlay = Gtk.Overlay()

        # Window-wide blurred backdrop
        bg_path = PORT_DIR / "launcher" / "banner_bg.jpg"
        if not bg_path.is_file():
            bg_path = Path(__file__).resolve().parent / "banner_bg.jpg"
        if not bg_path.is_file():
            bg_path = PORT_DIR / "launcher" / "banner_blurred.jpg"

        if bg_path.is_file():
            bg_pic = Gtk.Picture.new_for_filename(str(bg_path))
            bg_pic.set_content_fit(Gtk.ContentFit.COVER)
            bg_pic.set_can_shrink(True)
            root_overlay.set_child(bg_pic)
        else:
            root_overlay.set_child(Gtk.Box())

        toolbar = Adw.ToolbarView()
        toolbar.add_css_class("transparent-toolbar")

        header = Adw.HeaderBar()
        header.add_css_class("transparent-header")

        # Start: Add PKG or Game Folder button (MenuButton)
        add_menu = Gio.Menu()
        add_menu.append(tr("Распаковать PS4 PKG…"), "win.extract_pkg")
        add_menu.append(tr("Выбрать папку с eboot.bin…"), "win.choose_game_folder")
        add_button = Gtk.MenuButton(
            icon_name="list-add-symbolic",
            tooltip_text=tr("Добавить PKG или игру…"),
            menu_model=add_menu,
            css_classes=["flat"]
        )
        header.pack_start(add_button)

        # Center: ViewSwitcher (Game vs Log)
        self.stack = Adw.ViewStack()
        switcher = Adw.ViewSwitcher(stack=self.stack, policy=Adw.ViewSwitcherPolicy.WIDE)
        header.set_title_widget(switcher)

        # End: Preferences button (opens AdwPreferencesDialog)
        prefs_button = Gtk.Button(icon_name="preferences-system-symbolic",
                                  tooltip_text=tr("Настройки") + " (Ctrl+,)",
                                  css_classes=["flat"])
        prefs_button.connect("clicked", lambda _b: self.open_preferences())
        header.pack_end(prefs_button)

        # Gamepad status button
        self.gamepad_btn = Gtk.Button(css_classes=["flat"])
        gamepad_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.gamepad_icon = Gtk.Image.new_from_icon_name("input-gaming-symbolic")
        self.gamepad_label = Gtk.Label()
        self.gamepad_label.add_css_class("caption")
        gamepad_box.append(self.gamepad_icon)
        gamepad_box.append(self.gamepad_label)
        self.gamepad_btn.set_child(gamepad_box)
        self.gamepad_btn.connect("clicked", lambda _b: self.open_preferences(page="controls"))
        header.pack_end(self.gamepad_btn)

        toolbar.add_top_bar(header)

        self.toasts = Adw.ToastOverlay()
        self.toasts.set_child(self.stack)
        toolbar.set_content(self.toasts)

        root_overlay.add_overlay(toolbar)
        self.set_content(root_overlay)

        # Build preferences dialog with all granular settings
        self.prefs_dialog = self.build_preferences_dialog()

        # Keyboard shortcut for Ctrl+,
        controller = Gtk.ShortcutController()
        controller.set_scope(Gtk.ShortcutScope.LOCAL)
        trigger = Gtk.ShortcutTrigger.parse_string("<Control>comma")
        action = Gtk.CallbackAction.new(lambda *_: self.open_preferences() or True)
        controller.add_shortcut(Gtk.Shortcut.new(trigger, action))
        self.add_controller(controller)

        log_text = self.log_view.get_buffer().get_text(
            *self.log_view.get_buffer().get_bounds(), False) if hasattr(self, "log_view") else ""

        self.achievement_box = AchievementBox(toast_overlay=self.toasts)
        self.achievement_box.set_hexpand(True)
        self.achievement_box.set_vexpand(True)

        self.stack.add_titled_with_icon(self.build_game_page(), "game", tr("Игра"),
                                        "input-gaming-symbolic")
        self.stack.add_titled_with_icon(self.build_trophies_page(), "trophies", tr("Трофеи"),
                                        "games-achievements-symbolic")
        self.stack.add_titled_with_icon(self.build_log_page(), "log", tr("Журнал"),
                                        "utilities-terminal-symbolic")
        self.log_view.get_buffer().set_text(log_text)

        self.update_launch_button()
        self.update_game_status()
        self.update_user_status()
        self.update_upscaler_status()
        self.update_pkg_status()
        self.update_gamepad_indicator()
        self.update_mods_quick_subtitle()

    def update_launch_button(self):
        running = self.process is not None
        pkg_busy = self.pkg_process is not None
        self.launch_button.set_label(tr("Остановить") if running else tr("Запустить"))
        self.launch_button.remove_css_class("destructive-action" if not running else "suggested-action")
        self.launch_button.add_css_class("destructive-action" if running else "suggested-action")
        self.launch_button.set_sensitive((self.fsr411_build is None) and not pkg_busy)
        if hasattr(self, "fsr411_button"):
            self.fsr411_button.set_sensitive(not running and not pkg_busy)

    def build_trophies_page(self):
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.add_css_class("game-backdrop-scroller")
        scroller.set_hexpand(True)
        scroller.set_vexpand(True)

        clamp = Adw.Clamp()
        clamp.set_maximum_size(960)
        clamp.set_tightening_threshold(780)
        clamp.set_margin_top(16)
        clamp.set_margin_bottom(20)
        clamp.set_margin_start(16)
        clamp.set_margin_end(16)
        clamp.set_child(self.achievement_box)

        scroller.set_child(clamp)
        return scroller

    def build_game_page(self):
        # Scrolled container for the page contents
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.add_css_class("game-backdrop-scroller")

        clamp = Adw.Clamp()
        clamp.set_maximum_size(860)
        clamp.set_tightening_threshold(680)
        clamp.set_margin_top(22)
        clamp.set_margin_bottom(24)
        clamp.set_margin_start(20)
        clamp.set_margin_end(20)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)

        # ── Hero Card ──
        hero_card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        hero_card.add_css_class("hero-banner-card")

        # Poster image (icon0.png)
        icon_path = self.game_dir() / "sce_sys" / "icon0.png"
        if not icon_path.is_file():
            candidates = [
                Path(__file__).resolve().parent / "icon0.png",
                PORT_DIR.parent / "CUSA03173" / "sce_sys" / "icon0.png",
                PORT_DIR / "CUSA03173" / "sce_sys" / "icon0.png",
                Path("/home/lowell/Games/bloodborne/CUSA03173/sce_sys/icon0.png"),
            ]
            for cand in candidates:
                if cand.is_file():
                    icon_path = cand
                    break
        if icon_path.is_file():
            self.poster = Gtk.Picture.new_for_filename(str(icon_path))
            self.poster.set_size_request(88, 88)
            self.poster.set_content_fit(Gtk.ContentFit.COVER)
            self.poster.add_css_class("card")
        else:
            self.poster = Gtk.Image.new_from_icon_name("package-x-generic-symbolic")
            self.poster.set_pixel_size(72)
            self.poster.add_css_class("card")
        hero_card.append(self.poster)

        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        info_box.set_hexpand(True)
        info_box.set_valign(Gtk.Align.CENTER)

        title_lbl = Gtk.Label(label="Bloodborne™", xalign=0)
        title_lbl.add_css_class("title-1")
        info_box.append(title_lbl)

        sub_lbl = Gtk.Label(label="CUSA03173 · v1.09 · FromSoftware", xalign=0)
        sub_lbl.add_css_class("subtitle")
        sub_lbl.add_css_class("dim-label")
        info_box.append(sub_lbl)

        tags_box = Gtk.Box(spacing=8)
        tags_box.set_margin_top(4)

        tag_fps = Gtk.Label(label=f"{self.settings['fps_mode']} FPS")
        tag_fps.add_css_class("caption")
        tag_fps.add_css_class("dim-label")
        tags_box.append(tag_fps)

        tag_sep = Gtk.Label(label="•")
        tag_sep.add_css_class("caption")
        tag_sep.add_css_class("dim-label")
        tags_box.append(tag_sep)

        tag_up = Gtk.Label(label=self.ini.get("upscaler", "fsr4").upper())
        tag_up.add_css_class("caption")
        tag_up.add_css_class("dim-label")
        tags_box.append(tag_up)

        tag_sep2 = Gtk.Label(label="•")
        tag_sep2.add_css_class("caption")
        tag_sep2.add_css_class("dim-label")
        tags_box.append(tag_sep2)

        tag_drv = Gtk.Label(label="Vulkan (X11)")
        tag_drv.add_css_class("caption")
        tag_drv.add_css_class("dim-label")
        tags_box.append(tag_drv)

        tag_sep3 = Gtk.Label(label="•")
        tag_sep3.add_css_class("caption")
        tag_sep3.add_css_class("dim-label")
        tags_box.append(tag_sep3)

        self.tag_playtime = Gtk.Label(label="⏱ 0m")
        self.tag_playtime.add_css_class("caption")
        self.tag_playtime.add_css_class("dim-label")
        tags_box.append(self.tag_playtime)
        self.update_playtime_label()

        info_box.append(tags_box)
        hero_card.append(info_box)

        self.launch_button = Gtk.Button(valign=Gtk.Align.CENTER)
        self.launch_button.add_css_class("suggested-action")
        self.launch_button.add_css_class("pill")
        self.launch_button.add_css_class("large-button")
        self.launch_button.connect("clicked", self.on_launch)
        hero_card.append(self.launch_button)

        content_box.append(hero_card)

        # ── 1. Game Files & Storage Group ──
        files_group = Adw.PreferencesGroup(title=tr("Файлы игры"))
        files_group.add_css_class("clean-card-group")

        # Game Directory Row
        self.game_row = Adw.ActionRow(title=tr("Папка игры"), activatable=True)
        self.game_row.connect("activated", self.on_choose_game)
        self.game_row.add_prefix(Gtk.Image.new_from_icon_name("folder-symbolic"))
        self.game_status = Gtk.Image()
        self.game_row.add_suffix(self.game_status)
        self.game_row.add_suffix(flat_button("folder-open-symbolic", tr("Выбрать папку с eboot.bin"),
                                             self.on_choose_game))
        self.game_row.add_suffix(flat_button("system-file-manager-symbolic",
                                             tr("Открыть в файловом менеджере"),
                                             lambda _b: open_folder(self, self.game_dir())))
        files_group.add(self.game_row)

        # Saves & Shaders Row
        self.user_row = Adw.ActionRow(title=tr("Папка сохранений"), activatable=True)
        self.user_row.connect("activated", self.on_choose_user)
        self.user_row.add_prefix(Gtk.Image.new_from_icon_name("drive-harddisk-symbolic"))
        self.user_status = Gtk.Image()
        self.user_row.add_suffix(self.user_status)
        self.user_row.add_suffix(flat_button("document-save-symbolic", tr("Создать резервную копию"),
                                             lambda _b: self.quick_backup_save()))
        self.user_row.add_suffix(flat_button("emblem-documents-symbolic", tr("Резервные копии сохранений"),
                                             lambda _b: self.open_save_backups_dialog()))
        self.user_row.add_suffix(flat_button("folder-open-symbolic", tr("Выбрать папку сохранений"),
                                             self.on_choose_user))
        self.user_row.add_suffix(flat_button("system-file-manager-symbolic",
                                             tr("Открыть в файловом менеджере"),
                                             lambda _b: open_folder(self, self.user_dir())))
        self.user_reset = flat_button("edit-undo-symbolic", tr("Вернуть папку по умолчанию"),
                                      self.on_reset_user)
        self.user_reset.set_visible(bool(self.settings.get("user_dir")))
        self.user_row.add_suffix(self.user_reset)
        files_group.add(self.user_row)

        content_box.append(files_group)

        # ── 2. Quick Access & Shortcuts Group ──
        quick = Adw.PreferencesGroup(title=tr("Быстрый доступ"))
        quick.add_css_class("clean-card-group")

        # Mods Quick Row
        mods_quick = Adw.ActionRow(title=tr("Моды"), subtitle=tr("Открыть папку модов игры"), activatable=True)
        mods_quick.add_prefix(Gtk.Image.new_from_icon_name("applications-games-symbolic"))
        mods_quick.add_suffix(flat_button("archive-insert-symbolic", tr("Установить мод из архива…"),
                                          lambda _b: self.on_install_mod_archive()))
        mods_quick.add_suffix(flat_button("system-file-manager-symbolic", tr("Открыть папку модов"),
                                          lambda _b: open_folder(self, self.mods_dir())))
        mods_quick.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
        mods_quick.connect("activated", lambda *_: self.open_preferences(page="mods"))
        quick.add(mods_quick)
        self.mods_quick = mods_quick

        # Patches & QoL Quick Row
        patches_quick = Adw.ActionRow(title=GLib.markup_escape_text(tr("Патчи и улучшения (QoL)")),
                                      subtitle=GLib.markup_escape_text(tr("60 FPS, исправления графики, камеры и производительности")),
                                      activatable=True)
        patches_quick.add_prefix(Gtk.Image.new_from_icon_name("applications-system-symbolic"))
        patches_quick.add_suffix(flat_button("software-update-available-symbolic",
                                             tr("Скачать свежие патчи с GitHub"),
                                             lambda _b: self.on_download_patches()))
        patches_quick.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
        patches_quick.connect("activated", lambda *_: self.open_preferences(page="patches"))
        quick.add(patches_quick)

        # PKG Extraction Row (Moved to Quick Access)
        self.pkg_row = Adw.ActionRow(title=tr("Распаковать PKG"),
                                     subtitle=tr("Извлечь игру или обновление из файла .pkg"),
                                     activatable=True)
        self.pkg_row.connect("activated", lambda *_: self.on_pkg_button_clicked())
        self.pkg_row.add_prefix(Gtk.Image.new_from_icon_name("package-x-generic-symbolic"))
        self.pkg_spinner = Gtk.Spinner()
        self.pkg_spinner.set_visible(False)
        self.pkg_row.add_suffix(self.pkg_spinner)
        self.pkg_button = flat_button("archive-extract-symbolic", tr("Распаковать PS4 PKG"),
                                      lambda _b: self.on_pkg_button_clicked())
        self.pkg_row.add_suffix(self.pkg_button)
        self.pkg_row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
        quick.add(self.pkg_row)

        # Trophies Quick Row
        trophies_quick = Adw.ActionRow(title=tr("Трофеи и достижения"),
                                       subtitle=tr("Отслеживание платины и достижений"),
                                       activatable=True)
        trophies_quick.add_prefix(Gtk.Image.new_from_icon_name("games-achievements-symbolic"))
        trophies_quick.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
        trophies_quick.connect("activated", lambda *_: self.stack.set_visible_child_name("trophies"))
        quick.add(trophies_quick)

        # Settings Quick Row
        settings_quick = Adw.ActionRow(title=tr("Настройки графики и контроллера"),
                                       subtitle=tr("Разрешение, FSR, геймпад и клавиши"),
                                       activatable=True)
        settings_quick.add_prefix(Gtk.Image.new_from_icon_name("video-display-symbolic"))
        settings_quick.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
        settings_quick.connect("activated", lambda *_: self.open_preferences())
        quick.add(settings_quick)

        content_box.append(quick)

        clamp.set_child(content_box)
        scroller.set_child(clamp)
        return scroller

    def build_preferences_dialog(self):
        dialog = Adw.PreferencesDialog()
        dialog.set_title(tr("Настройки"))
        dialog.set_search_enabled(True)

        # 1. Page: Display & Graphics
        display_page = Adw.PreferencesPage(title=tr("Экран и графика"),
                                           icon_name="video-display-symbolic")

        screen = Adw.PreferencesGroup(title=tr("Экран"))
        self.output_row = combo_row(tr("Разрешение вывода"),
                                    tr("Апскейлер дорисовывает кадр; Steam Deck — 720p"),
                                    OUTPUT_RES, self.ini.get("output_res", "1920x1080"))
        screen.add(self.output_row)
        self.live_row = combo_row(tr("Смена разрешения на лету"),
                                  tr("Без перезапуска, но медленнее на Steam Deck и старых GPU"),
                                  LIVE_RESOLUTION, self.ini.get("live_resolution", "0"))
        screen.add(self.live_row)
        self.fullscreen_row = Adw.SwitchRow(title=tr("Полноэкранный режим"),
                                            active=self.settings["fullscreen"])
        screen.add(self.fullscreen_row)
        self.present_row = combo_row(tr("Режим показа кадров"), None, PRESENT_MODES,
                                     self.settings["present_mode"])
        screen.add(self.present_row)
        self.hdr_row = Adw.SwitchRow(title=tr("Разрешить HDR"), active=self.settings["hdr"])
        screen.add(self.hdr_row)
        display_page.add(screen)

        upscaler = Adw.PreferencesGroup(
            title=tr("Апскейлер"),
            description=tr("Хранится в bbport.ini; в игре меняется через меню (Insert или L3+R3)"))
        self.upscaler_row = combo_row(tr("Апскейлер"), None, UPSCALERS, self.ini["upscaler"])
        self.upscaler_row.connect("notify::selected", lambda *_: self.update_upscaler_status())
        upscaler.add(self.upscaler_row)
        self.fsr411_row = Adw.ActionRow(title=tr("FSR 4.1.1 из своей DLL AMD"))
        self.fsr411_button = Gtk.Button(valign=Gtk.Align.CENTER)
        self.fsr411_button.connect("clicked", self.on_fsr411_button)
        self.fsr411_row.add_suffix(self.fsr411_button)
        self.fsr411_row.set_visible((FSR4CAP_DIR / "build_assets.sh").is_file())
        upscaler.add(self.fsr411_row)
        self.update_fsr411_row()
        self.preset_row = combo_row(tr("Пресет"), None, PRESETS, int(self.ini.get("preset", "4")))
        self.preset_row.connect("notify::selected", lambda *_: self.update_upscaler_status())
        self.output_row.connect("notify::selected", lambda *_: self.update_upscaler_status())
        upscaler.add(self.preset_row)
        self.frame_gen_row = combo_row(
            tr("Генерация кадров"),
            tr("DLSS FG (RTX 40+) или FSR 3.1 FG ×2; удваивает FPS отображения"),
            FRAME_GENERATION,
            self.ini.get("frame_generation", "off"))
        upscaler.add(self.frame_gen_row)
        self.dlss_preset_row = combo_row(
            tr("Пресет модели DLSS"),
            tr("Выбор нейросетевой модели DLSS (Transformer / CNN)"),
            DLSS_PRESETS,
            self.ini.get("dlss_preset", "auto"))
        upscaler.add(self.dlss_preset_row)
        self.sharpen_row = Adw.SwitchRow(title=tr("Резкость (RCAS)"),
                                         active=self.ini.get("sharpen") == "1")
        upscaler.add(self.sharpen_row)
        self.sharpness_row = Adw.SpinRow.new_with_range(0.0, 2.0, 0.05)
        self.sharpness_row.set_title(tr("Сила резкости"))
        self.sharpness_row.set_digits(2)
        self.sharpness_row.set_value(float(self.ini.get("sharpness", "0.5")))
        upscaler.add(self.sharpness_row)
        self.motion_row = Adw.SwitchRow(
            title=tr("Векторы движения объектов"),
            subtitle=tr("Меньше гостинга на персонажах; стоит около 10% FPS"),
            active=self.ini.get("object_motion") == "1")
        upscaler.add(self.motion_row)
        self.show_fps_row = Adw.SwitchRow(title=tr("Показывать FPS"),
                                          active=self.ini.get("show_fps") == "1")
        upscaler.add(self.show_fps_row)
        display_page.add(upscaler)

        frames = Adw.PreferencesGroup(title=tr("Частота кадров"))
        self.fps_row = combo_row(tr("Режим"), tr("Какой патч частоты кадров применить к игре"),
                                 FPS_MODES, self.settings["fps_mode"])
        frames.add(self.fps_row)
        self.limit_row = Adw.SpinRow.new_with_range(0, 480, 1)
        self.limit_row.set_title(tr("Ограничение FPS"))
        self.limit_row.set_subtitle(tr("0 — без ограничения; укажите число, чтобы ограничить FPS"))
        self.limit_row.set_value(self.settings["fps_limit"])
        frames.add(self.limit_row)
        display_page.add(frames)

        effects = Adw.PreferencesGroup(title=tr("Эффекты игры"),
                                       description=tr("Патчи игры, применяются при запуске"))
        self.lod_row = combo_row(tr("Детализация моделей"), None, MODEL_LOD,
                                 self.ini.get("model_lod", "0"))
        effects.add(self.lod_row)
        self.effect_rows = {}
        for key, title, default in EFFECTS:
            row = Adw.SwitchRow(title=tr(title),
                                active=self.ini.get(key, "1" if default else "0") == "1")
            if key == "debug_menu":
                row.set_subtitle(tr("Установите DbgFont14h.ccm и DbgFont14h.tpf в dvdroot_ps4/font "
                                    "из мода Nexus #253"))
            self.effect_rows[key] = row
            effects.add(row)
        display_page.add(effects)
        dialog.add(display_page)

        # 2. Page: Controls
        controls_page = Adw.PreferencesPage(title=tr("Управление"),
                                            icon_name="input-gaming-symbolic")
        controls = Adw.PreferencesGroup(title=tr("Контроллер"))
        self.gamepad_row = Adw.ComboRow(title=tr("Контроллер"))
        self.gamepad_row.connect("notify::selected", lambda *_: self.show_gamepad())
        self.gamepad_row.add_suffix(flat_button("view-refresh-symbolic", tr("Обновить список"),
                                                lambda _button: self.fill_gamepads()))
        self.fill_gamepads()
        controls.add(self.gamepad_row)
        self.control_rows = {}
        for kind, title, icon in (("key", tr("Клавиатура"), "input-keyboard-symbolic"),
                                  ("pad", tr("Геймпад"), "input-gaming-symbolic")):
            expander = Adw.ExpanderRow(title=title,
                                       subtitle=tr("Назначение кнопок; применяется при запуске игры"))
            for name, label, key_default, pad_default in CONTROLS:
                default = key_default if kind == "key" else pad_default
                if default is None:
                    continue
                row = Adw.ActionRow(title=tr(label))
                row.add_suffix(flat_button(icon, tr("Назначить"),
                                           lambda _b, k=kind, n=name: self.assign_control(k, n)))
                row.add_suffix(flat_button("edit-undo-symbolic", tr("Сбросить"),
                                           lambda _b, k=kind, n=name: self.set_control(k, n, None)))
                expander.add_row(row)
                self.control_rows[(kind, name)] = (row, default)
                self.show_control(kind, name)
            controls.add(expander)
        controls_page.add(controls)
        dialog.add(controls_page)

        # 3. Page: Mods & Patches
        mods_page = Adw.PreferencesPage(title=tr("Моды и патчи"),
                                        icon_name="applications-games-symbolic")
        self.mods_group = Adw.PreferencesGroup(
            title=tr("Моды"), description=tr(
                "Распакуйте каждый мод в отдельную папку (с dvdroot_ps4 или сразу с chr/, parts/ и т. п.). "
                "При совпадении файлов побеждает мод ниже в списке. Применяется при запуске."))
        self.mods_enabled_row = Adw.SwitchRow(title=tr("Загружать моды"),
                                               active=self.settings["mods_enabled"])
        self.mods_group.add(self.mods_enabled_row)
        self.mods_folder_row = Adw.ActionRow(title=tr("Папка модов"))
        self.mods_folder_row.add_suffix(flat_button("archive-insert-symbolic", tr("Установить мод из архива…"),
                                                    self.on_install_mod_archive))
        self.mods_folder_row.add_suffix(flat_button("folder-open-symbolic", tr("Выбрать папку модов"),
                                                    self.on_choose_mods))
        self.mods_folder_row.add_suffix(flat_button("system-file-manager-symbolic", tr("Открыть папку модов"),
                                                    lambda _b: open_folder(self, self.mods_dir())))
        self.mods_folder_row.add_suffix(flat_button("view-refresh-symbolic", tr("Обновить список"),
                                                    self.on_refresh_mods))
        self.mods_group.add(self.mods_folder_row)
        self.mod_list = FolderList(self.mods_group)
        self.refresh_mods()
        mods_page.add(self.mods_group)

        self.patches_group = Adw.PreferencesGroup(
            title=tr("Сторонние патчи"),
            description=tr("XML-патчи в формате shadPS4 для версии 01.09 из папки патчей. "
                           "Применяются при запуске."))
        self.patches_folder_row = Adw.ActionRow(title=tr("Папка патчей"))
        self.patches_folder_row.add_suffix(flat_button("software-update-available-symbolic",
                                                       tr("Скачать свежие патчи с GitHub"),
                                                       lambda _b: self.on_download_patches()))
        self.patches_folder_row.add_suffix(flat_button("folder-open-symbolic", tr("Выбрать папку патчей"),
                                                       self.on_choose_patches))
        self.patches_folder_row.add_suffix(flat_button(
            "system-file-manager-symbolic", tr("Открыть папку патчей"),
            lambda _b: open_folder(self, patches_dir(self.settings))))
        self.patches_folder_row.add_suffix(flat_button("view-refresh-symbolic", tr("Обновить список"),
                                                       self.on_refresh_patches))
        self.patches_group.add(self.patches_folder_row)
        self.patch_list = FolderList(self.patches_group)
        self.refresh_patches()
        mods_page.add(self.patches_group)
        dialog.add(mods_page)

        # 4. Page: System & Advanced
        system_page = Adw.PreferencesPage(title=tr("Система"),
                                          icon_name="preferences-system-symbolic")
        launcher = Adw.PreferencesGroup(title=tr("Интерфейс"))
        self.ui_language_row = combo_row(tr("Язык лаунчера") + " / Launcher language", None,
                                         UI_LANGUAGES, self.settings.get("ui_language", ""))
        self.ui_language_row.connect("notify::selected", self.on_ui_language)
        launcher.add(self.ui_language_row)
        self.language_row = combo_row(tr("Язык системы"), None, LANGUAGES, self.settings["language"])
        launcher.add(self.language_row)
        system_page.add(launcher)

        mode = Adw.PreferencesGroup(title=tr("Режим работы"))
        self.pc_model_row = Adw.SwitchRow(
            title=tr("Новая модель памяти и трансляции"),
            subtitle=tr(PC_MODEL_SUBTITLE if AMD_GPU is not False else PC_MODEL_NO_AMD),
            active=self.settings.get("pc_model", False) and AMD_GPU is not False)
        self.pc_model_row.set_sensitive(AMD_GPU is not False)
        mode.add(self.pc_model_row)
        system_page.add(mode)

        perf = Adw.PreferencesGroup(title=tr("Производительность"))
        self.pipe_row = combo_row(
            tr("Двухстадийный конвейер GPU"),
            tr("Быстрее на 20–30%; при нестабильности выключите"), DRAW_PIPE,
            self.settings["draw_pipe"])
        perf.add(self.pipe_row)
        self.readbacks_row = combo_row(tr("Чтение данных GPU процессором"), None, READBACKS,
                                       self.settings["readbacks"])
        perf.add(self.readbacks_row)
        self.preupload_row = combo_row(
            tr("Фоновая загрузка в видеопамять"),
            tr("Меньше рывков при подгрузке зон"), PREUPLOAD,
            self.settings.get("preupload", ""))
        perf.add(self.preupload_row)
        system_page.add(perf)

        dev = Adw.PreferencesGroup(title=tr("Для разработчика"))
        self.mangohud_row = Adw.SwitchRow(title="MangoHud", active=self.settings["mangohud"])
        dev.add(self.mangohud_row)
        self.save_log_row = Adw.SwitchRow(
            title=tr("Сохранять журнал и статистику в файл"),
            subtitle=tr("В папку logs в каталоге данных: для разбора рывков и вылетов"),
            active=self.settings.get("save_log", False))
        dev.add(self.save_log_row)
        self.crash_diag_row = Adw.SwitchRow(
            title=tr("Диагностика вылетов"),
            subtitle=tr("Проверяет кучу игры и записывает записи в её память; немного медленнее"),
            active=self.settings.get("crash_diag", False))
        dev.add(self.crash_diag_row)
        self.as_0_3_row = Adw.SwitchRow(
            title=tr("Синхронизация как в 0.3"),
            subtitle=tr("Для поиска регрессий: старая модель памяти и ожидания копий как в релизе 0.3"),
            active=self.settings.get("as_0_3", False))
        dev.add(self.as_0_3_row)
        self.stats_row = Adw.SwitchRow(title=tr("Статистика кадров в журнале"),
                                       subtitle="BB_FRAME_STATS",
                                       active=self.settings["frame_stats"])
        dev.add(self.stats_row)
        self.profile_row = Adw.SwitchRow(title=tr("Профиль GPU в журнале"),
                                          subtitle="BB_GPU_PROFILE",
                                          active=self.settings["gpu_profile"])
        dev.add(self.profile_row)
        self.validation_row = Adw.SwitchRow(title=tr("Слои валидации Vulkan"),
                                            subtitle=tr("Сильно замедляет"),
                                            active=self.settings["vk_validation"])
        dev.add(self.validation_row)
        self.extra_row = Adw.EntryRow(title=tr("Доп. переменные (ИМЯ=значение через пробел)"),
                                      text=self.settings["extra_env"])
        dev.add(self.extra_row)
        system_page.add(dev)

        dialog.add(system_page)
        self.prefs_pages = {
            "display": display_page,
            "controls": controls_page,
            "mods": mods_page,
            "patches": mods_page,
            "system": system_page,
        }
        return dialog

    def open_preferences(self, page=None):
        if hasattr(self, "prefs_dialog") and self.prefs_dialog:
            if page and hasattr(self, "prefs_pages") and page in self.prefs_pages:
                self.prefs_dialog.set_visible_page(self.prefs_pages[page])
            self.prefs_dialog.present(self)

    def on_add_game_or_pkg(self, _button=None):
        self.start_extract_pkg_dialog()

    def on_pkg_button_clicked(self):
        if self.pkg_process:
            self.stop_pkg_extraction()
        else:
            self.start_extract_pkg_dialog()

    def update_pkg_status(self):
        if not hasattr(self, "pkg_row") or not self.pkg_row:
            return
        running = self.pkg_process is not None
        if running:
            self.pkg_spinner.set_visible(True)
            self.pkg_spinner.start()
            self.pkg_button.set_icon_name("process-stop-symbolic")
            self.pkg_button.set_tooltip_text(tr("Отменить распаковку"))
            self.pkg_button.add_css_class("destructive-action")
            self.pkg_button.remove_css_class("flat")
            if self.pkg_total_files > 0:
                pct = (self.pkg_done_files / self.pkg_total_files) * 100.0
                self.pkg_row.set_subtitle(
                    tr("Распаковка: {:.1f}% ({}/{})").format(pct, self.pkg_done_files, self.pkg_total_files))
            else:
                self.pkg_row.set_subtitle(tr("Идёт распаковка PKG…"))
        else:
            self.pkg_spinner.stop()
            self.pkg_spinner.set_visible(False)
            self.pkg_button.set_icon_name("archive-extract-symbolic")
            self.pkg_button.set_tooltip_text(tr("Распаковать PS4 PKG"))
            self.pkg_button.remove_css_class("destructive-action")
            self.pkg_button.add_css_class("flat")
            self.pkg_row.set_subtitle(tr("Извлечь игру или обновление из файла .pkg"))
        self.update_launch_button()

    def start_extract_pkg_dialog(self):
        if self.pkg_process:
            self.toasts.add_toast(Adw.Toast(title=tr("Идёт распаковка PKG…")))
            return
        dialog = Gtk.FileDialog(title=tr("Выберите PS4 PKG для распаковки"))
        pkg_filter = Gtk.FileFilter()
        pkg_filter.set_name("PS4 PKG (*.pkg)")
        pkg_filter.add_pattern("*.pkg")
        pkg_filter.add_pattern("*.PKG")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(pkg_filter)
        dialog.set_filters(filters)
        dialog.set_default_filter(pkg_filter)

        def on_pkg_chosen(f_dialog, result):
            try:
                chosen = f_dialog.open_finish(result)
            except GLib.Error:
                return
            if not chosen or not chosen.get_path():
                return
            pkg_path = chosen.get_path()

            # Now prompt for target games folder
            folder_dialog = Gtk.FileDialog(title=tr("Выберите папку для распаковки игры"))
            def_target = self.game_dir().parent if self.game_dir().exists() else PORT_DIR.parent
            if def_target.is_dir():
                folder_dialog.set_initial_folder(Gio.File.new_for_path(str(def_target)))

            def on_folder_chosen(fold_dialog, f_result):
                try:
                    chosen_folder = fold_dialog.select_folder_finish(f_result)
                except GLib.Error:
                    return
                if not chosen_folder or not chosen_folder.get_path():
                    return
                dest_dir = chosen_folder.get_path()
                self.extract_pkg(pkg_path, dest_dir)

            folder_dialog.select_folder(self, None, on_folder_chosen)

        dialog.open(self, None, on_pkg_chosen)

    def extract_pkg(self, pkg_path, dest_dir):
        if not PKG_EXTRACTOR_PATH.is_file():
            self.alert(tr("Ошибка"), tr("Экстрактор PKG не найден: {}").format(PKG_EXTRACTOR_PATH))
            return
        try:
            os.chmod(str(PKG_EXTRACTOR_PATH), 0o755)
        except OSError:
            pass

        dest_path = Path(dest_dir)
        dest_path.mkdir(parents=True, exist_ok=True)

        self.pkg_target_dir = dest_path
        self.pkg_file_name = Path(pkg_path).name
        self.pkg_total_files = 0
        self.pkg_done_files = 0

        self.append_log(f"\n— {tr('Извлечение PKG: {}').format(self.pkg_file_name)} —\n")
        self.append_log(f"PKG: {pkg_path}\nDestination: {dest_dir}\n\n")
        self.toasts.add_toast(Adw.Toast(title=tr("Извлечение PKG: {}").format(self.pkg_file_name)))
        self.stack.set_visible_child_name("log")

        launcher = Gio.SubprocessLauncher.new(
            Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_MERGE
        )
        command = [
            "setsid", "bash", "-c", 'exec "$@" < /dev/null', "_",
            str(PKG_EXTRACTOR_PATH), str(pkg_path), str(dest_dir)
        ]
        try:
            self.pkg_process = launcher.spawnv(command)
        except GLib.Error as error:
            self.toasts.add_toast(Adw.Toast(title=tr("Не удалось запустить: {}").format(error.message)))
            self.pkg_process = None
            return

        self.pkg_stream = Gio.DataInputStream.new(self.pkg_process.get_stdout_pipe())
        self.read_pkg_line()
        self.pkg_process.wait_async(None, self.on_pkg_exit)
        self.update_pkg_status()

    def read_pkg_line(self):
        if self.pkg_stream:
            self.pkg_stream.read_line_async(GLib.PRIORITY_DEFAULT, None, self.on_pkg_line)

    def on_pkg_line(self, stream, result):
        try:
            line, _length = stream.read_line_finish_utf8(result)
        except GLib.Error:
            return
        if line is None:
            return
        self.append_log(line + "\n")
        m = re.search(r"Extracting file\s+(\d+)/(\d+)", line)
        if m:
            self.pkg_done_files = int(m.group(1))
            self.pkg_total_files = int(m.group(2))
            self.update_pkg_status()
        self.read_pkg_line()

    def stop_pkg_extraction(self):
        if not self.pkg_process:
            return
        pid = int(self.pkg_process.get_identifier())
        try:
            os.killpg(pid, signal.SIGTERM)
        except OSError:
            self.pkg_process.force_exit()
        self.toasts.add_toast(Adw.Toast(title=tr("Распаковка отменена")))
        self.append_log(tr("\n— распаковка PKG отменена пользователем —\n"))

    def on_pkg_exit(self, process, result):
        try:
            process.wait_finish(result)
        except GLib.Error:
            pass
        status = process.get_exit_status() if process.get_if_exited() else -1
        self.pkg_process = None
        self.pkg_stream = None
        self.update_pkg_status()

        if status == 0:
            self.append_log(tr("\n— Распаковка PKG успешно завершена —\n"))
            # Auto-detect extracted game directory
            cand = None
            target = self.pkg_target_dir
            if target:
                if (target / "CUSA03173" / "eboot.bin").is_file():
                    cand = target / "CUSA03173"
                elif (target / "eboot.bin").is_file():
                    cand = target
                else:
                    for found in target.rglob("eboot.bin"):
                        cand = found.parent
                        break
            if cand:
                self.settings["game_dir"] = str(cand)
                self.update_game_status()
                self.store()
                self.toasts.add_toast(Adw.Toast(title=tr("PKG успешно извлечён в {}").format(cand)))
            else:
                self.toasts.add_toast(Adw.Toast(title=tr("PKG успешно извлечён в {}").format(target or "")))
        else:
            self.append_log(tr("\n— Ошибка извлечения PKG (код {}) —\n").format(status))
            self.toasts.add_toast(Adw.Toast(title=tr("Ошибка извлечения PKG (код {})").format(status)))

    def on_ui_language(self, row, _param):
        choice = combo_value(row)
        if choice == self.settings.get("ui_language", ""):
            return
        self.store()
        self.settings["ui_language"] = choice
        save_settings(self.settings)
        if self.process:
            # The log keeps streaming into the current page; rebuild on the next start.
            set_language(choice)
            self.toasts.add_toast(Adw.Toast(
                title=tr("Применится после перезапуска лаунчера, пока игра запущена")))
            return
        set_language(choice)
        # After this handler returns: the row that emitted the signal is replaced.
        GLib.idle_add(lambda: self.build() and False)

    def game_dir(self):
        return Path(self.settings["game_dir"]).expanduser()

    def user_dir(self):
        return Path(self.settings["user_dir"]).expanduser() if self.settings["user_dir"] \
            else DATA_DIR / "user"

    def update_user_status(self):
        path = self.user_dir()
        custom = bool(self.settings["user_dir"])
        self.user_row.set_subtitle(str(path) if custom else tr("По умолчанию: {}").format(path))
        saves = path / "savedata"
        found = saves.is_dir() and any(saves.iterdir())
        self.user_status.set_from_icon_name("object-select-symbolic" if found else "document-new-symbolic")
        self.user_status.set_tooltip_text(tr("Найдены сохранения") if found
                                          else tr("Сохранений пока нет: игра создаст их здесь"))
        self.user_reset.set_visible(custom)
        self.user_reset.set_sensitive(custom)

    def choose_folder(self, title, current, done):
        dialog = Gtk.FileDialog(title=title)
        if Path(current).is_dir():
            dialog.set_initial_folder(Gio.File.new_for_path(str(current)))

        def finish(dialog, result):
            try:
                folder = dialog.select_folder_finish(result)
            except GLib.Error:
                return
            if folder:
                done(folder.get_path())
        dialog.select_folder(self, None, finish)

    def on_choose_user(self, _button):
        def chosen(path):
            self.settings["user_dir"] = path
            self.update_user_status()
            self.store()
        self.choose_folder(tr("Папка сохранений"), self.user_dir(), chosen)

    def on_reset_user(self, _button):
        self.settings["user_dir"] = ""
        self.update_user_status()
        self.store()

    def quick_backup_save(self, refresh_callback=None):
        saves_dir = self.user_dir() / "savedata"
        if not saves_dir.is_dir() or not any(saves_dir.iterdir()):
            self.toasts.add_toast(Adw.Toast(title=tr("Папка сохранений пуста")))
            return

        backups_root = self.user_dir() / "backups"
        backups_root.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dest = backups_root / f"save_{ts}"
        try:
            shutil.copytree(saves_dir, dest)
            self.toasts.add_toast(Adw.Toast(title=tr("Резервная копия создана: {}").format(dest.name)))
            if refresh_callback:
                refresh_callback()
        except Exception as e:
            self.toasts.add_toast(Adw.Toast(title=f"Backup error: {e}"))

    def restore_save_backup(self, backup_path, on_done=None):
        saves_dir = self.user_dir() / "savedata"
        if not backup_path.is_dir():
            return
        if saves_dir.is_dir() and any(saves_dir.iterdir()):
            safety_ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            safety_dir = self.user_dir() / "backups" / f"auto_safety_{safety_ts}"
            try:
                shutil.copytree(saves_dir, safety_dir)
            except Exception:
                pass

        try:
            if saves_dir.is_dir():
                shutil.rmtree(saves_dir)
            shutil.copytree(backup_path, saves_dir)
            self.update_user_status()
            self.toasts.add_toast(Adw.Toast(title=tr("Сохранение восстановлено из {}").format(backup_path.name)))
            if on_done:
                on_done()
        except Exception as e:
            self.toasts.add_toast(Adw.Toast(title=f"Restore error: {e}"))

    def delete_save_backup(self, backup_path, refresh_callback=None):
        try:
            if backup_path.is_dir():
                shutil.rmtree(backup_path)
            self.toasts.add_toast(Adw.Toast(title=tr("Резервная копия удалена")))
            if refresh_callback:
                refresh_callback()
        except Exception as e:
            self.toasts.add_toast(Adw.Toast(title=f"Delete error: {e}"))

    def open_save_backups_dialog(self):
        dlg = Adw.PreferencesDialog()
        dlg.set_title(tr("Резервные копии сохранений"))
        page = Adw.PreferencesPage()
        dlg.add(page)

        header_grp = Adw.PreferencesGroup()
        create_row = Adw.ActionRow(title=tr("Создать резервную копию"),
                                   subtitle=tr("Сохранить текущее состояние игры"),
                                   activatable=True)
        create_row.add_prefix(Gtk.Image.new_from_icon_name("document-new-symbolic"))
        create_row.add_suffix(flat_button("list-add-symbolic", tr("Создать"),
                                          lambda _b: self.quick_backup_save(refresh_list)))
        create_row.connect("activated", lambda *_: self.quick_backup_save(refresh_list))
        header_grp.add(create_row)
        page.add(header_grp)

        list_grp = Adw.PreferencesGroup(title=tr("Резервные копии"))
        page.add(list_grp)

        backup_rows = []

        def get_dir_size(path):
            total = 0
            for root, dirs, files in os.walk(path):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        total += os.path.getsize(fp)
                    except OSError:
                        pass
            return total

        def format_bytes(b):
            if b < 1024:
                return f"{b} B"
            elif b < 1024 * 1024:
                return f"{b / 1024:.1f} KB"
            return f"{b / (1024 * 1024):.1f} MB"

        def refresh_list():
            for r in backup_rows:
                list_grp.remove(r)
            backup_rows.clear()

            backups_root = self.user_dir() / "backups"
            candidates = []
            if backups_root.is_dir():
                for p in backups_root.iterdir():
                    if p.is_dir():
                        candidates.append(p)
            candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)

            if not candidates:
                empty_row = Adw.ActionRow(title=tr("Нет резервных копий"),
                                          subtitle=tr("Создайте резервную копию перед битвой с боссом"))
                empty_row.add_prefix(Gtk.Image.new_from_icon_name("folder-symbolic"))
                list_grp.add(empty_row)
                backup_rows.append(empty_row)
                return

            for p in candidates:
                mtime_str = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                size_str = format_bytes(get_dir_size(p))
                row = Adw.ActionRow(title=p.name, subtitle=f"{mtime_str} · {size_str}")
                row.add_prefix(Gtk.Image.new_from_icon_name("document-save-symbolic"))
                btn_rst = flat_button("edit-undo-symbolic", tr("Восстановить"),
                                      lambda _b, path=p: self.restore_save_backup(path, dlg.close))
                btn_del = flat_button("user-trash-symbolic", tr("Удалить"),
                                      lambda _b, path=p: self.delete_save_backup(path, refresh_list))
                row.add_suffix(btn_rst)
                row.add_suffix(btn_del)
                list_grp.add(row)
                backup_rows.append(row)

        refresh_list()
        dlg.present(self)

    def update_upscaler_status(self):
        value = combo_value(self.upscaler_row)
        if value == "fsr4":
            ok = (PORT_DIR / "fsr4_shaders").is_dir()
            hint = tr("Ассеты найдены") if ok else tr("Нет ассетов: tools/fetch_fsr4_assets.sh")
        elif value == "fsr411":
            directory = fsr411_dir()
            problem = fsr411_problem(directory, combo_value(self.output_row),
                                     int(combo_value(self.preset_row)))
            hint = tr("Ассеты для выбранного режима найдены") if not problem else (
                tr("{}. Соберите FSR 4.1.1 из своей DLL кнопкой «Выбрать DLL…» ниже").format(problem))
        else:
            hint = tr("Сглаживание в разрешении вывода без модели FSR") if value == "taa" else None
        self.preset_row.set_sensitive(value not in ("taa", "off"))
        self.sharpen_row.set_sensitive(value != "off")
        self.sharpness_row.set_sensitive(value != "off")
        self.upscaler_row.set_subtitle(hint or "")

    def game_problem(self, path):
        """game_check.problem for the folder, kept until its eboot.bin or param.sfo changes (the
        image hash reads ~90 MB)."""
        try:
            key = (str(path),) + tuple(
                (f.stat().st_size, f.stat().st_mtime_ns) for f in (path / "eboot.bin", path / "sce_sys/param.sfo"))
        except OSError:
            key = (str(path),)
        if getattr(self, "_game_problem_key", None) != key:
            self._game_problem_key = key
            self._game_problem = game_check.problem(path)
        return self._game_problem

    def update_game_status(self):
        path = self.game_dir()
        ok = bool(self.settings["game_dir"]) and (path / "eboot.bin").is_file()
        self.game_row.set_subtitle(str(path) if self.settings["game_dir"] else tr("не выбрана"))
        # Other versions of the game start and then crash in its code (issues #7, #13, #14).
        problem = self.game_problem(path) if ok else None
        if not ok:
            tooltip = tr("Нет eboot.bin в папке")
        elif problem:
            kind, title, version = problem
            tooltip = {
                "missing_update": tr("Нужно обновление 1.09: скопируйте файлы дампа обновления 1.09 в папку игры с заменой (найдена версия {})").format(version),
                "wrong_eboot": tr("eboot.bin не от версии 1.09: скопируйте eboot.bin из дампа обновления 1.09 в папку игры с заменой"),
                "other_title": tr("Поддерживается только CUSA03173 с обновлением 1.09 (найдено {})").format(title),
                "unreadable": tr("eboot.bin не читается как расшифрованный исполняемый файл PS4: сделайте дамп заново"),
            }[kind]
            self.game_row.set_subtitle(f"{path}\n{tooltip}")
        else:
            tooltip = tr("Bloodborne CUSA03173, версия 1.09")
        self.game_status.set_from_icon_name("object-select-symbolic" if ok and not problem else "dialog-warning-symbolic")
        self.game_status.set_tooltip_text(tooltip)
        self.launch_button.set_sensitive(ok or self.process is not None)

        # Refresh poster icon
        icon_path = self.game_dir() / "sce_sys" / "icon0.png"
        if not icon_path.is_file():
            candidates = [
                Path(__file__).resolve().parent / "icon0.png",
                PORT_DIR.parent / "CUSA03173" / "sce_sys" / "icon0.png",
                PORT_DIR / "CUSA03173" / "sce_sys" / "icon0.png",
                Path("/home/lowell/Games/bloodborne/CUSA03173/sce_sys/icon0.png"),
            ]
            for cand in candidates:
                if cand.is_file():
                    icon_path = cand
                    break
        if hasattr(self, "poster") and self.poster and icon_path.is_file() and isinstance(self.poster, Gtk.Picture):
            self.poster.set_filename(str(icon_path))

    def on_choose_game(self, _button):
        def chosen(path):
            self.settings["game_dir"] = path
            self.update_game_status()
            self.store()
        self.choose_folder(tr("Папка игры (с eboot.bin)"), self.game_dir(), chosen)

    def show_control(self, kind, name):
        row, default = self.control_rows[(kind, name)]
        value = self.ini.get(f"{kind}.{name}")
        if value is None:
            row.set_subtitle(tr("{} (по умолчанию)").format(default) if default else tr("не назначено"))
        else:
            row.set_subtitle(value or tr("не назначено"))

    def set_control(self, kind, name, value):
        """value: the binding, or None for the default."""
        self.ini[f"{kind}.{name}"] = value
        self.show_control(kind, name)
        self.store()

    def assign_control(self, kind, name):
        tool = PORT_DIR / ("bin" if PACKAGED else "out") / "bb-gpu-capabilities"
        try:
            process = Gio.Subprocess.new([str(tool), "--read-input", kind],
                                         Gio.SubprocessFlags.STDOUT_PIPE)
        except GLib.Error as error:
            self.toasts.add_toast(Adw.Toast(title=tr("Не удалось запустить: {}").format(error.message)))
            return
        row, _default = self.control_rows[(kind, name)]
        row.set_subtitle(tr("Нажмите клавишу или кнопку… (Esc — отмена)"))

        def done(proc, result):
            try:
                _ok, out, _err = proc.communicate_utf8_finish(result)
            except GLib.Error:
                out = ""
            words = (out or "").strip().split(" ", 1)
            if len(words) == 2 and words[0] == kind:
                self.set_control(kind, name, words[1])
            else:
                self.show_control(kind, name)
        process.communicate_utf8_async(None, None, done)

    def fill_gamepads(self):
        """The controller choices: the first connected one, the connected ones, and the saved
        choice while it is not connected."""
        current = self.settings.get("gamepad", "")
        choices = [(tr("Авто"), "", tr("Первый подключённый"))]
        choices += [(name, guid, name) for guid, name in connected_gamepads()]
        if current and current not in [guid for _, guid, _ in choices]:
            name = self.settings.get("gamepad_name") or current
            choices.append((tr("{} (не подключён)").format(name), current, name))
        self.gamepad_row.set_model(Gtk.StringList.new([label for label, _, _ in choices]))
        self.gamepad_row.values = [guid for _, guid, _ in choices]
        self.gamepad_row.names = [name for _, _, name in choices]
        self.gamepad_row.set_selected(self.gamepad_row.values.index(current) if current in self.gamepad_row.values else 0)
        self.show_gamepad()

    def show_gamepad(self):
        names = getattr(self.gamepad_row, "names", None)
        selected = names[self.gamepad_row.get_selected()] if names else ""
        self.gamepad_row.set_subtitle("\n".join(
            line for line in (selected, tr("Выбранный берётся, как только подключится")) if line))

    def update_gamepad_indicator(self):
        if not hasattr(self, "gamepad_btn") or not self.gamepad_btn:
            return True
        gamepads = connected_gamepads()
        if gamepads:
            first_guid, first_name = gamepads[0]
            battery_pct = None
            try:
                ps_dir = Path("/sys/class/power_supply")
                if ps_dir.is_dir():
                    for dev in ps_dir.iterdir():
                        name_lower = dev.name.lower()
                        if any(k in name_lower for k in ("controller", "ps-", "sony", "gamepad", "joy", "xbox", "xpadneo", "switch", "nintendo")):
                            cap_file = dev / "capacity"
                            if cap_file.is_file():
                                battery_pct = int(cap_file.read_text().strip())
                                break
            except Exception:
                pass

            # Compute friendly short label
            short_name = "Gamepad"
            name_l = first_name.lower()
            if "8bitdo" in name_l:
                short_name = "8BitDo"
            elif "dualsense" in name_l or "ps5" in name_l:
                short_name = "DualSense"
            elif "dualshock" in name_l or "ps4" in name_l:
                short_name = "DualShock 4"
            elif "xbox" in name_l:
                short_name = "Xbox"
            elif "switch" in name_l or "nintendo" in name_l:
                short_name = "Switch Pro"
            elif first_name.strip():
                short_name = first_name.strip().split()[0][:12]

            if battery_pct is not None:
                self.gamepad_label.set_label(f"{short_name} · {battery_pct}%")
                if battery_pct >= 70:
                    icon = "battery-level-80-symbolic"
                elif battery_pct >= 40:
                    icon = "battery-level-50-symbolic"
                elif battery_pct >= 15:
                    icon = "battery-level-20-symbolic"
                else:
                    icon = "battery-level-0-symbolic"
                self.gamepad_icon.set_from_icon_name(icon)
                tooltip = f"{first_name}\n{tr('Заряд')}: {battery_pct}%"
            else:
                self.gamepad_label.set_label(short_name)
                self.gamepad_icon.set_from_icon_name("input-gaming-symbolic")
                tooltip = f"{first_name}\n{tr('Подключено через USB/адаптер')}\n{tr('Уровень заряда не сообщается этим устройством')}"

            self.gamepad_label.set_visible(True)
            self.gamepad_btn.set_tooltip_text(tooltip)
            self.gamepad_btn.set_opacity(1.0)
        else:
            self.gamepad_icon.set_from_icon_name("input-gaming-symbolic")
            self.gamepad_label.set_visible(False)
            self.gamepad_btn.set_tooltip_text(tr("Геймпад не подключён"))
            self.gamepad_btn.set_opacity(0.45)
        return True

    def store(self):
        s = self.settings
        s["gamepad"] = combo_value(self.gamepad_row)
        s["gamepad_name"] = self.gamepad_row.names[self.gamepad_row.get_selected()]
        s["language"] = combo_value(self.language_row)
        s["fullscreen"] = self.fullscreen_row.get_active()
        s["present_mode"] = combo_value(self.present_row)
        s["hdr"] = self.hdr_row.get_active()
        s["fps_mode"] = combo_value(self.fps_row)
        s["fps_limit"] = int(self.limit_row.get_value())
        s["draw_pipe"] = combo_value(self.pipe_row)
        s["readbacks"] = combo_value(self.readbacks_row)
        s["preupload"] = combo_value(self.preupload_row)
        s["mangohud"] = self.mangohud_row.get_active()
        s["frame_stats"] = self.stats_row.get_active()
        s["save_log"] = self.save_log_row.get_active()
        s["crash_diag"] = self.crash_diag_row.get_active()
        if self.pc_model_row.get_sensitive():
            s["pc_model"] = self.pc_model_row.get_active()
        s["as_0_3"] = self.as_0_3_row.get_active()
        s["gpu_profile"] = self.profile_row.get_active()
        s["vk_validation"] = self.validation_row.get_active()
        s["extra_env"] = self.extra_row.get_text().strip()
        s["mods_enabled"] = self.mods_enabled_row.get_active()
        self.save_mod_profile()
        self.save_patch_profile()
        save_settings(s)
        self.ini.update({
            "upscaler": combo_value(self.upscaler_row),
            "frame_generation": combo_value(self.frame_gen_row),
            "dlss_preset": combo_value(self.dlss_preset_row),
            "preset": str(combo_value(self.preset_row)),
            "sharpen": "1" if self.sharpen_row.get_active() else "0",
            "sharpness": f"{self.sharpness_row.get_value():.2f}",
            "object_motion": "1" if self.motion_row.get_active() else "0",
            "show_fps": "1" if self.show_fps_row.get_active() else "0",
            "output_res": combo_value(self.output_row),
            "model_lod": combo_value(self.lod_row),
            "live_resolution": combo_value(self.live_row),
            **{key: "1" if row.get_active() else "0" for key, row in self.effect_rows.items()},
        })
        save_ini(self.ini, self.ini_lines)
        self.ini, self.ini_lines = load_ini()

    def environment(self):
        return game_environment(self.settings)

    # --- mods ----------------------------------------------------------------------------

    def mods_dir(self):
        return Path(self.settings.get("mods_dir") or DATA_DIR / "mods").expanduser()

    def save_mod_profile(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        rows = self.mod_list.rows
        profile = {"order": [name for name, _ in rows],
                   "disabled": [name for name, row in rows if not row.get_active()]}
        (DATA_DIR / "mods.json").write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n")

    def refresh_mods(self):
        self.mod_list.clear()
        self.mods_folder_row.set_subtitle(str(self.mods_dir()))
        try:
            profile = json.loads((DATA_DIR / "mods.json").read_text())
        except (OSError, ValueError):
            profile = {}
        available = discover_mods(self.mods_dir())
        order = list(dict.fromkeys(n for n in [*profile.get("order", []), *available] if n in available))
        for name in order:
            row = Adw.SwitchRow(title=name, active=name not in profile.get("disabled", []))
            row.add_suffix(flat_button("go-up-symbolic", tr("Загрузить раньше"),
                                        lambda _b, n=name: self.move_mod(n, -1)))
            row.add_suffix(flat_button("go-down-symbolic", tr("Загрузить позже"),
                                        lambda _b, n=name: self.move_mod(n, 1)))
            self.mod_list.add(name, row)
        if not order:
            self.mods_folder_row.set_subtitle(f"{self.mods_dir()} — {tr('Модов нет')}")
        self.update_mods_quick_subtitle()

    def move_mod(self, name, direction):
        rows = self.mod_list.rows
        index = next(i for i, (n, _) in enumerate(rows) if n == name)
        target = index + direction
        if 0 <= target < len(rows):
            rows[index], rows[target] = rows[target], rows[index]
            self.save_mod_profile()
            self.refresh_mods()

    def on_refresh_mods(self, _button):
        self.save_mod_profile()
        self.refresh_mods()

    def on_choose_mods(self, _button):
        self.save_mod_profile()

        def chosen(path):
            self.settings["mods_dir"] = path
            self.refresh_mods()
            self.store()
        self.choose_folder(tr("Папка модов"), self.mods_dir(), chosen)

    def on_install_mod_archive(self, _button=None):
        dialog = Gtk.FileDialog(title=tr("Выберите архив мода (.zip, .7z, .tar)"))
        arc_filter = Gtk.FileFilter()
        arc_filter.set_name("Archive (*.zip, *.7z, *.tar, *.rar)")
        for pat in ("*.zip", "*.ZIP", "*.7z", "*.7Z", "*.tar", "*.tar.gz", "*.tgz", "*.tar.xz", "*.rar", "*.RAR"):
            arc_filter.add_pattern(pat)
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(arc_filter)
        dialog.set_filters(filters)
        dialog.set_default_filter(arc_filter)

        def finish(dialog, result):
            try:
                chosen = dialog.open_finish(result)
            except GLib.Error:
                return
            if not chosen or not chosen.get_path():
                return
            self.install_mod_archive(Path(chosen.get_path()))

        dialog.open(self, None, finish)

    def install_mod_archive(self, archive_path):
        mod_name = archive_path.stem
        if mod_name.endswith(".tar"):
            mod_name = Path(mod_name).stem
        mod_name = re.sub(r'[^a-zA-Z0-9_\-\. ]', '_', mod_name).strip()
        if not mod_name:
            mod_name = "mod"

        target_dir = self.mods_dir() / mod_name
        target_dir.mkdir(parents=True, exist_ok=True)

        extracted = False
        lower = archive_path.name.lower()
        try:
            if lower.endswith(".zip"):
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    zf.extractall(target_dir)
                extracted = True
            elif lower.endswith((".tar", ".tar.gz", ".tgz", ".tar.xz", ".tar.bz2")):
                with tarfile.open(archive_path, 'r:*') as tf:
                    tf.extractall(target_dir)
                extracted = True
            elif shutil.which("7z"):
                res = subprocess.run(["7z", "x", "-y", f"-o{target_dir}", str(archive_path)], capture_output=True)
                extracted = (res.returncode == 0)
            elif shutil.which("unrar") and lower.endswith(".rar"):
                res = subprocess.run(["unrar", "x", "-o+", str(archive_path), str(target_dir)], capture_output=True)
                extracted = (res.returncode == 0)
        except Exception as e:
            self.toasts.add_toast(Adw.Toast(title=f"Error extracting mod: {e}"))
            return

        if extracted:
            self.refresh_mods()
            self.update_mods_quick_subtitle()
            self.toasts.add_toast(Adw.Toast(title=tr("Мод успешно установлен: {}").format(mod_name)))
        else:
            self.toasts.add_toast(Adw.Toast(title=f"Could not extract {archive_path.name}"))

    def update_mods_quick_subtitle(self):
        if not hasattr(self, "mods_quick") or not self.mods_quick:
            return
        try:
            available = discover_mods(self.mods_dir())
            try:
                profile = json.loads((DATA_DIR / "mods.json").read_text())
            except (OSError, ValueError):
                profile = {}
            disabled = set(profile.get("disabled", []))
            active_count = len([m for m in available if m not in disabled])
            if active_count > 0:
                self.mods_quick.set_subtitle(tr("Активных модов: {}").format(active_count))
            else:
                self.mods_quick.set_subtitle(tr("Модов нет"))
        except Exception:
            self.mods_quick.set_subtitle(tr("Открыть папку модов игры"))

    # --- third-party patches -------------------------------------------------------------

    def save_patch_profile(self):
        """patches.json: the switches that differ from each file's isEnabled."""
        enabled, disabled = [], []
        for key, row in self.patch_list.rows:
            if row.get_active() != row.default:
                (enabled if row.get_active() else disabled).append(key)
        path = DATA_DIR / "patches.json"
        try:
            profile = json.loads(path.read_text())
        except (OSError, ValueError):
            profile = {}
        # Patches of files not listed now (another folder) keep their choice.
        shown = {key for key, _ in self.patch_list.rows}
        profile = {"enabled": sorted({k for k in profile.get("enabled", []) if k not in shown} | set(enabled)),
                   "disabled": sorted({k for k in profile.get("disabled", []) if k not in shown} | set(disabled))}
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n")

    def refresh_patches(self):
        self.patch_list.clear()
        directory = patches_dir(self.settings)
        try:
            profile = json.loads((DATA_DIR / "patches.json").read_text())
        except (OSError, ValueError):
            profile = {}
        found = external_patches(directory)
        for key, path, meta in found:
            default = (meta.get("isEnabled", "false").lower() == "true") and (path.name not in ("Bloodborne.xml", "community_patches.xml"))
            active = key in profile.get("enabled", []) or (default and key not in profile.get("disabled", []))
            subtitle = key.split("/", 1)[0]
            if meta.get("Author"):
                subtitle += " · " + tr("Автор: {}").format(meta.get("Author"))
            row = Adw.SwitchRow(title=GLib.markup_escape_text(meta.get("Name") or key),
                                subtitle=GLib.markup_escape_text(subtitle), active=active)
            if meta.get("Note"):
                row.set_tooltip_text(meta.get("Note").replace("\\n", "\n"))
            row.default = default
            self.patch_list.add(key, row)
        self.patches_folder_row.set_subtitle(
            str(directory) if found else f"{directory} — {tr('Патчей нет')}")

    def on_download_patches(self, _button=None):
        target_dir = patches_dir(self.settings)
        target_dir.mkdir(parents=True, exist_ok=True)
        dest_file = target_dir / "community_patches.xml"
        url = "https://raw.githubusercontent.com/shadps4-emu/ps4_cheats/main/PATCHES/Bloodborne.xml"
        self.toasts.add_toast(Adw.Toast(title=tr("Загрузка патчей с GitHub…")))

        def download_worker():
            import urllib.request
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Bloodborne-Launcher"})
                with urllib.request.urlopen(req, timeout=12) as resp:
                    content = resp.read()
                dest_file.write_bytes(content)
                GLib.idle_add(on_success)
            except Exception as e:
                GLib.idle_add(lambda err=str(e): on_error(err))

        def on_success():
            self.refresh_patches()
            self.toasts.add_toast(Adw.Toast(title=tr("Патчи успешно обновлены!")))

        def on_error(err):
            self.toasts.add_toast(Adw.Toast(title=tr("Ошибка загрузки: {}").format(err)))

        import threading
        threading.Thread(target=download_worker, daemon=True).start()

    def on_refresh_patches(self, _button):
        self.save_patch_profile()
        self.refresh_patches()

    def on_choose_patches(self, _button):
        self.save_patch_profile()

        def chosen(path):
            self.settings["patches_dir"] = path
            self.refresh_patches()
            self.store()
        self.choose_folder(tr("Папка патчей"), patches_dir(self.settings), chosen)

    # --- log page ------------------------------------------------------------------------

    def build_log_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.log_view = Gtk.TextView(editable=False, monospace=True, cursor_visible=False,
                                     wrap_mode=Gtk.WrapMode.WORD_CHAR)
        self.log_view.set_top_margin(8)
        self.log_view.set_left_margin(8)
        self.log_view.set_right_margin(8)
        scroller = Gtk.ScrolledWindow(vexpand=True, child=self.log_view)
        self.log_scroller = scroller
        box.append(scroller)
        return box

    def append_log(self, text):
        buffer = self.log_view.get_buffer()
        buffer.insert(buffer.get_end_iter(), text)
        extra = buffer.get_line_count() - MAX_LOG_LINES
        if extra > 0:
            buffer.delete(buffer.get_start_iter(), buffer.get_iter_at_line(extra)[1])
        adj = self.log_scroller.get_vadjustment()
        GLib.idle_add(lambda: adj.set_value(adj.get_upper()) and False)

    # --- process -------------------------------------------------------------------------

    def format_playtime(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def update_playtime_label(self):
        if not hasattr(self, "tag_playtime") or not self.tag_playtime:
            return
        total_sec = self.settings.get("playtime_seconds", 0)
        if self.session_start:
            total_sec += int(time.time() - self.session_start)
        self.tag_playtime.set_label(f"⏱ {self.format_playtime(total_sec)}")
        lines = [
            tr("Общее время: {}").format(self.format_playtime(total_sec)),
            tr("Запусков: {}").format(self.settings.get("play_count", 0)),
        ]
        if self.settings.get("last_played"):
            lines.append(tr("Последний запуск: {}").format(self.settings.get("last_played")))
        self.tag_playtime.set_tooltip_text("\n".join(lines))

    def _tick_playtime(self):
        if self.process is not None and self.session_start:
            self.update_playtime_label()
            return True
        return False

    def on_launch(self, _button):
        if self.process:
            self.stop_game()
            return
        self.store()
        self.log_view.get_buffer().set_text("")
        launcher = Gio.SubprocessLauncher.new(
            Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_MERGE)
        launcher.set_environ([f"{k}={v}" for k, v in self.environment().items()])
        launcher.set_cwd(str(PORT_DIR))
        try:
            # setsid: the game and its helpers form one process group, stopped together.
            self.process = launcher.spawnv(["setsid", "bash", str(PORT_DIR / "run.sh")])
        except GLib.Error as error:
            self.toasts.add_toast(Adw.Toast(title=tr("Не удалось запустить: {}").format(error.message)))
            return
        self.session_start = time.time()
        self.settings["play_count"] = self.settings.get("play_count", 0) + 1
        self.settings["last_played"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_settings(self.settings)
        if hasattr(self, "playtime_timer_id") and self.playtime_timer_id:
            GLib.source_remove(self.playtime_timer_id)
        self.playtime_timer_id = GLib.timeout_add_seconds(1, self._tick_playtime)
        self.update_playtime_label()

        self.stream = Gio.DataInputStream.new(self.process.get_stdout_pipe())
        self.read_line()
        self.process.wait_async(None, self.on_exit)
        self.update_launch_button()
        self.stack.set_visible_child_name("log")

    def read_line(self):
        self.stream.read_line_async(GLib.PRIORITY_DEFAULT, None, self.on_line)

    def on_line(self, stream, result):
        try:
            line, _length = stream.read_line_finish_utf8(result)
        except GLib.Error:
            return
        if line is None:
            return
        self.append_log(line + "\n")
        self.read_line()

    def stop_game(self):
        if not self.process:
            return
        pid = int(self.process.get_identifier())
        try:
            os.killpg(pid, signal.SIGTERM)
        except OSError:
            self.process.force_exit()
        GLib.timeout_add_seconds(3, self.kill_if_running, pid)

    def kill_if_running(self, pid):
        if self.process:
            try:
                os.killpg(pid, signal.SIGKILL)
            except OSError:
                pass
        return False

    def on_exit(self, process, result):
        try:
            process.wait_finish(result)
        except GLib.Error:
            pass
        status = process.get_exit_status() if process.get_if_exited() else -1
        self.process = None
        if self.session_start:
            duration = int(time.time() - self.session_start)
            self.settings["playtime_seconds"] = self.settings.get("playtime_seconds", 0) + duration
            self.session_start = None
            save_settings(self.settings)
        if hasattr(self, "playtime_timer_id") and self.playtime_timer_id:
            GLib.source_remove(self.playtime_timer_id)
            self.playtime_timer_id = None
        self.update_playtime_label()
        self.update_launch_button()
        self.update_game_status()
        self.append_log(tr("\n— игра завершилась (код {}) —\n").format(status))

    def on_close(self, _window):
        if self.session_start:
            duration = int(time.time() - self.session_start)
            self.settings["playtime_seconds"] = self.settings.get("playtime_seconds", 0) + duration
            self.session_start = None
            save_settings(self.settings)
        self.store()
        if hasattr(self, "achievement_box") and self.achievement_box:
            self.achievement_box.destroy_watcher()
        if self.process:
            self.stop_game()
        if self.fsr411_build:
            self.stop_fsr411_build()
        if self.pkg_process:
            self.stop_pkg_extraction()
        return False

    # --- FSR 4.1.1 from the user's DLL -----------------------------------------------------

    def update_fsr411_row(self, progress=None):
        building = self.fsr411_build is not None
        self.fsr411_button.set_label(tr("Отменить") if building else tr("Выбрать DLL…"))
        if progress:
            self.fsr411_row.set_subtitle(progress)
        elif not building:
            self.fsr411_row.set_subtitle(tr(
                "Собрать FSR 4.1.1 из amd_fidelityfx_upscaler_dx12.dll 4.1.x (OptiScaler: папка "
                "FSR4_LATEST, или из игры с FSR 4.1). Нужен GE-Proton 10+, Proton Experimental или "
                "Proton-CachyOS; 2–5 минут (RDNA4: вдвое дольше, ещё и вариант FP8)"))

    def alert(self, heading, body):
        if hasattr(Adw, "AlertDialog"):
            dialog = Adw.AlertDialog(heading=heading, body=body)
            dialog.add_response("ok", "OK")
            dialog.present(self)
        else:
            self.toasts.add_toast(Adw.Toast(title=f"{heading}: {body}", timeout=10))

    def choose_dll(self, title, done):
        dialog = Gtk.FileDialog(title=title)
        dll = Gtk.FileFilter()
        dll.set_name("DLL")
        dll.add_pattern("*.dll")
        dll.add_pattern("*.DLL")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(dll)
        dialog.set_filters(filters)
        dialog.set_default_filter(dll)
        folder = self.settings.get("fsr411_dll_dir", "")
        if folder and Path(folder).is_dir():
            dialog.set_initial_folder(Gio.File.new_for_path(folder))

        def finish(dialog, result):
            try:
                chosen = dialog.open_finish(result)
            except GLib.Error:
                return
            if chosen and chosen.get_path():
                done(chosen.get_path())
        dialog.open(self, None, finish)

    def on_fsr411_button(self, _button):
        if self.fsr411_build:
            self.stop_fsr411_build()
            return
        self.choose_dll(tr("DLL апскейлера AMD (amd_fidelityfx_upscaler_dx12.dll)"),
                        self.on_fsr411_dll)

    def on_fsr411_dll(self, upscaler, loader=None):
        import dll_info
        self.settings["fsr411_dll_dir"] = str(Path(upscaler).parent)
        status, problem, details = dll_info.inspect(upscaler, loader)
        kind = details.get("kind")
        version = details.get("version", "?")
        if status == dll_info.UNSUPPORTED:
            if kind == "fsr4_0":
                body = tr(
                    "{}: FSR {}. Это официальная FSR 4.0.x от AMD: она включается только на "
                    "видеокартах RDNA4 (RX 9000), а под Proton на других видеокартах не "
                    "запускается, поэтому записать её нельзя.\n\nНужна FSR 4.1.x: например, "
                    "FSR4_LATEST из OptiScaler или DLL из игры с FSR 4.1.").format(
                        Path(upscaler).name, version)
            elif kind == "not_fsr4":
                body = tr("{}: в этой DLL нет FSR 4. Нужна amd_fidelityfx_upscaler_dx12.dll "
                          "версии 4.1.x.").format(Path(upscaler).name)
            else:
                models = ", ".join(details.get("models", [])) or tr("нет")
                body = tr(
                    "{}: версия {}, модели FSR 4: {}.\n\nbbport повторяет только официальную FSR 4.1.x "
                    "от AMD (модель v07_fp8_no_scale): например, FSR4_LATEST из OptiScaler или "
                    "amd_fidelityfx_upscaler_dx12.dll из игры с FSR 4.1. Сборки сообщества (4.0.2b и "
                    "подобные) устроены иначе и пока не поддерживаются.").format(
                        Path(upscaler).name, version, models)
            self.alert(tr("Эта DLL не подходит"), body)
            return
        if status == dll_info.NO_LOADER:
            if kind == "loader_is_upscaler":
                self.alert(tr("Это не загрузчик"), tr(
                    "{} — это DLL апскейлера. Загрузчик называется amd_fidelityfx_loader_dx12.dll "
                    "(у OptiScaler — amd_fidelityfx_dx12.dll) и лежит в той же папке игры, что и "
                    "DLL апскейлера.").format(Path(loader).name))
                return
            if loader:
                self.alert(tr("Загрузчик не подходит"), tr(
                    "{}: версия {}. Нужен загрузчик FidelityFX 2.x — из той же игры, что и DLL "
                    "апскейлера.").format(Path(loader).name, details.get("loader_version", "?")))
                return
            # A DLL without the FidelityFX API exports (AMD's own export it: no loader needed), and no
            # loader next to it or one folder up: ask for it.
            self.toasts.add_toast(Adw.Toast(title=tr(
                "Рядом с DLL нет загрузчика: выберите amd_fidelityfx_loader_dx12.dll из папки игры"),
                timeout=8))
            self.choose_dll(tr("Загрузчик FidelityFX (amd_fidelityfx_loader_dx12.dll или "
                               "amd_fidelityfx_dx12.dll)"),
                            lambda path: self.on_fsr411_dll(upscaler, path))
            return
        self.start_fsr411_build(upscaler, details.get("loader"))

    def start_fsr411_build(self, upscaler, loader):
        command, env = fsr411_build_command(upscaler, loader)
        launcher = Gio.SubprocessLauncher.new(
            Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_MERGE)
        launcher.set_environ([f"{k}={v}" for k, v in env.items()])
        launcher.set_cwd(str(PORT_DIR))
        try:
            # setsid: Proton and its helpers form one process group, cancelled together.
            self.fsr411_build = launcher.spawnv(["setsid", *command])
        except GLib.Error as error:
            self.toasts.add_toast(Adw.Toast(title=tr("Не удалось запустить: {}").format(error.message)))
            return
        self.append_log(tr("\n— сборка FSR 4.1.1 из {} —\n").format(upscaler))
        stream = Gio.DataInputStream.new(self.fsr411_build.get_stdout_pipe())
        stream.read_line_async(GLib.PRIORITY_DEFAULT, None, self.on_fsr411_line)
        self.fsr411_build.wait_async(None, self.on_fsr411_built)
        self.update_fsr411_row(tr("Подготовка…"))
        self.update_launch_button()

    def on_fsr411_line(self, stream, result):
        try:
            line, _length = stream.read_line_finish_utf8(result)
        except GLib.Error:
            return
        if line is None:
            return
        self.append_log(line + "\n")
        if self.fsr411_build:
            step = re.match(r"\[\s*(\d+)/(\d+)\]", line)
            if step:
                self.update_fsr411_row(tr("Запись проходов DLL под Proton: {} из {}").format(*step.groups()))
            elif line.startswith("Translating"):
                self.update_fsr411_row(tr("Перевод проходов в SPIR-V…"))
        stream.read_line_async(GLib.PRIORITY_DEFAULT, None, self.on_fsr411_line)

    def stop_fsr411_build(self):
        pid = int(self.fsr411_build.get_identifier())
        self.fsr411_cancelled = True
        try:
            os.killpg(pid, signal.SIGTERM)
        except OSError:
            self.fsr411_build.force_exit()

    def on_fsr411_built(self, process, result):
        try:
            process.wait_finish(result)
        except GLib.Error:
            pass
        status = process.get_exit_status() if process.get_if_exited() else -1
        cancelled = getattr(self, "fsr411_cancelled", False)
        self.fsr411_cancelled = False
        self.fsr411_build = None
        self.update_fsr411_row()
        self.update_launch_button()
        self.append_log(tr("— сборка FSR 4.1.1 завершилась (код {}) —\n").format(status))
        if status == 0:
            for index, (_label, value) in enumerate(UPSCALERS):
                if value == "fsr411":
                    self.upscaler_row.set_selected(index)
            self.update_upscaler_status()
            self.store()
            self.toasts.add_toast(Adw.Toast(title=tr("FSR 4.1.1 собран и выбран")))
        elif cancelled:
            self.toasts.add_toast(Adw.Toast(title=tr("Сборка FSR 4.1.1 отменена")))
        else:
            message = FSR411_BUILD_ERRORS.get(status, "Сборка не удалась (код {}): подробности в журнале")
            self.alert(tr("FSR 4.1.1 не собран"), tr(message).format(status))


class LauncherApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="io.github.bbport.Launcher",
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self):
        window = self.get_active_window() or LauncherWindow(self)
        window.present()


def play():
    """--play: the game with the saved settings, no window (Steam Deck game mode)."""
    settings = load_settings()
    if not (Path(settings["game_dir"]).expanduser() / "eboot.bin").is_file():
        print("bbport: choose the game folder in the launcher first", file=sys.stderr)
        return 1
    os.chdir(PORT_DIR)
    os.execvpe("bash", ["bash", str(PORT_DIR / "run.sh")], game_environment(settings))


def build_fsr411(arguments):
    """--build-fsr411 <upscaler DLL> [loader DLL]: the launcher's FSR 4.1.1 build, without a window."""
    if not 1 <= len(arguments) <= 2:
        print("usage: --build-fsr411 <amd_fidelityfx_upscaler_dx12.dll> [loader DLL]", file=sys.stderr)
        return 1
    command, env = fsr411_build_command(*arguments)
    return subprocess.call(command, env=env, cwd=PORT_DIR)


if __name__ == "__main__":
    if "--play" in sys.argv[1:]:
        sys.exit(play())
    if "--build-fsr411" in sys.argv[1:]:
        sys.exit(build_fsr411(sys.argv[sys.argv.index("--build-fsr411") + 1:]))
    sys.exit(LauncherApp().run(sys.argv))
