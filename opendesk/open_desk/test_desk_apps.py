# Copyright (c) 2026, Peter and contributors
# For license information, please see license.txt

"""The dock's rules, over plain data.

`resolve` takes everything it reads as arguments, so each rule in the module
docstring is one small table here: the fallback, the one-app rule, roles that
hide without releasing, a module of more than one shell, and an installed
app's shipped Dock.
"""

from types import SimpleNamespace
from unittest import TestCase

from opendesk.open_desk.desk_apps import (
	MODULE,
	OTHER,
	apps_from_app_data,
	installed_app_of,
	is_desk_route,
	resolve,
	row_type,
)

INSTALLED = ["frappe", "erpnext", "education", "commons"]
META = {
	"frappe": {"title": "Frappe Framework"},
	"erpnext": {"title": "ERPNext", "logo": "/erpnext.svg"},
	"education": {"title": "Education"},
	"commons": {"title": "Commons"},
}


def sidebar(name, app=None, module=None, header_icon=None, label=None):
	"""A shell as `_shells` hands it over: named after its module unless said otherwise."""
	return {
		"name": name,
		"app": app,
		"module": module or name,
		"label": label or name,
		"header_icon": header_icon,
	}


SIDEBARS = [
	sidebar("Users", app="frappe"),
	sidebar("Stock", app="erpnext", header_icon="package"),
	sidebar("Accounting", app="erpnext"),
	sidebar("Education", app="education"),
	# A custom module with no app on its sidebar: its Module Def has to say.
	sidebar("Students"),
	sidebar("Assessments"),
	sidebar("Helpdesk"),
]
# Keyed by scrubbed module name, as Frappe's boot `module_app` is.
MODULES = {"students": "education", "assessments": "commons"}


def dock(
	configured=(),
	user="someone@example.com",
	roles=("Desk User",),
	sidebars=SIDEBARS,
	frontends=None,
	hosts=None,
	docks=None,
	listed=None,
	everything=False,
):
	return resolve(
		configured=list(configured),
		sidebars=sidebars,
		installed_apps=INSTALLED,
		app_meta=META,
		module_apps=MODULES,
		user=user,
		user_roles=set(roles),
		frontends=frontends,
		hosts=hosts,
		docks=docks,
		listed=listed,
		everything=everything,
	)


def app(name, *modules, roles=(), icon=None):
	return {
		"name": name,
		"title": name,
		"icon": icon,
		"logo": None,
		"roles": list(roles),
		# A module's name, or a row as it is (a Category or Spacer).
		"modules": [m if isinstance(m, dict) else {"module": m, "label": None} for m in modules],
	}


def category(label):
	return {"type": "Category", "module": None, "label": label}


SPACER = {"type": "Spacer", "module": None, "label": None}


def layout(entry):
	"""An app's modules with what is drawn above each: a heading, a gap, or nothing."""
	return [
		(s["shell"], s.get("category") or ("gap" if s.get("space_before") else None))
		for s in entry["modules"]
	]


def titled(result, title):
	"""One dock entry by its title: a bound record sits at its installed app's place, not first."""
	return next(entry for entry in result if entry["title"] == title)


def shape(result):
	return [(entry["title"], [s["shell"] for s in entry["modules"]]) for entry in result]


class TestFallback(TestCase):
	def test_nothing_configured_is_one_entry_per_installed_app(self):
		self.assertEqual(
			shape(dock()),
			[
				("Frappe Framework", ["Users"]),
				("ERPNext", ["Accounting", "Stock"]),
				("Education", ["Education", "Students"]),
				("Commons", ["Assessments"]),
				# Neither an app nor a module says where Helpdesk goes.
				(OTHER, ["Helpdesk"]),
			],
		)

	def test_installed_apps_are_marked_and_keyed_apart_from_configured_ones(self):
		entry = dock()[1]
		self.assertEqual(entry["key"], "app:erpnext")
		self.assertFalse(entry["configured"])
		self.assertEqual(entry["logo"], "/erpnext.svg")

	def test_which_app_a_module_belongs_to(self):
		self.assertEqual(installed_app_of(sidebar("A", app="erpnext", module="Students"), MODULES), "erpnext")
		self.assertEqual(installed_app_of(sidebar("A", module=" Students "), MODULES), "education")
		self.assertIsNone(installed_app_of(sidebar("A", module="Nowhere"), MODULES))
		self.assertIsNone(installed_app_of(sidebar("Nowhere"), MODULES))


