# Copyright (c) 2026, Peter and contributors
# For license information, please see license.txt

"""Every name in Frappe that Open Desk hangs on, still there.

What it checks: the sidebar classes the dock patches and reads, the arrangement editor
`js/arrange.js` extends, the classes `scss/dock.scss` styles, the Apps screen's tiles
(which the dock opens a module list from and `apps_screen.py` arranges), the icon
sprites `module_tiles.py` reads, and -- for the two Dock methods the dock replaces
outright rather than wraps -- that Frappe's own have not changed since the dock was
written against them.

The desk half (`js/dock.js`, `js/user_menu.js`, `js/arrange.js`,
`js/boot_arrangement.js`, `public/js/user_menu_rows.js`) patches Frappe's
sidebar classes and reads their properties, markup and menu rows. In the
browser, a missing method switches the dock off and a changed one makes it give
up (`patch` in the dock), so a Frappe upgrade costs the dock, not the desk --
but quietly. This reads Frappe's own source instead, so the run after
`bench update` says which name moved, before anyone opens the desk.

A failure here is not a broken desk. It is the list of what to look at in
Frappe's diff before shipping the upgrade.

To check a Frappe before pulling it, point `OPENDESK_FRAPPE_SOURCE` at a copy of its
source (the directory holding `frappe/`), for instance one made with
`git -C apps/frappe archive upstream/version-16-hotfix frappe | tar -x -C /tmp/frappe-next`:

    OPENDESK_FRAPPE_SOURCE=/tmp/frappe-next ../env/bin/python -m unittest \
        opendesk.open_desk.test_frappe_seams

Python names are then looked for in that source rather than imported.
"""

import os
import re
from unittest import TestCase

import frappe

JS = ("public", "js", "frappe")

