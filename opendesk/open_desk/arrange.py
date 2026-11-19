# Copyright (c) 2026, Peter and contributors
# For license information, please see license.txt

"""The dock's two editors: which apps it lists, and which modules each app offers.

The desk draws both in Frappe's own arrangement editor (`frappe.ui.ArrangementEditor`,
the one behind Manage Dock and Edit Sidebar) -- see `js/arrange.js`. This is what they
read and write. Everything is stored where it already was, on `Desk App`
records, so the form and the editors are two ways into the same data:

- Manage Desk Apps orders and hides apps (`dock_after` and `hidden`), sets how each shows
  on the Apps screen (`apps_screen`, previewed with the tiles it would draw), and adds
  new ones: a Desk App of its own, with a title and an icon, which then needs modules
  before the dock shows it.
- Manage Modules orders, adds and takes modules off one app's list, with
  Category and Spacer rows between them: the record's modules table. It can also
  make a new module there and then: a custom Module Def of the site's own, made on
  save, so a new app can be filled without leaving the editor. Taking one of an
  installed app's own modules off its list switches the record to Replace, which is
  what sends a module to Other; with none taken off it stays in Add, so a module the
  app gains later still turns up.

Only the site's arrangement is edited ("For everyone"). There is no per-user layer:
Desk Apps are site records.

The dock order is the whole dock's, whichever editor wrote. Every app sits at its
default place unless its record anchors it after another (see `desk_apps`), so
a save writes an anchor only onto the apps that left the default order, and a record
is made only for an app that needs one to hold a position or to be hidden. A record
an editor made that no longer holds anything (`_is_placeholder`) is deleted again.
"""

import hashlib
import json

import frappe
from frappe import _

from opendesk.open_desk import apps_screen, module_tiles
from opendesk.open_desk import desk_apps as nav

APP = nav.APP


def _check():
	"""Both editors write Desk App records, so both need the right to."""
	frappe.has_permission(APP, "write", throw=True)
	frappe.has_permission(APP, "create", throw=True)


def records_stamp(for_update: bool = False) -> str:
	"""Where the Desk Apps stand: a fingerprint of every record's name and when it last changed.

	Each editor is handed one when it opens and sends it back with its save, which is refused if
	another save came in between (`_check_stamp`). A record saved -- its modules too, which are
	saved with it -- has a new `modified`; one made or deleted changes the names.
	"""
	table = frappe.qb.DocType(APP)
	query = frappe.qb.from_(table).select(table.name, table.modified).orderby(table.name)
	if for_update:
		query = query.for_update()
	records = [(name, str(modified)) for name, modified in query.run()]
	return hashlib.sha1(json.dumps(records).encode()).hexdigest()[:16]


def _check_stamp(seen: str | None) -> None:
	"""Refuse a save over Desk Apps someone else has saved since this editor read them.

	Without the check, the later of two editors open at once would write back every app's order
	and settings as it first read them, undoing the earlier save. The records are locked while
	they are read, so of two saves at once the second waits for the first and then sees it. A
	save that brings no stamp (a desk loaded before this check existed) is let through.
	"""
	if seen and seen != records_stamp(for_update=True):
		frappe.throw(
			_(
				"Someone else changed the desk apps since you opened this. Close it and open it "
				"again to see their changes."
			),
			frappe.TimestampMismatchError,
			title=_("Changed Meanwhile"),
		)


def _dock(module_sidebars: dict | None = None, app_data: list[dict] | None = None) -> list[dict]:
	"""Every app the dock could list, hidden ones included, in dock order.

	`app_data` is Frappe's answer for this user (`frappe.boot.get_app_data`), which nothing an
	editor saves changes: a save asks for it once and hands it to every step, rather than have
	each step rebuild it. The dock itself is read again after each write, since it is what the
	writes change.
	"""
	return nav.desk_apps(module_sidebars=module_sidebars, app_data=app_data, everything=True)


