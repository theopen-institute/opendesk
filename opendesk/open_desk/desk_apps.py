"""The dock: which apps it lists, and which modules each one offers.

Three levels, in this app's terms rather than Frappe's:

    Desk App     an entry on the dock
      Module     a Module Def, as Frappe 16.50 shows it: its `Sidebar`
        Item     a row in that sidebar (a `Sidebar Item`)

Only the top level is this app's. The bottom two are Frappe's own: since 16.50
every module has a sidebar (shipped by its app, or worked out from what the
module holds), resolved per user into `frappe.boot.module_sidebars` with the
site's and the user's Custom Sidebar layers applied. That is also where a site
overrides a module -- rename it, change its icon, add or hide its rows -- and a
custom Module Def is a synthetic module. So a module row here names a module
and nothing more: the dock calls it what its sidebar does.

This adds the level above, which Frappe has only for installed apps: its Dock
lists the open app's modules, and its Apps screen lists installed apps, neither
of which a site can regroup. The dock takes the Dock's place, and a Desk
App's modules table does the Dock's job for that app.

"App" here is not an installed app. A `Desk App` is whatever grouping a
site wants on its dock -- "Finance" holding modules from ERPNext and from
HRMS, say -- and a site may add as many as it likes.

One can also stand for an installed app, or for "Other", by naming it in
`installed_app`. It then takes that app's place on the dock rather than
appearing beside it: under its own title, roles and mark, falling back to the app's own logo and frontend as Frappe's Apps screen
has them (see `apps_from_app_data`). Its
modules table either adds to what the app already holds or, set to Replace, is
the whole list, and what the app would have held goes to Other. The table's row
order is the order the dock lists them in; what nobody has put in order follows
the app's default (see below). The table can also hold Category rows, a heading
over the modules after it, and Spacer rows, a gap; see `_layout`. Hidden takes it off the dock, and its modules
with it. "Other" is bindable like any installed app: the one group no hooks
describe, but as much the site's to rename, restrict or hide.

Where an app sits on the dock
-----------------------------
In its default place, unless it has been moved. The default is install order,
then Other, for installed apps and the records that stand for them; an app of
the site's own has no default place, so it sits at the top. A moved app's
record says which app it follows (`dock_after`, or "top"), and nothing else
needs a record to stay where it is: Manage Desk Apps anchors only what left the
default order (`arrange._store_order`), and `dock_sequence` puts each anchored
app back after its anchor. An anchor that is gone -- an app uninstalled, a
record renamed or disabled -- leaves the app at its default place.

The fallback is the installed apps
----------------------------------
A site that has configured nothing still gets a dock: one entry per installed
app, holding the modules that belong to it. And a site that has configured some
apps loses nothing it did not mention -- every module no `Desk App`
claims is still grouped under its installed app, after the configured ones. So
installing an app puts it on the dock without anybody touching this, and
configuring is only ever a matter of claiming what should move.

Which installed app a module belongs to is Frappe's answer, already in the
boot: each `module_sidebars` entry's `app` (its sidebar's own, else where the
module is placed -- `modules.txt`, or a custom module's `app_name`), with the
boot's `module_app` as the fallback. A companion app's modules go to the
app Frappe mounts it on (`app_hosts`). A module neither places is grouped
under "Other", which is the honest answer and a hint that it wants an app or
claiming.

An installed app Frappe does not list as somewhere to go has no entry of its own
either: its modules are grouped under Other. Frappe lists an app on its Apps screen
and in the sidebar's Apps switcher only when the app asks to be
(`add_to_apps_screen`) and is not mounted on another app's Dock; Telephony and
Print Designer do not ask, so they are plumbing rather than destinations
(`listed_apps`). A Desk App that stands for such an app brings it back.

An installed app's own order is its shipped `Dock` (`shipped_docks`): the
modules it names, in its order, and none of the ones it hides -- ERPNext ships
CRM and Support hidden. A hidden module is off the dock, not moved to Other,
until a Desk App lists it. The Dock's site and user layers are not read:
the dock replaces Manage Dock, so nothing could edit them any more. Modules the
Dock does not name, and every module of an app that ships none, follow in the
dock's own order (`_default_order`).

A module is one or more shells in the boot: usually one sidebar named after
it, but a renamed sidebar keeps its own name (ERPNext's "Quality" is module
"Quality Management") and a module may have two. A row claims the module, so
it claims all of them, and the dock has one entry per shell.

Two rules
---------
*A module is in one app.* The header has to say which app and module the page
you are on belongs to, and a module in two apps has no answer. Enforced when a
`Desk App` is saved; here the first to claim one keeps it, so a conflict
that got past the form still resolves the same way every time.

*A role-restricted app still claims its modules.* Otherwise somebody without
the role would find the same modules back under their installed app, and the
restriction would only have moved them. Roles decide who sees the app on the
dock; they are not permission. A module a person cannot open is not in their
`module_sidebars` to begin with.
"""

