# Copyright (c) 2026, Peter and contributors
# For license information, please see license.txt

"""Frappe's Apps screen, arranged from the Desk Apps.

Frappe 16.50's Apps screen (`/desk`, with Desktop Settings on "Apps") draws one tile per
entry in `frappe.boot.app_data` that is `on_apps_screen`, ordered by `sequence_id`, and
sends each to its landing route: the entry's `app_route`, else the first row of its
`dock`, else its first module (`Sidebar.app_landing_route`). So the screen is arranged
here, in the boot, and Frappe draws it -- nothing in the browser is patched.

Each app on the dock, in dock order, as its Desk App's Apps Screen setting says:

- Default (and every app with no record): what Frappe would do. An installed app gets
  its own tile when it asks for one (`add_to_apps_screen`, and not mounted on another
  app), and none otherwise -- Telephony and Print Designer do not ask. Other has no
  tile, since Frappe has no such app. An app of the site's own gets one.
- One Icon: its own tile, under its dock title and logo, whether or not the app asks.
- Icon per Module: a tile for each of its modules, in its order -- and one for its
  frontend, first, if it has one -- each opening that module. A module's picture is its
  row's Apps Screen Image, else its own icon -- the one its sidebar header and the Dock
  draw -- on a tile in its Desk App's Color, else its app's colour (`module_tiles`), else
  the letter Frappe draws.
  Not the artwork some apps ship under `public/icons/desktop_icons/`: that was drawn for
  the desktop before 16.50, for workspaces rather than modules, and matching it to a
  module by file name is guesswork.
- App and Module Icons: the app's own tile, then its module tiles, as above. The frontend
  gets no tile of its own when the app's tile already opens it.
- Hidden: no tile; it stays on the dock.

An app taken off the dock is off the Apps screen too, and every other entry is turned off.

A tile that leads to `/app/...`, the desk's address before 16.50, is pointed at the same page
under `/desk/...`. Frappe's own `app_home` is still `/app/build`: the desk does not treat that
as its own link, so the browser loads it from the server, which redirects it
(`website_redirects`) and reloads the whole page. The rewrite is the redirect's own, done
before the click, so the tile opens in place like every other.

A module tile is an `app_data` entry of its own, named `opendesk-module:<shell>`, whose
`dock` is that one module: Frappe's landing ladder then opens the module the way a dock
tile would. Such entries are only ever on the Apps screen; the module still belongs to
its dock app everywhere else.

Off unless Open Desk Settings' "Override Desktop Icons" is ticked, and off too
while Desktop Settings' Desktop Page is "Desktop Icons": that is Frappe's older icon grid,
drawn from Desktop Icon records with each user's own arrangement, which Frappe is retiring
(`frappe/desk/RETIRING.md`). A site that chose it gets it as Frappe draws it.
"""

import copy

import frappe

from opendesk.open_desk import desk_apps as nav
from opendesk.open_desk import module_tiles

DEFAULT = "Default"
ONE_ICON = "One Icon"
PER_MODULE = "Icon per Module"
BOTH = "App and Module Icons"
HIDDEN = "Hidden"


def extend_bootinfo(bootinfo: "frappe._dict") -> None:
	"""Arrange the Apps screen, when Open Desk Settings says so. Runs after the dock's hook."""
	from opendesk.open_desk import settings

	try:
		if not enabled():
			return
		if bootinfo.get("module_sidebars") is None or bootinfo.get("app_data") is None:
			return
		dock = bootinfo.get("desk_apps")
		if dock is None:
			dock = nav.desk_apps(module_sidebars=bootinfo.module_sidebars, app_data=bootinfo.app_data)
		# Arranged on a copy and handed over whole, so a failure halfway leaves Frappe's as it was.
		app_data = copy.deepcopy(bootinfo.app_data)
		arrange(
			app_data,
			dock,
			style=bootinfo.get("desktop_icon_style"),
			module_sidebars=bootinfo.get("module_sidebars"),
		)
		bootinfo.app_data = app_data
	except Exception:
		# The boot is every page load; a broken arrangement leaves Frappe's own screen.
		settings.log_boot_failure("Apps screen from Desk Apps: kept Frappe's")


MODES = (DEFAULT, ONE_ICON, PER_MODULE, BOTH, HIDDEN)


def enabled() -> bool:
	"""Whether this arranges the Apps screen: switched on, and the site's desktop is the Apps screen."""
	from frappe.desk.doctype.desktop_settings.desktop_settings import get_desktop_page

	from opendesk.open_desk import settings

	return settings.feature_enabled(settings.ENABLE_APPS_SCREEN) and get_desktop_page() == "Apps"