# Per file: methods defined there, `this.<property>` it sets, and strings (classes,
# row names, globals) it carries.
SEAMS = {
	("ui", "sidebar", "sidebar.js"): {
		"methods": [
			"dock_enabled",
			"open_module",
			"setup",
			"set_workspace_sidebar",
			"add_item",
			"empty",
			"open",
			"refresh_header",
			# An Apps screen tile's landing page, which the dock matches a click to (`js/dock.js`).
			"app_landing_route",
			"refresh_dock",
			"create_user_menu",
			# Kept from shutting the drawer when a module is picked in it, below 768px.
			"restore_expanded_state",
			"panel_can_close",
			# The module column redraws with the sidebar's visibility.
			"apply_page_visibility",
			"toggle",
			# Accordion Sidebar puts the rows it draws under the open module's heading.
			"make_sidebar",
			# Open Last Sidebar Item opens the module, then routes to the row's page.
			"select_shell",
			# And notes the row Frappe lit.
			"find_active_item",
		],
		"properties": [
			"$items_container",
			"wrapper",
			"current_module",
			"sidebar_expanded",
			"sidebar_header",
			"dock",
			"active_item",
		],
		"strings": [
			"workspace-selector",
			"navbar-modal-search-mobile",
			"sidebar-notification",
			"notification-count",
			"standard-items-band",
			"frappe.get_module_icon =",
			'frappe.router.on("change"',
			# The drawer closing below 768px, which hides the dock's tooltips.
			'trigger("sidebar-expand"',
		],
	},
	("ui", "sidebar", "dock.js"): {
		# `should_pin` is wrapped and `apply_pin` called for the dock in the drawer below 768px.
		"methods": [
			"make",
			"render_entries",
			"render_logo",
			"name_tile",
			"close",
			"refresh",
			"should_pin",
			"apply_pin",
			# Other apps' tiles join Frappe's Search and Notifications on the dock.
			"render_utilities",
			"make_utility",
		],
		"properties": [
			"sidebar",
			"$dock",
			"$items",
			"tooltips",
			"$header",
			"$header_logo",
			"$header_title",
			"is_pinned",
			"enabled",
			"rendered",
			"header_tooltip",
			"utility_tooltips",
		],
		"strings": [
			"frappe.ui.Dock =",
			"static pointer_can_reveal()",
			"dock-user",
			"dock-item",
			"dock-item-icon",
			"dock-item-label",
			"es-tooltip--plain",
			# Where Frappe shows Search and Notifications on the dock, and the class saying it does.
			"dock-utilities",
			"dock-owns-utilities",
		],
	},
	("ui", "sidebar", "sidebar_header.js"): {
		"methods": [
			"menu_items",
			"all_apps_item",
			"system_items",
			"navbar_items",
			"get_help_siblings",
			"refresh",
			# The Module Menu opens the header's own menu.
			"setup_menu",
		],
		"properties": ["wrapper", "$header_title", "$header_logo", "$drop_icon", "sidebar", "menu"],
		"strings": [
			"frappe.ui.SidebarHeader =",
			"switch-module",
			"switch-app",
			"all-apps",
			# The Sliding Sidebar's corner button does what Frappe's Edit Sidebar row does.
			"edit-sidebar",
			"arrangement_editor.bundle.js",
			"new frappe.ui.SidebarManager()",
		],
	},
	("ui", "sidebar", "sidebar_header.html"): {"strings": ["title-container"]},
	("ui", "sidebar", "sidebar_item.js"): {
		"strings": [
			"frappe.ui.sidebar_item.TypeButton =",
			"TypeSpacer",
			"section-break",
			"standard-sidebar-item",
		],
	},
	# The last: the dock escapes what it puts in a row, because the template prints labels as HTML.
	("ui", "sidebar", "sidebar_item.html"): {
		"strings": ["sidebar-item-container", "item-anchor", "sidebar-item-label", "{{ item.label }}"],
	},
	("ui", "sidebar", "sidebar_panel.js"): {
		"strings": ["frappe.ui.SidebarPanel =", "frappe.ui.sidebar_panels =", "toggle(name)"],
	},
	# `js/arrange.js` subclasses it: the methods it overrides or calls, and the fields it reads.
	("ui", "sidebar", "arrangement_editor.js"): {
		"methods": [
			"layers",
			"prepare",
			"title",
			"save_args",
			"can_add",
			"add",
			"apply",
			"copy",
			"reset",
			"is_own_add",
			"item_extras",
			"item_classes",
			"decorate_item",
			"entry_icon",
			"preview_item",
			"visibility_button",
			"hide_tooltip",
			"arranged_rows",
			"arrange",
			"render_panes",
			# Manage Desk Apps draws its preview switch over `render`, and the Apps screen in the preview.
			"render",
			"render_preview",
			"selection",
			# Read on open, saved on Save, and the order taken from the rows before either save.
			"read",
			"save",
			"sync_order",
			# Manage Modules' New Module button.
			"extra_pane_actions",
		],
		"properties": [
			"entries",
			"order",
			"hidden",
			"can_curate_site",
			"layer_config",
			"loaded",
			"dialog",
			"$body",
			"$preview",
		],
		"strings": [
			"frappe.ui.ArrangementEditor =",
			# The layer each editor declares: Frappe calls its `save` and shows its `saved()`.
			"this.layer_config.save",
			"this.layer_config.saved()",
		],
	},
	# The Module Menu opens and closes the header's menu, and chains onto its `opts.on_close`.
	("ui", "components", "dropdown.js"): {
		"methods": ["open", "close", "is_open"],
		"properties": ["opts"],
		"strings": ["frappe.ui.Dropdown =", "this.opts.on_close && this.opts.on_close(reason)"],
	},
	# Manage Desk Apps' Apps Screen menu marks the current choice; the rows' labels are text.
	("ui", "components", "menu.js"): {
		"strings": ["item.selected", "textContent", '"es-menu"', 'panel.setAttribute("role", "menu")']
	},
	# An Apps screen tile: where it leads, and the two links the dock recognises it by.
	("ui", "desktop_icon.html"): {"strings": ['class="icon-link"', 'class="icon-title"', "icon.logo_url"]},
	("utils", "utils.js"): {"methods": ["app_logo", "desktop_icon", "sidebar_for_module"]},
	# The dock's own tips and its mark's, destroyed when it redraws or gives up.
	("ui", "components", "tooltip.js"): {"methods": ["destroy"], "strings": ["frappe.ui.Tooltip ="]},
	# The dock's Search and bell are Frappe's, found by class: Search opens from a delegated click
	# on the class, the bell's panel answers to its trigger, and every count on the page is filled.
	("ui", "page.js"): {"strings": ['awesome_bar.setup(".navbar-modal-search-mobile")']},
	# The dock waits for the routed page to be on screen before reading its sidebar: Frappe
	# announces the page, then shows or hides the sidebar for it (`once_page_shows`).
	("views", "container.js"): {
		"strings": ['$(document).trigger("page-change", this.page);', "this.toggle_sidebar();"]
	},
	("ui", "toolbar", "awesome_bar.js"): {"strings": ['$(document).on("click", element']},
	("ui", "notifications", "notifications.js"): {
		"strings": [
			'name: "notifications"',
			'trigger_selector: ".sidebar-notification"',
			'$(".notification-count")',
		]
	},
	# Frappe replaces the boot's copies wholesale after a sidebar or workspace save, and
	# `js/boot_arrangement.js` places the modules again on each such assignment. A copy changed in
	# place instead would leave the desk naming Frappe's apps until a reload.
	("ui", "sidebar", "sidebar_manager.js"): {"strings": ["frappe.boot.module_sidebars = "]},
	("views", "workspace", "workspace.js"): {
		"strings": ["frappe.boot.module_sidebars = ", "frappe.boot.app_data = "]
	},
}