import frappe
from frappe import _

from opendesk.open_desk import module_tiles

APP = "Desk App"
APP_MODULE = "Desk App Module"

# Where a module goes when nothing says which app it belongs to.
OTHER = "Other"
OTHER_LOGO = "/assets/opendesk/images/opendesk-other-logo.svg"

# A Desk App bound to an installed app either adds its modules table to
# what the app already holds, or replaces it.
ADD = "Add"
REPLACE = "Replace"

# What a row of a Desk App's modules table is. Unset is a module, the
# field's default.
MODULE = "Module"
CATEGORY = "Category"
SPACER = "Spacer"

# The module an app starts from, when its name does not say so already.
HOME = "home"

# A `dock_after` that puts an app first on the dock rather than after another.
TOP = "top"


# The site-level half of the dock: everything `resolve` reads except the user. Its value is
# handed to `resolve` as keywords and outlives a restart, so the key names its shape: change
# what `_site_inputs` holds, and the version goes up, or new code would read an old copy
# between a deploy's restart and its migrate.
CACHE_KEY = "opendesk_dock:v3"


def extend_bootinfo(bootinfo: "frappe._dict") -> None:
	"""Hand the desk its dock, when the dock is switched on.

	On the boot rather than behind a call, so the dock draws with the sidebar
	instead of after it. Left off entirely while the switch is off: the dock's
	script checks the same flag and installs nothing.

	Runs after Frappe has built `module_sidebars` and `app_data` for this user
	(`load_desktop_data`, before any `boot_session` hook), and reads the modules
	and the installed apps from there, so the dock offers exactly what the desk
	would. The boot
	is otherwise left as Frappe made it: which dock app each module is in is
	written into the desk's copy by the browser (`js/boot_arrangement.js`),
	which can write it again whenever Frappe replaces that copy.
	"""
	from opendesk.open_desk import settings

	try:
		if not settings.feature_enabled(settings.ENABLE_DOCK):
			return
		module_sidebars = bootinfo.get("module_sidebars")
		if module_sidebars is None:
			return
		bootinfo.desk_apps = desk_apps(module_sidebars=module_sidebars, app_data=bootinfo.get("app_data"))
		bootinfo.opendesk_site_logo = site_logo()
	except Exception:
		# The boot is every page load: a broken dock must not take the desk with it.
		# Without `desk_apps` the browser half installs nothing.
		bootinfo.pop("desk_apps", None)
		settings.log_boot_failure("Open Desk dock: kept Frappe's Dock")


def site_logo() -> str | None:
	"""The site's own logo, for the mark at the top of the dock, or None for the home icon.

	What Frappe's `get_app_logo` reads first -- Website Settings' App Logo, then Navbar
	Settings' -- but not its fallback to the installed apps' `app_logo_url` hooks, which
	is usually Frappe's own logo: a site that has not set one gets the home icon.
	"""
	return (
		frappe.get_website_settings("app_logo")
		or frappe.get_cached_value("Navbar Settings", "Navbar Settings", "app_logo")
		or None
	)