class TestUnlistedApps(TestCase):
	"""An installed app Frappe does not list as somewhere to go: its modules are in Other."""

	LISTED = ("frappe", "erpnext", "commons")

	def test_its_modules_go_to_other_and_it_has_no_entry(self):
		result = dock(listed=self.LISTED)
		self.assertNotIn("app:education", [e["key"] for e in result])
		other = next(e for e in result if e["key"] == "app:Other")
		self.assertEqual({m["shell"] for m in other["modules"]}, {"Education", "Students", "Helpdesk"})

	def test_a_desk_app_standing_for_it_brings_it_back(self):
		result = dock([bound("School", "education")], listed=self.LISTED)
		self.assertEqual({m["shell"] for m in titled(result, "School")["modules"]}, {"Education", "Students"})
		other = next(e for e in result if e["key"] == "app:Other")
		self.assertEqual([m["shell"] for m in other["modules"]], ["Helpdesk"])

	def test_an_editor_still_lists_it_off_the_dock(self):
		entry = next(e for e in dock(listed=self.LISTED, everything=True) if e["key"] == "app:education")
		self.assertEqual((entry["hidden"], entry["unlisted"], entry["modules"]), (True, True, []))

	def test_not_given_every_installed_app_is_listed(self):
		self.assertIn("app:education", [e["key"] for e in dock()])


class TestConfigured(TestCase):
	def test_configured_apps_come_first_with_their_modules_in_table_order(self):
		result = dock([app("Finance", "Stock", "Accounting"), app("School", "Students", "Assessments")])
		self.assertEqual(
			shape(result),
			[
				("Finance", ["Stock", "Accounting"]),
				("School", ["Students", "Assessments"]),
				("Frappe Framework", ["Users"]),
				# Emptied by the claims above, so gone rather than drawn empty.
				("Education", ["Education"]),
				(OTHER, ["Helpdesk"]),
			],
		)
		self.assertEqual(result[0]["key"], "desk-app:Finance")
		self.assertTrue(result[0]["configured"])

	def test_apps_screen_is_passed_on(self):
		configured = app("Finance", "Accounting")
		configured["apps_screen"] = "Icon per Module"
		self.assertEqual(dock([configured])[0]["apps_screen"], "Icon per Module")
		self.assertIsNone(dock([app("Finance", "Accounting")])[0]["apps_screen"])

	def test_desktop_image_is_carried_only_when_set(self):
		row = {"module": "Accounting", "label": None, "desktop_image": "/files/books.png"}
		entry = dock([app("Finance", row, "Stock")])[0]
		by_name = {s["shell"]: s for s in entry["modules"]}
		self.assertEqual(by_name["Accounting"]["desktop_image"], "/files/books.png")
		self.assertNotIn("desktop_image", by_name["Stock"])

	def test_a_module_is_called_what_its_sidebar_is(self):
		# A label left on a module row from before is not a name for it.
		row = {"module": "Accounting", "label": "Books"}
		entry = dock([app("Finance", row)])[0]
		self.assertEqual(entry["modules"][0], {"shell": "Accounting", "label": "Accounting", "icon": None})

	def test_first_claim_wins(self):
		result = dock([app("Finance", "Stock"), app("Warehouse", "Stock", "Accounting")])
		self.assertEqual(shape(result)[:2], [("Finance", ["Stock"]), ("Warehouse", ["Accounting"])])

	def test_an_app_with_nothing_left_is_dropped(self):
		result = dock([app("Gone", "Deleted Module")])
		self.assertNotIn("Gone", [entry["title"] for entry in result])

	def test_roles_hide_the_app_without_releasing_its_sidebars(self):
		result = dock([app("Finance", "Accounting", "Stock", roles=["Accounts User"])])
		self.assertNotIn("Finance", [entry["title"] for entry in result])
		# Not back under ERPNext either: the restriction would only have moved them.
		self.assertNotIn("ERPNext", [entry["title"] for entry in result])

		allowed = dock([app("Finance", "Accounting", roles=["Accounts User"])], roles=["Accounts User"])
		self.assertEqual(allowed[0]["title"], "Finance")


# Two shells of one module, one renamed away from it, as Frappe's boot has them.
SHELLS = [
	*SIDEBARS,
	sidebar("Quality", app="erpnext", module="Quality Management", label="Quality"),
	sidebar("Audits", app="erpnext", module="Quality Management", label="Audits"),
]


class TestModules(TestCase):
	"""A row claims a module, which is every shell the boot has for it."""

	def test_a_row_claims_every_shell_of_its_module(self):
		result = dock([app("QA", "Quality Management")], sidebars=SHELLS)
		self.assertEqual(shape(result)[0], ("QA", ["Quality", "Audits"]))
		self.assertNotIn("Quality", shape(result)[2][1])

	def test_each_shell_keeps_its_own_label(self):
		entry = dock([app("QA", "Quality Management")], sidebars=SHELLS)[0]
		self.assertEqual([s["label"] for s in entry["modules"]], ["Quality", "Audits"])

	def test_a_renamed_shell_is_claimed_by_its_module_not_its_name(self):
		result = dock([app("QA", "Quality")], sidebars=SHELLS)
		self.assertNotIn("QA", [entry["title"] for entry in result])

	def test_unlabelled_modules_take_the_sidebars_label(self):
		shells = [sidebar("Loan Management", app="erpnext", label="Lending")]
		self.assertEqual(dock(sidebars=shells)[0]["modules"][0]["label"], "Lending")