# What a method does inside, where its name alone says too little. Read from the method's body.
# A tuple is a choice: any one of its strings will do, where Frappe's versions differ harmlessly.
METHOD_BODIES = {
	("ui", "sidebar", "sidebar.js"): {
		# The dock keeps its own copy of this click-away, letting through a pick that rebuilt the
		# drawer (`js/dock.js`): a change here is a change to copy there. 16.60 dropped the page
		# head's drawer button from the selector; the copy keeps it, matching nothing there.
		"setup_click_away": [
			'.off(".sidebar-click-away")',
			'"click.sidebar-click-away"',
			"if (!this.sidebar_expanded || !this.panel_can_close()) return;",
			(
				'".body-sidebar, .dock, .sidebar-toggle-btn, .sidebar-panel, .sidebar-collapse-arrow"',
				'".body-sidebar, .dock, .sidebar-panel, .sidebar-collapse-arrow"',
			),
			"this.close();",
		],
	},
	("ui", "sidebar", "dock.js"): {
		# The pair Frappe puts on the dock, carrying the classes search and the bell's panel answer
		# to; their unread count is the badge `scss/dock.scss` draws as a number.
		"render_utilities": ["navbar-modal-search-mobile", "sidebar-notification", "notification-count"],
		# Other apps' tiles are made with it: escaped label, raw classes and badge, tip kept apart.
		"make_utility": [
			'make_utility({ label, icon, css_class, badge = "" })',
			"${css_class}",
			"${badge}",
			"this.name_tile($item, label, this.utility_tooltips);",
		],
	},
}

# The sidebar's standard items, by class: Frappe draws these on a pinned dock too, and Open Desk
# hides the band beside it (`scss/dock.scss`). Anything else Frappe puts in the band would be out
# of reach. 16.60 adds Flow, which it draws on the dock as well (`render_utilities`).
STANDARD_ITEMS = (
	{"navbar-modal-search-mobile", "sidebar-notification hidden"},
	{"navbar-modal-search-mobile", "sidebar-notification hidden", "sidebar-flow"},
)

# Classes `scss/dock.scss` styles ahead of the Frappe that draws them, by the Frappe folder whose
# presence says it does: harmless where absent, and looked for wherever that folder is.
LATER_CLASSES = {"sidebar-flow": ("flow",)}

# The phone's tab bar and navigation sheet (16.60): what `js/dock.js` patches in it, and the Dock
# rows its sheet reads (`js/boot_arrangement.js`). Checked only where Frappe has it.
MOBILE_NAV = ("ui", "mobile_nav.js")
MOBILE_NAV_SEAMS = [
	"frappe.ui.MobileNav = class",
	"open_navigation() {",
	"render_dock($dock) {",
	"collect_dock_entries(sidebar.get_sidebar_app())",
	"$items_container.appendTo",
	"desk-mobile-sheet-dock-item",
	"this.sheet.set_title(",
	"module_label(module) {",
	"close_sheet() {",
	"frappe.ui.mobile_nav = new frappe.ui.MobileNav();",
]