def _parse(items) -> list[dict]:
	"""An editor's rows: a list of objects, sent as JSON or as the list itself."""
	try:
		rows = json.loads(items) if isinstance(items, str) else (items or [])
	except ValueError:
		rows = None
	if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
		frappe.throw(_("The editor sent rows this cannot read."), frappe.ValidationError)
	return rows


# ------------------------------------------------------------------------------------
# Manage Desk Apps
# ------------------------------------------------------------------------------------


@frappe.whitelist()
def get_dock() -> dict:
	"""The apps, in dock order, as the dock editor lists them, and the `stamp` its save brings back.

	Each with its Apps Screen setting and, for every setting it could have, the tiles
	that setting draws (`screen`), by the same rule the Apps screen is arranged by
	(`apps_screen.plan`): so the editor's preview of the Apps screen is never a guess.
	"""
	_check()
	from frappe.boot import get_app_data, get_icon_style, get_module_sidebars

	app_data = get_app_data()
	module_sidebars = get_module_sidebars()
	asked = {entry["app_name"] for entry in app_data if entry.get("on_apps_screen")}
	routes = {entry["app_name"]: entry.get("app_route") for entry in app_data}
	style = get_icon_style()
	apps = [
		{
			"key": app["key"],
			"title": app["title"],
			"icon": app.get("icon"),
			"logo": app.get("logo"),
			"hidden": bool(app.get("hidden")),
			"unlisted": bool(app.get("unlisted")),
			"roles": app.get("roles") or [],
			"configured": bool(app.get("configured")),
			"module_count": len(app.get("modules") or []),
			# An app Frappe does not list holds nothing while its modules are in Other: what it
			# would hold, and draw, once the editor shows it, so the editor can say so before Save.
			**(_shown_preview(app, asked, routes, module_sidebars, style) if app.get("unlisted") else {}),
			"apps_screen": app.get("apps_screen") or apps_screen.DEFAULT,
			"screen": {
				mode: _preview_tiles(
					app,
					apps_screen.plan(app, mode, asked, routes.get(app["app_name"])),
					module_sidebars,
					style,
				)
				for mode in apps_screen.MODES
			},
		}
		for app in _dock(module_sidebars, app_data)
	]
	return {"apps": apps, "stamp": records_stamp()}


def _shown_preview(app: dict, asked: set, routes: dict, module_sidebars: dict, style: str | None) -> dict:
	shown = {**app, "modules": app.get("own_modules") or []}
	return {
		"own_module_count": len(shown["modules"]),
		"own_screen": {
			mode: _preview_tiles(
				shown,
				apps_screen.plan(shown, mode, asked, routes.get(app["app_name"])),
				module_sidebars,
				style,
			)
			for mode in apps_screen.MODES
		},
	}


def _preview_tiles(app: dict, tiles: list[tuple], module_sidebars: dict, style: str | None) -> list[dict]:
	"""Tiles as the editor's preview draws them: a label and the picture the Apps screen would show."""
	preview = []
	for kind, item in tiles:
		if kind == "app":
			preview.append({"label": app["title"], "logo": app.get("logo"), "icon": app.get("icon")})
		elif kind == "frontend":
			preview.append({"label": item["label"], "logo": app.get("logo"), "icon": "external-link"})
		else:
			picture = item.get("desktop_image") or module_tiles.picture(
				item.get("icon"),
				((module_sidebars or {}).get(item["shell"]) or {}).get("app") or app.get("installed_app"),
				style,
				app.get("color"),
			)
			preview.append({"label": item["label"], "logo": picture, "icon": item.get("icon")})
	return preview