def desk_apps(
	user: str | None = None,
	module_sidebars: dict | None = None,
	everything: bool = False,
	app_data: list[dict] | None = None,
) -> list[dict]:
	"""The dock for `user` (the session user by default), read from the site.

	`module_sidebars` and `app_data` are the boot's, when there is a boot;
	otherwise Frappe builds them again for the session user.
	"""
	user = user or frappe.session.user
	if module_sidebars is None:
		from frappe.boot import get_module_sidebars

		module_sidebars = get_module_sidebars()
	if app_data is None:
		from frappe.boot import get_app_data

		app_data = get_app_data()
	app_meta, frontends = apps_from_app_data(app_data)
	return resolve(
		**_site_inputs(),
		app_meta=app_meta,
		frontends=frontends,
		sidebars=_shells(module_sidebars),
		hosts=app_hosts(),
		user=user,
		user_roles=set(frappe.get_roles(user)),
		everything=everything,
	)


def app_hosts() -> dict[str, str]:
	"""Each companion app and the installed app whose dock it mounts on.

	Frappe shows a companion's modules (India Compliance's, say) as its host's
	(ERPNext's), so the dock groups them there too. Frappe's answer, asked per
	request: it changes with the site's Dock records, which this does not watch.
	"""
	try:
		from frappe.boot import get_app_rail_host_map
	except ImportError:
		return {}
	return get_app_rail_host_map() or {}


def _site_inputs() -> dict:
	"""What the dock is built from that is the same for everyone, cached.

	Not the installed apps' titles, logos and frontends: Frappe gates those per
	user (`add_to_apps_screen`'s `has_permission`), so they come from this
	user's `app_data` instead (see `apps_from_app_data`).

	Five queries per desk load otherwise, for data that
	changes when an administrator edits the dock or installs an app. Kept in
	`frappe.client_cache` (process-local, invalidated through redis) and dropped
	by `clear_cache`, which the doc events on everything read here call. An app
	installed, removed or migrated needs no call: `install_app`, `remove_app`
	and migrate each run `frappe.clear_cache()`, which drops every key the site
	has.
	"""
	return frappe.client_cache.get_value(
		CACHE_KEY,
		generator=lambda: {
			"configured": _configured(),
			"installed_apps": active_apps(),
			"module_apps": module_apps(),
			"docks": shipped_docks(),
			"listed": listed_apps(),
		},
	)


def active_apps() -> list[str]:
	"""The installed apps the site has not switched off, in install order: what the dock offers.

	Frappe 17 lets a site disable an installed app without uninstalling it
	(`frappe.get_active_apps`): its modules leave the desk, and Frappe's Dock and Apps screen
	pass it over. The dock does the same -- and a Desk App standing for it waits, as for an app
	not installed (`resolve`), to come back when the app is enabled again. Enabling or disabling
	an app clears every cache, `_site_inputs` included. Before Frappe 17, every installed app.

	A Desk App's own "hidden" is the dock's alone: the app stays on Frappe's Apps screen and its
	modules can still be opened. A disabled app is off everywhere.
	"""
	get_active_apps = getattr(frappe, "get_active_apps", None)
	if callable(get_active_apps):
		return list(get_active_apps())
	return frappe.get_installed_apps()


def listed_apps() -> list[str]:
	"""The installed apps Frappe lists as somewhere to go, in install order.

	Frappe's own rule for its Apps screen and its sidebar's Apps switcher
	(`frappe.boot.get_app_data`'s `on_apps_screen`): the app declares
	`add_to_apps_screen` and is not mounted on another app's Dock. Read from the
	hooks rather than from `app_data`, which also turns an app off for a user its
	`has_permission` refuses -- that is not this app's to second-guess here.
	"""
	hosts = app_hosts()
	return [
		app
		for app in active_apps()
		if frappe.get_hooks("add_to_apps_screen", app_name=app) and app not in hosts
	]


def clear_cache(*args, **kwargs) -> None:
	"""Forget the dock's site-level inputs: now, and again when this transaction ends.

	A doc event, so it takes the hook's arguments. Again at the end because a read
	in between, inside this transaction, would put back a copy that is right for
	only one of commit and rollback.
	"""
	frappe.client_cache.delete_value(CACHE_KEY)
	if db := getattr(frappe.local, "db", None):
		db.after_commit.add(_forget)
		db.after_rollback.add(_forget)


