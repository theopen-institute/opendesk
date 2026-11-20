// Open Desk's arrangement of the desk's boot, kept when Frappe replaces it.
//
// The dock and the Apps screen both work by arranging two things in `frappe.boot` that Frappe's
// own desk reads:
//
//   - `module_sidebars[shell].app`, which app a module is in. Frappe's header takes its title and
//     logo from there, and it decides which app is open. The dock writes each module's dock app
//     into it, here, from the dock itself (`opendesk.boot_arrangement.place`).
//   - `app_data`, the apps Frappe knows. The dock adds an entry for each dock app Frappe has no
//     record of (a Desk App of its own, Other) and retitles a bound one; the Apps screen
//     setting has already arranged its tiles on the server (`apps_screen.py`).
//
// Frappe replaces both wholesale when a workspace or a sidebar is saved (`workspace.js`,
// `sidebar_manager.js`), with its own answer. So both are watched: whatever Frappe puts there is
// arranged again as it arrives, from wherever in Frappe it comes. A replaced `app_data` takes back
// the Apps screen's tiles, titles and order from the copy the boot arrived with; everything else
// in it is Frappe's new answer.
//
// The dock only places modules once it has checked that it can draw (`place`), and stops if it
// gives up (`release`), putting back what Frappe said.
frappe.provide("opendesk.boot_arrangement");