@frappe.whitelist(methods=["POST"])
def save_dock(items: str | list, stamp: str | None = None) -> dict:
	"""Store the dock's order, which apps are off it, and how each shows on the Apps screen.

	`items` is every app, in order, each with `hidden` and `apps_screen`.

	An item marked `new` is an app the editor added: it is made here, as a Desk App of
	its own, and stands in the order where the editor put it. Its `modules`, if the editor
	gave it any, are the rows Manage Modules drafted for it, stored as that editor's own
	save would (`_store_app_modules`), new modules included. Their keys come back under
	`created`.

	`stamp` is what `get_dock` handed the editor: refused if the records have moved on since.
	"""
	_check()
	_check_stamp(stamp)
	items = _parse(items)
	from frappe.boot import get_app_data, get_module_sidebars

	# Built once for the whole save: both are Frappe's, and nothing saved here changes them.
	module_sidebars = get_module_sidebars()
	app_data = get_app_data()
	created = []
	for item in items:
		if not item.get("new"):
			continue
		title = (item.get("title") or "").strip()
		if not title:
			frappe.throw(_("A new app needs a title."))
		if frappe.db.exists(APP, title):
			frappe.throw(_("There is already a Desk App called {0}.").format(frappe.bold(title)))
		doc = frappe.get_doc(
			{
				"doctype": APP,
				"title": title,
				"icon": item.get("icon") or None,
				"enabled": 1,
				"module_mode": nav.ADD,
			}
		).insert()
		item["key"] = f"desk-app:{doc.name}"
		created.append(item["key"])
		if item.get("modules"):
			# The order is written once, below, for every app: not after each new one too.
			module_sidebars = _store_app_modules(
				item["key"], _parse(item["modules"]), app_data, store_order=False
			)

	dock = _dock(module_sidebars, app_data)
	known = {app["key"] for app in dock}
	# Each app once, where the editor first put it.
	keys = list(dict.fromkeys(item["key"] for item in items if item.get("key") in known))
	# An app the editor did not list (installed since it opened) keeps its place at the end.
	keys += [app["key"] for app in dock if app["key"] not in keys]
	hidden = {item["key"] for item in items if item.get("hidden") and item.get("key") in known}
	screens = {
		item["key"]: item["apps_screen"]
		for item in items
		if item.get("key") in known and item.get("apps_screen") in apps_screen.MODES
	}
	_store_order(dock, keys, hidden, screens, app_data)
	return {**payload(module_sidebars, app_data), "created": created}


def _store_order(
	dock: list[dict],
	keys: list[str],
	hidden: set[str],
	screens: dict[str, str] | None = None,
	app_data: list[dict] | None = None,
) -> None:
	"""Write `keys` as the dock order, `hidden` as the apps off it, and `screens` as each
	app's Apps Screen setting, onto records.

	As few apps as possible are anchored; see `anchors_for`. An app the editor leaves
	off the dock keeps the setting it had: it has no tiles either way, and for an app
	whose modules are in Other by default a record to hold one would take them off it.
	"""
	screens = screens or {}
	if app_data is None:
		from frappe.boot import get_app_data

		app_data = get_app_data()

	by_key = {app["key"]: app for app in dock}
	listed = {*nav.listed_apps(), nav.OTHER}
	defaults = [f"app:{name}" for name in [*nav.active_apps(), nav.OTHER]]
	anchors = positions(keys, by_key, hidden, listed, defaults)
	meta = nav.apps_from_app_data(app_data)[0]

	for key in keys:
		app = by_key[key]
		anchor = anchors[key]
		is_hidden = 1 if key in hidden else 0
		current = app.get("apps_screen") or apps_screen.DEFAULT
		screen = current if is_hidden else screens.get(key, current)
		# An unlisted app is off the dock by default, so only bringing it back needs a record.
		if (
			not app.get("record")
			and not anchor
			and is_hidden == int(bool(app.get("unlisted")))
			and screen == apps_screen.DEFAULT
		):
			continue
		doc = _record_for(app)
		changed = (
			doc.is_new()
			or (doc.dock_after or None) != anchor
			or int(doc.hidden or 0) != is_hidden
			or (doc.apps_screen or apps_screen.DEFAULT) != screen
		)
		doc.dock_after = anchor
		doc.hidden = is_hidden
		doc.apps_screen = screen
		target = doc.installed_app
		# For an unlisted app a bare, shown record is what puts it on the dock, so it stays.
		if _is_placeholder(
			doc,
			nav.OTHER if target == nav.OTHER else (meta.get(target) or {}).get("title"),
			hidden_by_default=target not in listed,
		):
			if not doc.is_new():
				frappe.delete_doc(APP, doc.name)
		elif changed:
			doc.save()


