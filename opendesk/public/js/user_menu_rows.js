// Rows of this app's own in the desk's user menu (your avatar).
//
// Frappe 16.60 lists the menu's rows in `Sidebar.user_menu_options`, which both the user menu
// (`create_user_menu`, for the sidebar's user button and the Dock's avatar) and the phone's Profile
// page read. Where that method is there, it is wrapped: its rows pass through every change
// registered here, in the order they were registered. The Profile page only follows a row's `href`
// or `onclick`, and leaves Manage Dock out because there is no dock on a phone to arrange; so
// outside the user menu itself, a row it could not follow (a submenu alone, Help) or one marked
// `menu_only` (Manage Desk Apps) is left out of what it lists.
//
// Frappe 16.50 to 16.5x builds the menu in `create_user_menu` alone, as a `frappe.ui.Dropdown` it
// makes there and does not hand back, from a list of rows it writes inline. There is no hook to add
// a row. So there, for as long as that one call runs, the first Dropdown made -- the user menu --
// passes its rows through the same changes, and the call puts Frappe's Dropdown back whatever
// happens. Any other Dropdown made meanwhile is Frappe's, untouched.
//
// A feature registers a change with `opendesk.user_menu.add(change)`, which says whether the change
// will reach the menu -- so a feature that also takes a row away elsewhere can leave it there when
// it would not. A change takes the menu's groups (`[{group, options}]`) and the sidebar, and
// returns the groups to show; it is called once per menu made, and a row's `condition` is how a
// row follows state. A change that throws is skipped, so one broken feature cannot take the menu
// away.
//
// Nothing is installed until something registers, and nothing at all if Frappe has moved what this
// hangs on: then the menu is simply Frappe's.
frappe.provide("opendesk.user_menu");

(function () {
	const changes = [];
	let installed = false;

	opendesk.user_menu.add = function (change) {
		if (typeof change !== "function") return false;
		install();
		if (installed) changes.push(change);
		return installed;
	};

	function install() {
		if (installed) return;
		const Sidebar = frappe.ui && frappe.ui.Sidebar;
		if (
			!Sidebar ||
			!frappe.ui.Dropdown ||
			typeof Sidebar.prototype.create_user_menu !== "function"
		) {
			return;
		}
		installed = true;

		const create_user_menu = Sidebar.prototype.create_user_menu;
		const user_menu_options = Sidebar.prototype.user_menu_options;
		if (typeof user_menu_options === "function") {
			// Counted, not flagged: a menu made while another is being made is still a menu.
			let in_menu = 0;
			Sidebar.prototype.create_user_menu = function () {
				in_menu++;
				try {
					return create_user_menu.apply(this, arguments);
				} finally {
					in_menu--;
				}
			};
			Sidebar.prototype.user_menu_options = function () {
				const groups = apply_changes(user_menu_options.apply(this, arguments), this);
				return in_menu ? groups : followable(groups);
			};
			return;
		}

		// Frappe before 16.60: the rows are written inline in `create_user_menu`.
		Sidebar.prototype.create_user_menu = function () {
			const sidebar = this;
			const Dropdown = frappe.ui.Dropdown;
			let changed = false;
			frappe.ui.Dropdown = class extends Dropdown {
				constructor(opts = {}) {
					const first = !changed && Array.isArray(opts.options);
					if (first) changed = true;
					super(
						first ? { ...opts, options: apply_changes(opts.options, sidebar) } : opts
					);
				}
			};
			try {
				return create_user_menu.apply(this, arguments);
			} finally {
				frappe.ui.Dropdown = Dropdown;
			}
		};
	}

	// The rows a list outside the menu (the phone's Profile page) can open: a link or a click, and
	// not one kept to the menu. Frappe's own rows are all one or the other, and pass unchanged.
	function followable(groups) {
		if (!Array.isArray(groups)) return groups;
		return groups.map((group) =>
			group && Array.isArray(group.options)
				? {
						...group,
						options: group.options.filter(
							(row) => !row || ((row.href || row.onclick) && !row.menu_only)
						),
				  }
				: group
		);
	}

	function apply_changes(groups, sidebar) {
		return changes.reduce((current, change) => {
			try {
				const changed = change(current, sidebar);
				return Array.isArray(changed) ? changed : current;
			} catch (e) {
				console.error("opendesk: a user menu change failed", e);
				return current;
			}
		}, groups);
	}
})();
