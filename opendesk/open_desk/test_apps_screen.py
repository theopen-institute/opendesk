# Copyright (c) 2026, Peter and contributors
# For license information, please see license.txt

"""The Apps screen's arrangement, over plain data: `arrange` rewrites `app_data` in place."""

from unittest import TestCase

from opendesk.open_desk.apps_screen import BOTH, HIDDEN, ONE_ICON, PER_MODULE, arrange


def dock_app(key, app_name, title, modules=(), mode=None, logo=None, frontend=None):
	"""A dock entry; an `app:` key stands for an installed app, as the resolver marks it."""
	return {
		"key": key,
		"app_name": app_name,
		"installed_app": key.removeprefix("app:") if key.startswith("app:") else None,
		"title": title,
		"logo": logo,
		"apps_screen": mode,
		"frontend": frontend,
		"modules": [{"shell": m, "label": m} for m in modules],
	}


def app_data():
	return [
		{
			"app_name": "erpnext",
			"app_title": "ERPNext",
			"app_logo_url": "/e.svg",
			"on_apps_screen": True,
			"sequence_id": 1,
			"dock": [{"link_type": "Sidebar", "link_to": "Stock"}],
		},
		{
			"app_name": "hrms",
			"app_title": "Frappe HR",
			"app_logo_url": None,
			"on_apps_screen": True,
			"sequence_id": 2,
			"dock": [],
		},
		{
			"app_name": "telephony",
			"app_title": "Telephony",
			"app_logo_url": None,
			"on_apps_screen": False,
			"sequence_id": 3,
			"dock": [],
		},
	]


def shown(data):
	return [
		(e["app_name"], e["app_title"])
		for e in sorted((e for e in data if e["on_apps_screen"]), key=lambda e: e["sequence_id"])
	]