# Frappe 16.60's Studio apps, which `apps_screen.fold_studio_apps` makes tiles of as Frappe's
# browser half does. Checked only where the boot sends them.
STUDIO_SEAMS = {
	("boot.py",): ["bootinfo.studio_apps = get_desktop_apps()"],
	("public", "js", "frappe", "utils", "utils.js"): [
		"(frappe.boot.studio_apps || [])",
		"app_name: app.name",
		"app_title: app.app_title",
		"app_route: `/${app.route}`",
		"app_logo_url: app.favicon",
	],
	("studio", "doctype", "studio_app", "studio_app.py"): [
		".select(StudioApp.name, StudioApp.app_title, StudioApp.route, StudioApp.favicon)"
	],
}

# The boot data the server half reads, by the source that shapes it.
PYTHON_SEAMS = {
	# Each `module_sidebars` entry (`desk_apps._shells`, `arrange.py`, `js/boot_arrangement.js`).
	("desk", "doctype", "sidebar", "sidebar.py"): [
		'"name": self.name',
		'"module": self.module',
		'"label": self.label',
		'"app": self.app',
		'"header_icon": self.header_icon',
	],
	# Each `app_data` entry (`desk_apps.apps_from_app_data`, `apps_screen.py`, the dock).
	("boot.py",): [
		"on_apps_screen=",
		"sequence_id=",
		"app_name=",
		"app_title=",
		"app_route=",
		"desk_route=",
		"app_logo_url=",
		"dock=",
		# Module tiles take the Apps screen's icon style.
		"bootinfo.desktop_icon_style =",
		# Frappe's own map of module to app, which `desk_apps.module_apps` asks for by name. A boot
		# that builds it some other way may leave out what this function still puts in.
		"bootinfo.module_app = get_boot_module_app()",
	],
	# The arrangement applies only where the desktop is the Apps screen (`apps_screen.enabled`).
	("desk", "doctype", "desktop_settings", "desktop_settings.py"): ['APPS = "Apps"'],
}

# Fields the server half reads off Frappe's doctypes, by the doctype's schema.
DOCTYPE_FIELDS = {
	# An app's shipped Dock, read row by row (`desk_apps.shipped_docks`).
	("desk", "doctype", "dock_item", "dock_item.json"): ["link_type", "link_to", "hidden"],
	# The dock's mark (`desk_apps.site_logo`).
	("website", "doctype", "website_settings", "website_settings.json"): ["app_logo"],
	("core", "doctype", "navbar_settings", "navbar_settings.json"): ["app_logo"],
}

# Icons Open Desk draws by a name it works out rather than writes in the call.
COMPUTED_ICONS = ["chevrons-left", "chevrons-right", "box", "folder", "square"]

# The dock's drawers open over the sidebar, one above its z-index.
SCSS_SEAMS = {("desk", "sidebar.scss"): ["z-index: 1020"]}

# Where Frappe's own classes may be defined or drawn: its stylesheets and the sidebar's scripts
# and templates.
CLASS_SOURCES = [("public", "scss"), ("public", "js", "frappe", "ui", "sidebar")]

# The Apps screen page: the container its tiles are in, and the rule for where each leads.
DESKTOP_SEAMS = {
	("desk", "page", "desktop", "desktop.js"): [
		'find(".desktop-container")',
		"app_landing_route(app)",
		# Manage Desk Apps in the Apps screen's avatar menu, and the screen redrawn after a save
		# (`js/arrange.js`).
		'trigger("desktop_screen", { desktop: this })',
		"add_menu_item(item) {",
		'frappe.pages["desktop"].desktop_page = new DesktopPage(page)',
		"\tupdate() {",
	],
	# An editor's save hands the desk new workspaces, and it rebuilds its lookups from them.
	("public", "js", "frappe", "desk.js"): ["setup_workspaces() {"],
}

