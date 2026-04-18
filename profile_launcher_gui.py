from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

import fingerprint_manager as fpm


ROOT_DIR = Path(__file__).resolve().parent
PROFILES_DIR = ROOT_DIR / "Profiles"
USER_AGENT_FILE = ROOT_DIR / "UserAgent.json"
LOCAL_CHROMIUM_EXE = ROOT_DIR / "Chromium" / "chrome-win" / "chrome.exe"
try:
    _cfx_res = subprocess.run(
        ["python", "-m", "camoufox", "path"],
        capture_output=True,
        text=True,
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    LOCAL_CAMOUFOX_EXE = Path(_cfx_res.stdout.strip()) / "camoufox.exe"
except Exception:
    LOCAL_CAMOUFOX_EXE = Path("C:/Users/adars/AppData/Local/camoufox/camoufox/Cache/camoufox.exe")
EXTENSION_DIR = ROOT_DIR / "fingerprint_extension"

WINDOW_BG = "#f5efe4"
PANEL_BG = "#fffaf2"
CARD_BG = "#ffffff"
HEADER_BG = "#123049"
HEADER_ACCENT = "#f29e4c"
TEXT_PRIMARY = "#193042"
TEXT_MUTED = "#617488"
ACCENT = "#1f7a72"
ACCENT_DARK = "#175e59"
FP_ACTIVE = "#2d7dd2"
FP_LOCKED = "#d4a017"
FP_NONE = "#999999"
SUCCESS = "#2f855a"
SUCCESS_SOFT = "#dff6e6"
DANGER = "#c65d3a"
DANGER_DARK = "#9e462b"
DANGER_SOFT = "#fde7df"
BORDER = "#e4d9c6"
SEARCH_BG = "#f8f4ec"
STATUS_BG = "#f1ebde"
DEFAULT_WINDOW_SIZE = "412,915"
REFRESH_INTERVAL_MS = 5000
USER_DATA_DIR_PATTERNS = (
    re.compile(r'-profile\s+"([^"]+)"', re.IGNORECASE),
    re.compile(r'-profile\s+([^\s"]+)', re.IGNORECASE),
    re.compile(r'--profile\s+"([^"]+)"', re.IGNORECASE),
    re.compile(r'--profile\s+([^\s"]+)', re.IGNORECASE),
    re.compile(r'--user-data-dir(?:=|\s+)"([^"]+)"', re.IGNORECASE),
    re.compile(r'--user-data-dir(?:=|\s+)([^\s"]+)', re.IGNORECASE),
)
ANDROID_INFO_PATTERN = re.compile(
    r"Android\s+(?P<version>[\d.]+);\s*(?P<device>[^)]+?)\)\s+AppleWebKit",
    re.IGNORECASE,
)
INVALID_PROFILE_NAME_CHARS = set('<>:"/\\|?*')


@dataclass(slots=True)
class ProfileEntry:
    name: str
    path: Path
    user_agent: str
    android_version: str
    device_name: str
    browser_hint: Optional[Path] = None
    pids: List[int] = field(default_factory=list)
    fp_status: Dict = field(default_factory=dict)

    @property
    def is_running(self) -> bool:
        return bool(self.pids)

    @property
    def has_fingerprint(self) -> bool:
        return self.fp_status.get("exists", False)

    @property
    def fp_locked(self) -> bool:
        return self.fp_status.get("locked", False)


def browser_display_name(executable: Optional[Path]) -> str:
    if executable is None:
        return "No local browser"
    if executable.name.lower() == "chrome.exe":
        return "Local Chromium"
    return "Local Camoufox"


def extract_profile_dir(command_line: str) -> str:
    for pattern in USER_DATA_DIR_PATTERNS:
        match = pattern.search(command_line)
        if match:
            return match.group(1).strip()
    return ""

def natural_profile_key(name: str) -> tuple[int, str]:
    match = re.search(r"(\d+)$", name)
    if match:
        return int(match.group(1)), name.lower()
    return sys.maxsize, name.lower()


def decode_last_browser(path: Path) -> Optional[str]:
    if not path.exists():
        return None

    raw = path.read_bytes()
    candidates = []

    try:
        candidates.append(raw.decode("utf-16le", errors="ignore"))
    except Exception:
        pass

    try:
        candidates.append(raw.decode("utf-8", errors="ignore"))
    except Exception:
        pass

    for candidate in candidates:
        cleaned = candidate.replace("\x00", "").strip()
        if cleaned:
            return cleaned

    return None


def extract_android_info(user_agent: str) -> tuple[str, str]:
    match = ANDROID_INFO_PATTERN.search(user_agent)
    if not match:
        return "Android", "Mobile"
    version = match.group("version").strip()
    device = match.group("device").strip()
    return version, device


def shorten(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def normalize_path(value: str | Path) -> str:
    return str(Path(value)).strip().rstrip("\\").lower()


def load_profiles() -> List[ProfileEntry]:
    if not PROFILES_DIR.exists():
        raise FileNotFoundError(f"Profiles folder not found: {PROFILES_DIR}")
    if not USER_AGENT_FILE.exists():
        raise FileNotFoundError(f"UserAgent.json not found: {USER_AGENT_FILE}")

    user_agents = json.loads(USER_AGENT_FILE.read_text(encoding="utf-8"))
    if not isinstance(user_agents, list) or not user_agents:
        raise ValueError("UserAgent.json must contain a non-empty list.")

    profile_paths = sorted(
        [path for path in PROFILES_DIR.iterdir() if path.is_dir()],
        key=lambda item: natural_profile_key(item.name),
    )
    profiles: List[ProfileEntry] = []

    for index, profile_path in enumerate(profile_paths):
        user_agent = str(user_agents[index % len(user_agents)]).strip()
        android_version, device_name = extract_android_info(user_agent)
        hint_text = decode_last_browser(profile_path / "Last Browser")
        browser_hint = Path(hint_text) if hint_text else None

        profiles.append(
            ProfileEntry(
                name=profile_path.name,
                path=profile_path,
                user_agent=user_agent,
                android_version=android_version,
                device_name=device_name,
                browser_hint=browser_hint,
                fp_status=fpm.get_fingerprint_status(profile_path),
            )
        )

    return profiles


def list_running_profile_pids(profile_map: Dict[str, ProfileEntry]) -> Dict[str, List[int]]:
    running: Dict[str, List[int]] = {key: [] for key in profile_map}
    command = r"""
$items = Get-CimInstance -Query "SELECT ProcessId, Name, CommandLine FROM Win32_Process WHERE Name = 'camoufox.exe' OR Name = 'chrome.exe'" |
  Where-Object {
    $_.CommandLine -and (
      $_.CommandLine -like '*-profile*' -or
      $_.CommandLine -like '*--user-data-dir*'
    )
  } |
  Select-Object ProcessId, Name, CommandLine

if ($items) {
  $items | ConvertTo-Json -Compress -Depth 3
}
"""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    output = result.stdout.strip()
    if not output:
        return running

    try:
        processes = json.loads(output)
    except json.JSONDecodeError:
        return running

    if isinstance(processes, dict):
        processes = [processes]

    for process in processes:
        command_line = process.get("CommandLine") or ""
        process_id = int(process.get("ProcessId", 0) or 0)
        if not command_line or process_id <= 0:
            continue

        user_data_dir = extract_profile_dir(command_line)
        if not user_data_dir:
            continue

        normalized = normalize_path(user_data_dir)
        if normalized in running:
            running[normalized].append(process_id)

    return running


class ProfileLauncherApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Portable Browser Profile Launcher")
        self.root.geometry("1380x860")
        self.root.minsize(1100, 700)
        self.root.configure(bg=WINDOW_BG)

        self.profiles: List[ProfileEntry] = []
        self.profile_by_name: Dict[str, ProfileEntry] = {}
        self.profile_by_path: Dict[str, ProfileEntry] = {}
        self.selection_vars: Dict[str, tk.BooleanVar] = {}
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.rows: Dict[str, Dict[str, tk.Widget]] = {}
        self.filtered_names: List[str] = []
        self.refresh_job: Optional[str] = None
        self.canvas_window: Optional[int] = None
        self.badge_count_label: Optional[tk.Label] = None

        self.reload_profiles()
        resolved_browser = self.resolve_browser_path()
        self.status_var.set(
            f"{len(self.profiles)} profiles ready. {browser_display_name(resolved_browser)} loaded from {resolved_browser or 'not found'}."
        )
        self._configure_styles()
        self._build_layout()
        self.render_profile_rows()
        self.refresh_status(silent=True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def reload_profiles(self) -> None:
        current_selection = {
            name: variable.get()
            for name, variable in getattr(self, "selection_vars", {}).items()
        }
        self.profiles = load_profiles()
        self.profile_by_name = {profile.name: profile for profile in self.profiles}
        self.profile_by_path = {normalize_path(profile.path): profile for profile in self.profiles}

        new_selection_vars: Dict[str, tk.BooleanVar] = {}
        for profile in self.profiles:
            variable = self.selection_vars.get(profile.name)
            if variable is None:
                variable = tk.BooleanVar(value=current_selection.get(profile.name, False))
            else:
                variable.set(current_selection.get(profile.name, False))
            new_selection_vars[profile.name] = variable
        self.selection_vars = new_selection_vars

    def suggested_profile_name(self) -> str:
        used_names = {profile.name for profile in self.profiles}
        max_suffix = 0
        for name in used_names:
            match = re.fullmatch(r"Profiles_(\d+)", name, re.IGNORECASE)
            if match:
                max_suffix = max(max_suffix, int(match.group(1)))

        candidate = max_suffix + 1
        while f"Profiles_{candidate}" in used_names:
            candidate += 1
        return f"Profiles_{candidate}"

    def validate_profile_name(self, name: str) -> Optional[str]:
        cleaned = name.strip()
        if not cleaned:
            return "Profile name blank नहीं हो सकता."
        if cleaned in {".", ".."}:
            return "यह profile name valid नहीं है."
        if any(char in INVALID_PROFILE_NAME_CHARS for char in cleaned):
            return 'Profile name में ये characters allowed नहीं हैं: <>:"/\\|?*'
        if (PROFILES_DIR / cleaned).exists():
            return f"{cleaned} नाम का profile पहले से मौजूद है."
        return None

    def _configure_styles(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Launcher.Vertical.TScrollbar",
            troughcolor=PANEL_BG,
            background="#cbb89b",
            bordercolor=PANEL_BG,
            arrowcolor=TEXT_PRIMARY,
            lightcolor=PANEL_BG,
            darkcolor=PANEL_BG,
        )
        style.map(
            "Launcher.Vertical.TScrollbar",
            background=[("active", "#b7a07f")],
        )

    def _build_layout(self) -> None:
        shell = tk.Frame(self.root, bg=WINDOW_BG)
        shell.pack(fill="both", expand=True, padx=20, pady=18)
        shell.rowconfigure(2, weight=1)
        shell.columnconfigure(0, weight=1)

        self._build_header(shell)
        self._build_toolbar(shell)
        self._build_profile_list(shell)

        status_bar = tk.Label(
            shell,
            textvariable=self.status_var,
            bg=WINDOW_BG,
            fg=TEXT_MUTED,
            anchor="w",
            font=("Segoe UI", 10),
            pady=8,
        )
        status_bar.grid(row=3, column=0, sticky="ew")

    def _build_header(self, parent: tk.Widget) -> None:
        header = tk.Frame(parent, bg=HEADER_BG, height=150, bd=0, highlightthickness=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=0)

        left = tk.Frame(header, bg=HEADER_BG)
        left.grid(row=0, column=0, sticky="nsew", padx=24, pady=22)

        tk.Label(
            left,
            text="Portable Browser Manager",
            bg=HEADER_BG,
            fg="white",
            font=("Bahnschrift SemiBold", 24),
            anchor="w",
        ).pack(anchor="w")

        tk.Label(
            left,
            text="Profile launcher focused on stable local Chromium sessions and reusable profile directories.",
            bg=HEADER_BG,
            fg="#d8e4ef",
            font=("Segoe UI", 11),
            anchor="w",
            justify="left",
        ).pack(anchor="w", pady=(8, 0))

        badge_frame = tk.Frame(header, bg=HEADER_BG)
        badge_frame.grid(row=0, column=1, padx=24, pady=24, sticky="e")

        badge = tk.Frame(badge_frame, bg=HEADER_ACCENT, padx=18, pady=12)
        badge.pack(anchor="e")
        tk.Label(
            badge,
            text="Profile Runtime",
            bg=HEADER_ACCENT,
            fg="#33210f",
            font=("Bahnschrift SemiBold", 13),
        ).pack(anchor="e")
        fp_count = sum(1 for p in self.profiles if p.has_fingerprint)
        self.badge_count_label = tk.Label(
            badge,
            text=f"{len(self.profiles)} profiles • {fp_count} fingerprints active",
            bg=HEADER_ACCENT,
            fg="#5b3816",
            font=("Segoe UI", 10),
        )
        self.badge_count_label.pack(anchor="e")

    def _build_toolbar(self, parent: tk.Widget) -> None:
        wrapper = tk.Frame(parent, bg=WINDOW_BG)
        wrapper.grid(row=1, column=0, sticky="ew", pady=(18, 14))
        wrapper.columnconfigure(1, weight=1)

        stats_holder = tk.Frame(wrapper, bg=WINDOW_BG)
        stats_holder.grid(row=0, column=0, sticky="w")

        self.total_value = self._stat_card(stats_holder, "Total Profiles", str(len(self.profiles)), "#11324d", "#edf4ff")
        self.running_value = self._stat_card(stats_holder, "Running", "0", SUCCESS, SUCCESS_SOFT)
        self.selected_value = self._stat_card(stats_holder, "Selected", "0", HEADER_ACCENT, "#fff1de")

        controls = tk.Frame(wrapper, bg=PANEL_BG, padx=18, pady=16, highlightbackground=BORDER, highlightthickness=1)
        controls.grid(row=0, column=1, sticky="ew", padx=(20, 0))
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(3, weight=1)

        tk.Label(
            controls,
            text="Browser Engine",
            bg=PANEL_BG,
            fg=TEXT_PRIMARY,
            font=("Bahnschrift SemiBold", 11),
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        tk.Label(
            controls,
            text=f"{browser_display_name(self.resolve_browser_path())} (preferred for stable logins)",
            bg=SEARCH_BG,
            fg=TEXT_PRIMARY,
            padx=12,
            pady=10,
            font=("Bahnschrift SemiBold", 10),
            anchor="w",
            justify="left",
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
        ).grid(row=0, column=1, sticky="ew", padx=(0, 18))

        tk.Label(
            controls,
            text="Search profile / device",
            bg=PANEL_BG,
            fg=TEXT_PRIMARY,
            font=("Bahnschrift SemiBold", 11),
        ).grid(row=0, column=2, sticky="w", padx=(0, 10))

        search_entry = tk.Entry(
            controls,
            textvariable=self.search_var,
            bg=SEARCH_BG,
            fg=TEXT_PRIMARY,
            relief="flat",
            insertbackground=TEXT_PRIMARY,
            font=("Segoe UI", 10),
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        search_entry.grid(row=0, column=3, sticky="ew")
        self.search_var.trace_add("write", lambda *_: self.render_profile_rows())

        tk.Label(
            controls,
            text=str(self.resolve_browser_path() or LOCAL_CHROMIUM_EXE),
            bg=PANEL_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
            anchor="w",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        actions = tk.Frame(controls, bg=PANEL_BG)
        actions.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(14, 0))

        self._action_button(actions, "New Profile", self.create_profile, "#284b63", "white").pack(side="left")
        self._action_button(actions, "Select Visible", self.select_visible, "#f0f4f8", TEXT_PRIMARY).pack(side="left")
        self._action_button(actions, "Clear Selection", self.clear_selection, "#f7efe3", TEXT_PRIMARY).pack(side="left", padx=(10, 0))
        self._action_button(actions, "Open Selected", self.open_selected, ACCENT, "white").pack(side="left", padx=(18, 0))
        self._action_button(actions, "Close Selected", self.close_selected, DANGER, "white").pack(side="left", padx=(10, 0))
        self._action_button(actions, "Delete Selected", self.delete_selected, "#7d2e3e", "white").pack(side="left", padx=(10, 0))
        self._action_button(actions, "Refresh Status", lambda: self.refresh_status(silent=False), "#183b56", "white").pack(side="left", padx=(10, 0))

        # Fingerprint action buttons
        fp_actions = tk.Frame(controls, bg=PANEL_BG)
        fp_actions.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(10, 0))

        self._action_button(fp_actions, "🛡️ Sync All FP", self.sync_all_fingerprints, FP_ACTIVE, "white").pack(side="left")
        self._action_button(fp_actions, "🔒 Lock All", self.lock_all_fingerprints, FP_LOCKED, "white").pack(side="left", padx=(10, 0))
        self._action_button(fp_actions, "🔓 Unlock All", self.unlock_all_fingerprints, "#6b7280", "white").pack(side="left", padx=(10, 0))
        self._action_button(fp_actions, "🔄 Regen Selected", self.regen_selected_fingerprints, "#6d28d9", "white").pack(side="left", padx=(10, 0))

        note = tk.Label(
            fp_actions,
            text="Stable local Chromium launch is preferred; Camoufox remains only as fallback.",
            bg=PANEL_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 10),
        )
        note.pack(side="right")

    def _stat_card(self, parent: tk.Widget, title: str, value: str, accent_color: str, bg_color: str) -> tk.Label:
        card = tk.Frame(parent, bg=bg_color, padx=18, pady=14, highlightbackground=BORDER, highlightthickness=1)
        card.pack(side="left", padx=(0, 12))

        tk.Label(
            card,
            text=title,
            bg=bg_color,
            fg=TEXT_MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        value_label = tk.Label(
            card,
            text=value,
            bg=bg_color,
            fg=accent_color,
            font=("Bahnschrift SemiBold", 22),
        )
        value_label.pack(anchor="w", pady=(4, 0))
        return value_label

    def _action_button(self, parent: tk.Widget, text: str, command, bg: str, fg: str) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=bg if bg in (ACCENT, DANGER, "#183b56") else "#e8ecef",
            activeforeground=fg,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=10,
            font=("Bahnschrift SemiBold", 10),
        )

    def _build_profile_list(self, parent: tk.Widget) -> None:
        container = tk.Frame(parent, bg=PANEL_BG, highlightbackground=BORDER, highlightthickness=1)
        container.grid(row=2, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        headings = tk.Frame(container, bg=PANEL_BG, padx=20, pady=16)
        headings.grid(row=0, column=0, sticky="ew")
        headings.columnconfigure(2, weight=1)

        tk.Label(headings, text="Pick", bg=PANEL_BG, fg=TEXT_MUTED, font=("Bahnschrift SemiBold", 11)).grid(row=0, column=0, sticky="w")
        tk.Label(headings, text="Profile", bg=PANEL_BG, fg=TEXT_MUTED, font=("Bahnschrift SemiBold", 11)).grid(row=0, column=1, sticky="w", padx=(16, 0))
        tk.Label(headings, text="Assigned Android User-Agent", bg=PANEL_BG, fg=TEXT_MUTED, font=("Bahnschrift SemiBold", 11)).grid(row=0, column=2, sticky="w", padx=(14, 0))
        tk.Label(headings, text="Action", bg=PANEL_BG, fg=TEXT_MUTED, font=("Bahnschrift SemiBold", 11)).grid(row=0, column=3, sticky="e")

        canvas_holder = tk.Frame(container, bg=PANEL_BG)
        canvas_holder.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 10))
        canvas_holder.rowconfigure(0, weight=1)
        canvas_holder.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_holder,
            bg=PANEL_BG,
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            canvas_holder,
            orient="vertical",
            command=self.canvas.yview,
            style="Launcher.Vertical.TScrollbar",
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.list_frame = tk.Frame(self.canvas, bg=PANEL_BG)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")

        self.list_frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(self.canvas_window, width=event.width),
        )
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event: tk.Event) -> None:
        if event.delta:
            self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def render_profile_rows(self) -> None:
        visible_profiles = self._filtered_profiles()
        self.filtered_names = [profile.name for profile in visible_profiles]

        for child in self.list_frame.winfo_children():
            child.destroy()
        self.rows.clear()

        if not visible_profiles:
            empty = tk.Label(
                self.list_frame,
                text="No profiles matched your search.",
                bg=PANEL_BG,
                fg=TEXT_MUTED,
                font=("Segoe UI", 12),
                pady=40,
            )
            empty.pack(fill="x")
            self.update_stats()
            return

        for profile in visible_profiles:
            self._create_profile_row(profile)

        self.update_stats()

    def _filtered_profiles(self) -> List[ProfileEntry]:
        query = self.search_var.get().strip().lower()
        if not query:
            return self.profiles

        visible: List[ProfileEntry] = []
        for profile in self.profiles:
            haystack = " ".join(
                [
                    profile.name.lower(),
                    profile.device_name.lower(),
                    profile.android_version.lower(),
                    profile.user_agent.lower(),
                ]
            )
            if query in haystack:
                visible.append(profile)
        return visible

    def _create_profile_row(self, profile: ProfileEntry) -> None:
        row_bg = CARD_BG
        card = tk.Frame(
            self.list_frame,
            bg=row_bg,
            padx=16,
            pady=14,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        card.pack(fill="x", padx=10, pady=7)
        card.columnconfigure(2, weight=1)

        checkbox = tk.Checkbutton(
            card,
            variable=self.selection_vars[profile.name],
            command=self.update_stats,
            bg=row_bg,
            activebackground=row_bg,
            selectcolor=row_bg,
            cursor="hand2",
        )
        checkbox.grid(row=0, column=0, rowspan=2, sticky="n", pady=(4, 0))

        info = tk.Frame(card, bg=row_bg)
        info.grid(row=0, column=1, rowspan=2, sticky="nw", padx=(16, 16))

        tk.Label(
            info,
            text=profile.name,
            bg=row_bg,
            fg=TEXT_PRIMARY,
            font=("Bahnschrift SemiBold", 15),
            anchor="w",
        ).pack(anchor="w")

        meta_text = f"{profile.device_name}  •  Android {profile.android_version}"
        tk.Label(
            info,
            text=meta_text,
            bg=row_bg,
            fg=TEXT_MUTED,
            font=("Segoe UI", 10),
            anchor="w",
        ).pack(anchor="w", pady=(4, 2))

        # Fingerprint status badge
        fp_badge_frame = tk.Frame(info, bg=row_bg)
        fp_badge_frame.pack(anchor="w", pady=(2, 2))

        if profile.has_fingerprint:
            fp_gpu = profile.fp_status.get("gpu", "")
            if profile.fp_locked:
                fp_badge_text = f"🔒 FP Locked  •  {fp_gpu}"
                fp_badge_bg = "#fef3c7"
                fp_badge_fg = "#92400e"
            else:
                fp_badge_text = f"🛡️ FP Active  •  {fp_gpu}"
                fp_badge_bg = "#dbeafe"
                fp_badge_fg = "#1e40af"
        else:
            fp_badge_text = "⚠ No Fingerprint"
            fp_badge_bg = "#fde7df"
            fp_badge_fg = "#9e462b"

        fp_badge = tk.Label(
            fp_badge_frame,
            text=fp_badge_text,
            bg=fp_badge_bg,
            fg=fp_badge_fg,
            font=("Segoe UI", 9),
            padx=8,
            pady=2,
        )
        fp_badge.pack(side="left")

        # Per-profile lock toggle button
        lock_text = "Unlock" if profile.fp_locked else "Lock"
        lock_btn = tk.Button(
            fp_badge_frame,
            text=lock_text,
            command=lambda n=profile.name: self.toggle_fp_lock(n),
            bg="#e5e7eb",
            fg=TEXT_PRIMARY,
            relief="flat",
            cursor="hand2",
            padx=6,
            pady=1,
            font=("Segoe UI", 8),
        )
        lock_btn.pack(side="left", padx=(6, 0))

        # Per-profile regen button
        regen_btn = tk.Button(
            fp_badge_frame,
            text="Regen",
            command=lambda n=profile.name: self.regen_single_fingerprint(n),
            bg="#e5e7eb",
            fg=TEXT_PRIMARY,
            relief="flat",
            cursor="hand2",
            padx=6,
            pady=1,
            font=("Segoe UI", 8),
        )
        regen_btn.pack(side="left", padx=(4, 0))

        tk.Label(
            info,
            text=str(profile.path),
            bg=row_bg,
            fg="#8a7f70",
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(anchor="w")

        details = tk.Frame(card, bg=row_bg)
        details.grid(row=0, column=2, rowspan=2, sticky="nsew")
        details.columnconfigure(0, weight=1)

        status_chip = tk.Label(
            details,
            text="Checking...",
            bg=STATUS_BG,
            fg=TEXT_PRIMARY,
            font=("Bahnschrift SemiBold", 10),
            padx=10,
            pady=4,
        )
        status_chip.grid(row=0, column=0, sticky="w")

        tk.Label(
            details,
            text=shorten(profile.user_agent, 140),
            bg=row_bg,
            fg=TEXT_PRIMARY,
            justify="left",
            wraplength=620,
            font=("Segoe UI", 10),
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", pady=(10, 0))

        actions = tk.Frame(card, bg=row_bg)
        actions.grid(row=0, column=3, rowspan=2, sticky="e", padx=(18, 0))

        action_button = tk.Button(
            actions,
            text="Open",
            command=lambda name=profile.name: self.open_profile_by_name(name),
            bg=ACCENT,
            fg="white",
            activebackground=ACCENT_DARK,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=10,
            font=("Bahnschrift SemiBold", 10),
            width=10,
        )
        action_button.pack(anchor="e")

        close_button = tk.Button(
            actions,
            text="Close",
            command=lambda name=profile.name: self.close_profile_by_name(name),
            bg=DANGER,
            fg="white",
            activebackground=DANGER_DARK,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=9,
            font=("Bahnschrift SemiBold", 10),
            width=10,
            disabledforeground="#f4d5cb",
        )
        close_button.pack(anchor="e", pady=(10, 0))

        self.rows[profile.name] = {
            "card": card,
            "status": status_chip,
            "open_button": action_button,
            "close_button": close_button,
        }
        self._sync_row_state(profile)

    def update_stats(self) -> None:
        selected_count = sum(1 for name in self.filtered_names if self.selection_vars[name].get())
        running_count = sum(1 for profile in self.profiles if profile.is_running)
        fp_count = sum(1 for profile in self.profiles if profile.has_fingerprint)
        self.total_value.config(text=str(len(self.profiles)))
        self.running_value.config(text=str(running_count))
        self.selected_value.config(text=str(selected_count))
        if self.badge_count_label is not None:
            self.badge_count_label.config(text=f"{len(self.profiles)} profiles • {fp_count} fingerprints active")

    def _sync_row_state(self, profile: ProfileEntry) -> None:
        row = self.rows.get(profile.name)
        if not row:
            return

        card = row["card"]
        status_chip = row["status"]
        open_button = row["open_button"]
        close_button = row["close_button"]

        if profile.is_running:
            card.config(bg="#fcfffd", highlightbackground="#bfe7d0")
            status_chip.config(
                text=f"Running  •  PID {profile.pids[0]}" + (f" +{len(profile.pids) - 1}" if len(profile.pids) > 1 else ""),
                bg=SUCCESS_SOFT,
                fg=SUCCESS,
            )
            open_button.config(
                state="disabled",
                bg="#6ba39d",
                activebackground="#6ba39d",
                disabledforeground="#e8fffb",
            )
            close_button.config(
                state="normal",
                command=lambda name=profile.name: self.close_profile_by_name(name),
                bg=DANGER,
                activebackground=DANGER_DARK,
            )
        else:
            card.config(bg=CARD_BG, highlightbackground=BORDER)
            status_chip.config(text="Stopped", bg=STATUS_BG, fg=TEXT_PRIMARY)
            open_button.config(
                state="normal",
                command=lambda name=profile.name: self.open_profile_by_name(name),
                bg=ACCENT,
                activebackground=ACCENT_DARK,
            )
            close_button.config(
                state="disabled",
                bg=DANGER,
                activebackground=DANGER_DARK,
            )

    def select_visible(self) -> None:
        for name in self.filtered_names:
            self.selection_vars[name].set(True)
        self.update_stats()
        self.status_var.set(f"{len(self.filtered_names)} visible profiles selected.")

    def clear_selection(self) -> None:
        for variable in self.selection_vars.values():
            variable.set(False)
        self.update_stats()
        self.status_var.set("Selection cleared.")

    def create_profile(self) -> None:
        suggested_name = self.suggested_profile_name()
        profile_name = simpledialog.askstring(
            "New Profile",
            "Naya profile name dijiye:",
            initialvalue=suggested_name,
            parent=self.root,
        )
        if profile_name is None:
            return

        error = self.validate_profile_name(profile_name)
        if error:
            messagebox.showerror("Invalid profile name", error)
            return

        profile_path = PROFILES_DIR / profile_name.strip()
        try:
            profile_path.mkdir(parents=False, exist_ok=False)
            (profile_path / "Default").mkdir(exist_ok=True)
        except Exception as exc:
            messagebox.showerror("Profile create failed", f"{profile_name} create नहीं हो पाया.\n\n{exc}")
            return

        self.reload_profiles()
        self.render_profile_rows()
        self.selection_vars[profile_name.strip()].set(True)
        self.update_stats()
        self.status_var.set(
            f"{profile_name.strip()} create हो गया. Open दबाते hi {browser_display_name(self.resolve_browser_path())} ise initialize karega."
        )

    def delete_selected(self) -> None:
        self.refresh_status(silent=True)
        names = [name for name in self.filtered_names if self.selection_vars[name].get()]
        if not names:
            messagebox.showinfo("No profile selected", "Delete Selected के लिए कम से कम एक profile चुनें.")
            return

        running_names = [name for name in names if self.profile_by_name[name].is_running]
        if running_names:
            messagebox.showwarning(
                "Close running profiles first",
                "Running profiles delete नहीं किए जा सकते.\n\nपहले इन्हें बंद करें:\n" + "\n".join(running_names),
            )
            return

        profile_word = "profiles" if len(names) > 1 else "profile"
        confirmed = messagebox.askyesno(
            "Delete selected profiles",
            f"{len(names)} {profile_word} permanently delete होंगे.\n\n"
            + "\n".join(names)
            + "\n\nक्या delete करना है?",
            parent=self.root,
        )
        if not confirmed:
            return

        failures: List[str] = []
        for name in names:
            try:
                shutil.rmtree(self.profile_by_name[name].path)
            except Exception as exc:
                failures.append(f"{name}: {exc}")

        self.reload_profiles()
        self.render_profile_rows()
        self.refresh_status(silent=True)

        if failures:
            messagebox.showerror(
                "Delete completed with errors",
                "कुछ profiles delete नहीं हो पाए:\n\n" + "\n".join(failures),
            )
            self.status_var.set(f"{len(names) - len(failures)} profiles deleted, {len(failures)} failed.")
        else:
            self.status_var.set(f"{len(names)} selected profiles permanently deleted.")

    def open_selected(self) -> None:
        names = [name for name in self.filtered_names if self.selection_vars[name].get()]
        if not names:
            messagebox.showinfo("No profile selected", "Open Selected के लिए कम से कम एक profile चुनें.")
            return

        failures = 0
        for name in names:
            if not self.open_profile_by_name(name, show_message=False):
                failures += 1

        self.refresh_status(silent=True)
        if failures:
            self.status_var.set(f"{len(names) - failures} profiles opened, {failures} failed.")
        else:
            self.status_var.set(f"{len(names)} selected profiles launched in {browser_display_name(self.resolve_browser_path())}.")

    def close_selected(self) -> None:
        names = [name for name in self.filtered_names if self.selection_vars[name].get()]
        if not names:
            messagebox.showinfo("No profile selected", "Close Selected के लिए कम से कम एक profile चुनें.")
            return

        closed_any = False
        for name in names:
            closed_any = self.close_profile_by_name(name, show_message=False) or closed_any

        self.refresh_status(silent=True)
        if closed_any:
            self.status_var.set(f"{len(names)} selected profiles close command sent.")
        else:
            self.status_var.set("Selected profiles were not running.")

    def resolve_browser_path(self) -> Optional[Path]:
        if LOCAL_CHROMIUM_EXE.exists():
            return LOCAL_CHROMIUM_EXE
        if LOCAL_CAMOUFOX_EXE.exists():
            return LOCAL_CAMOUFOX_EXE
        return None

    def build_launch_arguments(self, executable: Path, profile: ProfileEntry) -> List[str]:
        is_mobile = "Mobile" in profile.user_agent or "Android" in profile.user_agent
        
        if is_mobile:
            device = profile.device_name.lower()
            # Samsung
            if "sm-g973" in device: width, height = 360, 760 # Galaxy S10
            elif "sm-g991" in device: width, height = 360, 800 # Galaxy S21
            elif "sm-g996" in device: width, height = 384, 854 # Galaxy S21+
            elif "sm-s918" in device: width, height = 412, 915 # Galaxy S23 Ultra
            elif "sm-a" in device or "sm-m" in device: width, height = 412, 892
            # Google
            elif "pixel 6" in device: width, height = 412, 915
            elif "pixel 7 pro" in device: width, height = 412, 892
            # Xiaomi / Redmi / Poco
            elif "redmi note" in device or "poco" in device or "m2101" in device: width, height = 393, 851
            # OnePlus
            elif "oneplus" in device: width, height = 412, 915
            # Vivo / Oppo / Realme
            elif "vivo" in device: width, height = 390, 844
            elif "realme" in device or "rmx" in device: width, height = 393, 851
            elif "oppo" in device: width, height = 393, 851
            # Moto / Nokia / Infinix
            elif "moto" in device: width, height = 412, 915
            elif "nokia" in device: width, height = 390, 844
            elif "infinix" in device: width, height = 393, 851
            # Default Mobile fallback
            else: width, height = 412, 915
        else:
            width, height = 1280, 800

        if executable.name.lower() == "chrome.exe":
            return [
                str(executable),
                f"--user-data-dir={profile.path}",
                "--no-first-run",
                "--no-default-browser-check",
                "--new-window",
                f"--window-size={width},{height}",
                "about:blank",
            ]

        args = [
            str(executable),
            "-profile", str(profile.path),
            "--new-instance",
            "--no-remote",
            "-width", str(width),
            "-height", str(height),
            "about:blank",
        ]
        return args

    def open_profile_by_name(self, profile_name: str, show_message: bool = True) -> bool:
        profile = self.profile_by_name[profile_name]
        if profile.is_running:
            if show_message:
                self.status_var.set(f"{profile.name} पहले से running है.")
            return True

        executable = self.resolve_browser_path()
        if executable is None:
            messagebox.showerror(
                "Browser not found",
                "No local browser executable found.\n\n"
                f"Checked:\n{LOCAL_CHROMIUM_EXE}\n{LOCAL_CAMOUFOX_EXE}",
            )
            return False

        # Auto-generate fingerprint if not present
        if not profile.has_fingerprint:
            fpm.create_fingerprint(
                profile_path=profile.path,
                profile_name=profile.name,
                user_agent=profile.user_agent,
            )
            profile.fp_status = fpm.get_fingerprint_status(profile.path)

        if executable.name.lower() != "chrome.exe":
            # Camoufox fallback is kept only as a compatibility backup.
            user_js = profile.path / "user.js"
            prefs = [
                f'user_pref("general.useragent.override", "{profile.user_agent}");',
            ]
            if "Mobile" in profile.user_agent or "Android" in profile.user_agent:
                prefs.extend([
                    'user_pref("general.appversion.override", "5.0 (Android)");',
                    'user_pref("general.platform.override", "Linux armv8l");',
                    'user_pref("general.osname.override", "Android");',
                    'user_pref("dom.maxTouchPoints", 5);'
                ])
            try:
                with open(user_js, "w", encoding="utf-8") as f:
                    f.write("\n".join(prefs) + "\n")
            except Exception:
                pass

        args = self.build_launch_arguments(executable, profile)
        try:
            subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as exc:
            messagebox.showerror("Launch failed", f"{profile.name} launch नहीं हो पाया.\n\n{exc}")
            return False

        gpu_info = profile.fp_status.get("gpu", "")
        self.status_var.set(f"{profile.name} launched with fingerprint: {profile.device_name} • {gpu_info}.")
        self.root.after(1200, lambda: self.refresh_status(silent=True))
        return True

    def close_profile_by_name(self, profile_name: str, show_message: bool = True) -> bool:
        profile = self.profile_by_name[profile_name]
        if not profile.is_running:
            if show_message:
                self.status_var.set(f"{profile.name} running नहीं है.")
            return False

        for pid in profile.pids:
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

        if show_message:
            self.status_var.set(f"{profile.name} के browser process बंद करने की कोशिश की गई.")
        self.root.after(1200, lambda: self.refresh_status(silent=True))
        return True

    def refresh_status(self, silent: bool = False) -> None:
        try:
            running_map = list_running_profile_pids(self.profile_by_path)
        except Exception:
            running_map = {}

        for profile in self.profiles:
            profile.pids = running_map.get(normalize_path(profile.path), [])
            self._sync_row_state(profile)

        self.update_stats()
        if not silent:
            running_count = sum(1 for profile in self.profiles if profile.is_running)
            self.status_var.set(f"Status refreshed. {running_count} profile(s) currently running.")

        self._schedule_refresh()

    def _schedule_refresh(self) -> None:
        if self.refresh_job is not None:
            self.root.after_cancel(self.refresh_job)
        self.refresh_job = self.root.after(REFRESH_INTERVAL_MS, lambda: self.refresh_status(silent=True))

    # ── Fingerprint Actions ─────────────────────────────────────────────

    def sync_all_fingerprints(self) -> None:
        """Generate/update fingerprints for all unlocked profiles."""
        profiles_data = [
            {"path": p.path, "name": p.name, "user_agent": p.user_agent}
            for p in self.profiles
        ]
        results = fpm.bulk_sync(profiles_data)
        locked = sum(1 for issues in results.values() if any("Locked" in i for i in issues))
        synced = len(results) - locked
        self.reload_profiles()
        self.render_profile_rows()
        self.refresh_status(silent=True)
        self.status_var.set(f"Fingerprints synced: {synced} updated, {locked} locked (skipped).")

    def lock_all_fingerprints(self) -> None:
        paths = [p.path for p in self.profiles]
        count = fpm.bulk_lock(paths)
        self.reload_profiles()
        self.render_profile_rows()
        self.status_var.set(f"{count} fingerprints locked.")

    def unlock_all_fingerprints(self) -> None:
        paths = [p.path for p in self.profiles]
        count = fpm.bulk_unlock(paths)
        self.reload_profiles()
        self.render_profile_rows()
        self.status_var.set(f"{count} fingerprints unlocked.")

    def regen_selected_fingerprints(self) -> None:
        names = [name for name in self.filtered_names if self.selection_vars[name].get()]
        if not names:
            messagebox.showinfo("No profile selected", "Regen Selected ke liye kam se kam ek profile chunein.")
            return
        count = 0
        skipped = 0
        for name in names:
            profile = self.profile_by_name[name]
            fp, issues = fpm.regenerate_fingerprint(
                profile_path=profile.path,
                profile_name=profile.name,
                user_agent=profile.user_agent,
                keep_identity=True,
            )
            if any("Locked" in i for i in issues):
                skipped += 1
            else:
                count += 1
        self.reload_profiles()
        self.render_profile_rows()
        self.status_var.set(f"{count} fingerprints regenerated (identity preserved), {skipped} locked (skipped).")

    def toggle_fp_lock(self, profile_name: str) -> None:
        profile = self.profile_by_name[profile_name]
        if profile.fp_locked:
            fpm.unlock_fingerprint(profile.path)
            self.status_var.set(f"{profile_name} fingerprint unlocked.")
        else:
            if not profile.has_fingerprint:
                fpm.create_fingerprint(profile.path, profile.name, profile.user_agent)
            fpm.lock_fingerprint(profile.path)
            self.status_var.set(f"{profile_name} fingerprint locked.")
        self.reload_profiles()
        self.render_profile_rows()

    def regen_single_fingerprint(self, profile_name: str) -> None:
        profile = self.profile_by_name[profile_name]
        if profile.fp_locked:
            messagebox.showinfo("Locked", f"{profile_name} ka fingerprint locked hai. Pehle unlock karein.")
            return
        fpm.regenerate_fingerprint(
            profile_path=profile.path,
            profile_name=profile.name,
            user_agent=profile.user_agent,
            keep_identity=True,
        )
        self.reload_profiles()
        self.render_profile_rows()
        self.status_var.set(f"{profile_name} fingerprint regenerated (identity stable).")

    def on_close(self) -> None:
        if self.refresh_job is not None:
            self.root.after_cancel(self.refresh_job)
        self.canvas.unbind_all("<MouseWheel>")
        self.root.destroy()


def main() -> None:
    root: Optional[tk.Tk] = None
    try:
        root = tk.Tk()
        app = ProfileLauncherApp(root)
    except Exception as exc:
        message = f"GUI start नहीं हो पाया:\n\n{exc}"
        try:
            if root is None:
                root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Startup error", message)
        finally:
            raise

    root.mainloop()


if __name__ == "__main__":
    main()
