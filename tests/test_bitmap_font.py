# SPDX-FileCopyrightText: 2026 Michael Traver
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass

import pytest

from adafruit_bitmap_font import bitmap_font
from tests.displayio import Bitmap


@dataclass
class FontParam:
    # The path to the font file.
    path: str

    # The font's expected bounding box.
    expected_bounding_box: tuple

    # The font's expected ascent and descent.
    expected_ascent: int
    expected_descent: int

    # A code point known to exist in the font.
    code_point: int

    # The expected width and height of the glyph specified by code_point.
    expected_glyph_width: int
    expected_glyph_height: int

    # A code point known not to exist in the font.
    unknown_code_point: int


@pytest.fixture(
    params=[
        pytest.param(
            FontParam(
                path="examples/fonts/Junction-regular-24.bdf",
                expected_bounding_box=(37, 43, -3, -9),
                expected_ascent=24,
                expected_descent=8,
                code_point=ord("A"),
                unknown_code_point=0x10FFFF,
                expected_glyph_width=22,
                expected_glyph_height=26,
            ),
            id="bdf",
        ),
        pytest.param(
            FontParam(
                path="examples/fonts/Junction-regular-24.pcf",
                expected_bounding_box=(37, 43, -3, -9),
                expected_ascent=24,
                expected_descent=8,
                code_point=ord("A"),
                unknown_code_point=0x10FFFF,
                expected_glyph_width=22,
                expected_glyph_height=26,
            ),
            id="pcf",
        ),
        pytest.param(
            FontParam(
                path="examples/fonts/unifont-16.0.02-ascii-emoji.bin",
                # The lvfontbin impl takes the width to be the header's default
                # advanceWidth, which is only set if the glyph advanceWidth
                # bits length is 0. The glyph advanceWidth bits length for this
                # particular font is non-zero, which leads to a bounding box width
                # of 0 even though its glyphs do in fact have width.
                expected_bounding_box=(0, 16, 0, -2),
                expected_ascent=14,
                expected_descent=-2,
                code_point=ord("A"),
                unknown_code_point=0x10FFFF,
                expected_glyph_width=6,
                expected_glyph_height=10,
            ),
            id="lvfontbin",
        ),
    ],
)
def font_and_params(request):
    return bitmap_font.load_font(request.param.path, Bitmap), request.param


def test_bounding_box(font_and_params):
    font, params = font_and_params

    bb = font.get_bounding_box()
    assert len(bb) == 4
    assert bb == params.expected_bounding_box


def test_ascent(font_and_params):
    font, params = font_and_params

    assert font.ascent == params.expected_ascent


def test_descent(font_and_params):
    font, params = font_and_params

    assert font.descent == params.expected_descent


def test_known_glyph_exists(font_and_params):
    font, params = font_and_params

    glyph = font.get_glyph(params.code_point)
    assert glyph is not None


def test_unknown_glyph_returns_none(font_and_params):
    font, params = font_and_params

    glyph = font.get_glyph(params.unknown_code_point)
    assert glyph is None


def test_glyph_metrics(font_and_params):
    font, params = font_and_params

    glyph = font.get_glyph(params.code_point)
    assert glyph is not None
    assert glyph.width == params.expected_glyph_width
    assert glyph.height == params.expected_glyph_height


def test_cache_known_glyph_on_get(font_and_params):
    font, params = font_and_params

    # The code point should not be present in the cache since
    # no glyphs have been loaded.
    assert params.code_point not in font._glyphs

    glyph = font.get_glyph(params.code_point)

    # This code point exists in the font so we should get a Glyph.
    assert glyph is not None

    # The glyph should now be cached.
    assert params.code_point in font._glyphs
    assert font._glyphs[params.code_point] is glyph


def test_cache_unknown_glyph_on_get(font_and_params):
    font, params = font_and_params

    # The code point should not be present in the cache since
    # no glyphs have been loaded.
    assert params.unknown_code_point not in font._glyphs

    glyph = font.get_glyph(params.unknown_code_point)

    # This code point does not exist in the font so we should get None.
    assert glyph is None

    # None should now be cached.
    assert params.unknown_code_point in font._glyphs
    assert font._glyphs[params.unknown_code_point] is None


def test_cache_known_glyph_on_load(font_and_params):
    font, params = font_and_params

    # The code point should not be present in the cache since
    # no glyphs have been loaded.
    assert params.code_point not in font._glyphs

    font.load_glyphs(params.code_point)

    # The glyph should now be cached.
    assert params.code_point in font._glyphs
    assert font._glyphs[params.code_point] is not None


def test_cache_unknown_glyph_on_load(font_and_params):
    font, params = font_and_params

    # The code point should not be present in the cache since
    # no glyphs have been loaded.
    assert params.unknown_code_point not in font._glyphs

    font.load_glyphs(params.unknown_code_point)

    # None should now be cached.
    assert params.unknown_code_point in font._glyphs
    assert font._glyphs[params.unknown_code_point] is None