COMPANION_SHELLS = [sidebar("Accounting", app="erpnext"), sidebar("GST", app="india_compliance")]
HOSTS = {"india_compliance": "erpnext"}


class TestCompanionApps(TestCase):
	"""A companion app's modules are its host's, as Frappe's desk shows them."""

	def test_grouped_under_the_host(self):
		self.assertEqual(
			dict(shape(dock(sidebars=COMPANION_SHELLS, hosts=HOSTS)))["ERPNext"], ["Accounting", "GST"]
		)

	def test_without_a_mount_it_is_not_an_installed_app(self):
		self.assertEqual(dict(shape(dock(sidebars=COMPANION_SHELLS)))[OTHER], ["GST"])

	def test_a_desk_app_still_claims_it(self):
		result = dock([app("Tax", "GST")], sidebars=COMPANION_SHELLS, hosts=HOSTS)
		self.assertEqual(shape(result)[0], ("Tax", ["GST"]))


class FakeClientCache:
	"""`frappe.client_cache`'s two calls the dock makes, over a dict."""

	def __init__(self):
		self.store = {}

	def get_value(self, key, generator=None):
		if key not in self.store:
			self.store[key] = generator()
		return self.store[key]

	def delete_value(self, key):
		self.store.pop(key, None)


class SiteInputsAreCached(TestCase):
	def test_read_once_until_something_they_are_read_from_changes(self):
		from unittest.mock import patch

		from opendesk.open_desk import desk_apps as nav

		reads = []
		cache = FakeClientCache()
		with (
			patch.object(nav.frappe, "client_cache", cache),
			patch.object(nav.frappe, "local", SimpleNamespace(db=None)),
			patch.object(nav, "_configured", side_effect=lambda: reads.append("configured") or []),
			patch.object(nav, "module_apps", return_value={}),
			patch.object(nav, "shipped_docks", return_value={}),
			patch.object(nav, "listed_apps", return_value=["frappe"]),
			patch.object(nav.frappe, "get_installed_apps", return_value=["frappe"]),
		):
			nav._site_inputs()
			nav._site_inputs()
			self.assertEqual(reads, ["configured"])
			nav.clear_cache()
			nav._site_inputs()
			self.assertEqual(reads, ["configured", "configured"])


class ActiveApps(TestCase):
	"""Frappe 17 can switch an installed app off; the dock follows it where Frappe can."""

	def active(self, get_active_apps):
		from unittest.mock import patch

		from opendesk.open_desk import desk_apps as nav

		with (
			patch.object(nav.frappe, "get_active_apps", get_active_apps, create=True),
			patch.object(nav.frappe, "get_installed_apps", return_value=["frappe", "erpnext", "hrms"]),
		):
			return nav.active_apps()

	def test_the_apps_frappe_has_not_switched_off(self):
		self.assertEqual(self.active(lambda: ["frappe", "erpnext"]), ["frappe", "erpnext"])

	def test_every_installed_app_where_frappe_cannot_switch_one_off(self):
		self.assertEqual(self.active(None), ["frappe", "erpnext", "hrms"])


class ReplaceKeepsWhatTheEditorDidNotSee(TestCase):
	"""Manage Modules lists what its user can open; a Replace record's other modules stay off."""

	def leaves_out(self, mode, rows, visible):
		from unittest.mock import patch

		from opendesk.open_desk import arrange
		from opendesk.open_desk import desk_apps as nav

		module_apps = {"accounts": "erpnext", "payroll": "erpnext", "crm": "crm_app"}
		with (
			patch.object(nav, "_site_inputs", return_value={"module_apps": module_apps}),
			patch.object(nav, "app_hosts", return_value={"crm_app": "erpnext"}),
		):
			return arrange._leaves_out_unseen(mode, "erpnext", rows, visible)

	def test_a_module_the_editor_could_not_see_keeps_replace(self):
		# Payroll is not visible to this editor and not in the table: it was taken off before.
		self.assertTrue(self.leaves_out("Replace", [{"module": "Accounts"}], {"Accounts", "CRM"}))

	def test_every_own_module_seen_or_listed_lets_it_go_to_add(self):
		rows = [{"module": "Accounts"}, {"module": "Payroll"}, {"module": "CRM"}]
		self.assertFalse(self.leaves_out("Replace", rows, {"Accounts", "CRM"}))
		self.assertFalse(self.leaves_out("Replace", [{"module": "Accounts"}], {"Payroll", "CRM"}))

	def test_an_add_record_is_not_turned_into_replace(self):
		self.assertFalse(self.leaves_out("Add", [], set()))