def positions(
	keys: list[str], by_key: dict[str, dict], hidden: set[str], listed: set[str], defaults: list[str]
) -> dict[str, str | None]:
	"""What each app in `keys` follows on the dock (`anchors_for`), leaving out the apps not on it.

	An app Frappe does not list (`listed`, which holds Other too), kept hidden, is not on the dock
	at all: its modules are under Other. Its place there means nothing, and a place is something its
	record would hold -- enough to keep that record, which, hidden, would take the app's modules off
	the dock altogether instead of leaving them in Other. So it follows nothing, and nothing follows
	it.
	"""
	off = {key for key in keys if key in hidden and _is_unlisted(by_key[key], listed)}
	placed = [key for key in keys if key not in off]
	anchors = anchors_for(placed, defaults, {key for key in placed if by_key[key].get("record")})
	return {**anchors, **dict.fromkeys(off)}


def _is_unlisted(app: dict, listed: set[str]) -> bool:
	"""Whether a dock app stands for an installed app Frappe does not list as somewhere to go."""
	target = app.get("installed_app")
	return bool(target) and target not in listed


def anchors_for(keys: list[str], defaults: list[str], with_record: set[str]) -> dict[str, str | None]:
	"""What each app in `keys` follows on the dock so that it reads `keys`: None for its default place.

	The longest run of apps still in their default order stays unanchored
	(`_unmoved`), and each of the rest follows the app before it in `keys`, or the
	top. `desk_apps.dock_sequence` turns this back into `keys`.
	"""
	stay = _unmoved(keys, defaults, with_record)
	return {
		key: None if key in stay else (keys[index - 1] if index else nav.TOP)
		for index, key in enumerate(keys)
	}


def _unmoved(keys: list[str], defaults: list[str], with_record: set[str]) -> set[str]:
	"""The apps of `keys` that can stay unanchored: a run in default order, chosen to anchor as few as it can.

	The heaviest increasing subsequence by default position. An app without a record
	weighs far more than one with, since anchoring it means making a record for it.
	"""
	rank = {key: i for i, key in enumerate(defaults)}
	candidates = [key for key in keys if key in rank]
	weight = [1 if key in with_record else 1000 for key in candidates]
	best = list(weight)
	previous: list[int | None] = [None] * len(candidates)
	for i, key in enumerate(candidates):
		for j in range(i):
			if rank[candidates[j]] < rank[key] and best[j] + weight[i] > best[i]:
				best[i], previous[i] = best[j] + weight[i], j
	stay: set[str] = set()
	at = max(range(len(candidates)), key=best.__getitem__, default=None)
	while at is not None:
		stay.add(candidates[at])
		at = previous[at]
	return stay


def _is_placeholder(doc, default_title: str | None, hidden_by_default: bool = False) -> bool:
	"""Whether a record stands for an installed app and says nothing about it but that.

	What `_record_for` makes for an app that only needed a position: bound, enabled,
	under the app's own title, in Add mode, with no position, modules, roles, mark or
	frontend of its own, and as visible as the app is without a record -- shown, or for an
	app Frappe does not list (`hidden_by_default`), off the dock with its modules in Other.
	A hidden record for such an app would instead take its modules off the dock altogether,
	so taking it off again is going back to no record.
	"""
	return bool(
		doc.installed_app
		and doc.enabled
		and bool(doc.hidden) == hidden_by_default
		and not doc.dock_after
		and (doc.module_mode or nav.ADD) == nav.ADD
		and not doc.modules
		and not doc.roles
		and not (doc.icon or doc.logo or doc.color or doc.frontend_url or doc.frontend_label)
		and (doc.apps_screen or apps_screen.DEFAULT) == apps_screen.DEFAULT
		and doc.title == (default_title or doc.installed_app)
	)