# Frappe's server functions Open Desk calls outside the boot module, by module.
SERVER_FUNCTIONS = {
	"frappe.desk.doctype.dock.dock": ["get_app_base"],
	"frappe.desk.doctype.desktop_settings.desktop_settings": ["get_desktop_page"],
	"frappe.desk.desktop": ["get_workspaces"],
}

# The Dock's slots, by class, top to bottom. Open Desk fills `dock-items` (`render_entries`), the mark
# in `dock-logo` (`render_logo`) and adds other apps' tiles to `dock-utilities`; a new slot is
# something Frappe draws on the dock that may already be there in Open Desk's own way, as Search and
# Notifications were before Frappe 16.53 drew them too.
DOCK_SLOTS = ["dock-logo", "dock-utilities", "dock-items", "dock-user"]

# The two Dock methods the dock replaces rather than wraps (`render_logo`, `render_entries` in
# `js/dock.js`), as Frappe wrote them when the dock last matched them. A change fails here: read
# what Frappe changed, carry it into the dock's version if it matters, then update the
# fingerprint.
REPLACED = {"render_entries": "deaead8e8747244a", "render_logo": "3bc6ff7131056e0f"}

# What the server half calls in `frappe.boot`, and the boot keys the desk half reads.
BOOT_FUNCTIONS = [
	"get_module_sidebars",
	"get_app_data",
	"get_app_rail_host_map",
	"get_boot_module_app",
	"get_icon_style",
]
BOOT_KEYS = ["module_sidebars", "app_data"]


# Another Frappe's source to check instead of the installed one (see the module's docstring).
FRAPPE_SOURCE = os.environ.get("OPENDESK_FRAPPE_SOURCE")


def _frappe_path(*parts: str) -> str:
	if FRAPPE_SOURCE:
		return os.path.join(FRAPPE_SOURCE, "frappe", *parts)
	return frappe.get_app_path("frappe", *parts)


def _source(*parts: str) -> str:
	with open(_frappe_path(*parts), encoding="utf-8") as f:
		return f.read()


def _defines(module: str, name: str) -> bool:
	"""Whether a Frappe module has a function of this name: imported, or read in `FRAPPE_SOURCE`."""
	if FRAPPE_SOURCE:
		parts = module.split(".")[1:]
		path = os.path.join(*parts, "__init__.py") if os.path.isdir(_frappe_path(*parts)) else None
		source = _source(path) if path else _source(*parts[:-1], parts[-1] + ".py")
		return bool(re.search(rf"(?m)^def {re.escape(name)}\(", source))
	import importlib

	return callable(getattr(importlib.import_module(module), name, None))


