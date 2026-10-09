# SPDX-License-Identifier: GPL-2.0-or-later
"""Launcher translations. The Russian text is the key; other languages are looked up by it.

ui_language in the launcher settings: "ru", "en", "pt_BR" or "" (the system locale:
Russian for ru_*, Brazilian Portuguese for pt_BR*, English otherwise).
"""
import os

EN = {
    # Window, pages, buttons
    "Запустить": "Play",
    "Остановить": "Stop",
    "Настройки": "Settings",
    "Журнал": "Log",
    "Не удалось запустить: {}": "Could not start: {}",
    "\n— игра завершилась (код {}) —\n": "\n— the game exited (code {}) —\n",
    # Launcher language
    "Язык лаунчера": "Launcher language",
    "Как в системе": "System",
    "Применится после перезапуска лаунчера, пока игра запущена":
        "Applies after restarting the launcher while the game is running",
    # Game
    "Игра": "Game",
    "Папка игры": "Game folder",
    "Папка игры (CUSA03173)": "Game folder (CUSA03173)",
    "Выбрать папку с eboot.bin": "Choose the folder with eboot.bin",
    "Быстрый доступ": "Quick Access",
    "Файлы игры": "Game Files",
    "Настройки графики и контроллера": "Graphics and Controller Settings",
    "Разрешение, FSR, геймпад и клавиши": "Resolution, FSR, gamepad and key bindings",
    "Выберите PKG или папку с игрой": "Choose PKG or game folder",
    "Система": "System",
    "Открыть папку модов игры": "Open mods folder",
    "Экран и графика": "Display and Graphics",
    "Моды и патчи": "Mods and Patches",
    "Добавить PKG или игру…": "Add PKG or game…",
    "Интерфейс": "Interface",
    "Настройки модов": "Mod Settings",
    "Извлечь PKG…": "Extract PKG…",
    "Распаковать PS4 PKG": "Extract PS4 PKG",
    "Распаковать PS4 PKG…": "Extract PS4 PKG…",
    "Распаковать PKG": "Extract PKG",
    "Ошибка": "Error",
    "Выберите PS4 PKG для распаковки": "Select PS4 PKG to extract",
    "Выберите папку для распаковки игры": "Select folder to extract game into",
    "Извлечение PKG: {}": "Extracting PKG: {}",
    "PKG успешно извлечён в {}": "PKG successfully extracted into {}",
    "Ошибка извлечения PKG (код {})": "PKG extraction error (code {})",
    "\n— Ошибка извлечения PKG (код {}) —\n": "\n— PKG extraction error (code {}) —\n",
    "Распаковка PKG": "Extract PKG",
    "Извлечь игру или обновление из файла .pkg": "Extract game or update from .pkg file",
    "Идёт распаковка PKG…": "Extracting PKG…",
    "Распаковка: {:.1f}% ({}/{})": "Extracting: {:.1f}% ({}/{})",
    "Отменить распаковку": "Cancel extraction",
    "Распаковка отменена": "Extraction cancelled",
    "Готово! PKG распакован в: {}": "Done! PKG extracted to: {}",
    "Папка назначения для распаковки": "Destination folder for extraction",
    "Экстрактор PKG не найден: {}": "PKG extractor not found: {}",
    "\n— распаковка PKG отменена пользователем —\n": "\n— PKG extraction cancelled by user —\n",
    "\n— Распаковка PKG успешно завершена —\n": "\n— PKG extraction completed successfully —\n",
    "Выбран файл: {}": "Selected file: {}",
    "Выбрать папку с eboot.bin…": "Choose folder with eboot.bin…",
    "Трофеи": "Trophies",
    "Трофеи и достижения": "Trophies and Achievements",
    "Отслеживание платины и достижений": "Track platinum and achievements progress",
    "Трофеи Bloodborne": "Bloodborne Trophies",
    "Трофей разблокирован!": "Trophy Unlocked!",
    "Все": "All",
    "Открыто": "Unlocked",
    "Закрыто": "Locked",
    "Открыть в файловом менеджере": "Open in the file manager",
    "Папка сохранений": "Saves folder",
    "Выбрать папку сохранений": "Choose the saves folder",
    "Вернуть папку по умолчанию": "Back to the default folder",
    "Язык системы": "System language",
    "По умолчанию: {}": "Default: {}",
    "Найдены сохранения": "Saves found",
    "Сохранений пока нет: игра создаст их здесь": "No saves yet: the game will create them here",
    "не выбрана": "not chosen",
    "Найден eboot.bin": "eboot.bin found",
    # Save Backups
    "Резервные копии сохранений": "Save Backups",
    "Создать резервную копию": "Create Backup",
    "Сохранить текущее состояние игры": "Save current game state",
    "Создать": "Create",
    "Резервные копии": "Backups",
    "Восстановить": "Restore",
    "Удалить": "Delete",
    "Резервная копия создана: {}": "Backup created: {}",
    "Сохранение восстановлено из {}": "Save restored from {}",
    "Резервная копия удалена": "Backup deleted",
    "Нет резервных копий": "No backups yet",
    "Создайте резервную копию перед битвой с боссом": "Create a backup before a boss fight",
    "Папка сохранений пуста": "Saves folder is empty",
    # Gamepad & Status
    "Геймпад не подключён": "No gamepad connected",
    "Геймпад подключён": "Gamepad connected",
    "Заряд": "Battery",
    "Подключён": "Connected",
    "Уровень заряда не сообщается этим устройством": "Battery level not reported by this device",
    "Подключено через USB/адаптер": "Connected via USB/adapter",
    # Playtime & Stats
    "Общее время: {}": "Total playtime: {}",
    "Запусков: {}": "Launches: {}",
    "Последний запуск: {}": "Last played: {}",
    # Patches & QoL Hub
    "Патчи и улучшения (QoL)": "Patches & QoL Hub",
    "60 FPS, исправления графики, камеры и производительности": "60 FPS, visual, camera and performance fixes",
    "Скачать свежие патчи с GitHub": "Download community patches from GitHub",
    "Загрузка патчей с GitHub…": "Downloading patches from GitHub…",
    "Патчи успешно обновлены!": "Patches successfully updated!",
    "Ошибка загрузки: {}": "Download error: {}",
    # Mods installer
    "Установить мод из архива…": "Install mod from archive…",
    "Мод успешно установлен: {}": "Mod successfully installed: {}",
    "Активных модов: {}": "Active mods: {}",
    "Выберите архив мода (.zip, .7z, .tar)": "Select mod archive (.zip, .7z, .tar)",
    "Нет eboot.bin в папке": "No eboot.bin in the folder",
    "Управление": "Controls",
    "Клавиатура": "Keyboard",
    "Геймпад": "Gamepad",
    "Назначение кнопок; применяется при запуске игры": "Button assignments; applied when the game starts",
    "Назначить": "Assign",
    "Сбросить": "Reset",
    "{} (по умолчанию)": "{} (default)",
    "не назначено": "not assigned",
    "Нажмите клавишу или кнопку… (Esc — отмена)": "Press a key or a button… (Esc cancels)",
    "Крест": "Cross",
    "Круг": "Circle",
    "Квадрат": "Square",
    "Треугольник": "Triangle",
    "Тачпад, левая половина (жесты)": "Touchpad, left half (gestures)",
    "Тачпад, правая половина (личные вещи)": "Touchpad, right half (key items)",
    "Крестовина вверх": "D-pad up",
    "Крестовина вниз": "D-pad down",
    "Крестовина влево": "D-pad left",
    "Крестовина вправо": "D-pad right",
    "Движение вперёд": "Move forward",
    "Движение назад": "Move back",
    "Движение влево": "Move left",
    "Движение вправо": "Move right",
    "Камера вверх": "Camera up",
    "Камера вниз": "Camera down",
    "Камера влево": "Camera left",
    "Камера вправо": "Camera right",
    "Контроллер": "Controller",
    "Выбранный берётся, как только подключится": "The chosen one is used as soon as it connects",
    "Первый подключённый": "First connected",
    "{} (не подключён)": "{} (not connected)",
    "Нужно обновление 1.09: скопируйте файлы дампа обновления 1.09 в папку игры с заменой (найдена версия {})":
        "The 1.09 update is needed: copy the dumped 1.09 update into the game folder, replacing files (found version {})",
    "eboot.bin не от версии 1.09: скопируйте eboot.bin из дампа обновления 1.09 в папку игры с заменой":
        "eboot.bin is not from 1.09: copy eboot.bin from the dumped 1.09 update into the game folder, replacing it",
    "Поддерживается только CUSA03173 с обновлением 1.09 (найдено {})":
        "Only CUSA03173 with update 1.09 is supported (found {})",
    "eboot.bin не читается как расшифрованный исполняемый файл PS4: сделайте дамп заново":
        "eboot.bin cannot be read as a decrypted PS4 executable: dump the game again",
    "Bloodborne CUSA03173, версия 1.09": "Bloodborne CUSA03173, version 1.09",
    "Папка игры (с eboot.bin)": "Game folder (with eboot.bin)",
    # Languages
    "Английский": "English",
    "Русский": "Russian",
    "Японский": "Japanese",
    "Французский": "French",
    "Испанский": "Spanish",
    "Немецкий": "German",
    "Итальянский": "Italian",
    # Mods
    "Моды": "Mods",
    "Распакуйте каждый мод в отдельную папку (с dvdroot_ps4 или сразу с chr/, parts/ и т. п.). "
    "При совпадении файлов побеждает мод ниже в списке. Применяется при запуске.":
        "Extract each mod into its own folder (with dvdroot_ps4, or chr/, parts/, ... directly). "
        "When files collide, the mod lower in the list wins. Applied at start.",
    "Загружать моды": "Load mods",
    "Папка модов": "Mods folder",
    "Выбрать папку модов": "Choose the mods folder",
    "Открыть папку модов": "Open the mods folder",
    "Обновить список": "Refresh the list",
    "Загрузить раньше": "Load earlier",
    "Загрузить позже": "Load later",
    "Модов нет": "No mods",
    # Patches
    "Сторонние патчи": "Third-party patches",
    "XML-патчи в формате shadPS4 для версии 01.09 из папки патчей. Применяются при запуске.":
        "shadPS4-format XML patches for version 01.09 from the patches folder. Applied at start.",
    "Папка патчей": "Patches folder",
    "Выбрать папку патчей": "Choose the patches folder",
    "Открыть папку патчей": "Open the patches folder",
    "Патчей нет": "No patches",
    "Автор: {}": "Author: {}",
    # Screen
    "Экран": "Display",
    "Разрешение вывода": "Output resolution",
    "Апскейлер дорисовывает кадр; Steam Deck — 720p": "The upscaler fills the frame; Steam Deck: 720p",
    "Полноэкранный режим": "Fullscreen",
    "Смена разрешения на лету": "Live resolution changes",
    "Без перезапуска, но медленнее на Steam Deck и старых GPU":
        "No restart needed, but slower on the Steam Deck and older GPUs",
    "Авто (по видеокарте)": "Auto (by GPU)",
    "Выключена (быстрее)": "Off (faster)",
    "Включена": "On",
    "Режим показа кадров": "Present mode",
    "Разрешить HDR": "Allow HDR",
    # Upscaler
    "Апскейлер": "Upscaler",
    "Хранится в bbport.ini; в игре меняется через меню (Insert или L3+R3)":
        "Stored in bbport.ini; in game, change it in the menu (Insert or L3+R3)",
    "TAA (нативное сглаживание)": "TAA (native anti-aliasing)",
    "Выключен": "Off",
    "Пресет": "Preset",
    "Резкость (RCAS)": "Sharpening (RCAS)",
    "Сила резкости": "Sharpness",
    "Векторы движения объектов": "Object motion vectors",
    "Меньше гостинга на персонажах; стоит около 10% FPS": "Less ghosting on characters; costs about 10% FPS",
    "Показывать FPS": "Show FPS",
    "Ассеты найдены": "Assets found",
    "Нет ассетов: tools/fetch_fsr4_assets.sh": "No assets: tools/fetch_fsr4_assets.sh",
    "Ассеты для выбранного режима найдены": "Assets for the selected mode found",
    "{}. Соберите FSR 4.1.1 из своей DLL кнопкой «Выбрать DLL…» ниже":
        "{}. Build FSR 4.1.1 from your own DLL with the “Choose DLL…” button below",
    "FSR 4.1.1 из своей DLL AMD": "FSR 4.1.1 from your own AMD DLL",
    "Отменить": "Cancel",
    "Выбрать DLL…": "Choose DLL…",
    "DLL апскейлера AMD (amd_fidelityfx_upscaler_dx12.dll)": "AMD upscaler DLL (amd_fidelityfx_upscaler_dx12.dll)",
    "нет": "none",
    "Эта DLL не подходит": "This DLL does not fit",
    "{}: версия {}, модели FSR 4: {}.\n\nbbport повторяет только официальную FSR 4.1.x от AMD (модель v07_fp8_no_scale): например, FSR4_LATEST из OptiScaler или amd_fidelityfx_upscaler_dx12.dll из игры с FSR 4.1. Сборки сообщества (4.0.2b и подобные) устроены иначе и пока не поддерживаются.":
        "{}: version {}, FSR 4 models: {}.\n\nbbport replays AMD's official FSR 4.1.x only (model v07_fp8_no_scale): for example FSR4_LATEST from OptiScaler, or amd_fidelityfx_upscaler_dx12.dll from a game with FSR 4.1. Community builds (4.0.2b and the like) are laid out differently and are not supported yet.",
    "Загрузчик не подходит": "The loader does not fit",
    "Загрузчик FidelityFX (amd_fidelityfx_loader_dx12.dll или amd_fidelityfx_dx12.dll)":
        "FidelityFX loader (amd_fidelityfx_loader_dx12.dll or amd_fidelityfx_dx12.dll)",
    "\n— сборка FSR 4.1.1 из {} —\n": "\n— building FSR 4.1.1 from {} —\n",
    "Подготовка…": "Preparing…",
    "Запись проходов DLL под Proton: {} из {}": "Recording the DLL's passes under Proton: {} of {}",
    "Перевод проходов в SPIR-V…": "Translating the passes to SPIR-V…",
    "— сборка FSR 4.1.1 завершилась (код {}) —\n": "— FSR 4.1.1 build finished (code {}) —\n",
    "FSR 4.1.1 собран и выбран": "FSR 4.1.1 built and selected",
    "Сборка FSR 4.1.1 отменена": "FSR 4.1.1 build cancelled",
    "FSR 4.1.1 не собран": "FSR 4.1.1 was not built",
    "DLL не подходит: подробности в журнале": "The DLL does not fit: details in the log",
    "Не хватает программ для сборки: список в журнале": "Tools for the build are missing: the list is in the log",
    "Записанные проходы не совпали с тем, что повторяет bbport (другая версия DLL или новая видеокарта?): подробности в журнале":
        "The recorded passes do not match what bbport replays (another DLL version, or a new GPU?): details in the log",
    "Не найден загрузчик FidelityFX 2.x": "No FidelityFX loader 2.x found",
    "Не найден подходящий Proton: установите GE-Proton 10 или новее (ProtonUp-Qt) или Proton Experimental / Proton-CachyOS в Steam. Если они есть — запустите в Steam любую игру с этим Proton, чтобы Steam поставил его рантайм":
        "No suitable Proton found: install GE-Proton 10 or newer (ProtonUp-Qt), or Proton Experimental / Proton-CachyOS in Steam. If you have them, start any game with that Proton in Steam so that Steam installs its runtime",
    "Ни один Proton не запустил FSR 4.1 из этой DLL. Либо они слишком старые (подходят GE-Proton 10+, Proton Experimental, Proton-CachyOS 11), либо DLL не включает FSR 4.1 на этой видеокарте (Steam Deck?): тогда соберите на ПК с Radeon RX 7000/9000 и скопируйте папку fsr4_411. Подробности в журнале":
        "No Proton started this DLL's FSR 4.1. Either they are too old (GE-Proton 10+, Proton Experimental, Proton-CachyOS 11 work), or the DLL does not enable FSR 4.1 on this GPU (Steam Deck?): then build on a PC with a Radeon RX 7000/9000 and copy the fsr4_411 folder. Details in the log",
    "На NixOS запись идёт на самой системе (systemd --user) через umu-launcher из nix-shell, а здесь их не нашлось: установите umu-launcher или Nix. Подробности в журнале":
        "On NixOS the recording runs on the system itself (systemd --user) with umu-launcher from nix-shell, and neither was found: install umu-launcher or Nix. Details in the log",
    "{}: FSR {}. Это официальная FSR 4.0.x от AMD: она включается только на видеокартах RDNA4 (RX 9000), а под Proton на других видеокартах не запускается, поэтому записать её нельзя.\n\nНужна FSR 4.1.x: например, FSR4_LATEST из OptiScaler или DLL из игры с FSR 4.1.":
        "{}: FSR {}. This is AMD's official FSR 4.0.x: it is enabled on RDNA4 GPUs (RX 9000) only and does not start under Proton on other GPUs, so it cannot be recorded.\n\nFSR 4.1.x is needed: for example FSR4_LATEST from OptiScaler, or the DLL of a game with FSR 4.1.",
    "{}: в этой DLL нет FSR 4. Нужна amd_fidelityfx_upscaler_dx12.dll версии 4.1.x.":
        "{}: this DLL has no FSR 4 inside. amd_fidelityfx_upscaler_dx12.dll version 4.1.x is needed.",
    "Это не загрузчик":
        "This is not the loader",
    "{} — это DLL апскейлера. Загрузчик называется amd_fidelityfx_loader_dx12.dll (у OptiScaler — amd_fidelityfx_dx12.dll) и лежит в той же папке игры, что и DLL апскейлера.":
        "{} is the upscaler DLL. The loader is called amd_fidelityfx_loader_dx12.dll (amd_fidelityfx_dx12.dll in OptiScaler) and lies in the same game folder as the upscaler DLL.",
    "{}: версия {}. Нужен загрузчик FidelityFX 2.x — из той же игры, что и DLL апскейлера.":
        "{}: version {}. A FidelityFX loader 2.x is needed, from the same game as the upscaler DLL.",
    "Рядом с DLL нет загрузчика: выберите amd_fidelityfx_loader_dx12.dll из папки игры":
        "No loader next to the DLL: choose amd_fidelityfx_loader_dx12.dll from the game's folder",
    "Собрать FSR 4.1.1 из amd_fidelityfx_upscaler_dx12.dll 4.1.x (OptiScaler: папка FSR4_LATEST, или из игры с FSR 4.1). Нужен GE-Proton 10+, Proton Experimental или Proton-CachyOS; 2–5 минут (RDNA4: вдвое дольше, ещё и вариант FP8)":
        "Build FSR 4.1.1 from amd_fidelityfx_upscaler_dx12.dll 4.1.x (OptiScaler: the FSR4_LATEST folder, or from a game with FSR 4.1). Needs GE-Proton 10+, Proton Experimental or Proton-CachyOS; 2–5 minutes (RDNA4: twice as long, with the FP8 variant)",
    "Сборка не удалась (код {}): подробности в журнале": "The build failed (code {}): details in the log",
    "Сглаживание в разрешении вывода без модели FSR": "Anti-aliasing at the output resolution, no FSR model",
    "Нет или повреждён файл {}": "Missing or damaged file {}",
    # Effects
    "Эффекты игры": "Game effects",
    "Патчи игры, применяются при запуске": "Game patches, applied at start",
    "Детализация моделей": "Model detail",
    "Как в игре": "As in the game",
    "Максимальная (-2)": "Highest (-2)",
    "Ниже (1)": "Lower (1)",
    "Минимальная (2)": "Lowest (2)",
    "Хроматическая аберрация": "Chromatic aberration",
    "Глубина резкости (DoF)": "Depth of field (DoF)",
    "Размытие в движении": "Motion blur",
    "Затенение SSAO": "SSAO",
    "Собственное сглаживание игры": "The game's own anti-aliasing",
    "Тени от динамических источников": "Dynamic light shadows",
    "Отражения SSR (не было в игре)": "SSR reflections (not in the original game)",
    "Пропуск заставок при запуске": "Skip the intro videos",
    "Свободная камера (Cross + L3 / Space + Z)": "Free camera (Cross + L3 / Space + Z)",
    "Debug menu (левый touchpad / Tab; нужны шрифты)": "Debug menu (left touchpad / Tab; needs fonts)",
    "Установите DbgFont14h.ccm и DbgFont14h.tpf в dvdroot_ps4/font из мода Nexus #253":
        "Install DbgFont14h.ccm and DbgFont14h.tpf into dvdroot_ps4/font from Nexus mod #253",
    # Frame rate
    "Частота кадров": "Frame rate",
    "Режим": "Mode",
    "Какой патч частоты кадров применить к игре": "Which frame rate patch to apply to the game",
    "Без ограничения (патч)": "Unlocked (patch)",
    "30 (как на PS4)": "30 (as on PS4)",
    "Ограничение FPS": "FPS limit",
    "0 — без ограничения; укажите число, чтобы ограничить FPS":
        "0: no limit; set a number to cap the frame rate",
    # Performance
    "Производительность": "Performance",
    "Двухстадийный конвейер GPU": "Two-stage GPU pipeline",
    "Быстрее на 20–30%; при нестабильности выключите": "20–30% faster; turn off if unstable",
    "Авто": "Auto",
    "Включён при 8 и более потоках процессора": "On with 8 or more CPU threads",
    "Включён": "On",
    "Стабильнее, но медленнее": "More stable, but slower",
    "Чтение данных GPU процессором": "GPU data readbacks by the CPU",
    "По умолчанию": "Default",
    "Фоновая загрузка в видеопамять": "Background pre-upload into VRAM",
    "Меньше рывков при подгрузке зон": "Fewer hitches when areas stream in",
    "Обычная": "Normal",
    "Без лишней видеопамяти": "No extra VRAM",
    "Полная": "Full",
    "Около 3 ГБ видеопамяти сверху": "About 3 GB more VRAM",
    # Mode
    "Режим работы": "Mode",
    "Новая модель памяти и трансляции": "New memory and translation model",
    "Эксперимент, только видеокарты AMD. Видеокарта работает с памятью игры напрямую, как в игре для ПК, а команды графики переводятся, а не эмулируются; возможны ошибки. Выключено — старая модель памяти, как в 0.3, со всеми исправлениями":
        "Experimental, AMD GPUs only. The GPU works with the game's memory directly, as in a PC game, and graphics commands are translated rather than emulated; errors are possible. Off: the old memory model, as in 0.3, with all the fixes",
    "Только для видеокарт AMD, а на этом компьютере её нет. Используется старая модель памяти, как в 0.3, со всеми исправлениями":
        "AMD GPUs only, and this computer has none. The old memory model is used, as in 0.3, with all the fixes",
    "Синхронизация как в 0.3": "Synchronisation as in 0.3",
    "Для поиска регрессий: старая модель памяти и ожидания копий как в релизе 0.3":
        "For finding regressions: the old memory model and copy waits as released in 0.3",
    "Выключена": "Off",
    "Выключены": "Off",
    # Developer
    "Для разработчика": "Developer",
    "Статистика кадров в журнале": "Frame statistics in the log",
    "Сохранять журнал и статистику в файл": "Save the log and statistics to a file",
    "Диагностика вылетов": "Crash diagnostics",
    "Проверяет кучу игры и записывает записи в её память; немного медленнее":
        "Checks the game's heap and logs writes into its memory; a little slower",
    "В папку logs в каталоге данных: для разбора рывков и вылетов":
        "Into the logs folder of the data directory: to look into stutters and crashes",
    "Профиль GPU в журнале": "GPU profile in the log",
    "Слои валидации Vulkan": "Vulkan validation layers",
    "Сильно замедляет": "Much slower",
    "Доп. переменные (ИМЯ=значение через пробел)": "Extra variables (NAME=value, space-separated)",
}