def bound(name, installed_app, *sidebars, mode="Add", hidden=0, **kwargs):
	return {
		**app(name, *sidebars, **kwargs),
		"installed_app": installed_app,
		"module_mode": mode,
		"hidden": hidden,
	}


class TestBoundApps(TestCase):
	"""A Desk App standing for an installed app, or for Other."""

	def test_takes_the_installed_apps_place_and_keeps_its_modules(self):
		result = dock([bound("Books", "erpnext")])
		# ERPNext's place: after Frappe, as installed.
		self.assertEqual(shape(result)[1], ("Books", ["Accounting", "Stock"]))
		# Not drawn a second time among the installed apps.
		self.assertNotIn("ERPNext", [entry["title"] for entry in result])
		self.assertEqual(result[1]["key"], "app:erpnext")
		self.assertTrue(result[1]["configured"])

	def test_add_mode_adds(self):
		books = bound("Books", "erpnext", "Stock", "Students")
		entry = titled(dock([books]), "Books")
		# The listed ones in table order, then what ERPNext already held.
		self.assertEqual([s["shell"] for s in entry["modules"]], ["Stock", "Students", "Accounting"])
		# Claimed away from Education.
		self.assertIn(("Education", ["Education"]), shape(dock([books])))

	def test_replace_mode_keeps_only_the_list_and_sends_the_rest_to_other(self):
		result = shape(dock([bound("Books", "erpnext", "Stock", mode="Replace")]))
		self.assertEqual(dict(result)["Books"], ["Stock"])
		self.assertEqual(result[-1], (OTHER, ["Accounting", "Helpdesk"]))

	def test_another_app_claiming_one_of_its_sidebars_takes_it(self):
		result = dict(shape(dock([bound("Books", "erpnext"), app("Stores", "Stock")])))
		self.assertEqual((result["Books"], result["Stores"]), (["Accounting"], ["Stock"]))

	def test_hidden_takes_the_app_and_its_sidebars_off_the_dock(self):
		result = shape(dock([bound("Books", "erpnext", "Students", hidden=1)]))
		self.assertNotIn("Books", [title for title, _ in result])
		self.assertNotIn("ERPNext", [title for title, _ in result])
		self.assertFalse(any(s in ("Accounting", "Stock", "Students") for _, row in result for s in row))

	def test_roles_hide_without_releasing(self):
		books = bound("Books", "erpnext", roles=("Accounts User",))
		self.assertEqual(
			dict(shape(dock([books], roles=("Accounts User",))))["Books"], ["Accounting", "Stock"]
		)
		result = shape(dock([books]))
		self.assertFalse(any(title in ("Books", "ERPNext") for title, _ in result))

	def test_inherits_the_logo_and_frontend_unless_it_has_its_own(self):
		entry = titled(dock([bound("Books", "erpnext")], frontends={"erpnext": "/shop"}), "Books")
		self.assertEqual(entry["logo"], "/erpnext.svg")
		self.assertEqual(entry["frontend"], {"label": "Books app", "url": "/shop"})
		# An icon of its own is a mark of its own: the app's logo would cover it.
		entry = titled(dock([bound("Books", "erpnext", icon="book")]), "Books")
		self.assertEqual((entry["icon"], entry["logo"]), ("book", None))
		entry = titled(
			dock([{**bound("Books", "erpnext"), "logo": "/books.svg", "frontend_url": "/books"}]), "Books"
		)
		self.assertEqual((entry["logo"], entry["frontend"]["url"]), ("/books.svg", "/books"))

	def test_a_color_redraws_the_inherited_logo_but_not_its_own(self):
		from unittest.mock import patch

		from opendesk.open_desk import desk_apps

		with patch.object(
			desk_apps.module_tiles, "recoloured_logo", side_effect=lambda url, color: f"{url}?in={color}"
		):
			entry = titled(dock([{**bound("Books", "erpnext"), "color": "#2E7D32"}]), "Books")
			self.assertEqual((entry["logo"], entry["color"]), ("/erpnext.svg?in=#2E7D32", "#2E7D32"))
			entry = titled(
				dock([{**bound("Books", "erpnext"), "color": "#2E7D32", "logo": "/books.svg"}]), "Books"
			)
			self.assertEqual(entry["logo"], "/books.svg")
		# A logo that cannot be redrawn is kept as it is.
		with patch.object(desk_apps.module_tiles, "recoloured_logo", return_value=None):
			entry = titled(dock([{**bound("Books", "erpnext"), "color": "#2E7D32"}]), "Books")
			self.assertEqual(entry["logo"], "/erpnext.svg")

	def test_other_is_bindable(self):
		result = dock([bound("Unsorted", OTHER)])
		# Other's place: last.
		self.assertEqual(shape(result)[-1], ("Unsorted", ["Helpdesk"]))
		self.assertEqual(result[-1]["key"], f"app:{OTHER}")
		self.assertEqual(result[-1]["logo"], "/assets/opendesk/images/opendesk-other-logo.svg")
		self.assertNotIn(OTHER, [entry["title"] for entry in result])
		hidden = shape(dock([bound("Unsorted", OTHER, hidden=1)]))
		self.assertFalse(any(title in ("Unsorted", OTHER) for title, _ in hidden))

	def test_other_replacing_drops_what_it_does_not_list(self):
		result = shape(
			dock(
				[
					bound("Books", "erpnext", "Stock", mode="Replace"),
					bound("Unsorted", OTHER, "Users", mode="Replace"),
				]
			)
		)
		self.assertEqual((dict(result)["Books"], dict(result)["Unsorted"]), (["Stock"], ["Users"]))
		self.assertFalse(any(s in ("Accounting", "Helpdesk") for _, row in result for s in row))

	def test_only_the_first_record_for_an_app_stands_for_it(self):
		result = dock([bound("Books", "erpnext"), bound("Ledger", "erpnext", "Stock")])
		self.assertEqual(
			(dict(shape(result))["Books"], dict(shape(result))["Ledger"]), (["Accounting"], ["Stock"])
		)
		self.assertEqual(titled(result, "Ledger")["key"], "desk-app:Ledger")

	def test_a_record_for_an_app_not_installed_waits_for_it(self):
		# Its modules stay where they would be without it, and it is not drawn, even for an editor.
		result = dock([bound("Desk", "helpdesk", "Helpdesk")])
		self.assertNotIn("desk-app:Desk", [app["key"] for app in result])
		self.assertNotIn("Desk", [title for title, _modules in shape(result)])
		self.assertNotIn(
			"desk-app:Desk", [a["key"] for a in dock([bound("Desk", "helpdesk")], everything=True)]
		)


