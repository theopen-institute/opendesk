# Copyright (c) 2026, Peter and contributors
# For license information, please see license.txt

"""An Apps screen picture drawn from a module's own icon, over plain data."""

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