def _forget() -> None:
	frappe.client_cache.delete_value(CACHE_KEY)


def resolve(
	*,
	configured: list[dict],
	sidebars: list[dict],
	installed_apps: list[str],
	app_meta: dict[str, dict],
	module_apps: dict[str, str],
	user: str,
	user_roles: set[str],
	frontends: dict[str, str] | None = None,
	hosts: dict[str, str] | None = None,
	docks: dict[str, dict] | None = None,
	listed: list[str] | None = None,
	everything: bool = False,
) -> list[dict]:
	"""The dock, from plain data: every app at its default place or where it was moved to.

	`configured` is the enabled Desk Apps in title order, each with its
	`modules` rows (`type`, `module`, and a Category's `label`), `roles`, and optionally the
	`installed_app` it stands for, its `module_mode`, whether it is `hidden`,
	its `apps_screen` and the app it follows on the dock (`dock_after`).
	`sidebars` is the shells this user may open, from `module_sidebars`
	(`name`, `module`, `app`, `label`, `header_icon`; see `_shells`). The rest
	say what an installed app is called (`app_meta`) and where its own frontend
	is, outside the desk (`frontends`), both as this user's `app_data` has them;
	which app a module belongs to (`module_apps`, keyed by scrubbed module name,
	as the boot's `module_app` is); and which installed app a companion app
	mounts on (`hosts`, see `app_hosts`); each installed app's shipped
	order and hidden shells (`docks`, see `shipped_docks`); and which installed
	apps Frappe lists as somewhere to go (`listed`, see `listed_apps`; all of them
	when not given). An unlisted app's modules go to Other unless a Desk App
	stands for it.

	Every entry carries `frontend` -- `{label, url}` or None -- beside its
	`modules`, one per shell (`shell`, `label`, `icon`): a module may carry a
	`category` or `space_before` to draw above it (see `_layout`). An app is on
	the dock if it has either: a frontend with no desk modules (Frappe Builder,
	say) is somewhere to go too. `app_name` is the name the desk's boot knows it
	by (`js/boot_arrangement.js`); a configured entry also names its `record`.

	`everything` is the dock as an editor needs it (`arrange.py`): hidden and
	role-restricted apps stay in, at their place, marked `hidden`, and so do
	apps with nothing to offer, and so do unlisted apps, marked `hidden` and
	`unlisted`, each with the modules it would hold once shown (`own_modules`).
	"""
	frontends = frontends or {}
	hosts = hosts or {}
	docks = docks or {}
	# A record for an app since uninstalled, or switched off (`active_apps`), waits for it: it
	# claims nothing and is not drawn, not even for an editor, until the app is back.
	configured = [
		app
		for app in configured
		if not app.get("installed_app") or app["installed_app"] in (*installed_apps, OTHER)
	]
	by_module: dict[str, list[dict]] = {}
	for sidebar in sidebars:
		by_module.setdefault(sidebar.get("module") or sidebar["name"], []).append(sidebar)
	claimed: set[str] = set()

	# Claims first, all of them, so what is left for the installed apps is known
	# before any entry is drawn: a bound app early on the dock still gets the
	# modules no later app claims.
	claims: list[list[dict]] = []
	for app in configured:
		entries = []
		for row in app["modules"]:
			kind = row_type(row)
			if kind in (CATEGORY, SPACER):
				entries.append(_marker(row))
				continue
			if kind != MODULE:
				continue
			shells = [s for s in by_module.get(row.get("module") or "", []) if s["name"] not in claimed]
			# Gone since, out of this user's reach, or already claimed by an
			# earlier app.
			for sidebar in shells:
				claimed.add(sidebar["name"])
				entries.append(_entry(sidebar, row.get("desktop_image")))
		claims.append(entries)

	# Which configured app stands for which installed app: the first enabled one
	# to name it, as with claims. A later one naming the same app is only a
	# grouping of its own.
	bound: dict[str, int] = {}
	for index, app in enumerate(configured):
		target = app.get("installed_app")
		if target and target not in bound and (target in installed_apps or target == OTHER):
			bound[target] = index

	# Installed apps that have no entry of their own unless a record brings them back.
	unlisted = set(installed_apps) - set(installed_apps if listed is None else listed)

	grouped: dict[str, list[dict]] = {}
	# What each unlisted app would hold once a record brings it back, for an editor to show.
	unlisted_own: dict[str, list[dict]] = {}
	for sidebar in sidebars:
		if sidebar["name"] in claimed:
			continue
		owner = default_app_of(sidebar.get("app"), sidebar.get("module"), module_apps, hosts, installed_apps)
		# Hidden by the app's Dock: off the dock until a Desk App lists it, not sent to Other.
		if sidebar["name"] in (docks.get(owner) or {}).get("hidden", ()):
			continue
		if owner in unlisted and owner not in bound:
			unlisted_own.setdefault(owner, []).append(_entry(sidebar))
			owner = OTHER
		grouped.setdefault(owner, []).append(_entry(sidebar))

	# Replacing drops what the app would have held into Other, where every
	# sidebar nothing places goes -- unless it is Other that replaces, when
	# there is nowhere further for them to go.
	for target, index in bound.items():
		if configured[index].get("module_mode") == REPLACE and target != OTHER:
			grouped.setdefault(OTHER, []).extend(grouped.pop(target, []))

	dock: list[dict] = []
	for index, app in enumerate(configured):
		target = next((t for t, i in bound.items() if i == index), None)
		meta = app_meta.get(target) or {}
		# Listed rows in the table's order, then (Add) what the app already held,
		# in the default order.
		entries = list(claims[index])
		if target and app.get("module_mode") != REPLACE:
			names = {app["title"], meta.get("title") or target, target}
			entries += _default_order(grouped.get(target) or [], names, docks.get(target))
		entries = _layout(entries)

		# Hidden, or restricted to roles this user lacks: off the dock, and what it
		# holds goes with it rather than back to an installed app.
		roles = set(app.get("roles") or ())
		if not everything:
			if app.get("hidden"):
				continue
			if roles and not roles & user_roles:
				continue

		own_mark = app.get("logo") or app.get("icon")
		color = app.get("color") or None
		logo = app.get("logo") or (None if own_mark else _default_logo(target, meta))
		if color and logo and not app.get("logo"):
			# The installed app's own logo, in this record's colour where it can be redrawn.
			logo = module_tiles.recoloured_logo(logo, color) or logo
		frontend = _frontend(
			app["title"],
			app.get("frontend_url") or (frontends.get(target) if target else None),
			app.get("frontend_label"),
		)
		if entries or frontend or everything:
			dock.append(
				{
					# A bound app keeps its installed app's key: the browser finds an
					# app by it, and other apps anchor to it (`dock_after`).
					"key": f"app:{target}" if target else f"desk-app:{app['name']}",
					"app_name": _app_name(target) if target else f"desk-app:{app['name']}",
					"record": app["name"],
					"installed_app": target,
					**({"hidden": bool(app.get("hidden")), "roles": sorted(roles)} if everything else {}),
					"title": app["title"],
					"icon": app.get("icon") or None,
					"logo": logo,
					"color": color,
					"configured": True,
					"modules": entries,
					"frontend": frontend,
					# How the Apps screen shows it; see `apps_screen.py`.
					"apps_screen": app.get("apps_screen") or None,
				}
			)

	for app_name in [*installed_apps, OTHER]:
		if app_name in bound:
			continue
		# Its modules are in Other; an editor still lists it, off the dock, to bring back.
		if app_name in unlisted and not everything:
			continue
		entries = grouped.get(app_name) or []
		meta = app_meta.get(app_name) or {}
		title = meta.get("title") or (OTHER if app_name == OTHER else app_name)
		frontend = _frontend(title, frontends.get(app_name))
		if not entries and not frontend and not everything:
			continue
		dock.append(
			{
				"key": f"app:{app_name}",
				"app_name": _app_name(app_name),
				"installed_app": app_name,
				**(
					{
						"hidden": app_name in unlisted,
						"unlisted": app_name in unlisted,
						"roles": [],
						# Its modules, now under Other, as it would hold them once shown.
						**(
							{
								"own_modules": _default_order(
									unlisted_own.get(app_name) or [], {title, app_name}, docks.get(app_name)
								)
							}
							if app_name in unlisted
							else {}
						),
					}
					if everything
					else {}
				),
				"title": title,
				"icon": None,
				"logo": _default_logo(app_name, meta),
				"configured": False,
				"modules": _default_order(entries, {title, app_name}, docks.get(app_name)),
				"frontend": frontend,
			}
		)
	# Ordered over every app, shown or not, so an app anchored to one this user
	# does not see still finds its place.
	defaults = [f"app:{name}" for name in [*installed_apps, OTHER]]
	anchors = {}
	for index, app in enumerate(configured):
		target = next((t for t, i in bound.items() if i == index), None)
		key = f"app:{target}" if target else f"desk-app:{app['name']}"
		anchors[key] = (app.get("dock_after") or "").strip() or (None if target else TOP)
	position = {key: i for i, key in enumerate(dock_sequence(defaults, anchors))}
	dock.sort(key=lambda entry: position.get(entry["key"], len(position)))
	return dock