LANDING = [
	sidebar("Stock", app="erpnext"),
	sidebar("Accounting", app="erpnext"),
	sidebar("ERPNext", app="erpnext"),
	sidebar("Home", app="erpnext"),
	sidebar("Courses", app="education"),
	sidebar("Education", app="education"),
]


class TestOrder(TestCase):
	"""Chosen order where there is one; landing module, then alphabetical, where not."""

	def test_home_then_the_app_named_module_go_first(self):
		result = shape(dock(sidebars=LANDING))
		self.assertIn(("ERPNext", ["Home", "ERPNext", "Accounting", "Stock"]), result)
		self.assertIn(("Education", ["Education", "Courses"]), result)

	def test_a_landing_module_by_its_label_counts_too(self):
		shells = [sidebar("Start", app="erpnext", label="Home"), *LANDING[:2]]
		self.assertIn(("ERPNext", ["Start", "Accounting", "Stock"]), shape(dock(sidebars=shells)))

	def test_the_table_order_is_kept_and_the_rest_follow(self):
		entry = dock([bound("Books", "erpnext", "Stock", "Accounting")], sidebars=LANDING)[0]
		# The record is called Books, but the app is still ERPNext: its module still lands first.
		self.assertEqual([s["shell"] for s in entry["modules"]], ["Stock", "Accounting", "Home", "ERPNext"])

	def test_a_synthetic_app_is_only_its_table(self):
		entry = dock([app("Finance", "Stock", "Home", "Accounting")], sidebars=LANDING)[0]
		self.assertEqual([s["shell"] for s in entry["modules"]], ["Stock", "Home", "Accounting"])


# ERPNext's shipped Dock, as `shipped_docks` hands it over: its order, and what it hides.
DOCKED = [
	sidebar("Accounting", app="erpnext"),
	sidebar("CRM", app="erpnext"),
	sidebar("Selling", app="erpnext"),
	sidebar("Setup", app="erpnext"),
	sidebar("Accounts (Custom)", app="erpnext"),
	sidebar("Home", app="erpnext"),
	sidebar("Education", app="education"),
]
DOCKS = {"erpnext": {"order": ["Setup", "Accounting", "Selling", "CRM"], "hidden": ["CRM"]}}