def _record_for(app: dict):
	"""The Desk App behind a dock app, made bound to its installed app if it has none.

	Records are named by their title, and the app's title may already be taken -- by a
	disabled record kept for later, say -- so a new one takes the first free variant
	("ERPNext (erpnext)", then numbered).
	"""
	if app.get("record"):
		return frappe.get_doc(APP, app["record"])
	# `new_doc`, not `get_doc` of a dict: only the first marks the record new, and the save in
	# `_store_order` writes a new record whatever it holds -- one bringing an unlisted app back
	# differs from no record only by existing.
	doc = frappe.new_doc(APP)
	doc.update(
		{
			"title": _free_title(app["title"], app["installed_app"]),
			"installed_app": app["installed_app"],
			"enabled": 1,
			"module_mode": nav.ADD,
		}
	)
	return doc


def _free_title(title: str, installed_app: str | None) -> str:
	if not frappe.db.exists(APP, title):
		return title
	base = f"{title} ({installed_app})" if installed_app and installed_app != title else title
	candidate, n = base, 2
	while frappe.db.exists(APP, candidate):
		candidate, n = f"{base} {n}", n + 1
	return candidate


# ------------------------------------------------------------------------------------
# Manage Modules
# ------------------------------------------------------------------------------------


@frappe.whitelist()
def get_app_modules(key: str) -> dict:
	"""One app's module list as its editor shows it.

	`rows` is the list as the dock draws it -- each Category and Spacer a row of its
	own -- and then, taken off, the installed app's own modules it no longer lists.
	A module row names its Module Def and what the dock calls it, which is its
	sidebar's label: the editor renames Categories, not modules.
	"""
	_check()
	from frappe.boot import get_module_sidebars

	module_sidebars = get_module_sidebars()
	dock = _dock(module_sidebars)
	app = next((a for a in dock if a["key"] == key), None)
	if not app:
		frappe.throw(_("{0} is not on the dock.").format(frappe.bold(key)))

	rows, listed = [], set()
	for entry in app["modules"]:
		if entry.get("category"):
			rows.append({"kind": "category", "label": entry["category"]})
		elif entry.get("space_before"):
			rows.append({"kind": "spacer"})
		module = (module_sidebars.get(entry["shell"]) or {}).get("module") or entry["shell"]
		if module in listed:
			continue
		listed.add(module)
		rows.append(
			{
				"kind": "module",
				"module": module,
				"label": entry["label"],
				"icon": entry.get("icon"),
			}
		)

	# An installed app's (or Other's) own modules it does not list: taken off by Replace, or
	# hidden by the app's Dock.
	target = app.get("installed_app")
	if target:
		# Modules another app lists are that app's to give up, not this one's to take back.
		holders = {m["shell"] for other in dock if other is not app for m in other["modules"]}
		owner = _owner_of(module_sidebars)
		for shell, sidebar in module_sidebars.items():
			module = sidebar.get("module") or shell
			if module in listed or shell in holders or owner(module) != target:
				continue
			listed.add(module)
			rows.append(
				{
					"kind": "module",
					"module": module,
					"label": sidebar.get("label") or shell,
					"icon": sidebar.get("header_icon"),
					"hidden": True,
				}
			)

	return {"title": app["title"], "installed_app": target, "rows": rows, "stamp": records_stamp()}


@frappe.whitelist(methods=["POST"])
def save_app_modules(key: str, items: str | list, stamp: str | None = None) -> dict:
	"""Store one app's module list. `items` is every row, in order, each marked if taken off.

	What the editor was not shown is kept: a row naming a module the person editing cannot
	open (or one whose app is not installed just now) stays where it was, and so does each
	row's Apps Screen Image, which the editor does not carry.

	Taking one of an installed app's own modules off its list switches the record to
	Replace, which sends it to Other -- unless its Dock hides it, which already keeps
	it off the dock. Putting such a module back lists it. Other has nowhere further to send a module, so its
	list is only ever ordered and labelled: nothing is taken off it. A module that came
	from another app is simply released, back to that app, without changing the mode.

	`stamp` is what `get_app_modules` handed the editor: refused if the records have moved on.
	"""
	_check()
	_check_stamp(stamp)
	from frappe.boot import get_app_data

	app_data = get_app_data()
	return payload(_store_app_modules(key, _parse(items), app_data), app_data)


