"""
fingerprint_datasets.py
========================
Real-world device hardware profiles, GPU databases, font sets, WebGL parameters,
and timezone/locale mappings used by the Fingerprint Generator.

All data is sourced from actual device specifications — nothing is randomly generated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
#  Device Hardware Profiles
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class DeviceProfile:
    """Hardware specification of a real Android device."""
    model: str
    brand: str
    cpu_cores: int
    device_memory_gb: int          # navigator.deviceMemory
    gpu_renderer: str               # WebGL UNMASKED_RENDERER
    gpu_vendor: str                 # WebGL UNMASKED_VENDOR
    screen_width: int               # portrait width in CSS pixels
    screen_height: int              # portrait height in CSS pixels
    device_pixel_ratio: float
    max_touch_points: int
    # SoC info for consistency
    soc_name: str
    # Additional WebGL hints
    gl_version: str
    glsl_version: str
    max_texture_size: int
    max_renderbuffer_size: int
    max_viewport_dims: Tuple[int, int]
    max_vertex_attribs: int
    max_varying_vectors: int
    max_vertex_uniform_vectors: int
    max_fragment_uniform_vectors: int


# fmt: off
# ── Samsung Galaxy Series ──────────────────────────────────────────────
DEVICE_PROFILES: Dict[str, DeviceProfile] = {
    # --- Samsung ---
    "SM-G973F": DeviceProfile(
        model="SM-G973F", brand="Samsung", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Mali-G76 MP12", gpu_vendor="ARM",
        screen_width=360, screen_height=760, device_pixel_ratio=3.0,
        max_touch_points=10, soc_name="Exynos 9820",
        gl_version="OpenGL ES 3.2 v1.r19p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "SM-A505F": DeviceProfile(
        model="SM-A505F", brand="Samsung", cpu_cores=8, device_memory_gb=4,
        gpu_renderer="Mali-G72 MP3", gpu_vendor="ARM",
        screen_width=412, screen_height=892, device_pixel_ratio=2.625,
        max_touch_points=10, soc_name="Exynos 9610",
        gl_version="OpenGL ES 3.2 v1.r16p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "SM-M315F": DeviceProfile(
        model="SM-M315F", brand="Samsung", cpu_cores=8, device_memory_gb=6,
        gpu_renderer="Mali-G72 MP3", gpu_vendor="ARM",
        screen_width=412, screen_height=892, device_pixel_ratio=2.625,
        max_touch_points=10, soc_name="Exynos 9611",
        gl_version="OpenGL ES 3.2 v1.r16p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "SM-A715F": DeviceProfile(
        model="SM-A715F", brand="Samsung", cpu_cores=8, device_memory_gb=6,
        gpu_renderer="Adreno (TM) 618", gpu_vendor="Qualcomm",
        screen_width=412, screen_height=914, device_pixel_ratio=2.625,
        max_touch_points=10, soc_name="Snapdragon 730",
        gl_version="OpenGL ES 3.2 V@490.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "SM-G991B": DeviceProfile(
        model="SM-G991B", brand="Samsung", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Mali-G78 MP14", gpu_vendor="ARM",
        screen_width=360, screen_height=800, device_pixel_ratio=3.0,
        max_touch_points=10, soc_name="Exynos 2100",
        gl_version="OpenGL ES 3.2 v1.r26p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "SM-G996B": DeviceProfile(
        model="SM-G996B", brand="Samsung", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Mali-G78 MP14", gpu_vendor="ARM",
        screen_width=384, screen_height=854, device_pixel_ratio=2.8125,
        max_touch_points=10, soc_name="Exynos 2100",
        gl_version="OpenGL ES 3.2 v1.r26p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "SM-S918B": DeviceProfile(
        model="SM-S918B", brand="Samsung", cpu_cores=8, device_memory_gb=12,
        gpu_renderer="Adreno (TM) 740", gpu_vendor="Qualcomm",
        screen_width=384, screen_height=824, device_pixel_ratio=3.125,
        max_touch_points=10, soc_name="Snapdragon 8 Gen 2",
        gl_version="OpenGL ES 3.2 V@0615.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),

    # --- Xiaomi / Redmi / Poco ---
    "Redmi Note 10": DeviceProfile(
        model="Redmi Note 10", brand="Xiaomi", cpu_cores=8, device_memory_gb=4,
        gpu_renderer="Adreno (TM) 618", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 678",
        gl_version="OpenGL ES 3.2 V@490.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "M2101K6P": DeviceProfile(
        model="M2101K6P", brand="Xiaomi", cpu_cores=8, device_memory_gb=6,
        gpu_renderer="Adreno (TM) 619", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 732G",
        gl_version="OpenGL ES 3.2 V@490.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Redmi Note 9": DeviceProfile(
        model="Redmi Note 9", brand="Xiaomi", cpu_cores=8, device_memory_gb=4,
        gpu_renderer="Mali-G52 MC2", gpu_vendor="ARM",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="MediaTek Helio G85",
        gl_version="OpenGL ES 3.2 v1.r20p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Redmi Note 11": DeviceProfile(
        model="Redmi Note 11", brand="Xiaomi", cpu_cores=8, device_memory_gb=4,
        gpu_renderer="Adreno (TM) 619", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 680",
        gl_version="OpenGL ES 3.2 V@490.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Redmi Note 12": DeviceProfile(
        model="Redmi Note 12", brand="Xiaomi", cpu_cores=8, device_memory_gb=6,
        gpu_renderer="Adreno (TM) 619", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 685",
        gl_version="OpenGL ES 3.2 V@490.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Redmi Note 13": DeviceProfile(
        model="Redmi Note 13", brand="Xiaomi", cpu_cores=8, device_memory_gb=6,
        gpu_renderer="Adreno (TM) 619", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 685",
        gl_version="OpenGL ES 3.2 V@490.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Redmi Note 13 Pro": DeviceProfile(
        model="Redmi Note 13 Pro", brand="Xiaomi", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Adreno (TM) 710", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 7s Gen 2",
        gl_version="OpenGL ES 3.2 V@0580.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Poco X2": DeviceProfile(
        model="Poco X2", brand="Xiaomi", cpu_cores=8, device_memory_gb=6,
        gpu_renderer="Adreno (TM) 618", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 730G",
        gl_version="OpenGL ES 3.2 V@490.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Poco X3 Pro": DeviceProfile(
        model="Poco X3 Pro", brand="Xiaomi", cpu_cores=8, device_memory_gb=6,
        gpu_renderer="Adreno (TM) 640", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 860",
        gl_version="OpenGL ES 3.2 V@512.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Poco F4": DeviceProfile(
        model="Poco F4", brand="Xiaomi", cpu_cores=8, device_memory_gb=6,
        gpu_renderer="Adreno (TM) 650", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 870",
        gl_version="OpenGL ES 3.2 V@530.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Poco F5": DeviceProfile(
        model="Poco F5", brand="Xiaomi", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Adreno (TM) 730", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 7+ Gen 2",
        gl_version="OpenGL ES 3.2 V@0590.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Poco X6 Pro": DeviceProfile(
        model="Poco X6 Pro", brand="Xiaomi", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Mali-G615 MC6", gpu_vendor="ARM",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="MediaTek Dimensity 8300-Ultra",
        gl_version="OpenGL ES 3.2 v1.r38p1", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),

    # --- Google Pixel ---
    "Pixel 6": DeviceProfile(
        model="Pixel 6", brand="Google", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Mali-G78 MP20", gpu_vendor="ARM",
        screen_width=412, screen_height=915, device_pixel_ratio=2.625,
        max_touch_points=5, soc_name="Google Tensor",
        gl_version="OpenGL ES 3.2 v1.r26p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Pixel 7 Pro": DeviceProfile(
        model="Pixel 7 Pro", brand="Google", cpu_cores=8, device_memory_gb=12,
        gpu_renderer="Mali-G710 MP7", gpu_vendor="ARM",
        screen_width=412, screen_height=892, device_pixel_ratio=2.625,
        max_touch_points=5, soc_name="Google Tensor G2",
        gl_version="OpenGL ES 3.2 v1.r32p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),

    # --- Vivo ---
    "Vivo V20": DeviceProfile(
        model="Vivo V20", brand="Vivo", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Adreno (TM) 618", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=851, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 720G",
        gl_version="OpenGL ES 3.2 V@490.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Vivo Y20": DeviceProfile(
        model="Vivo Y20", brand="Vivo", cpu_cores=8, device_memory_gb=4,
        gpu_renderer="Adreno (TM) 610", gpu_vendor="Qualcomm",
        screen_width=360, screen_height=800, device_pixel_ratio=2.0,
        max_touch_points=5, soc_name="Snapdragon 460",
        gl_version="OpenGL ES 3.2 V@415.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Vivo Y33s": DeviceProfile(
        model="Vivo Y33s", brand="Vivo", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Mali-G52 MC2", gpu_vendor="ARM",
        screen_width=393, screen_height=873, device_pixel_ratio=2.0,
        max_touch_points=10, soc_name="MediaTek Helio G80",
        gl_version="OpenGL ES 3.2 v1.r20p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Vivo V25": DeviceProfile(
        model="Vivo V25", brand="Vivo", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Mali-G610 MC6", gpu_vendor="ARM",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="MediaTek Dimensity 900",
        gl_version="OpenGL ES 3.2 v1.r32p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Vivo X80": DeviceProfile(
        model="Vivo X80", brand="Vivo", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Mali-G610 MC6", gpu_vendor="ARM",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="MediaTek Dimensity 9000",
        gl_version="OpenGL ES 3.2 v1.r32p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Vivo X100": DeviceProfile(
        model="Vivo X100", brand="Vivo", cpu_cores=8, device_memory_gb=12,
        gpu_renderer="Mali-G720 MC12", gpu_vendor="ARM",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="MediaTek Dimensity 9300",
        gl_version="OpenGL ES 3.2 v1.r44p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),

    # --- Realme ---
    "Realme RMX3085": DeviceProfile(
        model="Realme RMX3085", brand="Realme", cpu_cores=8, device_memory_gb=4,
        gpu_renderer="Mali-G52 MC2", gpu_vendor="ARM",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="MediaTek Helio G95",
        gl_version="OpenGL ES 3.2 v1.r20p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Realme 7": DeviceProfile(
        model="Realme 7", brand="Realme", cpu_cores=8, device_memory_gb=6,
        gpu_renderer="Mali-G76 MC4", gpu_vendor="ARM",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="MediaTek Helio G95",
        gl_version="OpenGL ES 3.2 v1.r20p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Realme 8": DeviceProfile(
        model="Realme 8", brand="Realme", cpu_cores=8, device_memory_gb=6,
        gpu_renderer="Mali-G76 MC4", gpu_vendor="ARM",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="MediaTek Helio G95",
        gl_version="OpenGL ES 3.2 v1.r20p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Realme 9 Pro": DeviceProfile(
        model="Realme 9 Pro", brand="Realme", cpu_cores=8, device_memory_gb=6,
        gpu_renderer="Adreno (TM) 619", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 695",
        gl_version="OpenGL ES 3.2 V@490.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Realme 10 Pro": DeviceProfile(
        model="Realme 10 Pro", brand="Realme", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Adreno (TM) 619", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 695",
        gl_version="OpenGL ES 3.2 V@490.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Realme 11 Pro+": DeviceProfile(
        model="Realme 11 Pro+", brand="Realme", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Mali-G610 MC6", gpu_vendor="ARM",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="MediaTek Dimensity 7050",
        gl_version="OpenGL ES 3.2 v1.r32p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),

    # --- OnePlus ---
    "OnePlus 9": DeviceProfile(
        model="OnePlus 9", brand="OnePlus", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Adreno (TM) 660", gpu_vendor="Qualcomm",
        screen_width=412, screen_height=915, device_pixel_ratio=2.625,
        max_touch_points=10, soc_name="Snapdragon 888",
        gl_version="OpenGL ES 3.2 V@530.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "OnePlus 11": DeviceProfile(
        model="OnePlus 11", brand="OnePlus", cpu_cores=8, device_memory_gb=16,
        gpu_renderer="Adreno (TM) 740", gpu_vendor="Qualcomm",
        screen_width=412, screen_height=919, device_pixel_ratio=2.625,
        max_touch_points=10, soc_name="Snapdragon 8 Gen 2",
        gl_version="OpenGL ES 3.2 V@0615.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),

    # --- Nokia ---
    "Nokia 5.3": DeviceProfile(
        model="Nokia 5.3", brand="Nokia", cpu_cores=8, device_memory_gb=4,
        gpu_renderer="Adreno (TM) 610", gpu_vendor="Qualcomm",
        screen_width=412, screen_height=915, device_pixel_ratio=1.75,
        max_touch_points=5, soc_name="Snapdragon 665",
        gl_version="OpenGL ES 3.2 V@415.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Nokia 6.2": DeviceProfile(
        model="Nokia 6.2", brand="Nokia", cpu_cores=8, device_memory_gb=4,
        gpu_renderer="Adreno (TM) 610", gpu_vendor="Qualcomm",
        screen_width=412, screen_height=892, device_pixel_ratio=2.625,
        max_touch_points=5, soc_name="Snapdragon 636",
        gl_version="OpenGL ES 3.2 V@415.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Nokia X20": DeviceProfile(
        model="Nokia X20", brand="Nokia", cpu_cores=8, device_memory_gb=6,
        gpu_renderer="Adreno (TM) 619", gpu_vendor="Qualcomm",
        screen_width=412, screen_height=915, device_pixel_ratio=2.625,
        max_touch_points=5, soc_name="Snapdragon 480",
        gl_version="OpenGL ES 3.2 V@490.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Nokia G60": DeviceProfile(
        model="Nokia G60", brand="Nokia", cpu_cores=8, device_memory_gb=6,
        gpu_renderer="Adreno (TM) 619", gpu_vendor="Qualcomm",
        screen_width=412, screen_height=915, device_pixel_ratio=2.625,
        max_touch_points=5, soc_name="Snapdragon 695",
        gl_version="OpenGL ES 3.2 V@490.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Nokia XR21": DeviceProfile(
        model="Nokia XR21", brand="Nokia", cpu_cores=8, device_memory_gb=6,
        gpu_renderer="Adreno (TM) 619", gpu_vendor="Qualcomm",
        screen_width=412, screen_height=915, device_pixel_ratio=2.625,
        max_touch_points=5, soc_name="Snapdragon 695",
        gl_version="OpenGL ES 3.2 V@490.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),

    # --- Infinix ---
    "Infinix Hot 10": DeviceProfile(
        model="Infinix Hot 10", brand="Infinix", cpu_cores=8, device_memory_gb=4,
        gpu_renderer="PowerVR GE8320", gpu_vendor="Imagination Technologies",
        screen_width=393, screen_height=873, device_pixel_ratio=1.75,
        max_touch_points=5, soc_name="MediaTek Helio G25",
        gl_version="OpenGL ES 3.2 build 1.13@5776728", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=4096, max_renderbuffer_size=4096,
        max_viewport_dims=(4096, 4096), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Infinix Note 11": DeviceProfile(
        model="Infinix Note 11", brand="Infinix", cpu_cores=8, device_memory_gb=4,
        gpu_renderer="Mali-G52 MC2", gpu_vendor="ARM",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="MediaTek Helio G88",
        gl_version="OpenGL ES 3.2 v1.r20p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Infinix Zero 5G": DeviceProfile(
        model="Infinix Zero 5G", brand="Infinix", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Mali-G76 MC4", gpu_vendor="ARM",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="MediaTek Dimensity 900",
        gl_version="OpenGL ES 3.2 v1.r26p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Infinix GT 10 Pro": DeviceProfile(
        model="Infinix GT 10 Pro", brand="Infinix", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Mali-G610 MC6", gpu_vendor="ARM",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="MediaTek Dimensity 8050",
        gl_version="OpenGL ES 3.2 v1.r32p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Infinix Zero Ultra": DeviceProfile(
        model="Infinix Zero Ultra", brand="Infinix", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Mali-G610 MC6", gpu_vendor="ARM",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="MediaTek Dimensity 920",
        gl_version="OpenGL ES 3.2 v1.r32p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),

    # --- Oppo ---
    "Oppo A53": DeviceProfile(
        model="Oppo A53", brand="Oppo", cpu_cores=8, device_memory_gb=4,
        gpu_renderer="Adreno (TM) 610", gpu_vendor="Qualcomm",
        screen_width=360, screen_height=800, device_pixel_ratio=2.0,
        max_touch_points=5, soc_name="Snapdragon 460",
        gl_version="OpenGL ES 3.2 V@415.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Oppo A74": DeviceProfile(
        model="Oppo A74", brand="Oppo", cpu_cores=8, device_memory_gb=6,
        gpu_renderer="Adreno (TM) 618", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 662",
        gl_version="OpenGL ES 3.2 V@490.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Oppo Reno 7": DeviceProfile(
        model="Oppo Reno 7", brand="Oppo", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Mali-G57 MC2", gpu_vendor="ARM",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="MediaTek Dimensity 900",
        gl_version="OpenGL ES 3.2 v1.r26p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Oppo Reno 8": DeviceProfile(
        model="Oppo Reno 8", brand="Oppo", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Mali-G610 MC6", gpu_vendor="ARM",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="MediaTek Dimensity 1300",
        gl_version="OpenGL ES 3.2 v1.r32p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Oppo Find X7": DeviceProfile(
        model="Oppo Find X7", brand="Oppo", cpu_cores=8, device_memory_gb=16,
        gpu_renderer="Mali-G720 MC12", gpu_vendor="ARM",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="MediaTek Dimensity 9300",
        gl_version="OpenGL ES 3.2 v1.r44p0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=15, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),

    # --- Motorola ---
    "Moto G9": DeviceProfile(
        model="Moto G9", brand="Motorola", cpu_cores=8, device_memory_gb=4,
        gpu_renderer="Adreno (TM) 610", gpu_vendor="Qualcomm",
        screen_width=360, screen_height=800, device_pixel_ratio=2.0,
        max_touch_points=5, soc_name="Snapdragon 662",
        gl_version="OpenGL ES 3.2 V@415.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=8192, max_renderbuffer_size=8192,
        max_viewport_dims=(8192, 8192), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Moto G60": DeviceProfile(
        model="Moto G60", brand="Motorola", cpu_cores=8, device_memory_gb=6,
        gpu_renderer="Adreno (TM) 618", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 732G",
        gl_version="OpenGL ES 3.2 V@490.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Moto Edge 20": DeviceProfile(
        model="Moto Edge 20", brand="Motorola", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Adreno (TM) 642L", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 778G",
        gl_version="OpenGL ES 3.2 V@530.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Moto Edge 30": DeviceProfile(
        model="Moto Edge 30", brand="Motorola", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Adreno (TM) 642L", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 778G+",
        gl_version="OpenGL ES 3.2 V@530.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
    "Moto Edge 50": DeviceProfile(
        model="Moto Edge 50", brand="Motorola", cpu_cores=8, device_memory_gb=8,
        gpu_renderer="Adreno (TM) 710", gpu_vendor="Qualcomm",
        screen_width=393, screen_height=873, device_pixel_ratio=2.75,
        max_touch_points=10, soc_name="Snapdragon 7 Gen 1",
        gl_version="OpenGL ES 3.2 V@0580.0", glsl_version="OpenGL ES GLSL ES 3.20",
        max_texture_size=16384, max_renderbuffer_size=16384,
        max_viewport_dims=(16384, 16384), max_vertex_attribs=16,
        max_varying_vectors=31, max_vertex_uniform_vectors=256,
        max_fragment_uniform_vectors=224,
    ),
}
# fmt: on


# ---------------------------------------------------------------------------
#  WebGL Extensions per GPU Vendor
# ---------------------------------------------------------------------------

WEBGL_EXTENSIONS_QUALCOMM: List[str] = [
    "ANGLE_instanced_arrays",
    "EXT_blend_minmax",
    "EXT_color_buffer_half_float",
    "EXT_disjoint_timer_query",
    "EXT_float_blend",
    "EXT_frag_depth",
    "EXT_shader_texture_lod",
    "EXT_texture_compression_bptc",
    "EXT_texture_compression_rgtc",
    "EXT_texture_filter_anisotropic",
    "EXT_sRGB",
    "KHR_parallel_shader_compile",
    "OES_element_index_uint",
    "OES_fbo_render_mipmap",
    "OES_standard_derivatives",
    "OES_texture_float",
    "OES_texture_float_linear",
    "OES_texture_half_float",
    "OES_texture_half_float_linear",
    "OES_vertex_array_object",
    "WEBGL_color_buffer_float",
    "WEBGL_compressed_texture_astc",
    "WEBGL_compressed_texture_etc",
    "WEBGL_compressed_texture_etc1",
    "WEBGL_debug_renderer_info",
    "WEBGL_debug_shaders",
    "WEBGL_depth_texture",
    "WEBGL_draw_buffers",
    "WEBGL_lose_context",
    "WEBGL_multi_draw",
]

WEBGL_EXTENSIONS_ARM: List[str] = [
    "ANGLE_instanced_arrays",
    "EXT_blend_minmax",
    "EXT_color_buffer_half_float",
    "EXT_disjoint_timer_query",
    "EXT_float_blend",
    "EXT_frag_depth",
    "EXT_shader_texture_lod",
    "EXT_texture_compression_bptc",
    "EXT_texture_compression_rgtc",
    "EXT_texture_filter_anisotropic",
    "EXT_sRGB",
    "KHR_parallel_shader_compile",
    "OES_element_index_uint",
    "OES_fbo_render_mipmap",
    "OES_standard_derivatives",
    "OES_texture_float",
    "OES_texture_float_linear",
    "OES_texture_half_float",
    "OES_texture_half_float_linear",
    "OES_vertex_array_object",
    "WEBGL_color_buffer_float",
    "WEBGL_compressed_texture_astc",
    "WEBGL_compressed_texture_etc",
    "WEBGL_compressed_texture_etc1",
    "WEBGL_debug_renderer_info",
    "WEBGL_debug_shaders",
    "WEBGL_depth_texture",
    "WEBGL_draw_buffers",
    "WEBGL_lose_context",
    "WEBGL_multi_draw",
]

WEBGL_EXTENSIONS_POWERVR: List[str] = [
    "ANGLE_instanced_arrays",
    "EXT_blend_minmax",
    "EXT_color_buffer_half_float",
    "EXT_frag_depth",
    "EXT_shader_texture_lod",
    "EXT_texture_filter_anisotropic",
    "EXT_sRGB",
    "OES_element_index_uint",
    "OES_standard_derivatives",
    "OES_texture_float",
    "OES_texture_float_linear",
    "OES_texture_half_float",
    "OES_texture_half_float_linear",
    "OES_vertex_array_object",
    "WEBGL_color_buffer_float",
    "WEBGL_compressed_texture_astc",
    "WEBGL_compressed_texture_etc",
    "WEBGL_compressed_texture_etc1",
    "WEBGL_debug_renderer_info",
    "WEBGL_debug_shaders",
    "WEBGL_depth_texture",
    "WEBGL_draw_buffers",
    "WEBGL_lose_context",
]

WEBGL_EXTENSIONS_BY_VENDOR: Dict[str, List[str]] = {
    "Qualcomm": WEBGL_EXTENSIONS_QUALCOMM,
    "ARM": WEBGL_EXTENSIONS_ARM,
    "Imagination Technologies": WEBGL_EXTENSIONS_POWERVR,
}


# ---------------------------------------------------------------------------
#  Android System Fonts per OS Version
# ---------------------------------------------------------------------------

ANDROID_FONTS_BASE: List[str] = [
    "Roboto",
    "Noto Sans",
    "Noto Serif",
    "Noto Color Emoji",
    "Droid Sans",
    "Droid Sans Mono",
    "Droid Serif",
    "Roboto Condensed",
    "Roboto Mono",
    "Cutive Mono",
    "Coming Soon",
    "Dancing Script",
    "Carrois Gothic SC",
    "Noto Sans Devanagari",
    "Noto Sans Bengali",
    "Noto Sans Tamil",
    "Noto Sans Telugu",
    "Noto Sans Kannada",
    "Noto Sans Malayalam",
    "Noto Sans Gujarati",
    "Noto Sans Gurmukhi",
    "Noto Sans Oriya",
    "Noto Sans Arabic",
    "Noto Sans Thai",
    "Noto Sans Hebrew",
    "Noto Sans Armenian",
    "Noto Sans Georgian",
    "Noto Sans Myanmar",
    "Noto Sans Ethiopic",
    "Noto Sans Khmer",
    "Noto Sans Lao",
    "Noto Sans Sinhala",
    "Noto Sans CJK JP",
    "Noto Sans CJK SC",
    "Noto Sans CJK TC",
    "Noto Sans CJK KR",
    "Noto Sans Symbols",
]

ANDROID_FONTS_11_PLUS: List[str] = ANDROID_FONTS_BASE + [
    "Noto Sans Symbols 2",
    "Noto Sans Math",
    "Noto Sans Mono",
    "Noto Sans Display",
]

ANDROID_FONTS_12_PLUS: List[str] = ANDROID_FONTS_11_PLUS + [
    "Noto Sans UI",
    "Noto Emoji",
]

ANDROID_FONTS_13_PLUS: List[str] = ANDROID_FONTS_12_PLUS + [
    "Google Sans",
    "Google Sans Text",
]

ANDROID_FONTS_14_PLUS: List[str] = ANDROID_FONTS_13_PLUS + [
    "Google Sans Flex",
    "Noto Sans Variable",
]


def get_fonts_for_android_version(version: int) -> List[str]:
    """Return the realistic font list for a given Android major version."""
    if version >= 14:
        return ANDROID_FONTS_14_PLUS[:]
    if version >= 13:
        return ANDROID_FONTS_13_PLUS[:]
    if version >= 12:
        return ANDROID_FONTS_12_PLUS[:]
    if version >= 11:
        return ANDROID_FONTS_11_PLUS[:]
    return ANDROID_FONTS_BASE[:]


# ---------------------------------------------------------------------------
#  Timezone / Locale Database
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class TimezoneLocale:
    timezone_id: str
    timezone_offset: int     # minutes from UTC
    languages: List[str]
    primary_language: str


# Default: India (matches all current User-Agents)
DEFAULT_TIMEZONE_LOCALE = TimezoneLocale(
    timezone_id="Asia/Kolkata",
    timezone_offset=330,
    languages=["en-IN", "en", "hi"],
    primary_language="en-IN",
)

TIMEZONE_LOCALE_MAP: Dict[str, TimezoneLocale] = {
    "IN": DEFAULT_TIMEZONE_LOCALE,
    "US": TimezoneLocale("America/New_York", -300, ["en-US", "en"], "en-US"),
    "GB": TimezoneLocale("Europe/London", 0, ["en-GB", "en"], "en-GB"),
    "DE": TimezoneLocale("Europe/Berlin", 60, ["de-DE", "de", "en"], "de-DE"),
    "FR": TimezoneLocale("Europe/Paris", 60, ["fr-FR", "fr", "en"], "fr-FR"),
    "JP": TimezoneLocale("Asia/Tokyo", 540, ["ja-JP", "ja", "en"], "ja-JP"),
    "BR": TimezoneLocale("America/Sao_Paulo", -180, ["pt-BR", "pt", "en"], "pt-BR"),
    "RU": TimezoneLocale("Europe/Moscow", 180, ["ru-RU", "ru", "en"], "ru-RU"),
    "AE": TimezoneLocale("Asia/Dubai", 240, ["ar-AE", "ar", "en"], "ar-AE"),
    "SG": TimezoneLocale("Asia/Singapore", 480, ["en-SG", "en", "zh"], "en-SG"),
    "AU": TimezoneLocale("Australia/Sydney", 600, ["en-AU", "en"], "en-AU"),
    "CA": TimezoneLocale("America/Toronto", -300, ["en-CA", "en", "fr"], "en-CA"),
    "ID": TimezoneLocale("Asia/Jakarta", 420, ["id-ID", "id", "en"], "id-ID"),
    "PH": TimezoneLocale("Asia/Manila", 480, ["en-PH", "en", "fil"], "en-PH"),
    "NG": TimezoneLocale("Africa/Lagos", 60, ["en-NG", "en"], "en-NG"),
    "BD": TimezoneLocale("Asia/Dhaka", 360, ["bn-BD", "bn", "en"], "bn-BD"),
    "PK": TimezoneLocale("Asia/Karachi", 300, ["ur-PK", "ur", "en"], "ur-PK"),
}


# ---------------------------------------------------------------------------
#  Chrome Version → userAgentData brand info
# ---------------------------------------------------------------------------

def get_ua_data_brands(chrome_version: str) -> List[Dict[str, str]]:
    """Build the navigator.userAgentData.brands array from the Chrome major version."""
    major = chrome_version.split(".")[0] if chrome_version else "120"
    return [
        {"brand": "Chromium", "version": major},
        {"brand": "Google Chrome", "version": major},
        {"brand": "Not-A.Brand", "version": "99"},
    ]


def get_webgl_extensions(gpu_vendor: str) -> List[str]:
    """Return realistic WebGL extensions for the given GPU vendor."""
    return WEBGL_EXTENSIONS_BY_VENDOR.get(gpu_vendor, WEBGL_EXTENSIONS_QUALCOMM)[:]
