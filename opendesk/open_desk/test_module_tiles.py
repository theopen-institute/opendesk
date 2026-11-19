# Copyright (c) 2026, Peter and contributors
# For license information, please see license.txt

"""An Apps screen picture drawn from a module's own icon, over plain data."""

import os
import tempfile
from unittest import TestCase
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from opendesk.open_desk import module_tiles

SYMBOLS = {"calculator-duotone": ('viewBox="0 0 24 24" stroke="none"', '<path d="M1 1H2Z"/>')}


def sprites(color="#0289F7"):
	return (
		patch.object(module_tiles, "_symbols", return_value=SYMBOLS),
		patch.object(module_tiles, "app_color", return_value=color),
		patch.object(module_tiles.frappe, "get_installed_apps", return_value=["frappe", "erpnext"]),
	)


def drawn(icon, style="Solid"):
	a, b, c = sprites()
	with a, b, c:
		return module_tiles.draw(icon, "erpnext", style)


def pictured(icon, color="#0289F7"):
	a, b, c = sprites(color)
	with a, b, c:
		return module_tiles.picture(icon, "erpnext", "Solid")


class TestPicture(TestCase):
	def test_solid_is_the_glyph_in_white_on_the_apps_colour(self):
		svg = drawn("calculator-duotone")
		self.assertIn('fill="#0289F7"/>', svg)
		self.assertIn("--duotone-dark:#FFFFFF", svg)
		self.assertIn('<svg x="14" y="14" width="26" height="26" viewBox="0 0 24 24" stroke="none">', svg)

	def test_subtle_is_the_glyph_in_the_apps_colour_on_a_tint(self):
		svg = drawn("calculator-duotone", style="Subtle")
		self.assertIn('fill="#0289F7" fill-opacity="0.19"', svg)
		self.assertIn("--duotone-dark:#0289F7", svg)

	def test_a_line_icon_is_stroked_not_filled(self):
		# A Lucide symbol states no stroke or fill; the desk's CSS draws it, and an image has none.
		svg = drawn("calculator-duotone")
		self.assertIn(".glyph{fill:none;stroke:currentColor;", svg)
		self.assertIn('<g class="glyph"><svg x="14"', svg)
		# The symbol's own attributes stay on its own element, so they still win.
		self.assertIn('viewBox="0 0 24 24" stroke="none">', svg)

	def test_no_symbol_or_no_name_is_no_picture(self):
		self.assertIsNone(drawn("not-an-icon"))
		self.assertIsNone(drawn(None))
		self.assertIsNone(drawn('x" onload="alert(1)'))


class TestPictureURL(TestCase):
	"""The boot carries a URL to the picture, which names it and changes whenever it does."""

	def test_the_url_names_the_picture_and_its_hash(self):
		url = urlsplit(pictured("calculator-duotone"))
		self.assertEqual(url.path, "/api/method/opendesk.open_desk.module_tiles.tile")
		query = parse_qs(url.query)
		self.assertEqual(query["icon"], ["calculator-duotone"])
		self.assertEqual(query["app"], ["erpnext"])
		self.assertEqual(len(query["v"][0]), 12)

	def test_a_changed_picture_is_a_new_url(self):
		self.assertEqual(pictured("calculator-duotone"), pictured("calculator-duotone"))
		self.assertNotEqual(pictured("calculator-duotone"), pictured("calculator-duotone", "#E86C13"))

	def test_no_symbol_is_no_url(self):
		self.assertIsNone(pictured("not-an-icon"))
		self.assertIsNone(pictured('x" onload="alert(1)'))


class TestColor(TestCase):
	"""A Desk App's Color: over the app's own colour on a tile, and swapped into an SVG logo."""

	def test_a_color_given_wins_over_the_apps(self):
		a, b, c = sprites()
		with a, b, c:
			svg = module_tiles.draw("calculator-duotone", "erpnext", "Solid", "#2e7d32")
		self.assertIn('fill="#2E7D32"/>', svg)
		self.assertNotIn("#0289F7", svg)

	def test_the_color_is_in_the_url(self):
		a, b, c = sprites()
		with a, b, c:
			plain = module_tiles.picture("calculator-duotone", "erpnext", "Solid")
			green = module_tiles.picture("calculator-duotone", "erpnext", "Solid", "#2E7D32")
		self.assertEqual(parse_qs(urlsplit(green).query)["color"], ["#2E7D32"])
		self.assertNotIn("color", parse_qs(urlsplit(plain).query))

	def test_only_a_hex_colour_is_a_colour(self):
		self.assertEqual(module_tiles.hex_color(" #2e7d32 "), "#2E7D32")
		self.assertEqual(module_tiles.hex_color("#abc"), "#AABBCC")
		for value in (None, "", "green", "#2E7D3", "var(--x)", '#000000"/><script>'):
			self.assertIsNone(module_tiles.hex_color(value))

	def test_a_logos_main_colour_is_swapped(self):
		logo = (
			'<svg><path d="M0" fill="white"/><path d="M1" fill="#004880"/>'
			'<path d="M2" fill="#E7E5F9"/><path d="M3" fill="#E7E5F9"/><path stroke="#004880"/></svg>'
		)
		with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as f:
			f.write(logo)
		self.addCleanup(os.unlink, f.name)
		module_tiles._recoloured.cache_clear()
		with patch.object(module_tiles, "_asset_path", return_value=f.name):
			svg = module_tiles.recolour("/assets/education/edu-logo.svg", "#2e7d32")
			url = module_tiles.recoloured_logo("/assets/education/edu-logo.svg", "#2e7d32")
			self.assertIsNone(module_tiles.recolour("/assets/education/edu-logo.svg", "green"))
		self.assertEqual(svg.count("#2E7D32"), 2)
		self.assertNotIn("#004880", svg)
		self.assertEqual(svg.count("#E7E5F9"), 2)
		query = parse_qs(urlsplit(url).query)
		self.assertEqual((query["src"], query["color"]), (["/assets/education/edu-logo.svg"], ["#2E7D32"]))

	def test_only_an_installed_apps_public_svg_is_read(self):
		with patch.object(module_tiles.frappe, "get_installed_apps", return_value=["frappe"]):
			self.assertIsNone(module_tiles.recolour("/files/logo.svg", "#2E7D32"))
			self.assertIsNone(module_tiles.recolour("/assets/frappe/../../../../etc/passwd", "#2E7D32"))
			self.assertIsNone(module_tiles.recolour("/assets/other/logo.svg", "#2E7D32"))