def _store_app_modules(
	key: str, items: list[dict], app_data: list[dict] | None = None, store_order: bool = True
) -> dict:
	"""`save_app_modules`, for Manage Desk Apps' save as well: returns the `module_sidebars` it ends on.

	`store_order` keeps the dock's order as it was, which a new record could otherwise move;
	Manage Desk Apps' save leaves it out, since it writes the whole order itself afterwards.
	"""
	from frappe.boot import get_app_data, get_module_sidebars

	if app_data is None:
		app_data = get_app_data()
	module_sidebars = get_module_sidebars()
	dock = _dock(module_sidebars, app_data)
	app = next((a for a in dock if a["key"] == key), None)
	if not app:
		frappe.throw(_("{0} is not on the dock.").format(frappe.bold(key)))
	# An app Frappe lists nowhere, still hidden: the record saved here would be a hidden one that
	# claims these modules, and they would leave the dock with it, for everyone.
	if app.get("unlisted") and app.get("hidden"):
		frappe.throw(
			_("Show {0} on the dock and save first, then manage its modules.").format(
				frappe.bold(app.get("title") or key)
			)
		)
	target = app.get("installed_app")

	if _make_new_modules(items):
		# Frappe's answer now has them: each new module gets its own Home workspace, which
		# is what puts it in `module_sidebars`.
		module_sidebars = get_module_sidebars()
		dock = _dock(module_sidebars, app_data)
		app = next(a for a in dock if a["key"] == key)

	# The order the dock has now, held before a new record could move this app.
	order = [a["key"] for a in dock]
	hidden_apps = {a["key"] for a in dock if a.get("hidden")}

	visible = {sidebar.get("module") or shell for shell, sidebar in module_sidebars.items()}
	owner = _owner_of(module_sidebars)
	# Loaded once: its rows are read here, and the same document is saved below.
	doc = _record_for(app)
	old_rows = list(doc.modules)
	dock_hidden = set((nav._site_inputs()["docks"].get(target) or {}).get("hidden") or ())
	dock_hidden = {
		sidebar.get("module") or shell for shell, sidebar in module_sidebars.items() if shell in dock_hidden
	}
	images = {row.module: row.desktop_image for row in old_rows if row.module and row.get("desktop_image")}

	rows, taken_off = [], False
	for item in items:
		kind = item.get("kind")
		hidden = item.get("hidden") and target != nav.OTHER
		if hidden:
			module = item.get("module")
			if kind == "module" and target and owner(module) == target and module not in dock_hidden:
				taken_off = True
			continue
		if kind == "module" and item.get("module"):
			rows.append(
				{
					"type": nav.MODULE,
					"module": item["module"],
					"desktop_image": images.get(item["module"]),
				}
			)
		elif kind == "category" and (item.get("label") or "").strip():
			rows.append({"type": nav.CATEGORY, "label": item["label"].strip()})
		elif kind == "spacer":
			rows.append({"type": nav.SPACER})

	rows = _keep_unseen(rows, old_rows, visible)

	if target:
		taken_off = taken_off or _leaves_out_unseen(doc.module_mode, target, rows, visible)
		doc.module_mode = nav.REPLACE if taken_off else nav.ADD
	doc.set("modules", rows)
	doc.save()

	if store_order:
		_store_order(_dock(module_sidebars, app_data), order, hidden_apps, app_data=app_data)
	return module_sidebars


def _leaves_out_unseen(mode: str | None, target: str, rows: list[dict], visible: set[str]) -> bool:
	"""Whether a Replace record leaves out one of its app's own modules the editor did not show.

	The editor lists only what the person editing can open, so it cannot say whether one of the
	others was taken off. Replace sends such a module to Other now; a save that never showed it
	must not bring it back (which switching to Add would, for everyone).
	"""
	if mode != nav.REPLACE or target == nav.OTHER:
		return False
	hosts = nav.app_hosts()
	seen = {frappe.scrub(module) for module in visible}
	seen |= {frappe.scrub(row["module"]) for row in rows if row.get("module")}
	return any(
		hosts.get(app, app) == target and module not in seen
		for module, app in nav._site_inputs()["module_apps"].items()
	)