def dock_sequence(defaults: list[str], anchors: dict[str, str | None]) -> list[str]:
	"""Every app's key in dock order: the default order, with each anchored app after its anchor.

	`defaults` is the apps that have a default place, in that order. `anchors`
	maps the apps with a record to what they follow -- another app's key, `TOP`,
	or None for "where it would be anyway". Apps anchored to the same one keep
	the order `anchors` lists them in. An app whose anchor never turns up (gone,
	or a loop) goes to its default place, or the top if it has none.
	"""
	moved = {key: anchor for key, anchor in anchors.items() if anchor}
	order = [key for key in defaults if key not in moved]
	last_after: dict[str, str] = {}

	def insert(key: str, anchor: str) -> None:
		previous = last_after.get(anchor) or (None if anchor == TOP else anchor)
		order.insert(order.index(previous) + 1 if previous else 0, key)
		last_after[anchor] = key

	pending = list(moved.items())
	while pending:
		waiting = [(key, anchor) for key, anchor in pending if anchor != TOP and anchor not in order]
		for key, anchor in pending:
			if (key, anchor) not in waiting:
				insert(key, anchor)
		if len(waiting) == len(pending):
			break
		pending = waiting

	# What could not be placed: back where it would have been, or at the top.
	for key, _anchor in pending:
		if key in defaults:
			later = [k for k in defaults[defaults.index(key) + 1 :] if k in order]
			order.insert(order.index(later[0]) if later else len(order), key)
		else:
			insert(key, TOP)
	return order


