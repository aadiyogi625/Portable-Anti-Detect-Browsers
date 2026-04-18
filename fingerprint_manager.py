"""
fingerprint_manager.py
=======================
Manages fingerprint lifecycle: generate, load, save, lock/unlock, regenerate,
and bulk-sync operations across all profiles.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fingerprint_generator import generate_fingerprint, validate_fingerprint


FINGERPRINT_FILENAME = "fingerprint.json"
FINGERPRINT_VERSION = 2


# ---------------------------------------------------------------------------
#  Core I/O
# ---------------------------------------------------------------------------

def fingerprint_path(profile_path: Path) -> Path:
    """Return the path to fingerprint.json inside a profile directory."""
    return profile_path / FINGERPRINT_FILENAME


def load_fingerprint(profile_path: Path) -> Optional[Dict[str, Any]]:
    """Load an existing fingerprint.json from a profile.  Returns None if missing."""
    fp_file = fingerprint_path(profile_path)
    if not fp_file.exists():
        return None
    try:
        return json.loads(fp_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_fingerprint(profile_path: Path, fingerprint: Dict[str, Any]) -> None:
    """Write fingerprint.json to a profile directory (pretty-printed)."""
    fp_file = fingerprint_path(profile_path)
    fp_file.write_text(
        json.dumps(fingerprint, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
#  Status helpers
# ---------------------------------------------------------------------------

def has_fingerprint(profile_path: Path) -> bool:
    return fingerprint_path(profile_path).exists()


def is_locked(profile_path: Path) -> bool:
    fp = load_fingerprint(profile_path)
    if fp is None:
        return False
    return bool(fp.get("locked", False))


def get_fingerprint_status(profile_path: Path) -> Dict[str, Any]:
    """Return a summary dict for GUI display."""
    fp = load_fingerprint(profile_path)
    if fp is None:
        return {
            "exists": False,
            "locked": False,
            "version": 0,
            "generated_at": None,
            "device": None,
            "gpu": None,
        }
    info = fp.get("device_info", {})
    return {
        "exists": True,
        "locked": bool(fp.get("locked", False)),
        "version": fp.get("version", 1),
        "generated_at": fp.get("generated_at"),
        "device": info.get("model"),
        "gpu": info.get("gpu"),
    }


# ---------------------------------------------------------------------------
#  Generate / Regenerate
# ---------------------------------------------------------------------------

def create_fingerprint(
    profile_path: Path,
    profile_name: str,
    user_agent: str,
    force: bool = False,
    timezone_id: Optional[str] = None,
    timezone_offset: Optional[int] = None,
    locale_override: Optional[str] = None,
) -> Tuple[Dict[str, Any], List[str]]:
    """Generate a new fingerprint for a profile.

    Parameters
    ----------
    profile_path : Path
        Full path to the profile directory.
    profile_name : str
        Profile name (used for seeding).
    user_agent : str
        The User-Agent string assigned to this profile.
    force : bool
        If True, overwrites even if locked.
    timezone_id, timezone_offset, locale_override : optional
        Overrides for timezone/locale.

    Returns
    -------
    (fingerprint_dict, issues_list)
    """
    existing = load_fingerprint(profile_path)
    if existing and existing.get("locked") and not force:
        return existing, ["Fingerprint is locked — skipped."]

    # Preserve identity seed from existing fingerprint if available
    identity_seed = None
    if existing:
        identity_seed = existing.get("identity_seed")

    fp = generate_fingerprint(
        user_agent=user_agent,
        profile_name=profile_name,
        identity_seed=identity_seed,
        timezone_id=timezone_id,
        timezone_offset=timezone_offset,
        locale_override=locale_override,
    )

    issues = validate_fingerprint(fp)
    save_fingerprint(profile_path, fp)
    return fp, issues


def regenerate_fingerprint(
    profile_path: Path,
    profile_name: str,
    user_agent: str,
    keep_identity: bool = True,
    force: bool = False,
) -> Tuple[Dict[str, Any], List[str]]:
    """Regenerate fingerprint, optionally preserving identity seed.

    When keep_identity=True, the canvas/audio noise seeds remain stable
    so the fingerprint "identity" is consistent; other hardware values
    are re-derived from the device database (useful if database is updated).
    """
    existing = load_fingerprint(profile_path)
    if existing and existing.get("locked") and not force:
        return existing, ["Fingerprint is locked — skipped."]

    identity_seed = None
    if keep_identity and existing:
        identity_seed = existing.get("identity_seed")

    # Preserve timezone/locale overrides from existing fingerprint
    tz_id = None
    tz_off = None
    locale = None
    if existing:
        tz = existing.get("timezone", {})
        loc = existing.get("locale", {})
        tz_id = tz.get("id")
        tz_off = tz.get("offset")
        locale = loc.get("language")

    fp = generate_fingerprint(
        user_agent=user_agent,
        profile_name=profile_name,
        identity_seed=identity_seed,
        timezone_id=tz_id,
        timezone_offset=tz_off,
        locale_override=locale,
    )

    issues = validate_fingerprint(fp)
    save_fingerprint(profile_path, fp)
    return fp, issues


# ---------------------------------------------------------------------------
#  Lock / Unlock
# ---------------------------------------------------------------------------

def lock_fingerprint(profile_path: Path) -> bool:
    """Lock a fingerprint to prevent regeneration.  Returns False if no fingerprint exists."""
    fp = load_fingerprint(profile_path)
    if fp is None:
        return False
    fp["locked"] = True
    save_fingerprint(profile_path, fp)
    return True


def unlock_fingerprint(profile_path: Path) -> bool:
    """Unlock a fingerprint.  Returns False if no fingerprint exists."""
    fp = load_fingerprint(profile_path)
    if fp is None:
        return False
    fp["locked"] = False
    save_fingerprint(profile_path, fp)
    return True


# ---------------------------------------------------------------------------
#  Bulk Operations
# ---------------------------------------------------------------------------

@staticmethod
def _noop():
    pass


def bulk_sync(
    profiles: List[Dict[str, Any]],
    force: bool = False,
) -> Dict[str, List[str]]:
    """Generate/update fingerprints for all given profiles.

    Parameters
    ----------
    profiles : list of dicts
        Each dict must have keys: ``path`` (Path), ``name`` (str), ``user_agent`` (str).
    force : bool
        If True, overwrite even locked fingerprints.

    Returns
    -------
    dict mapping profile_name → list of issues (empty list = success).
    """
    results: Dict[str, List[str]] = {}
    for prof in profiles:
        path = Path(prof["path"])
        name = prof["name"]
        ua = prof["user_agent"]

        existing = load_fingerprint(path)
        if existing and existing.get("locked") and not force:
            results[name] = ["Locked — skipped."]
            continue

        _, issues = create_fingerprint(
            profile_path=path,
            profile_name=name,
            user_agent=ua,
            force=force,
        )
        results[name] = issues

    return results


def bulk_lock(profile_paths: List[Path]) -> int:
    """Lock all given profiles.  Returns count of successfully locked."""
    count = 0
    for path in profile_paths:
        if lock_fingerprint(path):
            count += 1
    return count


def bulk_unlock(profile_paths: List[Path]) -> int:
    """Unlock all given profiles.  Returns count of successfully unlocked."""
    count = 0
    for path in profile_paths:
        if unlock_fingerprint(path):
            count += 1
    return count


# ---------------------------------------------------------------------------
#  Extension data writer
# ---------------------------------------------------------------------------

def write_extension_config(profile_path: Path, extension_dir: Path) -> bool:
    """Write the fingerprint data to the extension directory so the
    content script can read it at runtime.

    The data is written as ``config.js`` in the extension directory —
    a simple variable assignment that the content script loads.
    """
    fp = load_fingerprint(profile_path)
    if fp is None:
        return False

    config_content = f"// Auto-generated — do not edit\nwindow.__FP_CONFIG__ = {json.dumps(fp, ensure_ascii=False)};\n"
    config_file = extension_dir / "config.js"
    config_file.write_text(config_content, encoding="utf-8")
    return True