PT_BR = {
    # Window, pages, buttons
    "Запустить": "Jogar",
    "Остановить": "Parar",
    "Настройки": "Configurações",
    "Журнал": "Log",
    "Не удалось запустить: {}": "Não foi possível iniciar: {}",
    "\n— игра завершилась (код {}) —\n": "\n— o jogo foi encerrado (código {}) —\n",
    # Launcher language
    "Язык лаунчера": "Idioma do launcher",
    "Как в системе": "Sistema",
    "Применится после перезапуска лаунчера, пока игра запущена":
        "Será aplicado após reiniciar o launcher enquanto o jogo estiver em execução",
    # Game
    "Игра": "Jogo",
    "Папка игры (CUSA03173)": "Pasta do jogo (CUSA03173)",
    "Выбрать папку с eboot.bin": "Selecionar a pasta com eboot.bin",
    "Открыть в файловом менеджере": "Abrir no gerenciador de arquivos",
    "Папка сохранений": "Pasta de salvamentos",
    "Выбрать папку сохранений": "Selecionar a pasta de salvamentos",
    "Вернуть папку по умолчанию": "Restaurar a pasta padrão",
    "Язык системы": "Idioma do sistema",
    "По умолчанию: {}": "Padrão: {}",
    "Найдены сохранения": "Salvamentos encontrados",
    "Сохранений пока нет: игра создаст их здесь": "Ainda não há salvamentos: o jogo os criará aqui",
    "не выбрана": "não selecionada",
    "Найден eboot.bin": "eboot.bin encontrado",
    "Нет eboot.bin в папке": "Não há eboot.bin na pasta",
    "Папка игры (с eboot.bin)": "Pasta do jogo (com eboot.bin)",
    # Languages
    "Английский": "Inglês",
    "Русский": "Russo",
    "Японский": "Japonês",
    "Французский": "Francês",
    "Испанский": "Espanhol",
    "Немецкий": "Alemão",
    "Итальянский": "Italiano",
    "English": "Inglês",
    # Mods
    "Моды": "Mods",
    "Распакуйте каждый мод в отдельную папку (с dvdroot_ps4 или сразу с chr/, parts/ и т. п.). "
    "При совпадении файлов побеждает мод ниже в списке. Применяется при запуске.":
        "Extraia cada mod para sua própria pasta (com dvdroot_ps4 ou diretamente com chr/, parts/, ...). "
        "Em caso de conflito de arquivos, o mod que estiver mais abaixo na lista terá prioridade. "
        "Aplicado ao iniciar.",
    "Загружать моды": "Carregar mods",
    "Папка модов": "Pasta de mods",
    "Выбрать папку модов": "Selecionar a pasta de mods",
    "Открыть папку модов": "Abrir a pasta de mods",
    "Обновить список": "Atualizar a lista",
    "Загрузить раньше": "Carregar antes",
    "Загрузить позже": "Carregar depois",
    "Модов нет": "Nenhum mod",
    # Patches
    "Сторонние патчи": "Patches de terceiros",
    "XML-патчи в формате shadPS4 для версии 01.09 из папки патчей. Применяются при запуске.":
        "Patches XML no formato do shadPS4 para a versão 01.09, carregados da pasta de patches. "
        "Aplicados ao iniciar.",
    "Папка патчей": "Pasta de patches",
    "Выбрать папку патчей": "Selecionar a pasta de patches",
    "Открыть папку патчей": "Abrir a pasta de patches",
    "Патчей нет": "Nenhum patch",
    "Автор: {}": "Autor: {}",
    # Screen
    "Экран": "Tela",
    "Разрешение вывода": "Resolução de saída",
    "Апскейлер дорисовывает кадр; Steam Deck — 720p": "O upscaler preenche o quadro; Steam Deck: 720p",
    "Полноэкранный режим": "Tela cheia",
    "Смена разрешения на лету": "Alteração de resolução em tempo real",
    "Без перезапуска, но медленнее на Steam Deck и старых GPU":
        "Não exige reinicialização, mas é mais lento no Steam Deck e em GPUs mais antigas",
    "Авто (по видеокарте)": "Automático (pela GPU)",
    "Выключена (быстрее)": "Desativado (mais rápido)",
    "Включена": "Ativado",
    "Режим показа кадров": "Modo de apresentação",
    "Разрешить HDR": "Permitir HDR",
    # Upscaler
    "Апскейлер": "Upscaler",
    "Хранится в bbport.ini; в игре меняется через меню (Insert или L3+R3)":
        "Armazenado em bbport.ini; no jogo, altere pelo menu (Insert ou L3+R3)",
    "TAA (нативное сглаживание)": "TAA (antisserrilhamento nativo)",
    "Выключен": "Desativado",
    "Пресет": "Predefinição",
    "Резкость (RCAS)": "Nitidez (RCAS)",
    "Сила резкости": "Intensidade da nitidez",
    "Векторы движения объектов": "Vetores de movimento dos objetos",
    "Меньше гостинга на персонажах; стоит около 10% FPS": "Menos ghosting nos personagens; custa cerca de 10% de FPS",
    "Показывать FPS": "Mostrar FPS",
    "Ассеты найдены": "Recursos encontrados",
    "Нет ассетов: tools/fetch_fsr4_assets.sh": "Recursos ausentes: tools/fetch_fsr4_assets.sh",
    "Ассеты для выбранного режима найдены": "Recursos encontrados para o modo selecionado",
    "{}. Соберите FSR 4.1.1 из своей DLL кнопкой «Выбрать DLL…» ниже":
        "{}. Gere o FSR 4.1.1 a partir da sua própria DLL com o botão “Escolher DLL…” abaixo",
    "FSR 4.1.1 из своей DLL AMD": "FSR 4.1.1 da sua própria DLL da AMD",
    "Отменить": "Cancelar",
    "Выбрать DLL…": "Escolher DLL…",
    "DLL апскейлера AMD (amd_fidelityfx_upscaler_dx12.dll)": "DLL do upscaler da AMD (amd_fidelityfx_upscaler_dx12.dll)",
    "нет": "nenhum",
    "Эта DLL не подходит": "Esta DLL não serve",
    "{}: версия {}, модели FSR 4: {}.\n\nbbport повторяет только официальную FSR 4.1.x от AMD (модель v07_fp8_no_scale): например, FSR4_LATEST из OptiScaler или amd_fidelityfx_upscaler_dx12.dll из игры с FSR 4.1. Сборки сообщества (4.0.2b и подобные) устроены иначе и пока не поддерживаются.":
        "{}: versão {}, modelos do FSR 4: {}.\n\nO bbport reproduz apenas o FSR 4.1.x oficial da AMD (modelo v07_fp8_no_scale): por exemplo, o FSR4_LATEST do OptiScaler ou a amd_fidelityfx_upscaler_dx12.dll de um jogo com FSR 4.1. Builds da comunidade (4.0.2b e similares) têm outra estrutura e ainda não são suportados.",
    "Загрузчик не подходит": "O carregador não serve",
    "Загрузчик FidelityFX (amd_fidelityfx_loader_dx12.dll или amd_fidelityfx_dx12.dll)":
        "Carregador do FidelityFX (amd_fidelityfx_loader_dx12.dll ou amd_fidelityfx_dx12.dll)",
    "\n— сборка FSR 4.1.1 из {} —\n": "\n— gerando o FSR 4.1.1 a partir de {} —\n",
    "Подготовка…": "Preparando…",
    "Запись проходов DLL под Proton: {} из {}": "Gravando as passagens da DLL no Proton: {} de {}",
    "Перевод проходов в SPIR-V…": "Traduzindo as passagens para SPIR-V…",
    "— сборка FSR 4.1.1 завершилась (код {}) —\n": "— geração do FSR 4.1.1 concluída (código {}) —\n",
    "FSR 4.1.1 собран и выбран": "FSR 4.1.1 gerado e selecionado",
    "Сборка FSR 4.1.1 отменена": "Geração do FSR 4.1.1 cancelada",
    "FSR 4.1.1 не собран": "O FSR 4.1.1 não foi gerado",
    "DLL не подходит: подробности в журнале": "A DLL não serve: detalhes no log",
    "Не хватает программ для сборки: список в журнале": "Faltam programas para a geração: a lista está no log",
    "Записанные проходы не совпали с тем, что повторяет bbport (другая версия DLL или новая видеокарта?): подробности в журнале":
        "As passagens gravadas não batem com o que o bbport reproduz (outra versão da DLL ou GPU nova?): detalhes no log",
    "Не найден загрузчик FidelityFX 2.x": "Carregador do FidelityFX 2.x não encontrado",
    "Не найден подходящий Proton: установите GE-Proton 10 или новее (ProtonUp-Qt) или Proton Experimental / Proton-CachyOS в Steam. Если они есть — запустите в Steam любую игру с этим Proton, чтобы Steam поставил его рантайм":
        "Nenhum Proton adequado encontrado: instale o GE-Proton 10 ou mais novo (ProtonUp-Qt), ou o Proton Experimental / Proton-CachyOS na Steam. Se já os tiver, abra qualquer jogo com esse Proton na Steam para que a Steam instale o runtime dele",
    "Ни один Proton не запустил FSR 4.1 из этой DLL. Либо они слишком старые (подходят GE-Proton 10+, Proton Experimental, Proton-CachyOS 11), либо DLL не включает FSR 4.1 на этой видеокарте (Steam Deck?): тогда соберите на ПК с Radeon RX 7000/9000 и скопируйте папку fsr4_411. Подробности в журнале":
        "Nenhum Proton iniciou o FSR 4.1 desta DLL. Ou eles são antigos demais (funcionam GE-Proton 10+, Proton Experimental, Proton-CachyOS 11), ou a DLL não ativa o FSR 4.1 nesta GPU (Steam Deck?): nesse caso, gere em um PC com Radeon RX 7000/9000 e copie a pasta fsr4_411. Detalhes no log",
    "На NixOS запись идёт на самой системе (systemd --user) через umu-launcher из nix-shell, а здесь их не нашлось: установите umu-launcher или Nix. Подробности в журнале":
        "No NixOS a gravação roda no próprio sistema (systemd --user) com o umu-launcher do nix-shell, e eles não foram encontrados: instale o umu-launcher ou o Nix. Detalhes no log",
    "{}: FSR {}. Это официальная FSR 4.0.x от AMD: она включается только на видеокартах RDNA4 (RX 9000), а под Proton на других видеокартах не запускается, поэтому записать её нельзя.\n\nНужна FSR 4.1.x: например, FSR4_LATEST из OptiScaler или DLL из игры с FSR 4.1.":
        "{}: FSR {}. Este é o FSR 4.0.x oficial da AMD: ele só é ativado em GPUs RDNA4 (RX 9000) e não inicia no Proton em outras GPUs, então não pode ser gravado.\n\nÉ preciso o FSR 4.1.x: por exemplo, o FSR4_LATEST do OptiScaler ou a DLL de um jogo com FSR 4.1.",
    "{}: в этой DLL нет FSR 4. Нужна amd_fidelityfx_upscaler_dx12.dll версии 4.1.x.":
        "{}: esta DLL não contém o FSR 4. É preciso a amd_fidelityfx_upscaler_dx12.dll versão 4.1.x.",
    "Это не загрузчик":
        "Este não é o carregador",
    "{} — это DLL апскейлера. Загрузчик называется amd_fidelityfx_loader_dx12.dll (у OptiScaler — amd_fidelityfx_dx12.dll) и лежит в той же папке игры, что и DLL апскейлера.":
        "{} é a DLL do upscaler. O carregador se chama amd_fidelityfx_loader_dx12.dll (amd_fidelityfx_dx12.dll no OptiScaler) e fica na mesma pasta do jogo que a DLL do upscaler.",
    "{}: версия {}. Нужен загрузчик FidelityFX 2.x — из той же игры, что и DLL апскейлера.":
        "{}: versão {}. É preciso um carregador do FidelityFX 2.x, do mesmo jogo que a DLL do upscaler.",
    "Рядом с DLL нет загрузчика: выберите amd_fidelityfx_loader_dx12.dll из папки игры":
        "Não há carregador ao lado da DLL: escolha a amd_fidelityfx_loader_dx12.dll da pasta do jogo",
    "Собрать FSR 4.1.1 из amd_fidelityfx_upscaler_dx12.dll 4.1.x (OptiScaler: папка FSR4_LATEST, или из игры с FSR 4.1). Нужен GE-Proton 10+, Proton Experimental или Proton-CachyOS; 2–5 минут (RDNA4: вдвое дольше, ещё и вариант FP8)":
        "Gerar o FSR 4.1.1 a partir de amd_fidelityfx_upscaler_dx12.dll 4.1.x (OptiScaler: pasta FSR4_LATEST, ou de um jogo com FSR 4.1). Requer GE-Proton 10+, Proton Experimental ou Proton-CachyOS; 2–5 minutos (RDNA4: o dobro, também com a variante FP8)",
    "Сборка не удалась (код {}): подробности в журнале": "A geração falhou (código {}): detalhes no log",
    "Сглаживание в разрешении вывода без модели FSR": "Antisserrilhamento na resolução de saída, sem modelo FSR",
    "Нет или повреждён файл {}": "Arquivo {} ausente ou corrompido",
    # Presets that are English source strings in the launcher
    "Native AA": "AA nativo",
    "Quality (x1.5)": "Qualidade (x1.5)",
    "Balanced (x1.7)": "Balanceado (x1.7)",
    "Performance (x2)": "Desempenho (x2)",
    "Ultra Performance (x3)": "Desempenho extremo (x3)",
    # Effects
    "Эффекты игры": "Efeitos do jogo",
    "Патчи игры, применяются при запуске": "Patches do jogo, aplicados ao iniciar",
    "Детализация моделей": "Detalhe dos modelos",
    "Как в игре": "Como no jogo",
    "Максимальная (-2)": "Máximo (-2)",
    "Ниже (1)": "Menor (1)",
    "Минимальная (2)": "Mínimo (2)",
    "Хроматическая аберрация": "Aberração cromática",
    "Глубина резкости (DoF)": "Profundidade de campo (DoF)",
    "Размытие в движении": "Desfoque de movimento",
    "Затенение SSAO": "SSAO",
    "Собственное сглаживание игры": "Antisserrilhamento nativo do jogo",
    "Тени от динамических источников": "Sombras de luzes dinâmicas",
    "Отражения SSR (не было в игре)": "Reflexos SSR (não existiam no jogo original)",
    "Пропуск заставок при запуске": "Pular vídeos de introdução",
    "Свободная камера (Cross + L3 / Space + Z)": "Câmera livre (Cross + L3 / Space + Z)",
    "Debug menu (левый touchpad / Tab; нужны шрифты)": "Menu de depuração (touchpad esquerdo / Tab; requer fontes)",
    "Установите DbgFont14h.ccm и DbgFont14h.tpf в dvdroot_ps4/font из мода Nexus #253":
        "Instale DbgFont14h.ccm e DbgFont14h.tpf em dvdroot_ps4/font a partir do mod #253 do Nexus",
    # Frame rate
    "Частота кадров": "Taxa de quadros",
    "Режим": "Modo",
    "Какой патч частоты кадров применить к игре": "Qual patch de taxa de quadros aplicar ao jogo",
    "Без ограничения (патч)": "Sem limite (patch)",
    "30 (как на PS4)": "30 (como no PS4)",
    "Ограничение FPS": "Limite de FPS",
    "0 — по частоте экрана (не выше 120 Гц); укажите число, чтобы ограничить иначе":
        "0: taxa de atualização da tela (até 120 Hz); defina um número para usar outro limite",
    # Performance
    "Производительность": "Desempenho",
    "Двухстадийный конвейер GPU": "Pipeline de GPU em dois estágios",
    "Быстрее на 20–30%; при нестабильности выключите": "20–30% mais rápido; desative se houver instabilidade",
    "Авто (8+ потоков)": "Automático (8+ threads)",
    "Включён": "Ativado",
    "Выключен (стабильнее)": "Desativado (mais estável)",
    "Чтение данных GPU процессором": "Leitura de dados da GPU pela CPU",
    "Relaxed (по умолчанию)": "Relaxed (padrão)",
    "Выключены": "Desativado",
    # Developer
    "Для разработчика": "Desenvolvedor",
    "Режим работы": "Modo",
    "Новая модель памяти и трансляции": "Novo modelo de memória e tradução",
    "Эксперимент, только видеокарты AMD. Видеокарта работает с памятью игры напрямую, как в игре для ПК, а команды графики переводятся, а не эмулируются; возможны ошибки. Выключено — старая модель памяти, как в 0.3, со всеми исправлениями":
        "Experimental, só GPUs AMD. A GPU usa a memória do jogo diretamente, como em um jogo de PC, e os comandos gráficos são traduzidos em vez de emulados; podem ocorrer erros. Desligado: o modelo de memória antigo, como na 0.3, com todas as correções",
    "Только для видеокарт AMD, а на этом компьютере её нет. Используется старая модель памяти, как в 0.3, со всеми исправлениями":
        "Só para GPUs AMD, e este computador não tem uma. É usado o modelo de memória antigo, como na 0.3, com todas as correções",
    "Синхронизация как в 0.3": "Sincronização como na 0.3",
    "Для поиска регрессий: старая модель памяти и ожидания копий как в релизе 0.3":
        "Para encontrar regressões: o modelo de memória antigo e as esperas de cópias como na versão 0.3",
    "Статистика кадров в журнале": "Estatísticas de quadros no log",
    "Профиль GPU в журнале": "Perfil da GPU no log",
    "Слои валидации Vulkan": "Camadas de validação do Vulkan",
    "Сильно замедляет": "Muito mais lento",
    "Доп. переменные (ИМЯ=значение через пробел)": "Variáveis extras (NOME=valor, separadas por espaço)",
}