def arrange(
	app_data: list[dict],
	dock: list[dict],
	style: str | None = None,
	module_sidebars: dict | None = None,
) -> None:
	"""Rewrite `app_data` in place so the Apps screen shows `dock` as its settings say.

	`style` is the boot's `desktop_icon_style`, the set the site draws (Solid or Subtle).
	`module_sidebars` is the boot's too: which app each module is Frappe's, for the
	colour of a picture drawn from the module's own icon.
	"""
	for entry in app_data:
		entry["app_route"] = desk_address(entry.get("app_route"))
	by_name = {entry.get("app_name"): entry for entry in app_data}
	# Frappe's own answer, read before it is overwritten: which apps asked for a tile.
	asked = {name for name, entry in by_name.items() if entry.get("on_apps_screen")}
	for entry in app_data:
		entry["on_apps_screen"] = False

	sequence = 0
	for app in dock:
		mode = app.get("apps_screen") or DEFAULT
		app_route = (by_name.get(app["app_name"]) or {}).get("app_route")
		for kind, item in plan(app, mode, asked, app_route):
			sequence += 1
			if kind == "app":
				_app_tile(app_data, by_name, app, sequence)
			elif kind == "frontend":
				app_data.append(
					_tile(
						f"opendesk-frontend:{app['key']}",
						item["label"],
						app.get("logo"),
						sequence,
						route=item["url"],
					)
				)
			else:
				app_data.append(
					_tile(
						f"opendesk-module:{item['shell']}",
						item["label"],
						item.get("desktop_image")
						or module_tiles.picture(
							item.get("icon"),
							((module_sidebars or {}).get(item["shell"]) or {}).get("app")
							or app.get("installed_app"),
							style,
							app.get("color"),
						),
						sequence,
						dock=[{"link_type": "Sidebar", "link_to": item["shell"]}],
					)
				)


def desk_address(route: str | None) -> str | None:
	"""`/app` and `/app/...` as `/desk` and `/desk/...`, as Frappe's redirect has them; anything else as it is."""
	if not route:
		return route
	path, sep, rest = route.partition("?")
	if path == "/app" or path.startswith("/app/"):
		return "/desk" + path[len("/app") :] + sep + rest
	return route


def plan(app: dict, mode: str | None, asked: set[str], app_route: str | None = None) -> list[tuple]:
	"""The tiles one dock app gets in `mode`, in order: `(kind, item)` for kind app, frontend or module.

	The rules in the module docstring, in one place, so the Apps screen and Manage Desk Apps'
	preview of it (`arrange.get_dock`) cannot disagree. `asked` is the apps Frappe gives a
	tile of their own; `app_route` is where Frappe's tile for this app already leads.
	"""
	mode = mode or DEFAULT
	if mode == DEFAULT:
		mode = ONE_ICON if _gets_a_tile(app, asked) else HIDDEN
	tiles = []
	if mode in (ONE_ICON, BOTH):
		tiles.append(("app", None))
	if mode in (PER_MODULE, BOTH):
		frontend = app.get("frontend")
		if frontend and not (mode == BOTH and frontend["url"] == app_route):
			tiles.append(("frontend", frontend))
		tiles += [("module", module) for module in app["modules"]]
	return tiles


def _gets_a_tile(app: dict, asked: set[str]) -> bool:
	"""Default: an installed app (or Other) as Frappe has it; an app of the site's own, yes."""
	if app.get("installed_app"):
		return app["app_name"] in asked
	return True


def _app_tile(app_data: list[dict], by_name: dict, app: dict, sequence: int) -> dict:
	"""The app's own tile, under its dock title and logo: Frappe's entry for it, or a new one."""
	entry = by_name.get(app["app_name"])
	if entry is None:
		entry = _tile(app["app_name"], app["title"], app.get("logo"), sequence)
		app_data.append(entry)
		by_name[app["app_name"]] = entry
	entry.update(on_apps_screen=True, sequence_id=sequence, app_title=app["title"])
	if app.get("logo"):
		entry["app_logo_url"] = app["logo"]
	elif app.get("color") and entry.get("app_logo_url"):
		# An app with an icon of its own and no logo keeps Frappe's logo here, in its colour.
		entry["app_logo_url"] = (
			module_tiles.recoloured_logo(entry["app_logo_url"], app["color"]) or entry["app_logo_url"]
		)
	# An app Frappe does not know has no dock of its own; its modules lead into it, so the
	# tile opens its first one even where the dock has not placed them.
	if not entry.get("dock") and not entry.get("app_route"):
		entry["dock"] = [{"link_type": "Sidebar", "link_to": m["shell"]} for m in app["modules"]]
	return entry


def _tile(
	app_name: str,
	title: str,
	logo: str | None,
	sequence: int,
	route: str = "",
	dock: list[dict] | None = None,
) -> dict:
	return {
		"app_name": app_name,
		"app_title": title,
		"app_logo_url": logo or None,
		"app_route": route,
		"desk_route": "",
		"on_apps_screen": True,
		"sequence_id": sequence,
		"dock": dock or [],
	}