class TestShippedDocks(TestCase):
	"""An installed app's shipped Dock orders and hides what nobody has configured."""

	def test_the_dock_orders_then_the_rest_follow_in_the_docks_order(self):
		result = dict(shape(dock(sidebars=DOCKED, docks=DOCKS)))
		self.assertEqual(result["ERPNext"], ["Setup", "Accounting", "Selling", "Home", "Accounts (Custom)"])

	def test_a_module_the_dock_hides_is_off_the_dock_not_in_other(self):
		result = dict(shape(dock(sidebars=DOCKED, docks=DOCKS)))
		self.assertNotIn("CRM", [shell for shells in result.values() for shell in shells])
		result = dict(
			shape(dock([bound("Books", "erpnext", "Setup", mode="Replace")], sidebars=DOCKED, docks=DOCKS))
		)
		self.assertNotIn("CRM", result.get(OTHER, []))

	def test_listing_a_hidden_module_puts_it_back(self):
		entry = dock([bound("Books", "erpnext", "CRM")], sidebars=DOCKED, docks=DOCKS)[0]
		self.assertEqual(
			shape([entry])[0][1], ["CRM", "Setup", "Accounting", "Selling", "Home", "Accounts (Custom)"]
		)

	def test_an_app_without_a_dock_keeps_the_docks_order(self):
		self.assertIn(("Education", ["Education"]), shape(dock(sidebars=DOCKED, docks=DOCKS)))

	def test_read_from_frappes_shipped_base(self):
		from unittest.mock import patch

		from opendesk.open_desk import desk_apps as nav

		bases = {
			"erpnext": [
				{"link_type": "Sidebar", "link_to": "Setup", "hidden": 0},
				{"link_type": "Workspace", "link_to": "Pinned", "hidden": 0},
				{"link_type": "Sidebar", "link_to": "CRM", "hidden": 1},
			],
		}
		with (
			patch.object(nav.frappe, "get_installed_apps", return_value=["frappe", "erpnext"]),
			patch("frappe.desk.doctype.dock.dock.get_app_base", side_effect=lambda app: bases.get(app, [])),
		):
			self.assertEqual(nav.shipped_docks(), {"erpnext": {"order": ["Setup", "CRM"], "hidden": ["CRM"]}})


class TestFrontends(TestCase):
	"""An app's own frontend, outside the desk, carried beside its sidebars."""

	def test_an_installed_app_carries_its_frontend(self):
		entry = next(e for e in dock(frontends={"commons": "/commons"}) if e["key"] == "app:commons")
		self.assertEqual(entry["frontend"], {"label": "Commons app", "url": "/commons"})
		self.assertEqual([s["shell"] for s in entry["modules"]], ["Assessments"])

	def test_apps_without_one_carry_none(self):
		self.assertTrue(all(entry["frontend"] is None for entry in dock()))

	def test_a_frontend_alone_puts_an_app_on_the_dock(self):
		# No sidebars anywhere for this app, only its frontend.
		entry = next(
			e
			for e in dock(frontends={"frappe": "/builder"}, sidebars=SIDEBARS[1:])
			if e["key"] == "app:frappe"
		)
		self.assertEqual(entry["modules"], [])
		self.assertEqual(entry["frontend"]["url"], "/builder")

	def test_a_configured_app_has_its_own_frontend_and_label(self):
		school = {**app("School", "Students"), "frontend_url": "/commons", "frontend_label": ""}
		self.assertEqual(dock([school])[0]["frontend"], {"label": "School app", "url": "/commons"})
		school["frontend_label"] = "Staff portal"
		self.assertEqual(dock([school])[0]["frontend"]["label"], "Staff portal")

	def test_a_configured_app_with_only_a_frontend_is_kept(self):
		portal = {**app("Portal"), "frontend_url": "/helpdesk"}
		self.assertEqual(dock([portal])[0]["title"], "Portal")

	def test_desk_links_are_not_frontends(self):
		for url in ("/app", "/desk", "/app/lending", "/desk/people?x=1", "/desk/build/"):
			with self.subTest(url=url):
				self.assertTrue(is_desk_route(url))
		for url in ("/helpdesk", "/commons/announcements", "/builder", "https://example.com/app/x"):
			with self.subTest(url=url):
				self.assertFalse(is_desk_route(url))

	def test_read_from_frappes_app_data(self):
		app_data = [
			{
				"app_name": "frappe",
				"app_title": "Framework",
				"app_route": "/app/build",
				"app_logo_url": ["/f.svg"],
			},
			{
				"app_name": "helpdesk",
				"app_title": "Helpdesk",
				"app_route": "/helpdesk",
				"app_logo_url": "/h.svg",
			},
			{
				"app_name": "hrms",
				"app_title": "Frappe HR",
				"app_route": "/desk/hr-setup",
				"app_logo_url": None,
			},
			# Turned away by its `has_permission`: Frappe empties the route, so no frontend.
			{"app_name": "lending", "app_title": "Lending", "app_route": "", "app_logo_url": "/l.svg"},
		]
		meta, frontends = apps_from_app_data(app_data)
		self.assertEqual(frontends, {"helpdesk": "/helpdesk"})
		self.assertEqual(meta["frappe"], {"title": "Framework", "logo": "/f.svg"})
		self.assertEqual(meta["hrms"], {"title": "Frappe HR", "logo": None})
		self.assertEqual(meta["lending"]["title"], "Lending")

	def test_an_app_frappe_hides_offers_no_frontend(self):
		_meta, frontends = apps_from_app_data(
			[{"app_name": "commons", "app_title": "Commons", "app_route": ""}]
		)
		entry = next(e for e in dock(frontends=frontends) if e["key"] == "app:commons")
		self.assertIsNone(entry["frontend"])


