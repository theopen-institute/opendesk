# Copyright (c) 2026, Peter and contributors
# For license information, please see license.txt

"""An Apps screen picture for a module, drawn from the icon the module already has.

Frappe's Apps screen tile takes an image (`app_logo_url`) or draws a letter. A module
has an icon already -- its sidebar's `header_icon`, which the Dock and the sidebar
header draw -- but that is a symbol in an icon sprite (`app_include_icons`), not an
image. So the symbol is lifted out of the sprite that holds it and set on a tile in the
shape and colour of the Apps screen's own artwork (`desktop_icons/<style>/*.svg`): a
54px rounded square, the glyph white on the app's colour (Solid), or in the app's
colour on a tint of it (Subtle). It is handed over as a URL (`tile`, below), so the tile is
an ordinary image and nothing in the browser changes.

A URL rather than the picture itself: a module's icon is a couple of kilobytes of SVG, and the
boot carries every tile on every page load. The URL ends in a hash of the picture it draws, so
it never changes what it shows, and the browser keeps each one rather than asking again.

The app's colour is its Desk App's Color, else the one its shipped artwork is drawn in,
else its logo's, else Frappe's grey -- read from the files, not kept here.

A Desk App's Color also redraws the app's own logo, when that logo is an installed app's
SVG (`recoloured_logo`): its main colour -- the first fill it states, as `app_color` reads a
logo -- is swapped for the new one wherever it appears. A logo in any other form is left as
it is; uploading a logo on the Desk App is the way to change those.
"""

import hashlib
import os
import re
from collections import Counter
from functools import lru_cache
from urllib.parse import urlencode

import frappe
from frappe import _

GREY = "#7B808A"
_FILL = re.compile(r'fill="(#[0-9A-Fa-f]{6})"')
_TILE = (
	"M38.5714 0H15.4286C6.90761 0 0 6.90761 0 15.4286V38.5714C0 47.0924 6.90761 54 15.4286 54"
	"H38.5714C47.0924 54 54 47.0924 54 38.5714V15.4286C54 6.90761 47.0924 0 38.5714 0Z"
)
# The desk's stylesheet is what draws most symbols: a Lucide or soft symbol states no stroke or
# fill of its own and leans on Frappe's `.icon` and `.soft-*` rules (scss/common/icons.scss),
# which an image never sees -- without these a line icon is a solid black shape. Set on a group
# around the glyph, so a symbol's own attributes (a duotone's `stroke="none"`) still win. The
# stroke is heavier than the desk's 1.5, to sit with the Apps screen's drawn artwork.
_GLYPH_CSS = (
	".glyph{fill:none;stroke:currentColor;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}"
	".soft-body,.soft-layer{fill:currentColor;fill-opacity:.1}"
	".soft-layer,.soft-accent{stroke:none}"
	".soft-accent{fill:currentColor;fill-opacity:.5}"
	".soft-accent-line{stroke-opacity:.5}"
)


def picture(icon: str | None, app: str | None, style: str | None, color: str | None = None) -> str | None:
	"""The tile for `icon`, in `color` else `app`'s colour, as a URL; None when no sprite has it."""
	color = hex_color(color)
	svg = draw(icon, app, style, color)
	if not svg:
		return None
	query = {"icon": icon, "app": app or "", "style": style or "", **({"color": color} if color else {})}
	query["v"] = _digest(svg)
	return f"/api/method/opendesk.open_desk.module_tiles.tile?{urlencode(query)}"


@frappe.whitelist(methods=["GET"])
def tile(icon: str, app: str | None = None, style: str | None = None, color: str | None = None) -> None:
	"""The picture `picture` points at, as an SVG image.

	Kept by the browser for good: the URL carries a hash of the picture (`v`), so a changed
	sprite or colour is a new URL. Drawn from the installed apps' own files, the icon's
	name and the colour, which are checked, so it is the same for everyone who may see the desk.
	"""
	svg = draw(icon, app or None, style or None, color or None)
	if not svg:
		# Not named back: `icon` is whatever the request said, and is only checked inside `draw`.
		raise frappe.DoesNotExistError(_("No such icon."))
	_send_svg(svg, f"{icon}.svg")


def recoloured_logo(url: str | None, color: str | None) -> str | None:
	"""`url`, an installed app's SVG logo, redrawn in `color`, as a URL; None when it cannot be."""
	color = hex_color(color)
	svg = recolour(url, color)
	if not svg:
		return None
	query = {"src": url, "color": color, "v": _digest(svg)}
	return f"/api/method/opendesk.open_desk.module_tiles.logo?{urlencode(query)}"


@frappe.whitelist(methods=["GET"])
def logo(src: str, color: str) -> None:
	"""The picture `recoloured_logo` points at, as an SVG image; kept for good, as `tile` is.

	Only an SVG file in an installed app's `public` folder is ever read (`_asset_path`).
	"""
	svg = recolour(src, color)
	if not svg:
		raise frappe.DoesNotExistError(_("No such logo."))
	_send_svg(svg, "logo.svg")


def recolour(url: str | None, color: str | None) -> str | None:
	"""The SVG logo at `url` with its main colour swapped for `color`; None when it cannot be."""
	color = hex_color(color)
	path = _asset_path(url)
	if not color or not path or not path.endswith(".svg"):
		return None
	return _recoloured(path, color)


