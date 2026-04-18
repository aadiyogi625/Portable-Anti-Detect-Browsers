"""
fingerprint_generator.py
=========================
Core engine that parses a User-Agent string and produces a fully consistent
browser fingerprint dictionary.  All values are derived from the device
hardware database (fingerprint_datasets.py), never randomly chosen.
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from fingerprint_datasets import (
    DEVICE_PROFILES,
    DEFAULT_TIMEZONE_LOCALE,
    DeviceProfile,
    get_fonts_for_android_version,
    get_ua_data_brands,
    get_webgl_extensions,
)


# ---------------------------------------------------------------------------
#  UA Parsing
# ---------------------------------------------------------------------------

_UA_ANDROID_RE = re.compile(
    r"Android\s+(?P<os_ver>[\d.]+);\s*(?P<device>[^)]+?)\)\s+AppleWebKit",
    re.IGNORECASE,
)
_UA_CHROME_RE = re.compile(
    r"Chrome/(?P<chrome_ver>[\d.]+)",
    re.IGNORECASE,
)


def parse_user_agent(ua: str) -> Dict[str, str]:
    """Extract device model, Android version, and Chrome version from a UA."""
    result: Dict[str, str] = {
        "os_version": "10",
        "device_model": "Generic Android",
        "chrome_version": "120.0.6099.230",
        "is_mobile": "Mobile" in ua,
    }

    m = _UA_ANDROID_RE.search(ua)
    if m:
        result["os_version"] = m.group("os_ver").strip()
        result["device_model"] = m.group("device").strip()

    m = _UA_CHROME_RE.search(ua)
    if m:
        result["chrome_version"] = m.group("chrome_ver").strip()

    return result


# ---------------------------------------------------------------------------
#  Device Lookup (fuzzy matching)
# ---------------------------------------------------------------------------

def _normalize_model(model: str) -> str:
    """Normalize a device model string for fuzzy matching."""
    return model.strip().lower().replace("-", " ").replace("_", " ")


def lookup_device(device_model: str) -> Optional[DeviceProfile]:
    """Find the best matching DeviceProfile for a UA device string.

    Tries exact match first, then substring match, then partial word match.
    """
    normalized = _normalize_model(device_model)

    # 1. Exact key match
    if device_model in DEVICE_PROFILES:
        return DEVICE_PROFILES[device_model]

    # 2. Normalized exact match
    for key, profile in DEVICE_PROFILES.items():
        if _normalize_model(key) == normalized:
            return profile

    # 3. Substring match — check if any DB key is contained in the UA device string
    for key, profile in DEVICE_PROFILES.items():
        if _normalize_model(key) in normalized:
            return profile

    # 4. Substring match — check if UA device string is contained in any DB key
    for key, profile in DEVICE_PROFILES.items():
        if normalized in _normalize_model(key):
            return profile

    # 5. Word overlap (at least 2 words in common)
    query_words = set(normalized.split())
    best = None
    best_score = 0
    for key, profile in DEVICE_PROFILES.items():
        key_words = set(_normalize_model(key).split())
        overlap = len(query_words & key_words)
        if overlap > best_score:
            best_score = overlap
            best = profile
    if best_score >= 1:
        return best

    return None


def _make_fallback_profile(device_model: str, os_version: str) -> DeviceProfile:
    """Create a reasonable fallback profile for unknown devices."""
    ver = int(os_version.split(".")[0]) if os_version else 10
    # Choose GPU based on brand hints in the device model
    model_lower = device_model.lower()
    if any(k in model_lower for k in ("sm-", "samsung", "galaxy")):
        gpu_renderer, gpu_vendor = "Mali-G72 MP3", "ARM"
        gl_ver, max_tex = "OpenGL ES 3.2 v1.r16p0", 8192
    elif any(k in model_lower for k in ("pixel",)):
        gpu_renderer, gpu_vendor = "Mali-G78 MP20", "ARM"
        gl_ver, max_tex = "OpenGL ES 3.2 v1.r26p0", 8192
    elif any(k in model_lower for k in ("redmi", "poco", "mi ", "xiaomi")):
        gpu_renderer, gpu_vendor = "Adreno (TM) 619", "Qualcomm"
        gl_ver, max_tex = "OpenGL ES 3.2 V@490.0", 16384
    else:
        gpu_renderer, gpu_vendor = "Adreno (TM) 618", "Qualcomm"
        gl_ver, max_tex = "OpenGL ES 3.2 V@490.0", 16384

    mem = 4 if ver <= 11 else 6
    return DeviceProfile(
        model=device_model, brand="Generic",
        cpu_cores=8, device_memory_gb=mem,
        gpu_renderer=gpu_renderer, gpu_vendor=gpu_vendor,
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Generic SoC",
        gl_version=gl_ver, glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=max_tex, max_renderbuffer_size=max_tex,
        max_viewport_dims=(max_tex, max_tex), max_vertex_attribs=16,
        max_varying_vectors=15 if gpu_vendor == "ARM" else 31,
        max_vertex_uniform_vectors=256, max_fragment_uniform_vectors=224,
    )


# ---------------------------------------------------------------------------
#  Deterministic Noise Seeds
# ---------------------------------------------------------------------------

def _profile_seed(profile_name: str, identity_seed: Optional[str] = None) -> int:
    """Produce a deterministic 32-bit integer seed from a profile name or identity seed."""
    key = identity_seed if identity_seed else profile_name
    h = hashlib.sha256(key.encode("utf-8")).digest()
    return struct.unpack("<I", h[:4])[0]


def _canvas_noise_seed(seed: int) -> int:
    return (seed * 2654435761) & 0xFFFFFFFF


def _audio_noise_seed(seed: int) -> int:
    return (seed * 2246822519) & 0xFFFFFFFF


# ---------------------------------------------------------------------------
#  Main Generator
# ---------------------------------------------------------------------------

def generate_fingerprint(
    user_agent: str,
    profile_name: str,
    identity_seed: Optional[str] = None,
    timezone_id: Optional[str] = None,
    timezone_offset: Optional[int] = None,
    locale_override: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a complete, internally consistent fingerprint dictionary.

    Parameters
    ----------
    user_agent : str
        The full User-Agent string assigned to this profile.
    profile_name : str
        Profile directory name (used for deterministic seeding).
    identity_seed : str, optional
        Override seed for identity-stable regeneration.  When supplied,
        canvas/audio noise stays the same across regenerations.
    timezone_id : str, optional
        Override timezone ID (e.g. ``"America/New_York"``).
    timezone_offset : int, optional
        Override timezone offset in minutes from UTC.
    locale_override : str, optional
        Override primary language (e.g. ``"en-US"``).

    Returns
    -------
    dict
        Fingerprint data ready to be serialized as JSON.
    """
    parsed = parse_user_agent(user_agent)
    device_model = parsed["device_model"]
    os_version = parsed["os_version"]
    chrome_version = parsed["chrome_version"]
    os_major = int(os_version.split(".")[0]) if os_version else 10

    # --- Device lookup ---
    device = lookup_device(device_model)
    if device is None:
        device = _make_fallback_profile(device_model, os_version)

    # --- Seeds ---
    base_seed = _profile_seed(profile_name, identity_seed)
    c_seed = _canvas_noise_seed(base_seed)
    a_seed = _audio_noise_seed(base_seed)

    # --- Timezone / Locale ---
    tz_locale = DEFAULT_TIMEZONE_LOCALE
    tz_id = timezone_id or tz_locale.timezone_id
    tz_off = timezone_offset if timezone_offset is not None else tz_locale.timezone_offset
    lang = locale_override or tz_locale.primary_language
    languages = [lang] if locale_override else tz_locale.languages[:]

    # Make sure primary language is first
    if lang not in languages:
        languages.insert(0, lang)

    # Add "en" fallback if not present
    if "en" not in languages:
        languages.append("en")

    # --- Build fingerprint ---
    chrome_major = chrome_version.split(".")[0]

    fingerprint: Dict[str, Any] = {
        "version": 2,
        "locked": False,
        "identity_seed": identity_seed or hashlib.sha256(profile_name.encode()).hexdigest()[:16],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profile_name": profile_name,
        "user_agent": user_agent,

        "navigator": {
            "platform": "Linux armv8l",
            "vendor": "Google Inc.",
            "appVersion": user_agent.replace("Mozilla/", "", 1) if user_agent.startswith("Mozilla/") else user_agent,
            "product": "Gecko",
            "productSub": "20030107",
            "deviceMemory": device.device_memory_gb,
            "hardwareConcurrency": device.cpu_cores,
            "maxTouchPoints": device.max_touch_points,
            "userAgentData": {
                "brands": get_ua_data_brands(chrome_version),
                "mobile": True,
                "platform": "Android",
                "platformVersion": os_version,
                "architecture": "",
                "model": device.model,
                "uaFullVersion": chrome_version,
            },
            "connection": {
                "effectiveType": "4g",
                "downlink": 10,
                "rtt": 50,
                "saveData": False,
            },
            "doNotTrack": None,
            "cookieEnabled": True,
            "pdfViewerEnabled": False,
        },

        "screen": {
            "width": device.screen_width,
            "height": device.screen_height,
            "availWidth": device.screen_width,
            "availHeight": device.screen_height,
            "colorDepth": 24,
            "pixelDepth": 24,
            "devicePixelRatio": device.device_pixel_ratio,
            "orientation": {
                "type": "portrait-primary",
                "angle": 0,
            },
        },

        "webgl": {
            "vendor": "WebKit",
            "renderer": "WebKit WebGL",
            "unmaskedVendor": device.gpu_vendor,
            "unmaskedRenderer": device.gpu_renderer,
            "version": device.gl_version,
            "shadingLanguageVersion": device.glsl_version,
            "maxTextureSize": device.max_texture_size,
            "maxRenderbufferSize": device.max_renderbuffer_size,
            "maxViewportDims": list(device.max_viewport_dims),
            "maxVertexAttribs": device.max_vertex_attribs,
            "maxVaryingVectors": device.max_varying_vectors,
            "maxVertexUniformVectors": device.max_vertex_uniform_vectors,
            "maxFragmentUniformVectors": device.max_fragment_uniform_vectors,
            "maxVertexTextureImageUnits": 16,
            "maxTextureImageUnits": 16,
            "maxCombinedTextureImageUnits": 32,
            "aliasedLineWidthRange": [1, 1],
            "aliasedPointSizeRange": [1, 1024],
            "extensions": get_webgl_extensions(device.gpu_vendor),
        },

        "canvas": {
            "noiseSeed": c_seed,
            "noiseIntensity": 0.0003,
        },

        "audio": {
            "noiseSeed": a_seed,
            "noiseIntensity": 0.00001,
        },

        "webrtc": {
            "ipHandlingPolicy": "disable_non_proxied_udp",
            "disableLocalIPs": True,
            "publicIPOverride": None,
        },

        "timezone": {
            "id": tz_id,
            "offset": tz_off,
        },

        "locale": {
            "languages": languages,
            "language": lang,
        },

        "fonts": {
            "available": get_fonts_for_android_version(os_major),
        },

        "plugins": {
            "list": [],           # Android Chrome has no plugins
            "mimeTypes": [],
        },

        "device_info": {
            "model": device.model,
            "brand": device.brand,
            "soc": device.soc_name,
            "gpu": device.gpu_renderer,
            "os_version": os_version,
            "chrome_version": chrome_version,
        },
    }

    return fingerprint