class TestCategoriesAndSpacers(TestCase):
	"""Category and Spacer rows ride on the module after them; `sidebars` stays modules only."""

	def test_each_marks_the_module_after_it(self):
		entry = dock(
			[app("Finance", category("Books"), "Accounting", SPACER, "Stock", category("People"), "Users")]
		)[0]
		self.assertEqual(layout(entry), [("Accounting", "Books"), ("Stock", "gap"), ("Users", "People")])

	def test_a_category_ends_a_spacer_next_to_it(self):
		entry = dock([app("Finance", "Accounting", SPACER, category("Stock"), SPACER, "Stock")])[0]
		self.assertEqual(layout(entry), [("Accounting", None), ("Stock", "Stock")])

	def test_a_category_whose_modules_are_gone_is_dropped(self):
		# Stock is claimed by the first app, so Finance's "Stores" heads nothing.
		finance = app("Finance", category("Stores"), "Stock", category("Books"), "Accounting")
		entry = dock([app("Ops", "Stock"), finance])[1]
		self.assertEqual(layout(entry), [("Accounting", "Books")])

	def test_a_gap_over_the_first_module_is_dropped(self):
		entry = dock([app("Finance", SPACER, "Accounting")])[0]
		self.assertEqual(layout(entry), [("Accounting", None)])

	def test_a_trailing_category_heads_what_the_app_holds_besides(self):
		entry = titled(dock([bound("Books", "erpnext", "Stock", category("More"))]), "Books")
		self.assertEqual(layout(entry), [("Stock", None), ("Accounting", "More")])

	def test_only_markers_is_no_app(self):
		self.assertNotIn("Finance", [e["title"] for e in dock([app("Finance", category("Empty"), SPACER)])])

	def test_a_category_without_a_label_is_a_gap(self):
		entry = dock([app("Finance", "Accounting", category("  "), "Stock")])[0]
		self.assertEqual(layout(entry), [("Accounting", None), ("Stock", "gap")])

	def test_a_row_without_a_type_is_a_module(self):
		self.assertEqual(row_type({"module": "Stock"}), MODULE)
		self.assertEqual(row_type({"type": "", "module": "Stock"}), MODULE)

	def test_a_row_of_no_known_type_is_skipped(self):
		entry = dock([app("Finance", "Accounting", {"type": "Sidebar", "module": "Stock", "label": None})])[0]
		self.assertEqual(layout(entry), [("Accounting", None)])


class TestKeepUnseen(TestCase):
	"""Manage Modules keeps rows for modules the person editing was not shown."""

	def row(self, module):
		return SimpleNamespace(
			module=module,
			get=lambda key, m=module: f"/files/{m}.png" if key == "desktop_image" else None,
		)

	def test_an_unseen_row_goes_back_after_the_row_it_followed(self):
		from opendesk.open_desk.arrange import _keep_unseen

		old = [self.row("Stock"), self.row("Secret"), self.row("Accounts")]
		new = [{"module": "Accounts"}, {"module": "Stock"}]
		result = _keep_unseen(new, old, visible={"Stock", "Accounts"})
		self.assertEqual([r["module"] for r in result], ["Accounts", "Stock", "Secret"])
		self.assertEqual(result[2]["desktop_image"], "/files/Secret.png")

	def test_an_unseen_first_row_stays_first(self):
		from opendesk.open_desk.arrange import _keep_unseen

		result = _keep_unseen(
			[{"module": "Stock"}], [self.row("Secret"), self.row("Stock")], visible={"Stock"}
		)
		self.assertEqual([r["module"] for r in result], ["Secret", "Stock"])


# The apps with a default place, in that order: installed, then Other.
DEFAULTS = ["app:frappe", "app:erpnext", "app:education", "app:Other"]


