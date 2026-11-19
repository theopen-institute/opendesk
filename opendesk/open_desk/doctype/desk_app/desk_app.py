# Copyright (c) 2026, Peter and contributors
# For license information, please see license.txt

"""An entry on the dock: a named group of modules, or the stand-in
for an installed app.

What the dock makes of these, and of the modules none of them claims, is
`opendesk.open_desk.desk_apps`. This controller only refuses the
shapes that resolver could not give a stable answer for:

- an installed app that is not installed, or one another enabled record
  already stands for. The dock has one place for each app, so the second is
  refused and told which record has it;

- a module row with no module, or a Category with no heading. A Category or
  Spacer row names no module; one picked before the type was changed is
  dropped rather than left to claim it unseen;
- the same module twice in one app, which would put it in the menu twice;
- a module another enabled app already holds. The header has to say which app
  the page you are on belongs to, so the second claim is refused and told which
  app has it. A disabled app claims nothing, so this is checked only while
  enabled -- and again when a disabled one is switched back on.

It also warns, without refusing, when a picture is a private file, which the
dock and the Apps screen cannot load.

And it tidies up after an app is uninstalled (`before_app_uninstall`,
`after_app_uninstall`).
"""

import re

import frappe
from frappe import _
from frappe.model.document import Document

from opendesk.open_desk import module_tiles
from opendesk.open_desk.desk_apps import (
	ADD,
	APP,
	APP_MODULE,
	MODULE,
	OTHER,
	REPLACE,
	SPACER,
	row_type,
)