# ---------------------------------------------------------------------------
#  Quick validation helper
# ---------------------------------------------------------------------------

def validate_fingerprint(fp: Dict[str, Any]) -> List[str]:
    """Return a list of consistency issues found in the fingerprint (empty = OK)."""
    issues: List[str] = []

    nav = fp.get("navigator", {})
    screen = fp.get("screen", {})
    webgl = fp.get("webgl", {})
    ua = fp.get("user_agent", "")

    # Check navigator platform matches mobile
    if nav.get("platform") != "Linux armv8l":
        issues.append("navigator.platform should be 'Linux armv8l' for Android")

    # Check touch support
    if nav.get("maxTouchPoints", 0) < 1:
        issues.append("maxTouchPoints should be >= 1 for mobile")

    # Check userAgentData.mobile
    ua_data = nav.get("userAgentData", {})
    if not ua_data.get("mobile"):
        issues.append("userAgentData.mobile should be True for Android UAs")

    # Check screen dimensions are mobile-like (portrait)
    w, h = screen.get("width", 0), screen.get("height", 0)
    if w > h:
        issues.append(f"Screen {w}x{h} is landscape — should be portrait for mobile")
    if w > 500:
        issues.append(f"Screen width {w} too large for mobile device")

    # Check GPU consistency — Adreno should have Qualcomm vendor
    renderer = webgl.get("unmaskedRenderer", "")
    vendor = webgl.get("unmaskedVendor", "")
    if "Adreno" in renderer and vendor != "Qualcomm":
        issues.append(f"Adreno GPU paired with vendor '{vendor}' — should be 'Qualcomm'")
    if "Mali" in renderer and vendor != "ARM":
        issues.append(f"Mali GPU paired with vendor '{vendor}' — should be 'ARM'")
    if "PowerVR" in renderer and vendor != "Imagination Technologies":
        issues.append(f"PowerVR GPU paired with vendor '{vendor}' — should be 'Imagination Technologies'")

    # Check plugins are empty for mobile
    plugins = fp.get("plugins", {}).get("list", [])
    if plugins:
        issues.append("Mobile Chrome should have empty plugin list")

    return issues


if __name__ == "__main__":
    # Quick self-test: generate fingerprints for a few sample UAs
    test_uas = [
        "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 Chrome/123.0.6312.80 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 14; Poco X6 Pro) AppleWebKit/537.36 Chrome/124.0.6367.78 Mobile Safari/537.36",
    ]
    for i, ua in enumerate(test_uas, 1):
        fp = generate_fingerprint(ua, f"Profiles_{i}")
        issues = validate_fingerprint(fp)
        info = fp["device_info"]
        print(f"Profile_{i}: {info['model']} | {info['gpu']} | {info['soc']}")
        if issues:
            print(f"  [!] Issues: {issues}")
        else:
            print(f"  [OK] Consistent")
    print("Done.")