class TestRailPosition(TestCase):
	"""Every app at its default place, unless its record anchors it after another."""

	def test_anchored_apps_follow_their_anchor_and_the_rest_keep_default_order(self):
		from opendesk.open_desk.desk_apps import TOP, dock_sequence

		anchors = {"app:education": TOP, "desk-app:Finance": "app:erpnext", "app:erpnext": None}
		self.assertEqual(
			dock_sequence(DEFAULTS, anchors),
			["app:education", "app:frappe", "app:erpnext", "desk-app:Finance", "app:Other"],
		)

	def test_a_chain_of_anchors_and_one_that_is_gone(self):
		from opendesk.open_desk.desk_apps import dock_sequence

		anchors = {
			"desk-app:B": "desk-app:A",
			"desk-app:A": "app:frappe",
			"app:erpnext": "app:uninstalled",
			"desk-app:C": "desk-app:C",
		}
		self.assertEqual(
			dock_sequence(DEFAULTS, anchors),
			[
				"desk-app:C",
				"app:frappe",
				"desk-app:A",
				"desk-app:B",
				"app:erpnext",
				"app:education",
				"app:Other",
			],
		)

	def test_every_arrangement_is_stored_and_read_back(self):
		from itertools import permutations

		from opendesk.open_desk.arrange import anchors_for
		from opendesk.open_desk.desk_apps import dock_sequence

		apps = [*DEFAULTS, "desk-app:Finance"]
		for keys in permutations(apps):
			with self.subTest(keys=keys):
				anchors = anchors_for(list(keys), DEFAULTS, {"desk-app:Finance"})
				self.assertEqual(dock_sequence(DEFAULTS, anchors), list(keys))

	def test_moving_one_app_anchors_only_that_app(self):
		from opendesk.open_desk.arrange import anchors_for

		keys = ["app:frappe", "app:education", "app:Other", "app:erpnext"]
		anchors = anchors_for(keys, DEFAULTS, set())
		self.assertEqual({k: a for k, a in anchors.items() if a}, {"app:erpnext": "app:Other"})

	def test_a_hidden_unlisted_app_holds_no_place_and_nothing_follows_it(self):
		"""Hidden, an app Frappe lists nowhere is off the dock with its modules in Other. A place
		would keep its record, which, hidden, would take those modules off the dock altogether."""
		from opendesk.open_desk.arrange import positions

		defaults = [*DEFAULTS[:-1], "app:telephony", "app:Other"]
		by_key = {key: {"key": key, "installed_app": key.removeprefix("app:")} for key in defaults}
		by_key["app:telephony"]["record"] = "Telephony"
		listed = {"frappe", "erpnext", "education", "Other"}
		keys = ["app:telephony", "app:education", "app:frappe", "app:erpnext", "app:Other"]

		hidden = positions(keys, by_key, {"app:telephony"}, listed, defaults)
		self.assertIsNone(hidden["app:telephony"])
		self.assertNotIn("app:telephony", hidden.values())
		self.assertEqual(hidden["app:education"], "top")

		shown = positions(keys, by_key, set(), listed, defaults)
		self.assertEqual(shown["app:telephony"], "top")

	def test_a_hidden_listed_app_keeps_its_place(self):
		from opendesk.open_desk.arrange import positions

		by_key = {key: {"key": key, "installed_app": key.removeprefix("app:")} for key in DEFAULTS}
		keys = ["app:education", "app:frappe", "app:erpnext", "app:Other"]
		anchors = positions(
			keys, by_key, {"app:education"}, {"frappe", "erpnext", "education", "Other"}, DEFAULTS
		)
		self.assertEqual(anchors["app:education"], "top")

	def test_a_bound_record_sits_at_its_apps_place_and_a_site_app_on_top(self):
		result = dock([bound("Books", "erpnext"), app("Finance", "Students")])
		self.assertEqual([entry["title"] for entry in result][:3], ["Finance", "Frappe Framework", "Books"])

	def test_dock_after_moves_an_app(self):
		finance = {**app("Finance", "Students"), "dock_after": "app:erpnext"}
		titles = [entry["title"] for entry in dock([finance])]
		self.assertEqual(titles.index("Finance"), titles.index("ERPNext") + 1)


class TestPlaceholder(TestCase):
	"""A record that says nothing but which app it stands for is deleted rather than kept."""

	def doc(self, **values):
		fields = {
			"installed_app": "telephony",
			"enabled": 1,
			"hidden": 0,
			"dock_after": None,
			"module_mode": "Add",
			"modules": [],
			"roles": [],
			"icon": None,
			"logo": None,
			"color": None,
			"frontend_url": None,
			"frontend_label": None,
			"apps_screen": "Default",
			"title": "Telephony",
		}
		return SimpleNamespace(**{**fields, **values})

	def test_an_unlisted_app_hidden_again_with_nothing_else_is_a_placeholder(self):
		from opendesk.open_desk.arrange import _is_placeholder

		self.assertTrue(_is_placeholder(self.doc(hidden=1), "Telephony", hidden_by_default=True))

	def test_an_unlisted_app_shown_is_kept(self):
		from opendesk.open_desk.arrange import _is_placeholder

		self.assertFalse(_is_placeholder(self.doc(), "Telephony", hidden_by_default=True))

	def test_a_place_or_a_setting_of_its_own_is_kept(self):
		from opendesk.open_desk.arrange import _is_placeholder

		for values in (
			{"dock_after": "top"},
			{"apps_screen": "One Icon"},
			{"title": "Calls"},
			{"color": "#2E7D32"},
		):
			with self.subTest(**values):
				self.assertFalse(_is_placeholder(self.doc(**values), "Telephony"))
