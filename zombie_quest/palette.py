"""ZQ-32: the locked 32-color palette for all authored art.

Every background, sprite sheet, UI element, and font atlas must use only
these colors. The palette is organized as 8 named ramps of 4 shades
(dark -> light) so tools and grading LUTs can reason about color roles,
not just values. Index 0 is BLACK, index 31 is WHITE (bone).

Enforcement runs at asset load time and in CI - never per frame.
"""
from __future__ import annotations

from collections import OrderedDict
from typing import Dict, FrozenSet, Iterable, List, Tuple

import pygame

Color = Tuple[int, int, int]

RAMPS: "OrderedDict[str, Tuple[Color, Color, Color, Color]]" = OrderedDict(
    night=((0, 0, 0), (30, 10, 60), (58, 34, 100), (94, 62, 148)),
    neon_magenta=((98, 26, 110), (168, 38, 150), (255, 20, 147), (255, 128, 196)),
    neon_cyan=((16, 70, 86), (30, 128, 148), (60, 190, 208), (120, 244, 255)),
    gold=((96, 56, 16), (164, 102, 24), (224, 160, 40), (255, 215, 0)),
    brick=((62, 26, 22), (110, 46, 34), (158, 76, 52), (206, 120, 86)),
    sick=((30, 54, 34), (62, 102, 58), (102, 158, 88), (158, 206, 130)),
    skin=((104, 64, 50), (160, 104, 78), (212, 152, 112), (246, 206, 164)),
    bone=((54, 52, 64), (106, 104, 118), (170, 168, 178), (240, 234, 224)),
)

ZQ32: Tuple[Color, ...] = tuple(color for ramp in RAMPS.values() for color in ramp)
BLACK: Color = ZQ32[0]
WHITE: Color = ZQ32[31]

_ZQ32_CODES: FrozenSet[int] = frozenset((r << 16) | (g << 8) | b for r, g, b in ZQ32)
_NEAREST_CACHE: Dict[Color, Color] = {}


class PaletteError(Exception):
    """Raised when a surface or mapping violates the ZQ-32 contract."""


def _code(color: Iterable[int]) -> int:
    r, g, b = tuple(color)[:3]
    return (int(r) << 16) | (int(g) << 8) | int(b)


def surface_colors(surface: pygame.Surface,
                   ignore_transparent: bool = True) -> List[Color]:
    """Unique opaque RGB colors present in a surface.

    Uses the numpy/surfarray fast path when numpy is available (~1ms for
    320x200); falls back to a pure-Python scan so the game itself never
    requires numpy.
    """
    try:
        import numpy as np
        from pygame import surfarray

        rgb = surfarray.array3d(surface)
        codes = (rgb[..., 0].astype(np.uint32) << 16) | \
                (rgb[..., 1].astype(np.uint32) << 8) | rgb[..., 2]
        if ignore_transparent and surface.get_flags() & pygame.SRCALPHA:
            alpha = surfarray.array_alpha(surface)
            codes = codes[alpha != 0]
        unique = np.unique(codes)
        return [(int(c) >> 16 & 255, int(c) >> 8 & 255, int(c) & 255) for c in unique]
    except ImportError:
        seen = set()
        width, height = surface.get_size()
        has_alpha = bool(surface.get_flags() & pygame.SRCALPHA)
        for x in range(width):
            for y in range(height):
                pixel = surface.get_at((x, y))
                if ignore_transparent and has_alpha and pixel[3] == 0:
                    continue
                seen.add((pixel[0], pixel[1], pixel[2]))
        return sorted(seen)


def assert_surface_palette(surface: pygame.Surface, context: str = "") -> None:
    """Raise PaletteError if any opaque pixel is outside ZQ-32."""
    offenders = [c for c in surface_colors(surface) if _code(c) not in _ZQ32_CODES]
    if offenders:
        shown = ", ".join(str(c) for c in offenders[:10])
        suffix = f" (+{len(offenders) - 10} more)" if len(offenders) > 10 else ""
        where = f" in {context}" if context else ""
        raise PaletteError(f"{len(offenders)} non-palette colors{where}: {shown}{suffix}")