TR = {
    # Window, pages, buttons
    "Запустить": "Başlat",
    "Остановить": "Durdur",
    "Настройки": "Ayarlar",
    "Журнал": "Günlük",
    "Не удалось запустить: {}": "Başlatılamadı: {}",
    "\n— игра завершилась (код {}) —\n": "\n— oyun kapandı (kod {}) —\n",
    # Launcher language
    "Язык лаунчера": "Başlatıcı dili",
    "Как в системе": "Sistem dili",
    "Применится после перезапуска лаунчера, пока игра запущена":
        "Oyun çalışırken yapılan dil değişikliği başlatıcı yeniden başlatıldığında uygulanır",
    # Game
    "Игра": "Oyun",
    "Папка игры": "Oyun klasörü",
    "Папка игры (CUSA03173)": "Oyun klasörü (CUSA03173)",
    "Выбрать папку с eboot.bin": "eboot.bin bulunan klasörü seç",
    "Выбрать папку с eboot.bin…": "eboot.bin bulunan klasörü seç…",
    "Быстрый доступ": "Hızlı Erişim",
    "Файлы игры": "Oyun Dosyaları",
    "Настройки графики и контроллера": "Grafik ve Kontrolcü Ayarları",
    "Разрешение, FSR, геймпад и клавиши": "Çözünürlük, FSR, gamepad ve tuşlar",
    "Выберите PKG или папку с игрой": "PKG veya oyun klasörü seçin",
    "Система": "Sistem",
    "Открыть папку модов игры": "Modlar klasörünü aç",
    "Экран и графика": "Ekran ve Grafikler",
    "Моды и патчи": "Modlar ve Yamalar",
    "Добавить PKG или игру…": "PKG veya oyun ekle…",
    "Интерфейс": "Arayüz",
    "Настройки модов": "Mod Ayarları",
    "Извлечь PKG…": "PKG Çıkart…",
    "Распаковать PS4 PKG": "PS4 PKG Çıkart",
    "Распаковать PS4 PKG…": "PS4 PKG Çıkart…",
    "Выберите PS4 PKG для распаковки": "Çıkartılacak PS4 PKG dosyasını seçin",
    "Выберите папку для распаковки игры": "Oyunun çıkartılacağı hedef klasörü seçin",
    "Извлечение PKG: {}": "PKG çıkartılıyor: {}",
    "PKG успешно извлечён в {}": "PKG başarıyla şuraya çıkartıldı: {}",
    "Ошибка извлечения PKG (код {})": "PKG çıkartma hatası (kod {})",
    "Распаковка PKG": "PKG Çıkart",
    "Извлечь игру или обновление из файла .pkg": ".pkg dosyasından oyunu veya güncellemeyi çıkart",
    "Идёт распаковка PKG…": "PKG çıkartılıyor…",
    "Распаковка: {:.1f}% ({}/{})": "Çıkartılıyor: %{:.1f} ({}/{})",
    "Отменить распаковку": "Çıkartmayı iptal et",
    "Распаковка отменена": "Çıkartma iptal edildi",
    "Готово! PKG распакован в: {}": "Tamamlandı! PKG şuraya çıkartıldı: {}",
    "Папка назначения для распаковки": "Çıkartma hedef klasörü",
    "Выбрать папку для распаковки игры": "Oyunun çıkartılacağı klasörü seç",
    "Экстрактор PKG не найден: {}": "PKG çıkartıcı bulunamadı: {}",
    "\n— распаковка PKG отменена пользователем —\n": "\n— PKG çıkartma kullanıcı tarafından iptal edildi —\n",
    "\n— Распаковка PKG успешно завершена —\n": "\n— PKG çıkartma başarıyla tamamlandı —\n",
    "Выбран файл: {}": "Seçilen dosya: {}",
    "Трофеи": "Kupalar",
    "Трофеи и достижения": "Kupalar ve Başarımlar",
    "Отслеживание платины и достижений": "Platin ve kupa ilerlemesini takip et",
    "Трофеи Bloodborne": "Bloodborne Kupaları",
    "Трофей разблокирован!": "Kupa Açıldı!",
    "Все": "Tümü",
    "Открыто": "Açıldı",
    "Закрыто": "Kilitli",
    "Открыть в файловом менеджере": "Dosya yöneticisinde aç",
    "Папка сохранений": "Kayıt klasörü",
    "Выбрать папку сохранений": "Kayıt klasörünü seç",
    "Вернуть папку по умолчанию": "Varsayılan klasöre sıfırla",
    "Язык системы": "Sistem dili",
    "По умолчанию: {}": "Varsayılan: {}",
    "Найдены сохранения": "Kayıtlar bulundu",
    "Сохранений пока нет: игра создаст их здесь": "Henüz kayıt yok: oyun burada oluşturacak",
    "Найден eboot.bin": "eboot.bin bulundu",
    # Save Backups
    "Резервные копии сохранений": "Kayıt Yedekleri",
    "Создать резервную копию": "Yedek Oluştur",
    "Сохранить текущее состояние игры": "Mevcut oyun durumunu kaydet",
    "Создать": "Oluştur",
    "Резервные копии": "Kayıt Yedekleri",
    "Восстановить": "Geri Yükle",
    "Удалить": "Sil",
    "Резервная копия создана: {}": "Yedek oluşturuldu: {}",
    "Сохранение восстановлено из {}": "Kayıt şuradan geri yüklendi: {}",
    "Резервная копия удалена": "Yedek silindi",
    "Нет резервных копий": "Henüz yedek yok",
    "Создайте резервную копию перед битвой с боссом": "Boss savaşından önce hızlı bir yedek oluşturun",
    "Папка сохранений пуста": "Kayıt klasörü boş",
    # Gamepad & Status
    "Геймпад не подключён": "Gamepad bağlı değil",
    "Геймпад подключён": "Gamepad bağlı",
    "Заряд": "Pil",
    "Подключён": "Bağlı",
    # Playtime & Stats
    "Общее время: {}": "Toplam oynama süresi: {}",
    "Запусков: {}": "Açılış sayısı: {}",
    "Последний запуск: {}": "Son oynanma: {}",
    # Patches & QoL Hub
    "Патчи и улучшения (QoL)": "Yamalar ve İyileştirmeler (QoL)",
    "60 FPS, исправления графики, камеры и производительности": "60 FPS, görsel, kamera ve performans düzeltmeleri",
    "Скачать свежие патчи с GitHub": "Topluluk Yamalarını GitHub'dan İndir",
    "Загрузка патчей с GitHub…": "Yamalar GitHub'dan indiriliyor…",
    "Патчи успешно обновлены!": "Yamalar başarıyla güncellendi!",
    "Ошибка загрузки: {}": "İndirme hatası: {}",
    # Mods installer
    "Установить мод из архива…": "Arşivden mod kur…",
    "Мод успешно установлен: {}": "Mod başarıyla kuruldu: {}",
    "Активных модов: {}": "Aktif mod: {}",
    "Выберите архив мода (.zip, .7z, .tar)": "Mod arşivini seçin (.zip, .7z, .tar)",
    "Нет eboot.bin в папке": "Klasörde eboot.bin yok",
    "Управление": "Kontroller",
    "Клавиатура": "Klavye",
    "Геймпад": "Gamepad",
    "Назначение кнопок; применяется при запуске игры": "Tuş atamaları; oyun başladığında uygulanır",
    "Назначить": "Ata",
    "Сбросить": "Sıfırla",
    "{} (по умолчанию)": "{} (varsayılan)",
    "не назначено": "atanmadı",
    "Нажмите клавишу или кнопку… (Esc — отмена)": "Bir tuşa veya butona basın… (Esc iptal)",
    "Крест": "Çarpı (X)",
    "Круг": "Daire (O)",
    "Квадрат": "Kare (□)",
    "Треугольник": "Üçgen (△)",
    "Тачпад, левая половина (жесты)": "Dokunmatik yüzey sol (jestler)",
    "Тачпад, правая половина (личные вещи)": "Dokunmatik yüzey sağ (eşyalar)",
    "Крестовина вверх": "Yön tuşu yukarı",
    "Крестовина вниз": "Yön tuşu aşağı",
    "Крестовина влево": "Yön tuşu sol",
    "Крестовина вправо": "Yön tuşu sağ",
    "Движение вперёд": "İleri hareket",
    "Движение назад": "Geri hareket",
    "Движение влево": "Sola hareket",
    "Движение вправо": "Sağa hareket",
    "Камера вверх": "Kamera yukarı",
    "Камера вниз": "Kamera aşağı",
    "Камера влево": "Kamera sol",
    "Камера вправо": "Kamera sağ",
    "Контроллер": "Kontrolcü",
    "Выбранный берётся, как только подключится": "Seçilen kontrolcü bağlandığında kullanılır",
    "Первый подключённый": "İlk bağlanan",
    "{} (не подключён)": "{} (bağlı değil)",
    "Нужно обновление 1.09: скопируйте файлы дампа обновления 1.09 в папку игры с заменой (найдена версия {})":
        "1.09 güncellemesi gerekli: 1.09 güncelleme dosyalarını oyun klasörüne kopyalayıp değiştirin (bulunan sürüm {})",
    "eboot.bin не от версии 1.09: скопируйте eboot.bin из дампа обновления 1.09 в папку игры с заменой":
        "eboot.bin 1.09 sürümüne ait değil: 1.09 güncellemesindeki eboot.bin dosyasını oyun klasörüne kopyalayın",
    "Поддерживается только CUSA03173 с обновлением 1.09 (найдено {})":
        "Yalnızca 1.09 güncellemeli CUSA03173 desteklenir (bulunan {})",
    "eboot.bin не читается как расшифрованный исполняемый файл PS4: сделайте дамп заново":
        "eboot.bin şifresi çözülmüş PS4 dosyası olarak okunamadı: lütfen oyunu tekrar dökümleyin (dump)",
    "Bloodborne CUSA03173, версия 1.09": "Bloodborne CUSA03173, sürüm 1.09",
    "Папка игры (с eboot.bin)": "Oyun klasörü (eboot.bin içeren)",
    # Languages
    "Английский": "İngilizce",
    "Русский": "Rusça",
    "Японский": "Japonca",
    "Французский": "Fransızca",
    "Испанский": "İspanyolca",
    "Немецкий": "Almanca",
    "Итальянский": "İtalyanca",
    # Mods
    "Моды": "Modlar",
    "Распакуйте каждый мод в отдельную папку (с dvdroot_ps4 или сразу с chr/, parts/ и т. п.). "
    "При совпадении файлов побеждает мод ниже в списке. Применяется при запуске.":
        "Her modu ayrı bir klasöre çıkartın (dvdroot_ps4 ile veya doğrudan chr/, parts/ vb.). "
        "Çakışan dosyalarda listede altta olan mod önceliklidir. Başlatmada uygulanır.",
    "Загружать моды": "Modları yükle",
    "Папка модов": "Modlar klasörü",
    "Выбрать папку модов": "Modlar klasörünü seç",
    "Открыть папку модов": "Modlar klasörünü aç",
    "Обновить список": "Listeyi yenile",
    "Загрузить раньше": "Daha önce yükle",
    "Загрузить позже": "Daha sonra yükle",
    "Модов нет": "Mod yok",
    # Patches
    "Сторонние патчи": "Üçüncü taraf yamalar",
    "XML-патчи в формате shadPS4 для версии 01.09 из папки патчей. Применяются при запуске.":
        "Yamalar klasöründeki 01.09 sürümü için shadPS4 biçimli XML yamaları. Başlatmada uygulanır.",
    "Папка патчей": "Yamalar klasörü",
    "Выбрать папку патчей": "Yamalar klasörünü seç",
    "Открыть папку патчей": "Yamalar klasörünü aç",
    "Патчей нет": "Yama yok",
    "Автор: {}": "Yazar: {}",
    # Screen
    "Экран": "Ekran",
    "Разрешение вывода": "Çıkış çözünürlüğü",
    "Апскейлер дорисовывает кадр; Steam Deck — 720p": "Upscaler kareyi tamamlar; Steam Deck: 720p",
    "Полноэкранный режим": "Tam ekran",
    "Смена разрешения на лету": "Anlık çözünürlük değiştirme",
    "Без перезапуска, но медленнее на Steam Deck и старых GPU":
        "Yeniden başlatma gerekmez ancak Steam Deck ve eski GPU'larda daha yavaştır",
    "Авто (по видеокарте)": "Otomatik (GPU'ya göre)",
    "Выключена (быстрее)": "Kapalı (daha hızlı)",
    "Включена": "Açık",
    "Режим показа кадров": "Kare sunum modu",
    "Разрешить HDR": "HDR'a izin ver",
    # Upscaler
    "Апскейлер": "Upscaler",
    "Хранится в bbport.ini; в игре меняется через меню (Insert или L3+R3)":
        "bbport.ini içinde saklanır; oyunda menüden değiştirilebilir (Insert veya L3+R3)",
    "Качество апскейлера": "Upscaler kalitesi",
    "Качество против производительности: Native AA берёт исходное разрешение без сжатия":
        "Kalite ve performans dengesi: Native AA tam çözünürlüğü kullanır",
    "Резкость RCAS": "RCAS keskinliği",
    "0 — без дополнительной резкости": "0 — ekstra keskinlik yok",
    "Ассеты найдены": "Varlıklar bulundu",
    "Нет ассетов: tools/fetch_fsr4_assets.sh": "Varlık bulunamadı: tools/fetch_fsr4_assets.sh",
    "Собрать FSR 4.1.1 из amd_fidelityfx_upscaler_dx12.dll…": "amd_fidelityfx_upscaler_dx12.dll dosyasından FSR 4.1.1 derle…",
    "Выбрать DLL…": "DLL Seç…",
    "Отменить": "İptal Et",
    # Effects
    "Эффекты": "Efektler",
    "Настройки графики игры": "Oyun grafik ayarları",
    "Качество моделей (LOD)": "Model kalitesi (LOD)",
    "Дистанция переключения моделей: ниже — лучше детализация вдали, но больше нагрузка":
        "Model geçiş mesafesi: daha düşük değerler uzakta daha iyi detay sağlar ancak yükü artırır",
    "Как в игре": "Oyundaki gibi",
    "Максимальная (-2)": "Maksimum (-2)",
    "Ниже (1)": "Düşük (1)",
    "Минимальная (2)": "Minimum (2)",
    # FPS
    "Частота кадров": "Kare hızı (FPS)",
    "Режим": "Mod",
    "Какой патч частоты кадров применить к игре": "Oyuna hangi kare hızı yaması uygulansın",
    "Без ограничения (патч)": "Sınırsız (yama)",
    "30 (как на PS4)": "30 (PS4 gibi)",
    "Ограничение FPS": "FPS Sınırı",
    "0 — по частоте экрана (не выше 120 Гц); укажите число, чтобы ограничить иначе":
        "0: ekran yenileme hızı (en fazla 120 Hz); farklı bir sınır için sayı girin",
    # Performance
    "Производительность": "Performans",
    "Двухстадийный конвейер GPU": "İki aşamalı GPU işlem hattı",
    "Быстрее на 20–30%; при нестабильности выключите": "%20–30 daha hızlı; kararsızlık olursa kapatın",
    "Авто (8+ потоков)": "Otomatik (8+ iş parçacığı)",
    "Включён": "Açık",
    "Выключен (стабильнее)": "Kapalı (daha kararlı)",
    "Чтение данных GPU процессором": "GPU verilerinin CPU tarafından okunması",
    "Relaxed (по умолчанию)": "Relaxed (varsayılan)",
    "Выключены": "Kapalı",
    # Developer
    "Для разработчика": "Geliştirici",
    "Режим работы": "Çalışma modu",
    "Новая модель памяти и трансляции": "Yeni bellek ve çeviri modeli",
    "Эксперимент, только видеокарты AMD. Видеокарта работает с памятью игры напрямую, как в игре для ПК, а команды графики переводятся, а не эмулируются; возможны ошибки. Выключено — старая модель памяти, как в 0.3, со всеми исправлениями":
        "Deneysel, yalnızca AMD GPU'lar. GPU doğrudan oyun belleğini kullanır ve komutlar öykünülmek yerine çevrilir. Kapalı: 0.3 sürümündeki eski bellek modeli",
    "Только для видеокарт AMD, а на этом компьютере её нет. Используется старая модель памяти, как в 0.3, со всеми исправлениями":
        "Yalnızca AMD GPU'lar için, bu bilgisayarda bulunamadı. 0.3 sürümündeki eski model kullanılıyor",
    "Синхронизация как в 0.3": "0.3 senkronizasyonu",
    "Для поиска регрессий: старая модель памяти и ожидания копий как в релизе 0.3":
        "Gerilemeleri tespit etmek için: 0.3 sürümündeki eski bellek ve kopya bekleme modeli",
    "Статистика кадров в журнале": "Günlükte kare istatistikleri",
    "Профиль GPU в журнале": "Günlükte GPU profili",
    "Слои валидации Vulkan": "Vulkan doğrulama katmanları",
    "Сильно замедляет": "Performansı ciddi şekilde düşürür",
    "Доп. переменные (ИМЯ=значение через пробел)": "Ek değişkenler (boşlukla ayrılmış AD=değer)",
    "FSR 4.1.1 собран и выбран": "FSR 4.1.1 derlendi ve seçildi",
    "Сборка FSR 4.1.1 отменена": "FSR 4.1.1 derlemesi iptal edildi",
    "FSR 4.1.1 не собран": "FSR 4.1.1 derlenemedi",
    "— сборка FSR 4.1.1 завершилась (код {}) —\n": "— FSR 4.1.1 derlemesi tamamlandı (kod {}) —\n",
    "\n— сборка FSR 4.1.1 из {} —\n": "\n— {} kaynağından FSR 4.1.1 derleniyor —\n",
    "Эта DLL не подходит": "Bu DLL uygun değil",
    "Это не загрузчик": "Bu bir yükleyici değil",
    "Загрузчик не подходит": "Yükleyici uygun değil",
    "Ошибка": "Hata",
    "\n— Ошибка извлечения PKG (код {}) —\n": "\n— PKG çıkartma hatası (kod {}) —\n",
    "Распаковать PKG": "PKG Çıkart",
    "Проверяет кучу игры и записывает записи в её память; немного медленнее": "Oyun belleğini denetler ve kayıtları belleğe yazar; biraz daha yavaş",
    "Сглаживание в разрешении вывода без модели FSR": "FSR modeli olmadan çıkış çözünürlüğünde kenar yumuşatma",
    "В папку logs в каталоге данных: для разбора рывков и вылетов": "Veri dizinindeki logs klasörüne: takılmaları ve çökmeleri analiz etmek için",
    "Векторы движения объектов": "Nesne hareket vektörleri",
    "0 — без ограничения; укажите число, чтобы ограничить FPS": "0: sınırsız; FPS sınırlamak için bir sayı girin",
    "Показывать FPS": "FPS Göster",
    "Меньше гостинга на персонажах; стоит около 10% FPS": "Karakterlerde daha az gölgelenme; yaklaşık %10 FPS bedeli vardır",
    "Сила резкости": "Keskinlik Gücü",
    "Запись проходов DLL под Proton: {} из {}": "Proton altında DLL geçişlerini kaydetme: {} / {}",
    "Рядом с DLL нет загрузчика: выберите amd_fidelityfx_loader_dx12.dll из папки игры": "DLL yanında yükleyici yok: oyun klasöründen amd_fidelityfx_loader_dx12.dll seçin",
    "Меньше рывков при подгрузке зон": "Bölge yüklemelerinde daha az takılma",
    "Патчи игры, применяются при запуске": "Oyun yamaları, başlangıçta uygulanır",
    "DLL апскейлера AMD (amd_fidelityfx_upscaler_dx12.dll)": "AMD upscaler DLL (amd_fidelityfx_upscaler_dx12.dll)",
    "FSR 4.1.1 из своей DLL AMD": "Özel AMD DLL'sinden FSR 4.1.1",
    "Фоновая загрузка в видеопамять": "VRAM'e arka plan yüklemesi",
    "{}. Соберите FSR 4.1.1 из своей DLL кнопкой «Выбрать DLL…» ниже": "{}. Aşağıdaki «DLL Seç…» butonuyla kendi DLL'nizden FSR 4.1.1 derleyin",
    "Диагностика вылетов": "Çökme teşhisi",
    "Детализация моделей": "Model detay seviyesi",
    "Сохранять журнал и статистику в файл": "Günlüğü ve istatistikleri dosyaya kaydet",
    "нет": "yok",
    "Ассеты для выбранного режима найдены": "Seçilen mod için varlıklar bulundu",
    "Подготовка…": "Hazırlanıyor…",
    "Авто": "Otomatik",
    "Перевод проходов в SPIR-V…": "Geçişleri SPIR-V formatına çevirme…",
    "Пресет": "Önayarlar",
    "Эффекты игры": "Oyun Efektleri",
    "Нет или повреждён файл {}": "{} dosyası eksik veya bozuk",
    "Резкость (RCAS)": "Keskinlik (RCAS)",
    "не выбрана": "seçilmedi",
    "TAA (нативное сглаживание)": "TAA (yerel kenar yumuşatma)",
    "Выключен": "Kapalı",
    "{}: версия {}, модели FSR 4: {}.\n\nbbport повторяет только официальную FSR 4.1.x от AMD (модель v07_fp8_no_scale): например, FSR4_LATEST из OptiScaler или amd_fidelityfx_upscaler_dx12.dll из игры с FSR 4.1. Сборки сообщества (4.0.2b и подобные) устроены иначе и пока не поддерживаются.":
        "{}: sürüm {}, FSR 4 modelleri: {}.\n\nbbport yalnızca AMD'nin resmi FSR 4.1.x sürümünü destekler (v07_fp8_no_scale modeli): örneğin OptiScaler'dan FSR4_LATEST veya FSR 4.1 içeren bir oyundan amd_fidelityfx_upscaler_dx12.dll. Topluluk sürümleri (4.0.2b vb.) farklı yapıdadır ve henüz desteklenmemektedir.",
    "Загрузчик FidelityFX (amd_fidelityfx_loader_dx12.dll или amd_fidelityfx_dx12.dll)": "FidelityFX yükleyici (amd_fidelityfx_loader_dx12.dll veya amd_fidelityfx_dx12.dll)",
    "DLL не подходит: подробности в журнале": "DLL uygun değil: ayrıntılar günlükte",
    "Не хватает программ для сборки: список в журнале": "Derleme için gerekli araçlar eksik: liste günlükte",
    "Записанные проходы не совпали с тем, что повторяет bbport (другая версия DLL или новая видеокарта?): подробности в журнале":
        "Kaydedilen geçişler bbport ile eşleşmedi (farklı DLL sürümü veya yeni GPU?): ayrıntılar günlükte",
    "Не найден загрузчик FidelityFX 2.x": "FidelityFX 2.x yükleyicisi bulunamadı",
    "Не найден подходящий Proton: установите GE-Proton 10 или новее (ProtonUp-Qt) или Proton Experimental / Proton-CachyOS в Steam. Если они есть — запустите в Steam любую игру с этим Proton, чтобы Steam поставил его рантайм":
        "Uygun Proton bulunamadı: Steam'e GE-Proton 10 veya daha yenisini (ProtonUp-Qt) ya da Proton Experimental / Proton-CachyOS kurun. Varsa, Steam'in çalışma zamanını yüklemesi için herhangi bir oyunu bu Proton ile başlatın",
    "Ни один Proton не запустил FSR 4.1 из этой DLL. Либо они слишком старые (подходят GE-Proton 10+, Proton Experimental, Proton-CachyOS 11), либо DLL не включает FSR 4.1 на этой видеокарте (Steam Deck?): тогда соберите на ПК с Radeon RX 7000/9000 и скопируйте папку fsr4_411. Подробности в журнале":
        "Hiçbir Proton bu DLL'den FSR 4.1 başlatamadı. Ya çok eskiler ya da DLL bu GPU'da FSR 4.1 etkinleştirmiyor: RX 7000/9000 olan bir PC'de derleyip fsr4_411 klasörünü kopyalayın. Ayrıntılar günlükte",
    "На NixOS запись идёт на самой системе (systemd --user) через umu-launcher из nix-shell, а здесь их не нашлось: установите umu-launcher или Nix. Подробности в журнале":
        "NixOS üzerinde kayıt sistemin kendisinde umu-launcher ile çalışır, ancak bulunamadı: umu-launcher veya Nix kurun. Ayrıntılar günlükte",
    "{}: FSR {}. Это официальная FSR 4.0.x от AMD: она включается только на видеокартах RDNA4 (RX 9000), а под Proton на других видеокартах не запускается, поэтому записать её нельзя.\n\nНужна FSR 4.1.x: например, FSR4_LATEST из OptiScaler или DLL из игры с FSR 4.1.":
        "{}: FSR {}. Bu resmi AMD FSR 4.0.x sürümüdür: yalnızca RDNA4 (RX 9000) kartlarda çalışır ve Proton altında diğer kartlarda başlatılamaz. FSR 4.1.x gereklidir: örneğin OptiScaler'dan FSR4_LATEST veya FSR 4.1 içeren bir oyun DLL'i.",
    "{}: в этой DLL нет FSR 4. Нужна amd_fidelityfx_upscaler_dx12.dll версии 4.1.x.": "{}: bu DLL içinde FSR 4 yok. 4.1.x sürümü amd_fidelityfx_upscaler_dx12.dll gereklidir.",
    "{} — это DLL апскейлера. Загрузчик называется amd_fidelityfx_loader_dx12.dll (у OptiScaler — amd_fidelityfx_dx12.dll) и лежит в той же папке игры, что и DLL апскейлера.":
        "{} bir upscaler DLL dosyasıdır. Yükleyici adı amd_fidelityfx_loader_dx12.dll (OptiScaler'da amd_fidelityfx_dx12.dll) olup oyun klasöründe yer alır.",
    "{}: версия {}. Нужен загрузчик FidelityFX 2.x — из той же игры, что и DLL апскейлера.": "{}: sürüm {}. Upscaler DLL ile aynı oyundan bir FidelityFX 2.x yükleyicisi gereklidir.",
    "Собрать FSR 4.1.1 из amd_fidelityfx_upscaler_dx12.dll 4.1.x (OptiScaler: папка FSR4_LATEST, или из игры с FSR 4.1). Нужен GE-Proton 10+, Proton Experimental или Proton-CachyOS; 2–5 минут (RDNA4: вдвое дольше, ещё и вариант FP8)":
        "amd_fidelityfx_upscaler_dx12.dll 4.1.x dosyasından FSR 4.1.1 derleyin (OptiScaler: FSR4_LATEST klasörü veya FSR 4.1 içeren bir oyundan). GE-Proton 10+, Proton Experimental veya Proton-CachyOS gerekir; 2–5 dakika sürer",
    "Сборка не удалась (код {}): подробности в журнале": "Derleme başarısız oldu (kod {}): ayrıntılar günlükte",
    "Хроматическая аберрация": "Kromatik Sapma (Chromatic Aberration)",
    "Глубина резкости (DoF)": "Alan Derinliği (DoF)",
    "Размытие в движении": "Hareket Bulanıklığı (Motion Blur)",
    "Затенение SSAO": "Ortam Kapatma (SSAO)",
    "Собственное сглаживание игры": "Oyunun Dahili Kenar Yumuşatması",
    "Тени от динамических источников": "Dinamik Işık Gölgeleri",
    "Отражения SSR (не было в игре)": "SSR Yansımaları (orijinal oyunda yoktu)",
    "Пропуск заставок при запуске": "Açılış Videolarını Atla",
    "Свободная камера (Cross + L3 / Space + Z)": "Serbest Kamera (Cross + L3 / Boşluk + Z)",
    "Debug menu (левый touchpad / Tab; нужны шрифты)": "Debug Menüsü (sol dokunmatik yüzey / Tab; yazı tipi gerekir)",
    "Установите DbgFont14h.ccm и DbgFont14h.tpf в dvdroot_ps4/font из мода Nexus #253": "Nexus mod #253'ten DbgFont14h.ccm ve DbgFont14h.tpf dosyalarını dvdroot_ps4/font klasörüne kurun",
    "Включён при 8 и более потоках процессора": "8 veya daha fazla CPU iş parçacığında açık",
    "Стабильнее, но медленнее": "Daha kararlı fakat daha yavaş",
    "По умолчанию": "Varsayılan",
    "Обычная": "Normal",
    "Без лишней видеопамяти": "Ek VRAM kullanmaz",
    "Полная": "Tam",
    "Около 3 ГБ видеопамяти сверху": "Yaklaşık 3 GB ek VRAM",
    "Выключена": "Kapalı",
    "Уровень заряда не сообщается этим устройством": "Pil seviyesi bu cihaz tarafından bildirilmiyor",
    "Подключено через USB/адаптер": "USB/Adaptör ile bağlı",
}


def system_language():
    for key in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
        value = os.environ.get(key, "")
        if value:
            locale = value.lower().replace("-", "_")
            if locale.startswith("ru"):
                return "ru"
            if locale.startswith("pt_br"):
                return "pt_BR"
            if locale.startswith("tr"):
                return "tr"
            return "en"
    return "en"


_language = system_language()


def set_language(choice):
    """choice: "ru", "en", "pt_BR", "tr" or "" (the system's)."""
    global _language
    _language = choice if choice in ("ru", "en", "pt_BR", "tr") else system_language()


def language():
    return _language


def tr(text):
    if _language == "en":
        return EN.get(text, text)
    if _language == "tr":
        return TR.get(text, EN.get(text, text))
    if _language == "pt_BR":
        # Strings added after the translation fall back to English, not to the Russian key.
        return PT_BR.get(text, EN.get(text, text))
    return text