class DeskApp(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.core.doctype.has_role.has_role import HasRole
		from frappe.types import DF

		from opendesk.open_desk.doctype.desk_app_module.desk_app_module import (
			DeskAppModule,
		)

		apps_screen: DF.Literal["Default", "One Icon", "Icon per Module", "App and Module Icons", "Hidden"]
		color: DF.Color | None
		enabled: DF.Check
		frontend_label: DF.Data | None
		frontend_url: DF.Data | None
		hidden: DF.Check
		icon: DF.Icon | None
		installed_app: DF.Autocomplete | None
		logo: DF.AttachImage | None
		module_mode: DF.Literal["Add", "Replace"]
		modules: DF.Table[DeskAppModule]
		dock_after: DF.Data | None
		roles: DF.Table[HasRole]
		title: DF.Data
	# end: auto-generated types

	def validate(self):
		self.dock_after = (self.dock_after or "").strip() or None
		self.validate_marks()
		self.validate_installed_app()
		self.validate_modules()
		self.warn_private_images()

	def validate_marks(self):
		"""Refuse what the dock and the Apps screen would put into the page as code.

		The frontend link becomes a link everyone on the site clicks, so it has to be a page
		on this site or a web address: anything else (`javascript:`) would run as whoever
		clicked it. The icon is the name of one of the desk's icons and goes into the page
		as part of a reference to it, so it is a plain name and nothing more.
		"""
		self.frontend_url = (self.frontend_url or "").strip() or None
		if self.frontend_url and not re.match(r"^(/(?!/)|https?://)", self.frontend_url, re.I):
			frappe.throw(
				_("The frontend link must be a page on this site (/...) or a web address (https://...).")
			)
		self.icon = (self.icon or "").strip() or None
		if self.icon and not re.fullmatch(r"[\w-]+", self.icon):
			frappe.throw(_("{0} is not an icon name.").format(frappe.bold(self.icon)))
		# Drawn into SVG pictures, so a hex colour and nothing else.
		color = (self.color or "").strip()
		self.color = module_tiles.hex_color(color)
		if color and not self.color:
			frappe.throw(_("{0} is not a colour: use one like #2E7D32.").format(frappe.bold(color)))

	def validate_installed_app(self):
		self.installed_app = (self.installed_app or "").strip() or None
		if not self.installed_app:
			return
		# Checked only when it changes, so a record for an app since uninstalled
		# can still be saved (the dock ignores it until the app is back).
		if self.has_value_changed("installed_app") and self.installed_app not in installed_app_names():
			frappe.throw(_("{0} is not an installed app.").format(frappe.bold(self.installed_app)))
		if not self.enabled:
			return
		held = frappe.get_all(
			APP,
			filters={"enabled": 1, "installed_app": self.installed_app, "name": ["!=", self.name or ""]},
			pluck="name",
			limit=1,
		)
		if held:
			frappe.throw(
				_("{0} already stands for {1}. An installed app can have only one enabled record.").format(
					frappe.bold(held[0]), frappe.bold(self.installed_app)
				)
			)

	def validate_modules(self):
		for row in self.modules:
			row.type = row_type(row)
			if row.type == MODULE:
				if not row.module:
					frappe.throw(_("Row {0}: pick a module.").format(row.idx))
				# A module is called what its sidebar calls it (see `desk_apps`).
				row.label = None
				continue
			row.module = None
			row.desktop_image = None
			if row.type == SPACER:
				row.label = None
			elif not (row.label or "").strip():
				frappe.throw(_("Row {0}: a Category needs a heading.").format(row.idx))

		seen = set()
		for row in self.module_rows():
			if row.module in seen:
				frappe.throw(
					_("Row {0}: {1} is already in this app.").format(row.idx, frappe.bold(row.module))
				)
			seen.add(row.module)

		if not self.enabled:
			return
		held = claimed_elsewhere(self.name)
		for row in self.module_rows():
			if row.module in held:
				frappe.throw(
					_("Row {0}: {1} is already in {2}. A module can belong to only one app.").format(
						row.idx, frappe.bold(row.module), frappe.bold(held[row.module])
					)
				)

	def after_rename(self, old: str, new: str, merge: bool = False):
		"""Keep the apps placed after this one there: an anchor names a site app by its record."""
		frappe.db.set_value(
			APP,
			{"dock_after": f"desk-app:{old}"},
			"dock_after",
			f"desk-app:{new}",
			update_modified=False,
		)

	def warn_private_images(self):
		"""Say so when a picture is a private file, which the dock and the Apps screen cannot load.

		A warning, not a refusal: the record is still right, only its picture
		is missing until the file is made public.
		"""
		private = [
			_("Logo") if (self.logo or "").startswith("/private/") else None,
			*(
				_("Row {0}: Apps Screen Image").format(row.idx)
				for row in self.modules
				if (row.desktop_image or "").startswith("/private/")
			),
		]
		if private := [p for p in private if p]:
			frappe.msgprint(
				_("These are private files, so they will not show: {0}. Make each file public.").format(
					", ".join(private)
				),
				indicator="orange",
				alert=True,
			)

	def module_rows(self):
		"""The rows that are modules, not Categories or Spacers."""
		return [row for row in self.modules if row.module]


def claimed_elsewhere(app: str | None) -> dict[str, str]:
	"""Every module an enabled app other than `app` holds, and which app holds it."""
	others = frappe.get_all(APP, filters={"enabled": 1, "name": ["!=", app or ""]}, pluck="name")
	if not others:
		return {}
	rows = frappe.get_all(
		APP_MODULE,
		filters={"parent": ["in", others], "parenttype": APP, "module": ["is", "set"]},
		fields=["parent", "module"],
		parent_doctype=APP,
	)
	return {row.module: row.parent for row in rows}


def installed_app_names() -> list[str]:
	return [*frappe.get_installed_apps(), OTHER]


@frappe.whitelist()
def installed_app_options() -> list[dict]:
	"""What the Installed App field offers: each installed app by title, then Other."""
	frappe.has_permission(APP, "read", throw=True)
	from frappe.boot import get_app_data

	from opendesk.open_desk.desk_apps import apps_from_app_data

	meta = apps_from_app_data(get_app_data())[0]
	return [
		{"value": name, "label": (meta.get(name) or {}).get("title") or name}
		for name in installed_app_names()
	]


# Uninstalling an app
# -------------------
#
# Frappe deletes every record that links to an uninstalled app's modules, Desk App Module rows
# among them. A record in Replace mode can be left listing no module at all, which would send
# every module of its app to Other -- after a reinstall too. Nobody chose that, so such a record
# goes back to Add, and the app keeps its own modules. A Replace record that listed none before
# the uninstall was left that way on purpose, and is left alone. (A dry run deletes nothing, so
# nothing changes either.)


def before_app_uninstall(app_name: str) -> None:
	"""Note how many modules each Replace record lists, before Frappe deletes any."""
	frappe.flags.opendesk_replace_rows = _replace_module_counts()


def after_app_uninstall(app_name: str) -> None:
	"""Switch to Add each Replace record the uninstall left listing no module."""
	before = frappe.flags.pop("opendesk_replace_rows", None) or {}
	emptied = [name for name, count in _replace_module_counts().items() if not count and before.get(name)]
	for name in emptied:
		doc = frappe.get_doc(APP, name)
		doc.module_mode = ADD
		doc.save(ignore_permissions=True)
	if emptied:
		# Frappe has committed the uninstall before calling this, and commits nothing after it.
		frappe.db.commit()


def _replace_module_counts() -> dict[str, int]:
	names = frappe.get_all(APP, filters={"module_mode": REPLACE}, pluck="name")
	if not names:
		return {}
	rows = frappe.get_all(
		APP_MODULE,
		filters={"parent": ["in", names], "parenttype": APP, "module": ["is", "set"]},
		fields=["parent"],
		parent_doctype=APP,
	)
	counts = dict.fromkeys(names, 0)
	for row in rows:
		counts[row.parent] += 1
	return counts