def nearest(color: Color) -> Color:
    """Closest ZQ-32 color by squared RGB distance. Idempotent on members."""
    key = (int(color[0]), int(color[1]), int(color[2]))
    cached = _NEAREST_CACHE.get(key)
    if cached is not None:
        return cached
    if _code(key) in _ZQ32_CODES:
        _NEAREST_CACHE[key] = key
        return key
    best = min(ZQ32, key=lambda p: (p[0] - key[0]) ** 2 + (p[1] - key[1]) ** 2 + (p[2] - key[2]) ** 2)
    _NEAREST_CACHE[key] = best
    return best


def quantize_surface(surface: pygame.Surface) -> pygame.Surface:
    """Return a copy with every opaque pixel snapped to its nearest ZQ-32 color."""
    result = surface.copy()
    width, height = result.get_size()
    has_alpha = bool(result.get_flags() & pygame.SRCALPHA)
    for x in range(width):
        for y in range(height):
            pixel = result.get_at((x, y))
            if has_alpha and pixel[3] == 0:
                continue
            snapped = nearest((pixel[0], pixel[1], pixel[2]))
            result.set_at((x, y), (*snapped, pixel[3]) if has_alpha else snapped)
    return result


def make_lut(mapping: Dict[Color, Color]) -> Dict[int, int]:
    """Build a palette-remap LUT. Domain and range must both be ZQ-32."""
    lut: Dict[int, int] = {}
    for source, target in mapping.items():
        source_code, target_code = _code(source), _code(target)
        if source_code not in _ZQ32_CODES:
            raise PaletteError(f"LUT source {source} is not a ZQ-32 color")
        if target_code not in _ZQ32_CODES:
            raise PaletteError(f"LUT target {target} is not a ZQ-32 color")
        lut[source_code] = target_code
    return lut


def apply_lut(surface: pygame.Surface, lut: Dict[int, int]) -> None:
    """Remap palette colors in place (identity for unmapped colors).

    numpy fast path when available; pure-Python fallback otherwise.
    """
    if not lut:
        return
    try:
        import numpy as np
        from pygame import surfarray

        pixels = surfarray.pixels3d(surface)
        codes = (pixels[..., 0].astype(np.uint32) << 16) | \
                (pixels[..., 1].astype(np.uint32) << 8) | pixels[..., 2]
        for source_code, target_code in lut.items():
            mask = codes == source_code
            if mask.any():
                pixels[mask, 0] = target_code >> 16 & 255
                pixels[mask, 1] = target_code >> 8 & 255
                pixels[mask, 2] = target_code & 255
        del pixels
    except ImportError:
        width, height = surface.get_size()
        for x in range(width):
            for y in range(height):
                pixel = surface.get_at((x, y))
                target_code = lut.get(_code(pixel))
                if target_code is not None:
                    surface.set_at((x, y), (target_code >> 16 & 255,
                                            target_code >> 8 & 255,
                                            target_code & 255, pixel[3]))


def ramp(name: str) -> Tuple[Color, Color, Color, Color]:
    """Look up a ramp by name (raises KeyError on unknown names)."""
    return RAMPS[name]


def swatch_sheet(cell: int = 24) -> pygame.Surface:
    """Render the palette as an 8x4 swatch grid for review docs."""
    sheet = pygame.Surface((4 * cell, len(RAMPS) * cell))
    for row, colors in enumerate(RAMPS.values()):
        for col, color in enumerate(colors):
            sheet.fill(color, (col * cell, row * cell, cell, cell))
    return sheet


def write_gpl(path: str) -> None:
    """Export the palette as a GIMP/Aseprite .gpl file (CI diff-checks this)."""
    lines = ["GIMP Palette", "Name: ZQ-32", "Columns: 4", "#"]
    for name, colors in RAMPS.items():
        for i, (r, g, b) in enumerate(colors):
            lines.append(f"{r:3d} {g:3d} {b:3d}\t{name}_{i}")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