class TestFrappeSeams(TestCase):
	def test_desk_names_are_still_in_frappe(self):
		for parts, seams in SEAMS.items():
			path = os.path.join(*parts)
			source = _source(*JS, *parts)
			# Asserted as booleans: a failure names the seam, not the whole file.
			for method in seams.get("methods", ()):
				with self.subTest(path=path, method=method):
					pattern = (
						rf"(?m)^\s*(static\s+|get\s+|async\s+)?{re.escape(method)}\s*\(.*\)\s*\{{\s*\}}?\s*$"
					)
					self.assertTrue(re.search(pattern, source), f"{method}() is not defined in {path}")
			for prop in seams.get("properties", ()):
				with self.subTest(path=path, property=prop):
					found = re.search(rf"this\.{re.escape(prop)}\b", source)
					self.assertTrue(found, f"this.{prop} is not in {path}")
			for text in seams.get("strings", ()):
				with self.subTest(path=path, string=text):
					self.assertTrue(text in source, f"{text!r} is not in {path}")

	def test_boot_still_offers_what_the_dock_reads(self):
		for name in BOOT_FUNCTIONS:
			with self.subTest(function=name):
				self.assertTrue(_defines("frappe.boot", name), f"frappe.boot.{name} is gone")
		source = _source("boot.py")
		for key in BOOT_KEYS:
			with self.subTest(key=key):
				self.assertIn(f"bootinfo.{key} =", source)

	def test_server_functions_are_still_there(self):
		"""Checked without a site: a name that moved would otherwise show only in the Error Log."""
		for module, names in SERVER_FUNCTIONS.items():
			for name in names:
				with self.subTest(function=f"{module}.{name}"):
					self.assertTrue(_defines(module, name), f"{module}.{name} is gone")

	def test_an_apps_shipped_dock_is_still_readable(self):
		"""`desk_apps.shipped_docks` reads each app's own Dock, before any layer."""
		from frappe.desk.doctype.dock import dock

		if not getattr(frappe.local, "site", None):
			self.skipTest("reads a site's Dock records: run with a site connected")
		for row in dock.get_app_base("frappe"):
			with self.subTest(row=row.get("link_to")):
				self.assertLessEqual({"link_type", "link_to", "hidden"}, set(row))

	def test_app_data_is_in_the_boot_before_extend_bootinfo_runs(self):
		"""The dock reads this user's `app_data` from the boot it extends (`desk_apps.py`)."""
		# `get_bootinfo` builds it (`load_desktop_data`), then the session runs the hooks.
		self.assertIn("load_desktop_data(bootinfo", _source("boot.py"))
		sessions = _source("sessions.py")
		self.assertLess(
			sessions.index("bootinfo = get_bootinfo()"), sessions.index('get_hooks("extend_bootinfo")')
		)

	def test_every_frappe_class_the_dock_styles_is_still_frappes(self):
		"""A renamed class throws nothing: the dock only looks wrong. So each is looked for here."""
		with open(frappe.get_app_path("opendesk", "open_desk", "scss", "dock.scss")) as f:
			stylesheet = re.sub(r"//[^\n]*|/\*[\s\S]*?\*/", "", f.read())
		classes = {
			name for name in re.findall(r"\.([a-z][\w-]*)", stylesheet) if not name.startswith("opendesk-")
		}
		self.assertTrue(classes, "read no classes from dock.scss")

		frappe_source = []
		for parts in CLASS_SOURCES:
			for root, _dirs, files in os.walk(_frappe_path(*parts)):
				for name in files:
					if name.endswith((".scss", ".js", ".html")):
						with open(os.path.join(root, name), encoding="utf-8") as f:
							frappe_source.append(f.read())
		frappe_source = "\n".join(frappe_source)

		for name in sorted(classes):
			later = LATER_CLASSES.get(name)
			if later and not os.path.isdir(_frappe_path(*later)):
				continue
			with self.subTest(css_class=name):
				found = re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", frappe_source)
				self.assertTrue(found, f".{name} is styled by dock.scss but is not in Frappe")
		for parts, texts in SCSS_SEAMS.items():
			source = _source("public", "scss", *parts)
			for text in texts:
				with self.subTest(path=os.path.join(*parts), string=text):
					self.assertTrue(text in source, f"{text!r} is not in {os.path.join(*parts)}")

	def test_the_dock_methods_the_dock_replaces_are_unchanged(self):
		import hashlib

		source = _source(*JS, "ui", "sidebar", "dock.js")
		for name, fingerprint in REPLACED.items():
			with self.subTest(method=name):
				found = re.search(rf"(?ms)^\t{name}\(.*?\) \{{\n.*?^\t\}}\n", source)
				self.assertTrue(found, f"Dock.{name} is not in dock.js")
				self.assertEqual(
					hashlib.sha256(found.group(0).encode()).hexdigest()[:16],
					fingerprint,
					f"Frappe changed Dock.{name}, which js/dock.js replaces: read the change",
				)

	def test_the_dock_has_the_slots_open_desk_fills(self):
		source = _source(*JS, "ui", "sidebar", "dock.js")
		make = re.search(r"(?ms)^\tmake\(\) \{\n.*?^\t\}\n", source)
		self.assertTrue(make, "Dock.make is not in dock.js")
		self.assertEqual(
			re.findall(r'<div class="(dock-[\w-]+)"', make.group(0)),
			DOCK_SLOTS,
			"Frappe changed the Dock's slots: see whether what it draws in a new one is already on "
			"Open Desk's dock",
		)

	def test_the_apps_screen_page_still_offers_what_the_dock_reads(self):
		for parts, texts in DESKTOP_SEAMS.items():
			source = _source(*parts)
			for text in texts:
				with self.subTest(path=os.path.join(*parts), string=text):
					self.assertIn(text, source)
		self.assertTrue(
			os.path.isfile(_frappe_path("public", "js", "arrangement_editor.bundle.js")),
			"js/arrange.js loads arrangement_editor.bundle.js, which Frappe no longer ships",
		)

	def test_icon_sprites_still_hold_symbols_module_tiles_can_read(self):
		"""`module_tiles` lifts `<symbol id="icon-...">` out of Frappe's sprites and sets their tones."""
		sprite = re.search(r'"/assets/frappe/([^"]*module-icons\.svg)"', _source("hooks.py"))
		self.assertTrue(sprite, "Frappe's hooks.py no longer lists its module-icons.svg sprite")
		source = _source("public", *sprite.group(1).split("/"))
		self.assertRegex(source, r'<symbol\b[^>]*\bid="icon-[\w-]+-duotone"')
		self.assertIn("--duotone-dark", source)
		self.assertIn("--duotone-light", source)

	def test_methods_still_do_what_open_desk_leans_on(self):
		for parts, methods in METHOD_BODIES.items():
			source = _source(*JS, *parts)
			for name, texts in methods.items():
				body = re.search(rf"(?ms)^\t{name}\(.*?\) \{{\n.*?^\t\}}\n", source)
				for text in texts:
					choices = text if isinstance(text, tuple) else (text,)
					with self.subTest(method=name, string=choices[0]):
						self.assertTrue(
							body and any(choice in body.group(0) for choice in choices),
							f"{choices[0]!r} is not in {name}()",
						)

	def test_the_user_menu_rows_are_where_open_desk_changes_them(self):
		"""`public/js/user_menu_rows.js` changes the menu's rows, and the dock finds Manage Dock there.

		16.60 lists them in `user_menu_options`, which the menu and the phone's Profile page read;
		before, `create_user_menu` wrote them inline into the first Dropdown it made.
		"""
		source = _source(*JS, "ui", "sidebar", "sidebar.js")

		def body(name):
			found = re.search(rf"(?ms)^\t{name}\(.*?\) \{{\n.*?^\t\}}\n", source)
			return found.group(0) if found else ""

		menu = body("create_user_menu")
		self.assertIn("new frappe.ui.Dropdown({", menu)
		rows = body("user_menu_options") if "options: this.user_menu_options()" in menu else menu
		self.assertIn("options: [", rows)
		self.assertIn('"workspace-selector"', rows)

	def test_the_phone_navigation_sheet_is_what_the_dock_patches(self):
		if not os.path.isfile(_frappe_path(*JS, *MOBILE_NAV)):
			self.skipTest("this Frappe has no phone tab bar (16.60)")
		source = _source(*JS, *MOBILE_NAV)
		for text in MOBILE_NAV_SEAMS:
			with self.subTest(string=text):
				self.assertIn(text, source)
		# The sheet is the phone's way to the sidebar: the page head's drawer button is gone, so the
		# dock in the drawer (`scss/dock.scss`) is out of reach and only the sheet's row matters.
		self.assertNotIn("sidebar-toggle-btn", _source(*JS, "ui", "page.html"))

	def test_studio_apps_are_still_tiles_open_desk_can_make(self):
		if "bootinfo.studio_apps" not in _source("boot.py"):
			self.skipTest("this Frappe sends no Studio apps (16.60)")
		for parts, texts in STUDIO_SEAMS.items():
			source = _source(*parts)
			for text in texts:
				with self.subTest(path=os.path.join(*parts), string=text):
					self.assertIn(text, source)

	def test_the_standard_items_are_the_ones_the_dock_redraws(self):
		source = _source(*JS, "ui", "sidebar", "sidebar.js")
		body = re.search(r"(?ms)^\tadd_standard_items\(.*?\) \{\n.*?^\t\}\n", source)
		self.assertTrue(body, "add_standard_items() is not in sidebar.js")
		classes = set(re.findall(r'class: "([^"]+)"', body.group(0)))
		self.assertIn(
			classes,
			STANDARD_ITEMS,
			"Frappe's sidebar band changed: beside the dock it is hidden, and only Search, "
			"Notifications and Flow are drawn again on the dock",
		)
		if "sidebar-flow" in classes:
			dock = _source(*JS, "ui", "sidebar", "dock.js")
			utilities = re.search(r"(?ms)^\trender_utilities\(.*?\) \{\n.*?^\t\}\n", dock)
			self.assertTrue(utilities and "window.flow?.toggle()" in utilities.group(0))

	def test_the_boot_data_keeps_its_shape(self):
		for parts, texts in PYTHON_SEAMS.items():
			source = _source(*parts)
			for text in texts:
				with self.subTest(path=os.path.join(*parts), string=text):
					self.assertTrue(text in source, f"{text!r} is not in {os.path.join(*parts)}")

	def test_doctype_fields_the_server_half_reads_are_still_there(self):
		import json

		for parts, fields in DOCTYPE_FIELDS.items():
			with open(_frappe_path(*parts), encoding="utf-8") as f:
				names = {field.get("fieldname") for field in json.load(f)["fields"]}
			for field in fields:
				with self.subTest(doctype=parts[-1], field=field):
					self.assertIn(field, names)

	def test_every_css_variable_the_dock_reads_is_defined(self):
		"""An undefined variable throws nothing either: the rule just draws nothing.

		A variable read with a fallback, `var(--x, ...)`, draws either way, so only bare ones count.
		"""
		with open(frappe.get_app_path("opendesk", "open_desk", "scss", "dock.scss")) as f:
			stylesheet = re.sub(r"//[^\n]*|/\*[\s\S]*?\*/", "", f.read())
		used = set(re.findall(r"var\((--[\w-]+)\s*\)", stylesheet))
		defined = set(re.findall(r"(--[\w-]+)\s*:", stylesheet))
		# Frappe's stylesheets, and the design tokens under `public/css/espresso`.
		for folder in ("scss", "css"):
			for root, _dirs, files in os.walk(_frappe_path("public", folder)):
				for name in files:
					if name.endswith((".scss", ".css")):
						with open(os.path.join(root, name), encoding="utf-8") as f:
							defined |= set(re.findall(r"(--[\w-]+)\s*:", f.read()))
		for name in sorted(used):
			with self.subTest(variable=name):
				self.assertTrue(name in defined, f"var({name}) in dock.scss is not defined in Frappe")

	def test_every_icon_open_desk_names_is_in_a_sprite(self):
		"""A missing icon draws an empty box, quietly. Looked for in the sprites Frappe loads."""
		names = set(COMPUTED_ICONS)
		for folder in (("open_desk", "js"), ("public", "js")):
			path = frappe.get_app_path("opendesk", *folder)
			for name in os.listdir(path):
				if name.endswith(".js"):
					with open(os.path.join(path, name), encoding="utf-8") as f:
						source = f.read()
					names |= set(re.findall(r'frappe\.utils\.icon\(\s*"([\w-]+)"', source))
					names |= set(re.findall(r'\bicon: "([\w-]+)"', source))
		symbols = set()
		for sprite in re.findall(r'"/assets/frappe/([^"]+\.svg)"', _source("hooks.py")):
			symbols |= set(re.findall(r'id="icon-([\w-]+)"', _source("public", *sprite.split("/"))))
		with open(frappe.get_app_path("opendesk", "public", "icons", "module-icons.svg")) as f:
			symbols |= set(re.findall(r'id="icon-([\w-]+)"', f.read()))
		for name in sorted(names):
			with self.subTest(icon=name):
				self.assertTrue(name in symbols, f"no sprite Frappe loads has the icon {name!r}")

	def test_the_editor_classes_arrange_js_uses_are_frappes(self):
		"""`js/arrange.js` draws rows and panes with the editor's own `ws-` classes."""
		with open(frappe.get_app_path("opendesk", "open_desk", "js", "arrange.js")) as f:
			used = set(re.findall(r"\b(ws-[\w-]+)", f.read()))
		frappe_source = _source(*JS, "ui", "sidebar", "arrangement_editor.js") + _source(
			"public", "scss", "desk", "arrangement_editor.scss"
		)
		for name in sorted(used):
			with self.subTest(css_class=name):
				self.assertRegex(frappe_source, rf"(?<![\w-]){re.escape(name)}(?![\w-])")