def _app_name(app_name: str) -> str:
	"""The name Frappe's boot knows a dock app by: the installed app's own, or one for Other."""
	return "opendesk-other" if app_name == OTHER else app_name


def _default_logo(app_name: str | None, meta: dict) -> str | None:
	"""An installed app's logo as Frappe's Apps screen has it, or Other's own."""
	return meta.get("logo") or (OTHER_LOGO if app_name == OTHER else None)


def _frontend(app_title: str, url: str | None, label: str | None = None) -> dict | None:
	"""An app's own frontend as the menus offer it, or None if it has none."""
	url = (url or "").strip()
	if not url:
		return None
	return {"label": (label or "").strip() or _("{0} app").format(app_title), "url": url}


def is_desk_route(url: str) -> bool:
	"""Whether a link leads into the desk rather than out of it.

	Several apps point their apps screen entry at a desk page (Frappe HR at
	`/desk/hr-setup`, Lending at `/app/lending`); that is the app's desk home,
	which its sidebars already reach, not a frontend of its own. `/app` is still
	one: 16.50's desk is `/desk`, and `/app` only redirects there.
	"""
	path = (url or "").strip().split("?")[0].split("#")[0].rstrip("/")
	return path in ("/app", "/desk") or path.startswith(("/app/", "/desk/"))