def hex_color(color: str | None) -> str | None:
	"""`color` as `#RRGGBB`, or None when it is not a hex colour (`#RGB` is spelled out)."""
	value = (color or "").strip()
	if re.fullmatch(r"#[0-9A-Fa-f]{3}", value):
		value = "#" + "".join(c * 2 for c in value[1:])
	return value.upper() if re.fullmatch(r"#[0-9A-Fa-f]{6}", value) else None


def _send_svg(svg: str, filename: str) -> None:
	frappe.response.update(
		type="download",
		filename=filename,
		filecontent=svg.encode(),
		content_type="image/svg+xml",
		display_content_as="inline",
	)
	headers = frappe.local.response_headers
	headers["Cache-Control"] = "private, max-age=31536000, immutable"
	# Opened on its own rather than as an image, it still runs nothing.
	headers["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'"
	headers["X-Content-Type-Options"] = "nosniff"


def draw(icon: str | None, app: str | None, style: str | None, color: str | None = None) -> str | None:
	"""The tile for `icon`, in `color` else `app`'s colour, as SVG source; None when no sprite has it."""
	if not icon or not re.fullmatch(r"[\w-]+", icon):
		return None
	symbol = _symbols(tuple(frappe.get_installed_apps())).get(icon)
	if not symbol:
		return None
	attrs, inner = symbol
	color = hex_color(color) or app_color(app)
	subtle = (style or "Solid").lower() == "subtle"
	square = f'fill="{color}" fill-opacity="0.19"' if subtle else f'fill="{color}"'
	ink = color if subtle else "#FFFFFF"
	return (
		'<svg xmlns="http://www.w3.org/2000/svg" width="54" height="54" viewBox="0 0 54 54">'
		# A duotone symbol paints with these; a line icon with `currentColor`.
		f"<style>svg{{--duotone-dark:{ink};--duotone-light:{ink}8C;color:{ink}}}{_GLYPH_CSS}</style>"
		f'<path d="{_TILE}" {square}/>'
		f'<g class="glyph"><svg x="14" y="14" width="26" height="26" {attrs}>{inner}</svg></g>'
		"</svg>"
	)


def _digest(svg: str) -> str:
	return hashlib.sha1(svg.encode(), usedforsecurity=False).hexdigest()[:12]


def app_color(app: str | None) -> str:
	"""The colour an app's Apps screen pictures are drawn in."""
	return (_app_colors(tuple(frappe.get_installed_apps())).get(app) if app else None) or GREY


@lru_cache(maxsize=8)
def _symbols(apps: tuple[str, ...]) -> dict[str, tuple[str, str]]:
	"""Every symbol in the installed apps' icon sprites: name -> (its attributes, its content).

	Read once per process for each set of installed `apps` (a process serves every site on
	the bench); the sprites change only with a deploy, which restarts it.
	A symbol's `id` is dropped and its `viewBox` kept, so it can be nested as an `<svg>`.
	"""
	symbols: dict[str, tuple[str, str]] = {}
	for url in frappe.get_hooks("app_include_icons") or []:
		path = _asset_path(url)
		if not path:
			continue
		with open(path, encoding="utf-8") as f:
			source = f.read()
		for match in re.finditer(r"<symbol\b([^>]*)>(.*?)</symbol>", source, re.S):
			attrs, inner = match.groups()
			name = re.search(r'\bid="icon-([\w-]+)"', attrs)
			if not name or name.group(1) in symbols:
				continue
			attrs = re.sub(r'\s*\b(id|class|style)="[^"]*"', "", attrs)
			symbols[name.group(1)] = (attrs.strip(), inner)
	return symbols


@lru_cache(maxsize=8)
def _app_colors(apps: tuple[str, ...]) -> dict[str, str]:
	"""Each installed app's colour: the commonest fill in its shipped Solid artwork, else in its logo."""
	colors = {}
	for app in apps:
		fills = Counter()
		solid = os.path.join(frappe.get_app_path(app), "public", "icons", "desktop_icons", "solid")
		if os.path.isdir(solid):
			for name in os.listdir(solid):
				if name.endswith(".svg"):
					with open(os.path.join(solid, name), encoding="utf-8") as f:
						fills.update(_FILL.findall(f.read()))
		if not fills:
			for logo in frappe.get_hooks("app_logo_url", app_name=app) or []:
				path = _asset_path(logo)
				if path and path.endswith(".svg"):
					with open(path, encoding="utf-8") as f:
						fills.update(_FILL.findall(f.read())[:1])
		fills.pop("#FFFFFF", None)
		fills.pop("#ffffff", None)
		if fills:
			colors[app] = fills.most_common(1)[0][0]
	return colors


@lru_cache(maxsize=64)
def _recoloured(path: str, color: str) -> str | None:
	"""Read once per process, like the sprites: an app's files change only with a deploy."""
	with open(path, encoding="utf-8") as f:
		source = f.read()
	main = next((fill for fill in _FILL.findall(source) if fill.upper() != "#FFFFFF"), None)
	if not main:
		return None
	return re.sub(re.escape(main), color, source, flags=re.I)


def _asset_path(url: str | None) -> str | None:
	"""The file behind an `/assets/<app>/...` URL, if it is one of an installed app's public files."""
	match = re.fullmatch(r"/?assets/([\w-]+)/(.+)", url or "")
	if not match or match.group(1) not in frappe.get_installed_apps():
		return None
	public = os.path.realpath(os.path.join(frappe.get_app_path(match.group(1)), "public"))
	path = os.path.realpath(os.path.join(public, match.group(2)))
	# A URL can come from a request (`logo`): nothing outside the app's public folder.
	if not path.startswith(public + os.sep):
		return None
	return path if os.path.isfile(path) else None