(function () {
	const boot = frappe.boot;
	if (!boot) return;
	const features = boot.opendesk_features || {};
	// Nothing to arrange, so Frappe's boot is left exactly as it is: no watchers installed.
	if (!features.dock && !features.apps_screen) return;

	// What the Apps screen setting decides about an app, and so takes back from a replacement.
	const ARRANGED = ["app_title", "app_logo_url", "app_route", "on_apps_screen", "sequence_id"];
	const snapshot = (app_data) => app_data.map((entry) => ({ ...entry }));

	// The Apps screen as the server arranged it, while that setting is on.
	let arranged =
		features.apps_screen && Array.isArray(boot.app_data) ? snapshot(boot.app_data) : null;
	// The dock's apps, once the dock asks for its modules to be placed.
	let dock = null;
	// Frappe's own answer for each module entry, so placing again, or giving up, starts from it.
	const origins = new WeakMap();
	// And for each `app_data` entry the dock retitled, and the entries it added: what `release`
	// puts back and takes out, so Frappe's header names Frappe's apps again.
	const retitled = new WeakMap();
	const added_entries = new WeakSet();

	function place_modules(module_sidebars) {
		if (!module_sidebars) return;
		const placement = {};
		(dock || []).forEach((app) =>
			(app.modules || []).forEach((module) => (placement[module.shell] = app.app_name))
		);
		Object.entries(module_sidebars).forEach(([shell, sidebar]) => {
			if (!sidebar || typeof sidebar !== "object") return;
			if (!origins.has(sidebar)) origins.set(sidebar, sidebar.app);
			sidebar.app = placement[shell] || origins.get(sidebar);
		});
	}

	// An added entry's Dock: one Sidebar row per module of the dock app, in its order. Frappe reads
	// an app's `dock` wherever it asks what is in an app -- the phone's navigation sheet
	// (`MobileNav.render_dock`, 16.60), an app's landing page (`app_landing_route`) -- and an entry
	// with none reads as an app with nothing in it.
	const dock_rows = (app) =>
		(app.modules || []).map((module) => ({ link_type: "Sidebar", link_to: module.shell }));

	// A dock app Frappe does not know gets an entry of its own, kept off the Apps screen; a bound
	// one gives Frappe's entry its title and logo.
	function add_dock_entries(app_data) {
		if (!dock || !Array.isArray(app_data)) return;
		const known = new Map(app_data.map((entry) => [entry.app_name, entry]));
		dock.forEach((app) => {
			const entry = known.get(app.app_name);
			if (entry && added_entries.has(entry)) {
				// Placed again after an editor's save: the app as it is now.
				Object.assign(entry, {
					app_title: app.title,
					app_logo_url: app.logo || null,
					dock: dock_rows(app),
				});
				return;
			}
			if (entry) {
				if (app.configured) {
					if (!retitled.has(entry)) {
						retitled.set(entry, {
							app_title: entry.app_title,
							app_logo_url: entry.app_logo_url,
						});
					}
					entry.app_title = app.title;
					if (app.logo) entry.app_logo_url = app.logo;
				}
				return;
			}
			const added = {
				app_name: app.app_name,
				app_title: app.title,
				app_logo_url: app.logo || null,
				app_route: "",
				desk_route: "",
				on_apps_screen: false,
				sequence_id: 100,
				dock: dock_rows(app),
			};
			app_data.push(added);
			added_entries.add(added);
			known.set(app.app_name, added);
		});
	}

	// Frappe's fresh `app_data`, with the Apps screen's arrangement put back over it: the arranged
	// entries in their order, then whatever Frappe has that the arrangement did not.
	function rearrange(fresh) {
		if (!arranged) return fresh;
		const by_name = new Map(fresh.map((entry) => [entry.app_name, entry]));
		const result = arranged.map((saved) => {
			const entry = by_name.get(saved.app_name);
			if (!entry) return { ...saved };
			by_name.delete(saved.app_name);
			const merged = { ...entry };
			ARRANGED.forEach((field) => (merged[field] = saved[field]));
			if (!(merged.dock || []).length) merged.dock = saved.dock;
			return merged;
		});
		return [...result, ...by_name.values()];
	}

	// Run `settle` on every value assigned to `frappe.boot[key]`, and keep what it returns. Left
	// alone if the property cannot be redefined.
	//
	// Another app's script may already watch the same property this way, from a bundle that loads
	// first. Its setter then runs first, and this settles what it kept, so neither has to know the
	// other is there.
	function watch(key, settle) {
		const descriptor = Object.getOwnPropertyDescriptor(boot, key);
		if (descriptor && !descriptor.configurable) return;
		const outer = descriptor && (descriptor.get || descriptor.set) ? descriptor : null;
		let value = boot[key];
		Object.defineProperty(boot, key, {
			configurable: true,
			enumerable: true,
			get: () => value,
			set: (next) => {
				value = next;
				try {
					if (outer && outer.set) {
						outer.set.call(boot, next);
						if (outer.get) value = outer.get.call(boot);
					}
					value = settle(value);
				} catch (e) {
					console.error(`opendesk: could not arrange frappe.boot.${key}`, e);
				}
			},
		});
	}

	watch("module_sidebars", (value) => {
		if (dock) place_modules(value);
		return value;
	});
	watch("app_data", (value) => {
		if (!Array.isArray(value)) return value;
		const result = rearrange(value);
		add_dock_entries(result);
		return result;
	});

	Object.assign(opendesk.boot_arrangement, {
		// Place each module in its dock app, now and whenever Frappe replaces the boot's copy.
		// Called again with the same array after the dock is refilled.
		place(dock_apps) {
			dock = dock_apps;
			place_modules(boot.module_sidebars);
			add_dock_entries(boot.app_data);
		},
		// Back to Frappe's placement, titles and logos, and stop placing. The Apps screen's own
		// arrangement, a setting of its own, stays.
		release() {
			dock = null;
			Object.values(boot.module_sidebars || {}).forEach((sidebar) => {
				if (sidebar && origins.has(sidebar)) sidebar.app = origins.get(sidebar);
			});
			const app_data = boot.app_data;
			if (!Array.isArray(app_data)) return;
			for (let i = app_data.length - 1; i >= 0; i--) {
				if (added_entries.has(app_data[i])) app_data.splice(i, 1);
			}
			app_data.forEach((entry) => {
				if (retitled.has(entry)) Object.assign(entry, retitled.get(entry));
			});
		},
		// An editor's save: the server's freshly arranged `app_data` is the arrangement from now on.
		adopt(app_data) {
			if (!Array.isArray(app_data)) return;
			arranged = features.apps_screen ? snapshot(app_data) : null;
			boot.app_data = app_data;
		},
	});
})();