def installed_app_of(sidebar: dict, module_apps: dict[str, str]) -> str | None:
	"""Which installed app a module belongs to, asked in the order the module docstring gives."""
	if sidebar.get("app"):
		return sidebar["app"]
	module = (sidebar.get("module") or "").strip()
	return module_apps.get(frappe.scrub(module)) if module else None


def default_app_of(
	app: str | None,
	module: str | None,
	module_apps: dict[str, str],
	hosts: dict[str, str],
	installed_apps,
) -> str:
	"""The installed app a module is grouped under when no Desk App claims it, or Other.

	A companion app's module goes to the app it mounts on, as Frappe's desk shows it.
	"""
	owner = installed_app_of({"app": app, "module": module}, module_apps)
	owner = hosts.get(owner, owner)
	return owner if owner in installed_apps else OTHER


def _default_order(entries: list[dict], app_names: set[str], dock: dict | None = None) -> list[dict]:
	"""Modules nobody has put in order: the app's Dock order, else its landing module, then the rest.

	An app that ships a Dock has said what order its modules go in, and those it
	names go first, in that order. The rest -- every module of an app that ships
	none, and custom modules placed in one that does -- are alphabetical, by what
	the menus call them, except that a module called "Home", or called what the
	app is (Education's "Education", Lending's "Lending"), is where the app
	starts, and goes first. Home before the app-named one if an app has both.
	A Desk App's modules table is an order someone chose, and is never
	passed through this.
	"""
	names = {name.casefold() for name in app_names if name}
	shipped = {shell: index for index, shell in enumerate((dock or {}).get("order") or ())}

	def rank(entry: dict) -> tuple[int, int, int, str]:
		if entry["shell"] in shipped:
			return 0, shipped[entry["shell"]], 0, ""
		keys = {entry["shell"].casefold(), entry["label"].casefold()}
		landing = 0 if HOME in keys else 1 if keys & names else 2
		return 1, 0, landing, entry["label"].casefold()

	return sorted(entries, key=rank)


def row_type(row) -> str:
	"""What a modules table row is: its type, or a module when unset.

	Any other value is no row the dock knows, and `resolve` skips it.
	"""
	return row.get("type") or MODULE


def _marker(row: dict) -> dict:
	"""A Category or Spacer row, as `_layout` reads it. A Category with no label is a Spacer."""
	label = (row.get("label") or "").strip()
	if row_type(row) == CATEGORY and label:
		return {"category": label}
	return {"space_before": True}


def _layout(rows: list[dict]) -> list[dict]:
	"""Modules only, each Category or Spacer moved onto the module that follows it.

	So everything that counts or picks modules -- the "N modules" subtitle, the
	landing module, the last one opened -- sees modules and nothing else, and a
	browser that drops a module this user cannot open moves what was above it
	on to the next (the dock does the same).

	A Category ends whatever came before it, so a Spacer just before or just
	after one adds nothing. One with no module after it in the table heads what
	the app holds besides (Add mode), and with nothing there either is dropped,
	as is a Category whose modules are all gone. A gap over the first module is
	dropped too: there is nothing above it to keep apart from.
	"""
	laid_out: list[dict] = []
	pending: dict = {}
	for row in rows:
		if "shell" not in row:
			if "category" in row or "category" not in pending:
				pending = dict(row)
			continue
		laid_out.append({**row, **pending})
		pending = {}
	if laid_out:
		laid_out[0].pop("space_before", None)
	return laid_out


def _entry(sidebar: dict, desktop_image: str | None = None) -> dict:
	entry = {
		"shell": sidebar["name"],
		"label": sidebar.get("label") or sidebar["name"],
		"icon": sidebar.get("header_icon") or None,
	}
	# Only the Apps screen draws it (`apps_screen.py`), so it is carried only
	# when a row sets one.
	if desktop_image:
		entry["desktop_image"] = desktop_image
	return entry