class TestArrange(TestCase):
	def test_dock_order_one_icon_each_and_everything_else_off(self):
		data = app_data()
		arrange(data, [dock_app("app:hrms", "hrms", "People"), dock_app("app:erpnext", "erpnext", "ERPNext")])
		self.assertEqual(shown(data), [("hrms", "People"), ("erpnext", "ERPNext")])

	def test_default_follows_frappe_for_installed_apps(self):
		"""Telephony does not ask for a tile; ERPNext does. Other is no app of Frappe's."""
		data = app_data()
		arrange(
			data,
			[
				dock_app("app:telephony", "telephony", "Telephony", modules=("Telephony",)),
				dock_app("app:erpnext", "erpnext", "ERPNext"),
				dock_app("app:Other", "opendesk-other", "Other", modules=("Misc",)),
			],
		)
		self.assertEqual(shown(data), [("erpnext", "ERPNext")])

	def test_one_icon_gives_an_app_a_tile_it_did_not_ask_for(self):
		data = app_data()
		arrange(data, [dock_app("app:telephony", "telephony", "Telephony", mode=ONE_ICON)])
		self.assertEqual(shown(data), [("telephony", "Telephony")])

	def test_default_gives_an_app_of_the_sites_own_a_tile(self):
		data = app_data()
		arrange(data, [dock_app("desk-app:Finance", "desk-app:Finance", "Finance", modules=("Accounts",))])
		self.assertEqual(shown(data), [("desk-app:Finance", "Finance")])

	def test_hidden_has_no_tile(self):
		data = app_data()
		arrange(
			data,
			[
				dock_app("app:hrms", "hrms", "Frappe HR", mode=HIDDEN),
				dock_app("app:erpnext", "erpnext", "ERPNext"),
			],
		)
		self.assertEqual(shown(data), [("erpnext", "ERPNext")])

	def test_icon_per_module_with_frontend_first_and_pictures(self):
		data = app_data()
		oi = dock_app(
			"desk-app:OI",
			"desk-app:OI",
			"OI",
			modules=("Members", "Student Accounts"),
			mode=PER_MODULE,
			frontend={"label": "OI app", "url": "/commons"},
		)
		oi["modules"][0]["desktop_image"] = "/files/members.png"
		arrange(data, [oi])
		tiles = sorted((e for e in data if e["on_apps_screen"]), key=lambda e: e["sequence_id"])
		self.assertEqual([t["app_title"] for t in tiles], ["OI app", "Members", "Student Accounts"])
		self.assertEqual(tiles[0]["app_route"], "/commons")
		self.assertEqual(tiles[1]["app_logo_url"], "/files/members.png")
		# No Apps Screen Image: Frappe draws its letter.
		self.assertIsNone(tiles[2]["app_logo_url"])
		self.assertEqual(tiles[2]["dock"], [{"link_type": "Sidebar", "link_to": "Student Accounts"}])

	def test_app_and_module_icons_puts_the_apps_tile_first(self):
		data = app_data()
		oi = dock_app(
			"desk-app:OI",
			"desk-app:OI",
			"OI",
			modules=("Members", "Student Accounts"),
			mode=BOTH,
			logo="/oi.svg",
			frontend={"label": "OI app", "url": "/commons"},
		)
		arrange(data, [oi, dock_app("app:erpnext", "erpnext", "ERPNext")])
		self.assertEqual(
			shown(data),
			[
				("desk-app:OI", "OI"),
				("opendesk-frontend:desk-app:OI", "OI app"),
				("opendesk-module:Members", "Members"),
				("opendesk-module:Student Accounts", "Student Accounts"),
				("erpnext", "ERPNext"),
			],
		)
		app_tile = next(e for e in data if e["app_name"] == "desk-app:OI")
		self.assertEqual(app_tile["dock"][0], {"link_type": "Sidebar", "link_to": "Members"})

	def test_app_and_module_icons_has_no_second_tile_for_the_frontend_the_app_opens(self):
		data = app_data()
		data[1]["app_route"] = "/hr"
		hr = dock_app(
			"app:hrms",
			"hrms",
			"Frappe HR",
			modules=("HR",),
			mode=BOTH,
			frontend={"label": "Frappe HR app", "url": "/hr"},
		)
		arrange(data, [hr])
		self.assertEqual(shown(data), [("hrms", "Frappe HR"), ("opendesk-module:HR", "HR")])

	def test_a_module_without_an_image_gets_a_picture_of_its_own_icon(self):
		"""Drawn by `module_tiles` in the module's app's colour; an Apps Screen Image comes first."""
		from unittest.mock import patch

		from opendesk.open_desk import apps_screen

		data = app_data()
		oi = dock_app("desk-app:OI", "desk-app:OI", "OI", modules=("Stock", "Members"), mode=PER_MODULE)
		oi["modules"][0]["icon"] = "shelf-rack-duotone"
		oi["modules"][1]["desktop_image"] = "/files/members.png"
		asked = []
		with patch.object(
			apps_screen.module_tiles,
			"picture",
			side_effect=lambda icon, app, style, color=None: asked.append((icon, app, style, color))
			or f"data:{icon}",
		):
			arrange(data, [oi], style="Subtle", module_sidebars={"Stock": {"app": "erpnext"}})
		tiles = sorted((e for e in data if e["on_apps_screen"]), key=lambda e: e["sequence_id"])
		self.assertEqual(
			[t["app_logo_url"] for t in tiles], ["data:shelf-rack-duotone", "/files/members.png"]
		)
		self.assertEqual(asked, [("shelf-rack-duotone", "erpnext", "Subtle", None)])

	def test_a_desk_apps_color_draws_its_module_tiles(self):
		from unittest.mock import patch

		from opendesk.open_desk import apps_screen

		oi = dock_app("desk-app:OI", "desk-app:OI", "OI", modules=("Stock",), mode=PER_MODULE)
		oi["modules"][0]["icon"] = "shelf-rack-duotone"
		oi["color"] = "#2E7D32"
		asked = []
		with patch.object(
			apps_screen.module_tiles,
			"picture",
			side_effect=lambda icon, app, style, color=None: asked.append(color) or "data:x",
		):
			arrange(app_data(), [oi], module_sidebars={"Stock": {"app": "erpnext"}})
		self.assertEqual(asked, ["#2E7D32"])

	def test_a_color_redraws_frappes_logo_when_the_record_has_none(self):
		from unittest.mock import patch

		from opendesk.open_desk import apps_screen

		data = app_data()
		erpnext = dock_app("app:erpnext", "erpnext", "ERPNext", modules=("Stock",), mode=ONE_ICON)
		erpnext["color"] = "#2E7D32"
		with patch.object(
			apps_screen.module_tiles,
			"recoloured_logo",
			side_effect=lambda url, color: f"{url}?in={color}",
		):
			arrange(data, [erpnext])
		entry = next(e for e in data if e["app_name"] == "erpnext")
		self.assertEqual(entry["app_logo_url"], "/e.svg?in=#2E7D32")
		# A logo of the record's own is drawn as it is.
		data = app_data()
		erpnext["logo"] = "/files/books.png"
		arrange(data, [erpnext])
		entry = next(e for e in data if e["app_name"] == "erpnext")
		self.assertEqual(entry["app_logo_url"], "/files/books.png")

	def test_plan_is_what_arrange_draws(self):
		"""Manage Desk Apps previews the Apps screen from `plan`, so it must be the arrangement's own rule."""
		from opendesk.open_desk.apps_screen import DEFAULT, MODES, plan

		oi = dock_app(
			"desk-app:OI",
			"desk-app:OI",
			"OI",
			modules=("Members",),
			frontend={"label": "OI app", "url": "/oi"},
		)
		self.assertEqual([k for k, _ in plan(oi, BOTH, set())], ["app", "frontend", "module"])
		self.assertEqual([k for k, _ in plan(oi, PER_MODULE, set())], ["frontend", "module"])
		self.assertEqual(plan(oi, HIDDEN, set()), [])
		telephony = dock_app("app:telephony", "telephony", "Telephony", modules=("Calls",))
		self.assertEqual(plan(telephony, DEFAULT, set()), [])
		self.assertEqual([k for k, _ in plan(telephony, DEFAULT, {"telephony"})], ["app"])
		self.assertEqual(len(MODES), 5)

	def test_a_tile_at_the_old_desk_address_is_moved_to_the_new_one(self):
		"""Frappe's own `app_home` is `/app/build`, which reloads the page on its way to `/desk/build`."""
		from opendesk.open_desk.apps_screen import desk_address

		data = app_data()
		data[0]["app_route"] = "/app/build"
		arrange(data, [dock_app("app:erpnext", "erpnext", "ERPNext")])
		self.assertEqual(data[0]["app_route"], "/desk/build")
		self.assertEqual(desk_address("/app"), "/desk")
		self.assertEqual(desk_address("/app/stock?x=1"), "/desk/stock?x=1")
		for route in ("/apps", "/application", "/helpdesk", "https://example.com/app/x", "", None):
			with self.subTest(route=route):
				self.assertEqual(desk_address(route), route)

	def test_an_app_frappe_does_not_know_gets_a_tile_opening_its_modules(self):
		data = app_data()
		arrange(
			data,
			[dock_app("desk-app:OI", "desk-app:OI", "OI", modules=("Members",), logo="/oi.svg")],
		)
		entry = next(e for e in data if e["app_name"] == "desk-app:OI")
		self.assertEqual((entry["app_logo_url"], entry["on_apps_screen"]), ("/oi.svg", True))
		self.assertEqual(entry["dock"], [{"link_type": "Sidebar", "link_to": "Members"}])

	def test_a_known_apps_own_dock_is_left_alone(self):
		data = app_data()
		arrange(data, [dock_app("app:erpnext", "erpnext", "ERPNext", modules=("Accounts",))])
		self.assertEqual(data[0]["dock"], [{"link_type": "Sidebar", "link_to": "Stock"}])