def _make_new_modules(items: list[dict]) -> list[str]:
	"""Make the modules the editor added as new: custom Module Defs, of no app.

	A module of no app belongs to the site, as the ones made on the Module Def form do;
	the Desk App listing it is what places it on the dock. Frappe gives each a Home
	workspace of its own when it is made.
	"""
	names = []
	for item in items:
		if item.get("kind") != "module" or not item.get("new") or item.get("hidden"):
			continue
		name = (item.get("module") or "").strip()
		if not name:
			frappe.throw(_("A new module needs a name."))
		if frappe.db.exists("Module Def", name):
			frappe.throw(
				_("There is already a module called {0}. Add it as a Module instead.").format(
					frappe.bold(name)
				)
			)
		frappe.has_permission("Module Def", "create", throw=True)
		frappe.get_doc({"doctype": "Module Def", "module_name": name, "custom": 1}).insert()
		item["module"] = name
		names.append(name)
	return names


def _owner_of(module_sidebars: dict):
	"""A function from a module to the installed app it belongs to by default, or Other."""
	module_apps = nav._site_inputs()["module_apps"]
	installed = set(nav.active_apps())
	hosts = nav.app_hosts()
	app_by_module = {}
	for shell, sidebar in module_sidebars.items():
		module = sidebar.get("module") or shell
		app_by_module.setdefault(module, sidebar.get("app"))

	def owner(module: str | None) -> str | None:
		if not module:
			return None
		return nav.default_app_of(app_by_module.get(module), module, module_apps, hosts, installed)

	return owner


def _keep_unseen(rows: list[dict], old_rows: list, visible: set[str]) -> list[dict]:
	"""Put back each old row for a module the editor did not show, after the row it followed."""
	result = list(rows)
	previous = None
	for row in old_rows:
		if row.module and row.module not in visible:
			kept = {
				"type": nav.MODULE,
				"module": row.module,
				"desktop_image": row.get("desktop_image"),
			}
			at = next(
				(i + 1 for i, r in enumerate(result) if previous and r.get("module") == previous),
				0 if previous is None else len(result),
			)
			result.insert(at, kept)
		if row.module:
			previous = row.module
	return result


# ------------------------------------------------------------------------------------
# What the desk redraws from
# ------------------------------------------------------------------------------------


def payload(module_sidebars: dict | None = None, app_data: list[dict] | None = None) -> dict:
	"""The dock and the Apps screen, as the boot would carry them now.

	So an editor's save is redrawn in place: `desk_apps`, `app_data` as the
	Apps screen arranges it, and `module_sidebars` and `workspaces`, which have any module
	just made and the Home workspace Frappe made for it -- without the second, the desk's
	router would not know the new module's page until a reload. The browser places each
	module in its dock app from the dock itself (`js/boot_arrangement.js`).
	"""
	from frappe.boot import get_app_data, get_module_sidebars

	if module_sidebars is None:
		module_sidebars = get_module_sidebars()
	# The save's own copy, if it has one, which this is the last to read: the Apps screen's
	# arrangement below rewrites it in place.
	if app_data is None:
		app_data = get_app_data()
	# Read before the Apps screen rewrites `app_data`, as in the boot.
	dock = nav.desk_apps(module_sidebars=module_sidebars, app_data=app_data)
	# The Apps screen as the boot would arrange it, or the desk's copy would be Frappe's.
	if apps_screen.enabled():
		from frappe.boot import get_icon_style

		apps_screen.arrange(app_data, dock, style=get_icon_style(), module_sidebars=module_sidebars)
	from frappe.desk.desktop import get_workspaces

	return {
		"desk_apps": dock,
		"app_data": app_data,
		"module_sidebars": module_sidebars,
		"workspaces": get_workspaces(),
		# Where the records stand after this save, for an editor still open over them.
		"stamp": records_stamp(),
	}