def _configured() -> list[dict]:
	apps = frappe.get_all(
		APP,
		filters={"enabled": 1},
		fields=[
			"name",
			"title",
			"icon",
			"logo",
			"color",
			"frontend_url",
			"frontend_label",
			"installed_app",
			"module_mode",
			"hidden",
			"apps_screen",
			"dock_after",
		],
		order_by="title asc",
	)
	if not apps:
		return []

	names = [app.name for app in apps]
	rows = frappe.get_all(
		APP_MODULE,
		filters={"parent": ["in", names], "parenttype": APP},
		fields=["parent", "type", "module", "label", "desktop_image"],
		order_by="parent asc, idx asc",
		parent_doctype=APP,
	)
	roles = frappe.get_all(
		"Has Role",
		filters={"parent": ["in", names], "parenttype": APP},
		fields=["parent", "role"],
		parent_doctype=APP,
	)

	for app in apps:
		app["modules"] = [row for row in rows if row.parent == app.name]
		app["roles"] = [row.role for row in roles if row.parent == app.name]
	return apps


def _shells(module_sidebars: dict) -> list[dict]:
	"""The shells in Frappe's `module_sidebars`, as `resolve` reads them, in the boot's order."""
	return [
		{
			"name": name,
			"module": sidebar.get("module") or name,
			"app": sidebar.get("app"),
			"label": sidebar.get("label") or name,
			"header_icon": sidebar.get("header_icon"),
		}
		for name, sidebar in module_sidebars.items()
	]


def shipped_docks() -> dict[str, dict]:
	"""Each installed app's shipped Dock: the shells it names, in order, and the ones it hides.

	Frappe's own base for an app's Dock (`get_app_base`): the record the app
	ships, with the rows of companion apps mounted on it appended, as Frappe's
	Dock has it before any site or user layer. The same for everyone, so cached
	with the rest of `_site_inputs`; an app's shipped Dock changes only when it is
	installed or migrated, which clears every cache. Rows that open a workspace or
	a URL are pins, not modules, and the dock has no place for them.
	"""
	from frappe.desk.doctype.dock.dock import get_app_base

	docks = {}
	for app in active_apps():
		rows = [row for row in get_app_base(app) if row.get("link_type") == "Sidebar"]
		if rows:
			docks[app] = {
				"order": [row["link_to"] for row in rows],
				"hidden": [row["link_to"] for row in rows if row.get("hidden")],
			}
	return docks


def module_apps() -> dict[str, str]:
	"""Which installed app each module belongs to, keyed by scrubbed module name.

	Frappe's own map, the one its boot carries as `module_app`: `modules.txt`,
	then each custom Module Def's `app_name` where that app is installed.
	"""
	from frappe.boot import get_boot_module_app

	return get_boot_module_app()


def apps_from_app_data(app_data: list[dict]) -> tuple[dict[str, dict], dict[str, str]]:
	"""Each installed app's title and logo, and its own frontend, from Frappe's `app_data`.

	`app_data` is what Frappe's Apps screen draws from, built per user
	(`frappe.boot.get_app_data`): the title and logo from `add_to_apps_screen`,
	else the `app_title` and `app_logo_url` hooks, and the route from
	`add_to_apps_screen`, else `app_home` -- empty when the app's
	`has_permission` turns this user away, so the dock never offers a frontend
	Frappe would hide. Routes that only open a desk page are not frontends.

	Read before the Apps screen is arranged from the dock (`apps_screen.py`),
	which rewrites these entries.
	"""
	meta: dict[str, dict] = {}
	frontends: dict[str, str] = {}
	for entry in app_data or []:
		app_name = entry.get("app_name")
		if not app_name:
			continue
		logo = entry.get("app_logo_url")
		# Frappe hands a hook's value over as the hook's list.
		if isinstance(logo, list | tuple):
			logo = next(iter(logo), None)
		meta[app_name] = {"title": entry.get("app_title") or app_name, "logo": logo or None}
		url = (entry.get("app_route") or "").strip()
		if url and not is_desk_route(url):
			frontends[app_name] = url
	return meta, frontends
