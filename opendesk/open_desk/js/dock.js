// The dock: apps down the left of the desk, where Frappe's Dock lists the open app's
// modules.
//
// Built on the Dock rather than beside it. Frappe 16.50 draws a column left of the sidebar (the
// Dock) holding the modules of whichever app owns the sidebar on screen, and a header menu over
// the sidebar. This keeps the column and everything Frappe does with it -- pinned or floating,
// hidden where a page hides it, the user menu at its foot -- and changes only what is in it:
//
//   - the column lists the apps `opendesk.open_desk.desk_apps` resolves (the
//     Desk Apps, then every installed app for the modules those leave unclaimed), the one
//     you are in lit, and its mark at the top is the site's, leading to the Apps screen;
//   - picking an app offers its modules, in one of seven ways Open Desk Settings' "Module
//     Picker" chooses between (below). Its tooltip is just its name;
//   - the header menu over the sidebar lists the open app's modules, under the Categories and
//     Spacers its Desk App sets, in place of Frappe's switcher rows;
//   - the header names the app as well as the module, since the dock's lit tile is an app and
//     Frappe's header names only the module;
//   - Frappe puts Search and Notifications (and from 16.60 Flow, where installed) at the top of
//     the dock while it is pinned (16.53, `Dock.render_utilities`). Other apps' tiles join them
//     there (`opendesk.dock.tools`, below): Commons' To Do, say, opening its own panel the way the
//     bell opens Notifications. Frappe's panels then open beside the dock, over the sidebar, rather
//     than beside the sidebar. All of them can sit at the bottom of the dock instead, over the
//     user menu ("Move Search, Notifications, and Flow to Bottom of Dock");
//   - the user menu's Manage Dock, which arranges a Dock nothing draws while the dock is on, gives
//     way to Manage Desk Apps, and a click on the module list's header opens Manage Modules for that
//     app (both `js/arrange.js`). They arrange what the dock does draw, and it is redrawn in
//     place when they save (`opendesk.dock.apply`).
//
// The module picker, "Module Menu" (the default), "App Menu", "Sliding Sidebar", "Module Tabs",
// "Three Column", "Accordion Dock" or "Accordion Sidebar" (`features.module_picker`), says where
// an app's modules are offered. What picking an app on the dock does is a setting of its own, the
// same in every picker (`features.app_pick`, "Picking an App"):
//
//   - Show Its Modules (the default): picking an app offers its modules, over the page you are
//     on, until one is picked -- as each picker describes below.
//   - Open Last Module: picking another app goes into it, to the module last open in it in this
//     browser, else its first, and the picker offers the rest from there. Picking the app you are
//     in offers its modules, as above.
//   - Open Last Sidebar Item: the same, to the sidebar item last open in the app -- the page of
//     the row Frappe lit -- rather than the module's landing page; the module last open in it
//     where there is no such item.
//
// App Menu. Frappe's own dock, nearly: the open app's mark at the top and its modules under it,
// a tile each, named in a tooltip, the sidebar holding the open module's content. The mark opens a menu of the apps -- in place of the Apps screen, which the
// menu's last row leads to. With Show Its Modules, an app picked from the menu takes the dock,
// mark and modules, over the page you are on, until a module is picked or it is put back as
// the band's is. On a phone too, the dock being in the sidebar's drawer ("Show Dock on Mobile");
// without it, the header menu offers the modules there.
//
// Sliding Sidebar. The sidebar's rows become the app's modules -- its frontend first, set apart,
// then the modules under their Categories and Spacers -- and its header is the app: its mark,
// its name, and how many modules it has. Nothing
// else moves: the page stays where it was until a module is picked, and navigating anywhere
// else puts back the sidebar for wherever you land. Frappe's own state is left alone, so
// leaving the list is only rebuilding the sidebar Frappe already thinks it is showing. An app
// with one module, or only a frontend, has no choice to show and opens it.
//
// The rows move to say which way you went: a module opened from the list comes in from the right
// (one level down), the list comes in from the left (one level up), and switching app or module
// sideways -- from the header menu, or an app of one module -- fades. Above a module's content,
// a row naming its app goes back up to the list. The header's menu, which would only list the
// modules again, is gone wherever nothing else is left in it, and Edit Sidebar is a pencil in the
// sidebar's lower right corner. Only what a person clicked here animates; the
// rebuilds Frappe makes on its own as you navigate just appear, or motion would stop meaning
// anything.
//
// Module Menu. Each level of the hierarchy has one surface: the dock holds apps, the sidebar's
// header holds the module -- the app over the module open in it, and a menu to change it -- and
// the sidebar's rows are always the module's content. The modules are never sidebar rows: they
// are the header's menu, the one on screen marked, ending in Manage Modules. Picking an app on
// the dock opens that menu on the app's modules, the header naming the app over "Choose a
// module" until it closes, over the sidebar of the page you are on, which stays as it is until
// a module is picked.
//
// Three Column. The three levels are three columns: the dock, then a column of the app's modules,
// then the sidebar, which only ever holds the module's content and is headed by the module alone,
// the column naming the app. Three columns are a lot of the screen, so each can give room back:
// the module column folds to its icons (its foot's button, remembered in this browser), and folded
// it opens over the sidebar while the pointer is on it, or when an app is picked on the dock; the
// sidebar folds as Frappe folds it. Picking another app on the dock shows its modules in the
// column, over the page you are on, until a module is picked or the page changes. Below 768px,
// where the dock and the sidebar are a drawer with no room for a third column, there is no column,
// and the header menu picks, as the Module Menu does.
//
// Module Tabs. Each level runs its own way: apps down the dock, the app's modules across a band at
// the top -- over the sidebar and the page alike, the app's mark and name first -- and the
// module's content down the sidebar. The band costs height rather than width, so the page loses no
// columns to it. Tabs that do not fit go under More, which takes the open module's name when that
// is one of them. Picking another app on the dock shows its modules in the band, none of them lit,
// until a module is picked, the page changes, or Escape or a click elsewhere puts it back. Below
// 768px there is no band, and the header menu offers the modules, as the Module Menu does. Beside
// the band the sidebar has no header, and Edit Sidebar is a pencil in its lower right corner, as
// in the Sliding Sidebar.
//
// Accordion Dock. The open app's tile opens up on the dock to show its modules under it, a tile
// each, named in a tooltip; the sidebar holds the open module's content. Moving into another app,
// its modules slide open under it as the last app's slide shut; picking another app on the dock
// opens its tray in the open app's place, the same way, until a module is picked or it is put back
// as the band's is. A click on the open app's own tile folds its tray away and back. On a phone
// too, the dock being in the sidebar's drawer ("Show Dock on Mobile"); without it, the header menu
// offers the modules there.
//
// Accordion Sidebar. The sidebar lists the open app's modules as headings, the open module's
// content under its own heading. A heading of another module opens it
// (its content sliding open as the last module's slides shut); the open module's heading folds
// its content away and back. Picking another app on the dock shows its modules' headings, every
// one closed, until one is picked or they are put back as the band's are. At every width: on a
// phone the sidebar is a drawer.
//
// In all of them but Three Column beside its column, the sidebar's header names the app over the
// module open in it, as the levels run, with the app's mark -- words alone with App Menu, whose
// dock carries the mark (`refresh_header`). And an app with one module, or only a frontend, has no choice to show and opens it.
//
// Which app a module is in is written into the boot by `js/boot_arrangement.js`: each module's
// dock app into `module_sidebars[shell].app`, and an `app_data` entry for each dock app Frappe
// does not know, so Frappe's own header names the right app and logo -- again whenever Frappe
// replaces either.
//
// Off unless Open Desk Settings' "Override Dock" is ticked, and off too if Frappe has moved
// what this hangs on: then the desk is simply Frappe's. Every change to Frappe's classes goes
// through `patch`, so if Frappe changes something this reads and a change throws, the dock
// switches itself off for the rest of the page and Frappe's own method runs instead (`give_up`).
// `test_frappe_seams.py` checks every name this hangs on is still in Frappe's source.
//
// Tiles of other apps' own, on the dock after Frappe's Search and Notifications. An app adds one by
// pushing a description onto `opendesk.dock.tools`, which it makes itself if it loads first:
//
//   frappe.provide("opendesk.dock");
//   (opendesk.dock.tools = opendesk.dock.tools || []).push({
//       name: "todos",                 // unique among the tiles
//       label: __("To Do"),            // the tooltip and the accessible name
//       icon: "list-todo",             // one of the desk's icons
//       class: "my-panel-trigger",     // optional: classes on the button
//       badge_class: "my-badge",       // optional: a count badge on the tile's corner, drawn hidden
//       condition: () => true,         // optional: whether this user gets the tile
//       on_click: ($button) => {},
//       on_draw: ($button) => {},      // optional: once the tile is on the page
//   });
//
// A plain array, read when the dock is made, so it does not matter which app's script
// loads first, and an app that adds a tile needs nothing from this one when the dock is off or
// this app is not installed. A tile that throws is left out.
frappe.provide("opendesk.dock");
opendesk.dock.tools = opendesk.dock.tools || [];

(function () {
	const features = (frappe.boot && frappe.boot.opendesk_features) || {};
	// Module Menu unless the settings say otherwise (`settings.module_picker`).
	const picker = features.module_picker || "header";
	const column_mode = picker === "column";
	const tabs_mode = picker === "tabs";
	const app_menu = picker === "app_menu";
	const dock_accordion = picker === "accordion_dock";
	const sidebar_accordion = picker === "accordion_sidebar";
	// Every picker but the two that list modules in the sidebar offers them from the header's menu
	// wherever it has nowhere else to show them: the column and the band are not drawn below
	// 768px, nor the dock where a page or a floating dock out of reach leaves it off.
	const menu_picker = picker !== "sidebar" && !sidebar_accordion;
	// What picking an app does, in whichever picker (`settings.app_pick`): offer its modules over
	// the page you are on ("offer", the default), or go into it, to the module last open in it
	// ("enter") or to the sidebar item last open in it ("enter_item").
	const enters_app = features.app_pick === "enter" || features.app_pick === "enter_item";
	const enters_item = features.app_pick === "enter_item";
	// Kept as one array for the life of the page: an editor's save refills it in place.
	const dock_apps = frappe.boot && frappe.boot.desk_apps;
	if (!features.dock || !Array.isArray(dock_apps) || !dock_apps.length) return;

	const Sidebar = frappe.ui && frappe.ui.Sidebar;
	const Dock = frappe.ui && frappe.ui.Dock;
	const Header = frappe.ui && frappe.ui.SidebarHeader;
	if (
		!Sidebar ||
		!Dock ||
		!Header ||
		[
			"dock_enabled",
			"open_module",
			"setup",
			"set_workspace_sidebar",
			"add_item",
			"empty",
		].some((m) => typeof Sidebar.prototype[m] !== "function") ||
		["make", "render_entries", "render_logo", "name_tile", "close"].some(
			(m) => typeof Dock.prototype[m] !== "function"
		) ||
		typeof Header.prototype.menu_items !== "function" ||
		typeof Sidebar.prototype.refresh_header !== "function" ||
		!(window.opendesk && opendesk.user_menu && opendesk.user_menu.add) ||
		!(opendesk.boot_arrangement && opendesk.boot_arrangement.place)
	) {
		return;
	}

	$("body").addClass("opendesk-dock-on");
	// Other apps' tiles beside Frappe's Search and Notifications on the dock are a switch of their
	// own, and need Frappe's way of making such a tile (`Dock.make_utility`, 16.53).
	const dock_tools = features.dock_tools && typeof Dock.prototype.make_utility === "function";
	if (dock_tools) $("body").addClass("opendesk-dock-tools-on");
	// And so is where they all go: the top of the dock, as Frappe has it, or its bottom.
	if (features.dock_tools_bottom) $("body").addClass("opendesk-dock-tools-bottom");
	// And so is the dock in the sidebar's drawer below 768px (`should_pin`, below).
	if (features.mobile_dock) $("body").addClass("opendesk-mobile-dock-on");
	opendesk.boot_arrangement.place(dock_apps);

	// Set once a change has thrown: from then on every patched method is Frappe's own.
	let broken = false;

	// Replace `proto[name]` with `impl`, which is handed a function calling Frappe's original with
	// the same arguments. If `impl` throws, the dock gives up and the original answers -- once:
	// not again if `impl` had already called it. An error thrown by the original itself is Frappe's
	// (a Navbar Settings row whose condition throws, say): it goes on to Frappe's caller as it would
	// without the dock, and the dock stays on.
	function patch(proto, name, impl) {
		const original = proto[name];
		proto[name] = function (...args) {
			let called = false;
			let result;
			let frappe_error;
			const call_original = () => {
				called = true;
				try {
					return (result = original.apply(this, args));
				} catch (e) {
					frappe_error = e;
					throw e;
				}
			};
			if (broken) return original.apply(this, args);
			try {
				return impl.call(this, call_original, args);
			} catch (e) {
				if (called && e === frappe_error) throw e;
				give_up(e);
				return called ? result : original.apply(this, args);
			}
		};
	}

	// Off for the rest of the page: Frappe's placement back, the dock's tools gone, and the sidebar
	// and Dock drawn again, now by Frappe alone.
	function give_up(error) {
		if (broken) return;
		broken = true;
		console.error(
			"opendesk: the dock met a change in Frappe and has switched itself off",
			error
		);
		// And to the site's Error Log, where it is seen: the console is this person's alone.
		try {
			frappe
				.xcall("opendesk.open_desk.settings.report_dock_failure", {
					error: String((error && error.stack) || error),
					route: frappe.get_route_str ? frappe.get_route_str() : "",
				})
				.catch(() => {});
		} catch (e) {
			// Reporting is a courtesy; the desk is Frappe's either way.
		}
		$("body").removeClass(
			"opendesk-dock-on opendesk-dock-tools-on opendesk-dock-tools-bottom opendesk-tabs-on opendesk-modules-beside"
		);
		const dock = frappe.app && frappe.app.sidebar && frappe.app.sidebar.dock;
		if (dock) {
			// Search and Notifications back under the mark, where Frappe made them.
			if (dock.$dock) {
				dock.$dock.find(".dock-utilities").insertAfter(dock.$dock.find(".dock-logo"));
			}
			const tips = dock.opendesk_tool_tips || [];
			tips.forEach((tip) => tip.destroy());
			if (dock.utility_tooltips) {
				dock.utility_tooltips = dock.utility_tooltips.filter((tip) => !tips.includes(tip));
			}
			dock.opendesk_tool_tips = [];
			if (dock.$items) destroy_tips(dock.$items.find(".opendesk-dock-group"));
		}
		$(".opendesk-dock-tool, .opendesk-module-tabs, .opendesk-edit-sidebar").remove();
		// The line the dock added under the header's title: Frappe's header has none.
		$(".sidebar-header .header-subtitle").remove();
		$(".opendesk-header-plain, .opendesk-header-hidden").removeClass(
			"opendesk-header-plain opendesk-header-hidden"
		);
		$(window).off(".opendesk-beside");
		$(document).off("page-change.opendesk sidebar-expand.opendesk");
		after_page.length = 0;
		$(document).off(".opendesk-browse");
		opendesk.boot_arrangement.release();
		setTimeout(() => {
			try {
				const sidebar = frappe.app && frappe.app.sidebar;
				if (!sidebar) return;
				sidebar.opendesk_module_list = null;
				sidebar.opendesk_picker_app = null;
				if (sidebar.opendesk_column) sidebar.opendesk_column.$el.remove();
				sidebar.opendesk_column = null;
				sidebar.opendesk_tabs = null;
				sidebar.opendesk_browsing = null;
				$("body").removeClass("opendesk-column-on");
				$(document).off(".opendesk-column");
				$(window).off(".opendesk-column");
				if (sidebar.sidebar_header) clear_list_header(sidebar.sidebar_header);
				if (sidebar.current_module) sidebar.setup(sidebar.current_module);
				if (sidebar.dock) {
					// The dock's mark leads to the Apps screen again, as Frappe's link.
					if (sidebar.dock.opendesk_app_menu) {
						const own = sidebar.dock;
						own.opendesk_app_menu.destroy();
						own.$header
							.off("keydown")
							.removeAttr("role tabindex")
							.attr("href", "/desk")
							// Frappe's own click on its mark, which the menu took off.
							.on("click", () => own.close());
						// Frappe names its mark only when it has no tooltip yet.
						if (own.header_tooltip) own.header_tooltip.destroy();
						own.header_tooltip = null;
					}
					sidebar.dock.opendesk_app_menu = null;
					sidebar.dock.rendered = null;
					sidebar.refresh_dock();
				}
			} catch (e) {
				console.error("opendesk: could not redraw Frappe's sidebar", e);
			}
		});
	}

	// A handler of the dock's own: a click, a key, a timer, a redraw an editor asked for. Frappe
	// calls none of these, so `patch` does not cover them; this does the same for them. If the
	// handler throws, the dock gives up, and `fallback`, when given, does what Frappe's own desk
	// would have done with the same event -- and from then on only `fallback` runs.
	function guarded(handler, fallback) {
		return function (...args) {
			if (!broken) {
				try {
					return handler.apply(this, args);
				} catch (e) {
					give_up(e);
				}
			}
			return fallback ? fallback.apply(this, args) : undefined;
		};
	}

	// An app's frontend, outside the desk: a page load of its own.
	function visit_frontend(app) {
		window.location.href = app.frontend.url;
	}

	// Frappe's way into a dock app, for a click the dock could not handle: its first module, else
	// its frontend.
	function frappe_open_app(sidebar, app) {
		const [first] = modules_of(app);
		if (first) sidebar.open_module(first.shell);
		else if (app.frontend) visit_frontend(app);
	}

	// The dock app holding a shell, by the placement the server wrote into the boot.
	function dock_app_of(shell) {
		const sidebar = shell && frappe.boot.module_sidebars[shell];
		const app_name = sidebar && sidebar.app;
		return (app_name && dock_apps.find((app) => app.app_name === app_name)) || null;
	}

	// A dock app's modules this user can open, in its order.
	function modules_of(app) {
		return (app.modules || []).filter((entry) => frappe.boot.module_sidebars[entry.shell]);
	}

	// An app's modules as every picker lists them, in order. A Category starts a group under its
	// name, and a Spacer starts one without; pickers with room for a name draw `category` as a
	// heading and `spacer` as a gap, the others a rule wherever `starts_group`.
	function module_layout(app) {
		return modules_of(app).map((entry, index) => ({
			entry,
			shell: entry.shell,
			label: __(entry.label),
			icon: entry.icon || frappe.get_module_icon(entry.shell) || "folder",
			category: entry.category ? __(entry.category) : null,
			spacer: !entry.category && !!entry.space_before && index > 0,
			starts_group: index > 0 && (!!entry.category || !!entry.space_before),
		}));
	}

	// Opening a module from a picker, and what Frappe's desk would do should that throw.
	function module_opener(sidebar, shell, motion = "fade") {
		return guarded(
			() => open_module(sidebar, shell, motion),
			() => sidebar.open_module(shell)
		);
	}

	// What an app's module list offers: its frontend, then its modules.
	function choice_count(app) {
		return modules_of(app).length + (app.frontend ? 1 : 0);
	}

	// Picking an app offers its modules, unless there is only one thing in it to pick. With Open
	// Last Module, picking an app other than the one you are in goes into it instead, to the module
	// last open in it, and the picker offers the rest from there; picking the app you are in still
	// offers its modules.
	//
	// A page that hides the sidebar (a page's `hide_sidebar`) can still show the dock, but neither
	// the sidebar nor its header can offer the modules there. Unless the dock carries them itself
	// (App Menu, Accordion Dock), the app is gone into instead, as Open Last Module would.
	function open_app(sidebar, app) {
		const can_offer =
			sidebar_shown(sidebar) || app_menu_shown(sidebar) || dock_accordion_shown(sidebar);
		const elsewhere = app !== dock_app_of(sidebar.current_module);
		if (modules_of(app).length && (!can_offer || (enters_app && elsewhere))) {
			enter_app(sidebar, app);
			return;
		}
		if (choice_count(app) > 1) {
			offer_modules(sidebar, app);
			return;
		}
		const [only] = modules_of(app);
		if (only) {
			open_module(sidebar, only.shell, "fade");
		} else if (app.frontend) {
			visit_frontend(app);
		}
	}

	// `open_module` builds the module's sidebar before it routes, so the rows are there to move.
	// Another module's build puts the Sliding Sidebar's list away as well (`setup`), so only the
	// same module needs it put away first -- which is a build of its own.
	function open_module(sidebar, shell, motion) {
		if (shell === sidebar.current_module) leave_module_list(sidebar);
		// Whatever app was on show is put away by the page that opens, not drawn back first.
		sidebar.opendesk_browsing = null;
		sidebar.open_module(shell);
		animate_rows(sidebar, motion);
	}

	const MOTIONS = ["forward", "back", "fade"];

	function animate_rows(sidebar, motion) {
		if (!MOTIONS.includes(motion)) return;
		const $rows = sidebar.$items_container;
		if (!$rows || !$rows.length) return;
		$rows.removeClass(MOTIONS.map((m) => `opendesk-enter-${m}`).join(" "));
		// Read a layout property so the class removed above takes effect first, and the same
		// transition twice in a row still plays.
		void $rows.get(0).offsetWidth;
		$rows.addClass(`opendesk-enter-${motion}`);
		// One listener, replaced each time: under reduced motion the animation never plays and
		// never ends, and a row's own animation ending must not end the container's.
		$rows.off("animationend.opendesk").on("animationend.opendesk", (event) => {
			if (event.target !== $rows.get(0)) return;
			$rows.off("animationend.opendesk").removeClass(`opendesk-enter-${motion}`);
		});
	}

	function offer_modules(sidebar, app) {
		if (column_shown(sidebar)) browse_column(sidebar, app);
		else if (modules_beside(sidebar)) browse_app(sidebar, app);
		// Accordion Sidebar on a module no dock app holds: the picked app's headings all the same.
		else if (sidebar_accordion) browse_app(sidebar, app);
		else if (menu_picker) open_picker(sidebar, app);
		else show_module_list(sidebar, app);
	}

	// Whether the modules are listed somewhere of their own -- the module column, the band of
	// tabs, under the app on the dock, or as the sidebar's headings -- rather than in the header's
	// menu.
	function modules_beside(sidebar) {
		return (
			app_menu_shown(sidebar) ||
			column_shown(sidebar) ||
			tabs_shown(sidebar) ||
			dock_accordion_shown(sidebar) ||
			sidebar_accordion_shown(sidebar)
		);
	}

	// The column or the band, whichever this picker draws, after anything that may show or hide
	// it; and the module on screen noted as the one its app was left in. When the modules move
	// between the header's menu and a place of their own -- the sidebar or the dock showing late,
	// on a page that loads after the route has changed, or the window crossing 768px -- the header
	// changes with them, so it is redrawn here. (`opendesk-modules-beside` on the body is for the
	// smoke test, `tests/smoke`, which reads it.)
	// Frappe re-resolves the sidebar as soon as the route changes, but shows the page -- and the
	// sidebar that page allows or hides -- only once the page is loaded (`container.change_to`,
	// which notes the route on the page and then calls `apply_page_visibility`). For a page not
	// loaded yet that is later, and until then the sidebar on screen is the last page's. What reads
	// the sidebar as the page leaves it (which module it was left on, where to offer an app's
	// modules) waits for the page, and is dropped if the route has moved on by then.
	const after_page = [];
	// The route of the page last put on screen: Frappe announces each (`page-change`) just before
	// it shows or hides the sidebar for it. Unknown until the first, when nothing waits.
	let shown_route = null;
	$(document).on("page-change.opendesk", () => {
		shown_route = frappe.get_route_str();
	});

	function page_settled() {
		return shown_route === null || shown_route === frappe.get_route_str();
	}

	function once_page_shows(run) {
		if (page_settled()) {
			run();
			return;
		}
		after_page.push({ route: frappe.get_route_str(), run });
	}

	function run_after_page() {
		if (!after_page.length || !page_settled()) return;
		const route = frappe.get_route_str();
		after_page.splice(0).forEach((pending) => {
			if (pending.route === route) pending.run();
		});
	}

	// Counted, so a caller can tell whether Frappe's own redraw already drew it.
	let beside_draws = 0;

	function draw_beside(sidebar) {
		beside_draws++;
		if (column_mode) draw_column(sidebar);
		else if (tabs_mode) draw_tabs(sidebar);
		once_page_shows(() => note_module(sidebar));
		const beside = modules_beside(sidebar);
		$("body").toggleClass("opendesk-modules-beside", beside);
		const moved = sidebar.opendesk_beside !== beside;
		sidebar.opendesk_beside = beside;
		if (moved) sidebar.refresh_header();
	}

	// Show Its Modules, in the band, the dock's tray or the sidebar's bars: another app's modules
	// on show over the page you are on, the dock lighting that app, until a module is picked, the
	// page changes, or Escape or a click outside the column, the band, the dock and the sidebar puts
	// them away.
	// (The module column shows it too, opening over the sidebar while folded, `browse_column`; the
	// Module Menu and the Sliding Sidebar have their own.)
	function browsing_app(sidebar) {
		return (sidebar.opendesk_browsing && sidebar.opendesk_browsing.app) || null;
	}

	function browse_app(sidebar, app) {
		const open = dock_app_of(sidebar.current_module);
		const was = browsing_app(sidebar);
		sidebar.opendesk_browsing = app === open ? null : { app, route: frappe.get_route_str() };
		if (!sidebar.opendesk_browsing) {
			if (was) redraw_browsing(sidebar, true);
			return;
		}
		watch_browsing();
		redraw_browsing(sidebar, false);
	}

	function leave_browsing(sidebar) {
		if (!sidebar.opendesk_browsing) return;
		sidebar.opendesk_browsing = null;
		redraw_browsing(sidebar, true);
	}

	function redraw_browsing(sidebar, leaving) {
		if (app_menu) redraw_dock(sidebar);
		if (column_mode && sidebar.opendesk_column) {
			// A folded column opened over the sidebar to show the app goes back with it.
			if (leaving) sidebar.opendesk_column.peek = false;
			draw_column(sidebar);
		}
		if (tabs_mode) draw_tabs(sidebar);
		if (dock_accordion) arrange_dock_groups(sidebar, false);
		if (sidebar_accordion) {
			if (!leaving) draw_accordion_browsing(sidebar);
			else if (sidebar.current_module) {
				// The page's own sidebar again, as Frappe builds it.
				sidebar.setup(sidebar.current_module);
				animate_rows(sidebar, "fade");
			}
			sidebar.refresh_header();
		}
		light_dock(sidebar);
	}

	let browsing_watched = false;
	function watch_browsing() {
		if (browsing_watched) return;
		browsing_watched = true;
		const sidebar = () => frappe.app && frappe.app.sidebar;
		$(document).on(
			"pointerdown.opendesk-browse",
			guarded((event) => {
				const current = sidebar();
				if (!current || !current.opendesk_browsing) return;
				if (
					$(event.target).closest(
						".opendesk-module-tabs, .opendesk-module-column, .dock, .body-sidebar"
					).length
				) {
					return;
				}
				leave_browsing(current);
			})
		);
		$(document).on(
			"keydown.opendesk-browse",
			guarded((event) => {
				const current = sidebar();
				if (
					event.key === "Escape" &&
					!escape_taken(event) &&
					current &&
					current.opendesk_browsing
				) {
					leave_browsing(current);
				}
			})
		);
	}

	// What decides whether the column, the band or the dock shows: the sidebar, and the dock.
	function shown_state(sidebar) {
		return `${sidebar_shown(sidebar)}|${!!(sidebar.dock && sidebar.dock.enabled)}`;
	}

	// Whether the page shows the sidebar: Frappe hides its wrapper on pages that ask it to.
	function sidebar_shown(sidebar) {
		return !!sidebar.wrapper && sidebar.wrapper.css("display") !== "none";
	}

	// Whether the dock can be reached: drawn beside the page or, with "Show Dock on Mobile", in the
	// drawer below 768px (pinned, see `should_pin` below), or floating where the pointer brings it
	// out. On a touch screen with a floating dock, it cannot; nor below 768px without the setting.
	function dock_reachable(sidebar) {
		const dock = sidebar.dock;
		return (
			!!dock &&
			dock.enabled &&
			(features.mobile_dock || !frappe.is_mobile()) &&
			(dock.is_pinned || Dock.pointer_can_reveal?.())
		);
	}

	// Three Column --------------------------------------------------------------------------------

	const COLUMN_FOLDED = "opendesk-module-column-folded";

	// Whether the column is on screen: wherever the dock is drawn and the sidebar is.
	function column_shown(sidebar) {
		return (
			column_mode &&
			!frappe.is_mobile() &&
			!!sidebar.dock &&
			sidebar.dock.enabled &&
			!!sidebar.wrapper &&
			sidebar.wrapper.css("display") !== "none"
		);
	}

	function saved_fold() {
		try {
			return localStorage.getItem(COLUMN_FOLDED) === "1";
		} catch (e) {
			return false;
		}
	}

	function save_fold(folded) {
		try {
			localStorage.setItem(COLUMN_FOLDED, folded ? "1" : "0");
		} catch (e) {
			// Storage refused: the column keeps its width until the page reloads.
		}
	}

	// Made once, beside the dock, the first time the dock draws.
	function column_of(sidebar) {
		if (sidebar.opendesk_column) return sidebar.opendesk_column;
		if (!sidebar.dock || !sidebar.dock.$dock) return null;
		const $el = $(`<nav class="opendesk-module-column" aria-label="${__("Modules")}">
			<div class="opendesk-column-panel">
				<div class="opendesk-column-head">
					<span class="opendesk-column-mark"></span>
					<span class="opendesk-column-title"></span>
				</div>
				<div class="opendesk-column-rows"></div>
				<div class="opendesk-column-foot">
					<button class="btn-reset opendesk-column-button opendesk-column-manage" type="button"></button>
					<button class="btn-reset opendesk-column-button opendesk-column-fold" type="button"></button>
				</div>
			</div>
		</nav>`).insertAfter(sidebar.dock.$dock);
		const column = {
			$el,
			$panel: $el.find(".opendesk-column-panel"),
			folded: saved_fold(),
			// Open over the sidebar while folded.
			peek: false,
			timer: null,
		};
		sidebar.opendesk_column = column;

		$el.find(".opendesk-column-fold").on(
			"click",
			guarded(() => {
				clearTimeout(column.timer);
				column.folded = !column.folded;
				column.peek = false;
				save_fold(column.folded);
				draw_column(sidebar);
			})
		);
		$el.find(".opendesk-column-manage").on(
			"click",
			guarded(() => {
				const app = column_app(sidebar);
				if (app) opendesk.dock.manage_modules(app.key);
			})
		);
		// Folded, the pointer on it opens it over the sidebar, after a moment so that crossing it
		// on the way to the sidebar does not; leaving puts it back, and any app it was showing.
		column.$panel
			.on(
				"mouseenter",
				guarded(() => {
					clearTimeout(column.timer);
					if (!column.folded || column.peek) return;
					column.timer = setTimeout(
						guarded(() => set_peek(sidebar, true)),
						250
					);
				})
			)
			.on(
				"mouseleave",
				guarded(() => {
					clearTimeout(column.timer);
					if (!column.peek) return;
					column.timer = setTimeout(
						guarded(() => leave_column(sidebar)),
						300
					);
				})
			);
		$(document).on(
			"pointerdown.opendesk-column",
			guarded((event) => {
				if (!column.peek) return;
				if ($(event.target).closest(".opendesk-module-column, .dock").length) return;
				leave_column(sidebar);
			})
		);
		$(document).on(
			"keydown.opendesk-column",
			guarded((event) => {
				if (event.key === "Escape" && !escape_taken(event) && column.peek) {
					leave_column(sidebar);
				}
			})
		);
		return column;
	}

	function set_peek(sidebar, peek) {
		const column = sidebar.opendesk_column;
		if (!column || column.peek === peek) return;
		clearTimeout(column.timer);
		column.peek = peek;
		draw_column(sidebar);
	}

	// Back to the open module's app, folded again if it was: a peek put away, and with it any
	// app the column was showing (`leave_browsing`).
	function leave_column(sidebar) {
		const column = sidebar.opendesk_column;
		if (!column) return;
		clearTimeout(column.timer);
		column.peek = false;
		if (sidebar.opendesk_browsing) leave_browsing(sidebar);
		else draw_column(sidebar);
	}

	// The app whose modules the column shows: one on show (`browse_app`), else the open module's.
	function column_app(sidebar) {
		return browsing_app(sidebar) || dock_app_of(sidebar.current_module);
	}

	// An app picked on the dock, shown in the column as in the band or the accordions, and a
	// folded column opened over the sidebar to show it -- the open app's too, picked again.
	function browse_column(sidebar, app) {
		const column = column_of(sidebar);
		if (!column) return;
		// A peek's pending close, from the pointer leaving the column for the dock, is overtaken.
		clearTimeout(column.timer);
		browse_app(sidebar, app);
		// After, since putting away an app on show folds the column back.
		if (column.folded) column.peek = true;
		draw_column(sidebar);
	}

	function draw_column(sidebar) {
		const column = column_of(sidebar);
		if (!column) return;
		const shown = column_shown(sidebar);
		$("body").toggleClass("opendesk-column-on", shown);
		column.$el.toggleClass("hidden", !shown);
		if (!shown) return;
		const app = column_app(sidebar);
		const open = !column.folded || column.peek;
		column.$el
			.toggleClass("opendesk-column-folded", column.folded)
			.toggleClass("opendesk-column-peek", column.peek);

		column.$el.find(".opendesk-column-mark").html(app ? app_mark(app) : "");
		column.$el.find(".opendesk-column-title").text(app ? __(app.title) : "");

		const $rows = column.$el.find(".opendesk-column-rows").empty();
		const row = (label, icon, active, on_click, fallback) => {
			const $row = $(`<button class="btn-reset opendesk-column-row ${
				active ? "active" : ""
			}" type="button">
				<span class="opendesk-column-icon">${frappe.utils.icon(icon, "md")}</span>
				<span class="opendesk-column-label"></span>
			</button>`);
			$row.find(".opendesk-column-label").text(label);
			// Folded, the label is the row's tooltip and accessible name.
			if (!open) $row.attr({ title: label, "aria-label": label });
			if (active) $row.attr("aria-current", "page");
			$row.on("click", guarded(on_click, fallback));
			$rows.append($row);
		};
		if (app && app.frontend) {
			row(app.frontend.label, "external-link", false, () => visit_frontend(app));
			$rows.append('<div class="opendesk-column-space"></div>');
		}
		(app ? module_layout(app) : []).forEach(({ entry, label, icon, category, spacer }) => {
			if (category) {
				$('<div class="opendesk-column-category"></div>').text(category).appendTo($rows);
			} else if (spacer) {
				$rows.append('<div class="opendesk-column-space"></div>');
			}
			row(
				label,
				icon,
				entry.shell === sidebar.current_module,
				() => {
					column.peek = false;
					open_module(sidebar, entry.shell, "fade");
					draw_column(sidebar);
				},
				() => sidebar.open_module(entry.shell)
			);
		});

		const fold = column.folded ? __("Expand modules") : __("Collapse modules");
		column.$el
			.find(".opendesk-column-fold")
			.attr({ title: fold, "aria-label": fold })
			.html(frappe.utils.icon(column.folded ? "chevrons-right" : "chevrons-left", "sm"));
		const manage = app ? __("Manage {0} Modules", [__(app.title)]) : "";
		column.$el
			.find(".opendesk-column-manage")
			.toggleClass("hidden", !app || !can_manage())
			.attr({ title: manage, "aria-label": manage })
			.html(frappe.utils.icon("settings-2", "sm"));
	}

	// Module Tabs ---------------------------------------------------------------------------------

	// Whether the band is on screen: wherever the sidebar is, from 768px up. Unlike the column it
	// does not need the dock beside it: a page without the dock still has its module's siblings.
	function tabs_shown(sidebar) {
		return (
			tabs_mode &&
			!frappe.is_mobile() &&
			!!sidebar.wrapper &&
			sidebar.wrapper.css("display") !== "none"
		);
	}

	// Made once, the first time the dock draws. Fixed across the top of the page, right of the
	// dock; the sidebar and the page are moved down under it (`opendesk-tabs-on`, `scss/dock.scss`).
	function tabs_of(sidebar) {
		if (sidebar.opendesk_tabs) return sidebar.opendesk_tabs;
		if (!sidebar.dock || !sidebar.dock.$dock) return null;
		const $el = $(`<nav class="opendesk-module-tabs hidden" aria-label="${__("Modules")}">
			<div class="opendesk-tabs-app">
				<span class="opendesk-tabs-mark"></span>
				<span class="opendesk-tabs-title"></span>
			</div>
			<div class="opendesk-tabs-row"></div>
			<div class="dropdown opendesk-tabs-more hidden">
				<button class="btn-reset opendesk-tab opendesk-tabs-more-button" type="button"
					data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
					<span class="opendesk-tab-label"></span>
					${frappe.utils.icon("chevron-down", "xs")}
				</button>
				<div class="dropdown-menu dropdown-menu-right opendesk-tabs-menu"></div>
			</div>
			<div class="opendesk-tabs-tools">
				<button class="btn-reset opendesk-tabs-button opendesk-tabs-frontend" type="button"></button>
				<button class="btn-reset opendesk-tabs-button opendesk-tabs-manage" type="button"></button>
			</div>
		</nav>`).insertAfter(sidebar.dock.$dock);
		const tabs = {
			$el,
			$row: $el.find(".opendesk-tabs-row"),
			$more: $el.find(".opendesk-tabs-more"),
			// The app the band shows, and one tab per module of it (`draw_tabs`).
			app: null,
			entries: [],
		};
		sidebar.opendesk_tabs = tabs;

		$el.find(".opendesk-tabs-frontend").on(
			"click",
			guarded(() => {
				if (tabs.app && tabs.app.frontend) window.location.href = tabs.app.frontend.url;
			})
		);
		$el.find(".opendesk-tabs-manage").on(
			"click",
			guarded(() => {
				if (tabs.app) opendesk.dock.manage_modules(tabs.app.key);
			})
		);
		// Which tabs fit is measured, so it is measured again whenever the band changes width.
		if (window.ResizeObserver) {
			new ResizeObserver(guarded(() => fit_tabs(tabs))).observe($el.get(0));
		}
		return tabs;
	}

	// The module each app was last left in, in this browser: `{app key: shell}`. Noted whenever
	// the sidebar is on screen (`note_module`), so only modules someone has had open on a page
	// with the sidebar count, not the one Frappe sets behind the Apps screen.
	const LAST_MODULES = "opendesk-last-modules";

	// Both read once and kept, as they are asked on every redraw; dropped when another tab of
	// this site writes them, so its picks are not written over.
	// An Escape a dialog or a menu answers is theirs: it closes that, and leaves what is behind.
	function escape_taken(event) {
		return (
			event.defaultPrevented ||
			!!$(event.target).closest(".modal, .es-menu, .dropdown-menu").length
		);
	}

	let last_modules_read = null;
	let last_items_read = null;
	window.addEventListener("storage", (event) => {
		if (event.key === LAST_MODULES) last_modules_read = null;
		if (event.key === LAST_ITEMS) last_items_read = null;
	});

	function stored_map(key) {
		try {
			const map = JSON.parse(localStorage.getItem(key) || "{}");
			// Anything else in the key (a list, a string) is not this map, and is written over.
			return map && typeof map === "object" && !Array.isArray(map) ? map : {};
		} catch (e) {
			return {};
		}
	}

	function last_modules() {
		return (last_modules_read = last_modules_read || stored_map(LAST_MODULES));
	}

	function remember_module(app, shell) {
		const last = last_modules();
		if (last[app.key] === shell) return;
		last[app.key] = shell;
		try {
			localStorage.setItem(LAST_MODULES, JSON.stringify(last));
		} catch (e) {
			// Storage refused (a private window, say): the app opens on its first module.
		}
	}

	function note_module(sidebar) {
		if (!sidebar.wrapper || sidebar.wrapper.css("display") === "none") return;
		const app = dock_app_of(sidebar.current_module);
		if (app) remember_module(app, sidebar.current_module);
	}

	// Where picking `app` goes: the module last open in it, while it still holds that module and
	// the user may open it, else its first.
	function return_module(app) {
		const modules = modules_of(app);
		const last = last_modules()[app.key];
		return (modules.find((entry) => entry.shell === last) || modules[0]).shell;
	}

	// And, for Open Last Sidebar Item, the sidebar item each app was last left on, in this browser:
	// `{app key: {shell, href}}` -- the module, and the link of the row Frappe lit on the page
	// (`Sidebar.active_item`), or no link where the page lit none. Noted after every route change,
	// once Frappe has lit the row (`set_workspace_sidebar`), wherever the sidebar is on screen.
	const LAST_ITEMS = "opendesk-last-items";

	function last_items() {
		return (last_items_read = last_items_read || stored_map(LAST_ITEMS));
	}

	function note_item(sidebar) {
		if (!sidebar.wrapper || sidebar.wrapper.css("display") === "none") return;
		const shell = sidebar.current_module;
		const app = dock_app_of(shell);
		if (!app) return;
		const href = desk_link(
			sidebar.active_item && sidebar.active_item.children(".item-anchor")
		);
		const last = last_items();
		const was = last[app.key];
		if (was && was.shell === shell && was.href === href) return;
		last[app.key] = { shell, href };
		try {
			localStorage.setItem(LAST_ITEMS, JSON.stringify(last));
		} catch (e) {
			// Storage refused: the app opens on the module last open in it, or its first.
		}
	}

	// A sidebar row's link, when it leads to a page of the desk: not one opening a site elsewhere,
	// nor a row that only opens or folds a group.
	function desk_link($anchor) {
		const href = $anchor && $anchor.length ? $anchor.attr("href") : null;
		if (!href || $anchor.attr("target") === "_blank") return null;
		try {
			const url = new URL(href, window.location.origin);
			if (url.origin !== window.location.origin) return null;
			if (!/^\/(desk|app)(\/|$)/.test(url.pathname)) return null;
			return url.pathname + url.search;
		} catch (e) {
			return null;
		}
	}

	// Into `app`, as Open Last Module or Open Last Sidebar Item says: the sidebar item last open in
	// it, while its module is still the app's and the user's, else the module last open in it.
	function enter_app(sidebar, app) {
		const item = enters_item && last_items()[app.key];
		if (!item || !item.href || !modules_of(app).some((entry) => entry.shell === item.shell)) {
			open_module(sidebar, return_module(app), "fade");
			return;
		}
		if (item.shell === sidebar.current_module) leave_module_list(sidebar);
		sidebar.opendesk_browsing = null;
		// The module first, so the page lands in that module's sidebar, then the page, as Frappe's
		// router follows a link to it: its query as route options.
		sidebar.select_shell(item.shell);
		const url = new URL(item.href, window.location.origin);
		if (url.search) frappe.route_options = Object.fromEntries(new URLSearchParams(url.search));
		frappe.set_route(url.pathname);
		animate_rows(sidebar, "fade");
	}

	function draw_tabs(sidebar) {
		const tabs = tabs_of(sidebar);
		if (!tabs) return;
		const browsing = browsing_app(sidebar);
		const app = browsing || dock_app_of(sidebar.current_module);
		// A module no dock app holds has no siblings to show.
		const shown = tabs_shown(sidebar) && !!app;
		$("body").toggleClass("opendesk-tabs-on", shown);
		tabs.$el
			.toggleClass("hidden", !shown)
			.toggleClass("opendesk-tabs-browsing", shown && !!browsing);
		draw_edit_button(sidebar);
		tabs.app = shown ? app : null;
		tabs.entries = [];
		tabs.$row.empty();
		if (!shown) return;

		tabs.$el.find(".opendesk-tabs-mark").html(app_mark(app));
		tabs.$el.find(".opendesk-tabs-title").text(__(app.title));

		module_layout(app).forEach(({ entry, label, starts_group }) => {
			// While another app is on show, none of its tabs is the page you are on.
			const active = !browsing && entry.shell === sidebar.current_module;
			const pick = module_opener(sidebar, entry.shell);
			// A group starts with a rule before its first tab, and under More with a heading or
			// a divider.
			const $tab = $(`<button class="btn-reset opendesk-tab" type="button">
				<span class="opendesk-tab-label"></span>
			</button>`)
				.toggleClass("active", active)
				.toggleClass("opendesk-tab-group", starts_group)
				.on("click", pick);
			$tab.find(".opendesk-tab-label").text(label);
			if (active) $tab.attr("aria-current", "page");
			if (entry.category) $tab.attr("title", __(entry.category));
			tabs.$row.append($tab);
			tabs.entries.push({ entry, label, active, pick, starts_group, $tab });
		});

		const frontend = app.frontend ? app.frontend.label : "";
		tabs.$el
			.find(".opendesk-tabs-frontend")
			.toggleClass("hidden", !app.frontend)
			.attr({ title: frontend, "aria-label": frontend })
			.html(frappe.utils.icon("external-link", "sm"));
		const manage = __("Manage {0} Modules", [__(app.title)]);
		tabs.$el
			.find(".opendesk-tabs-manage")
			.toggleClass("hidden", !can_manage())
			.attr({ title: manage, "aria-label": manage })
			.html(frappe.utils.icon("settings-2", "sm"));

		fit_tabs(tabs);
	}

	// The tabs that do not fit, from the end, go under More, which takes the open module's name
	// when that is one of them. At least the first tab always stays in the band.
	function fit_tabs(tabs) {
		const entries = tabs.entries;
		if (!entries.length || tabs.$el.hasClass("hidden")) return;
		entries.forEach((tab) => tab.$tab.removeClass("hidden"));
		tabs.$more.addClass("hidden");
		const row = tabs.$row.get(0);
		const overflows = () => row.scrollWidth > row.clientWidth + 1;
		const $button = tabs.$more.find(".opendesk-tabs-more-button");
		const label = (tab) =>
			$button
				.toggleClass("active", !!tab)
				.find(".opendesk-tab-label")
				.text(tab ? tab.label : __("More"));
		label(null);
		const hidden = [];
		let last = entries.length - 1;
		const hide_while_over = () => {
			for (; last > 0 && overflows(); last--) {
				entries[last].$tab.addClass("hidden");
				hidden.unshift(entries[last]);
			}
		};
		if (overflows()) {
			tabs.$more.removeClass("hidden");
			hide_while_over();
			// More takes the open module's name when that is among them, which widens it: the
			// tabs are measured again beside the wider button, and another may go under it.
			const open = hidden.find((tab) => tab.active);
			if (open) {
				label(open);
				hide_while_over();
			}
		}
		const $menu = tabs.$more.find(".opendesk-tabs-menu").empty();
		hidden.forEach((tab, n) => {
			if (tab.entry.category) {
				$('<h6 class="dropdown-header"></h6>')
					.text(__(tab.entry.category))
					.appendTo($menu);
			} else if (n > 0 && tab.starts_group) {
				$menu.append('<div class="dropdown-divider"></div>');
			}
			const $item = $('<button class="dropdown-item" type="button"></button>')
				.text(tab.label)
				.toggleClass("active", tab.active)
				.on("click", tab.pick);
			if (tab.active) $item.attr("aria-current", "page");
			$menu.append($item);
		});
	}

	// App Menu ------------------------------------------------------------------------------------

	// Whether the app's modules are the dock's tiles: wherever the dock can be reached.
	function app_menu_shown(sidebar) {
		return app_menu && dock_reachable(sidebar);
	}

	// The app the dock shows: one on show (Show Its Modules), else the open module's.
	function dock_menu_app(sidebar) {
		return browsing_app(sidebar) || dock_app_of(sidebar.current_module);
	}

	// The dock's tiles, as Frappe's Dock draws a module's app: its frontend, then its modules, a
	// rule standing for a Category or Spacer, the module on screen lit.
	function draw_module_tiles(dock, sidebar) {
		const app = dock_menu_app(sidebar);
		if (!app) return;
		const browsing = !!browsing_app(sidebar);
		const tile = (label, icon, active, on_click, fallback) => {
			const $tile = $(`<button class="dock-item opendesk-dock-module-tile" type="button">
				<span class="dock-item-icon">${frappe.utils.icon(icon, "md")}</span>
			</button>`)
				.attr("aria-label", label)
				.toggleClass("active", active)
				.on(
					"click",
					guarded(() => {
						dock.close();
						on_click();
					}, fallback)
				);
			if (active) $tile.attr("aria-current", "page");
			dock.name_tile($tile, label);
			dock.$items.append($tile);
		};
		const rule = () => dock.$items.append('<div class="opendesk-dock-rule"></div>');
		if (app.frontend) {
			tile(app.frontend.label, "external-link", false, () => visit_frontend(app));
			rule();
		}
		module_layout(app).forEach(({ shell, label, icon, starts_group }) => {
			if (starts_group) rule();
			tile(
				label,
				icon,
				!browsing && shell === sidebar.current_module,
				() => open_module(sidebar, shell, "fade"),
				() => sidebar.open_module(shell)
			);
		});
	}

	// The dock's mark: the app's, opening a menu of the apps rather than the Apps screen, which
	// the menu's last row leads to.
	function draw_app_logo(dock) {
		const sidebar = dock.sidebar;
		const app = dock_menu_app(sidebar);
		dock.$header_logo.html(app ? app_mark(app) : frappe.utils.icon("layout-grid", "md"));
		dock.$header_title.text(app ? __(app.title) : __("Apps"));
		dock.$header.attr("aria-label", __("Switch app"));
		if (!dock.header_tooltip) {
			dock.header_tooltip = new frappe.ui.Tooltip(dock.$header[0], {
				text: __("Switch app"),
				side: "right",
				delay: 0,
				offset: 10,
				class: "es-tooltip--plain",
			});
		}
		if (dock.opendesk_app_menu) return;
		// Frappe's own click on the mark puts a floating dock away, which would take the menu's
		// anchor with it; the menu's rows put it away instead. And the mark is no longer a link:
		// Frappe's router follows a link to the desk however its click was handled. A button
		// still, for the keyboard: Enter and Space open the menu.
		dock.$header
			.off("click")
			.removeAttr("href")
			.attr({ role: "button", tabindex: "0" })
			.on(
				"keydown",
				guarded((event) => {
					if (event.key !== "Enter" && event.key !== " ") return;
					event.preventDefault();
					// As Frappe's own menus open from the keyboard: at once, on the first row.
					const menu = dock.opendesk_app_menu;
					if (!menu) return;
					if (menu.is_open) menu.close("owner");
					else menu.open({ motion: "instant", focus: "first" });
				})
			);
		dock.opendesk_app_menu = new frappe.ui.Dropdown({
			trigger: dock.$header,
			side: "right",
			align: "start",
			options: () => app_menu_rows(sidebar),
		});
	}

	function app_menu_rows(sidebar) {
		const current = dock_menu_app(sidebar);
		return [
			{
				group: "",
				options: dock_apps
					.filter((app) => choice_count(app))
					.map((app) => ({
						name: `opendesk-app-menu-${app.key}`,
						label: __(app.title),
						...(app.logo ? { image: app.logo } : { icon: app.icon || "box" }),
						selected: app === current,
						onclick: guarded(
							() => {
								sidebar.dock.close();
								open_app(sidebar, app);
							},
							() => frappe_open_app(sidebar, app)
						),
					})),
			},
			{
				group: "",
				options: [
					{
						name: "opendesk-app-menu-apps-screen",
						label: __("Apps Screen"),
						icon: "layout-grid",
						href: "/desk",
					},
				],
			},
		];
	}

	// Accordion Dock ------------------------------------------------------------------------------

	// Whether the open app's modules are on the dock: wherever the dock can be reached.
	function dock_accordion_shown(sidebar) {
		return dock_accordion && dock_reachable(sidebar);
	}

	const DOCK_FOLDED = "opendesk-dock-group-folded";

	// An app's modules, under its tile: its frontend first, then a tile per module, named in a
	// tooltip as the apps are; a rule stands for a Category or Spacer. A tray is made the first time
	// its app opens and kept after, folded: opening and folding are a class on it
	// (`arrange_dock_groups`), so the tray of the app you leave closes while the one you go into
	// opens, and the tiles between them move gradually, whichever way you went.
	function make_dock_group(app) {
		return $(`<div class="opendesk-dock-group ${DOCK_FOLDED}" role="group">
			<div class="opendesk-dock-group-inner"></div>
		</div>`)
			.attr({ "aria-label": __("{0} modules", [__(app.title)]), inert: "" })
			.data("tips", []);
	}

	function fill_dock_group(sidebar, app, $group) {
		destroy_tips($group);
		const tips = [];
		const $inner = $group.find(".opendesk-dock-group-inner").empty();
		const tile = (label, icon, active, on_click, fallback) => {
			const $tile = $(`<button class="btn-reset opendesk-dock-module" type="button">
				${frappe.utils.icon(icon, "sm")}
			</button>`)
				.attr("aria-label", label)
				.toggleClass("active", active)
				.on(
					"click",
					guarded((event) => {
						event.stopPropagation();
						sidebar.dock.close();
						on_click();
					}, fallback)
				);
			if (active) $tile.attr("aria-current", "page");
			// As `Dock.name_tile` names a tile, but kept with the tray, which outlives a redraw.
			tips.push(
				new frappe.ui.Tooltip($tile[0], {
					text: label,
					side: "right",
					delay: 0,
					offset: 10,
					class: "es-tooltip--plain",
				})
			);
			$inner.append($tile);
		};
		if (app.frontend) {
			tile(app.frontend.label, "external-link", false, () => visit_frontend(app));
			$inner.append('<div class="opendesk-dock-group-rule"></div>');
		}
		module_layout(app).forEach(({ shell, label, icon, starts_group }) => {
			if (starts_group) $inner.append('<div class="opendesk-dock-group-rule"></div>');
			tile(
				label,
				icon,
				shell === sidebar.current_module,
				() => open_module(sidebar, shell, "fade"),
				() => sidebar.open_module(shell)
			);
		});
		$group.data("tips", tips);
	}

	function destroy_tips($groups) {
		$groups.each((_, group) => ($(group).data("tips") || []).forEach((tip) => tip.destroy()));
	}

	// The open app's tray open -- unless its tile folded it, until the page moves into another app
	// -- or the tray of an app on show (`browse_app`), and every other folded. `first` is the dock
	// being drawn afresh, where the open app's tray is simply there rather than sliding open.
	function arrange_dock_groups(sidebar, first) {
		const dock = sidebar.dock;
		if (!dock_accordion || !dock || !dock.$items) return;
		const open = dock_app_of(sidebar.current_module);
		if (sidebar.opendesk_dock_folded && (!open || sidebar.opendesk_dock_folded !== open.key)) {
			sidebar.opendesk_dock_folded = null;
		}
		const shown = dock_accordion_shown(sidebar);
		const browsing = browsing_app(sidebar);
		const target = browsing || open;
		dock.$items.children(".opendesk-dock-app").each((_, tile) => {
			const $tile = $(tile);
			const app = dock_apps.find((candidate) => candidate.key === tile.dataset.appKey);
			const has_tray = shown && !!app && app === target && choice_count(app) > 1;
			let $group = $tile.next(".opendesk-dock-group");
			if (!has_tray) {
				$tile.removeAttr("aria-expanded");
				$group.addClass(DOCK_FOLDED).attr("inert", "");
				return;
			}
			const opened = !!browsing || sidebar.opendesk_dock_folded !== app.key;
			if (!$group.length) {
				$group = make_dock_group(app).insertAfter($tile);
				if (first) $group.removeClass(DOCK_FOLDED);
				// Folded first, so that opening it slides.
				else void $group.get(0).offsetWidth;
			}
			fill_dock_group(sidebar, app, $group);
			$group.toggleClass(DOCK_FOLDED, !opened);
			if (opened) $group.removeAttr("inert");
			else $group.attr("inert", "");
			$tile.attr("aria-expanded", opened ? "true" : "false");
		});
	}

	// A redraw for the same apps in the same order moves the light and the trays and keeps every
	// tile, so a tray can slide rather than be drawn again. Says whether it could.
	function redraw_dock_in_place(dock, sidebar) {
		const drawn = dock.$items
			.children(".opendesk-dock-app")
			.map((_, tile) => tile.dataset.appKey)
			.get();
		const wanted = dock_apps.filter((app) => choice_count(app)).map((app) => app.key);
		if (!drawn.length || drawn.join("\n") !== wanted.join("\n")) return false;
		light_dock(sidebar);
		arrange_dock_groups(sidebar, false);
		return true;
	}

	// The dock's tiles and trays gone, so the next redraw draws them afresh -- after an editor
	// changed the apps' names or marks, say.
	function clear_dock(dock) {
		destroy_tips(dock.$items.find(".opendesk-dock-group"));
		dock.$items.empty();
	}

	// A click on the open app's own tile folds its modules away, or opens them again.
	function fold_dock_group(sidebar, app) {
		const folded = sidebar.opendesk_dock_folded === app.key;
		sidebar.opendesk_dock_folded = folded ? null : app.key;
		arrange_dock_groups(sidebar, false);
	}

	// Accordion Sidebar ---------------------------------------------------------------------------

	// Whether the sidebar lists the open app's modules: wherever it shows a module of a dock app.
	// At every width, the sidebar being the drawer it is on a phone.
	function sidebar_accordion_shown(sidebar) {
		return (
			sidebar_accordion &&
			!!sidebar.wrapper &&
			sidebar.wrapper.css("display") !== "none" &&
			!!(browsing_app(sidebar) || dock_app_of(sidebar.current_module))
		);
	}

	const ACCORDION_FOLDED = "opendesk-accordion-folded";

	// Frappe has drawn the open module's rows into the sidebar. They go under the module's own
	// heading, among the headings of the app's other modules -- its frontend first, then the
	// modules, a Category or Spacer starting a new group. A heading of another module opens it; the
	// open module's heading folds its rows away and back, without leaving the page.
	//
	// `leaving` is the module the sidebar showed before, and its rows. When it is another module of
	// the same app, its rows fold away under its heading while the new module's rows open under
	// theirs, so the headings between them move gradually, whichever way you went.
	function draw_accordion(sidebar, leaving) {
		const app = sidebar_accordion && dock_app_of(sidebar.current_module);
		const $container = sidebar.$items_container;
		sidebar.opendesk_accordion_shell = app ? sidebar.current_module : null;
		if (!app || !$container || !$container.length) return;
		const $content = $(`<div class="opendesk-accordion-content">
			<div class="opendesk-accordion-rows"></div>
		</div>`);
		$content.find(".opendesk-accordion-rows").append($container.children());
		const moving =
			!!leaving &&
			!!leaving.$content.length &&
			modules_of(app).some((entry) => entry.shell === leaving.shell);
		let $leaving_heading = null;

		if (app.frontend) {
			const visit = () => visit_frontend(app);
			accordion_heading($container, app.frontend.label, "external-link", null, visit, visit);
		}
		module_layout(app).forEach(({ entry, label, icon, starts_group }) => {
			const open = entry.shell === sidebar.current_module;
			const $heading = accordion_heading(
				$container,
				label,
				icon,
				open,
				() => {
					if (entry.shell !== sidebar.current_module) {
						open_module(sidebar, entry.shell);
						return;
					}
					const folded = !$content.hasClass(ACCORDION_FOLDED);
					$content.toggleClass(ACCORDION_FOLDED, folded);
					$heading
						.toggleClass("opendesk-accordion-open", !folded)
						.find(".item-anchor")
						.attr("aria-expanded", folded ? "false" : "true");
				},
				() => sidebar.open_module(entry.shell)
			);
			$heading.toggleClass("opendesk-accordion-group", starts_group);
			if (moving && entry.shell === leaving.shell) $leaving_heading = $heading;
			if (!open) return;
			$heading.addClass("opendesk-accordion-open");
			$content.insertAfter($heading);
		});

		if (!moving || !$leaving_heading) return;
		// Both as they were -- the new rows folded, the old ones open under their heading -- then,
		// after a reflow, the other way round, which the transitions carry.
		const $old = leaving.$content.attr({ inert: "", "aria-hidden": "true" });
		$old.insertAfter($leaving_heading);
		$leaving_heading.addClass("opendesk-accordion-open");
		$content.addClass(ACCORDION_FOLDED);
		void $container.get(0).offsetWidth;
		$content.removeClass(ACCORDION_FOLDED);
		$old.addClass(ACCORDION_FOLDED);
		$leaving_heading.removeClass("opendesk-accordion-open");
		// Gone once folded: a little after the 0.25s the transition takes.
		setTimeout(() => $old.remove(), 400);
	}

	// A module's bar: its icon and name, and -- `open` being true or false, not null -- the
	// chevron that turns over while its rows are open. A click or Enter or Space runs `on_click`,
	// or `fallback` once the dock has given up (`guarded`).
	function accordion_heading($container, label, icon, open, on_click, fallback) {
		const $heading = $(`<div class="sidebar-item-container opendesk-accordion-module">
			<div class="standard-sidebar-item">
				<a class="item-anchor" role="button" tabindex="0">
					<span class="sidebar-item-icon">${frappe.utils.icon(icon, "sm")}</span>
					<span class="sidebar-item-label"></span>
					<div class="sidebar-item-control"></div>
				</a>
			</div>
		</div>`);
		$heading.find(".sidebar-item-label").text(label);
		const $anchor = $heading.find(".item-anchor").attr("title", label);
		if (open !== null) {
			$anchor.attr("aria-expanded", open ? "true" : "false");
			$heading.find(".sidebar-item-control").html(frappe.utils.icon("chevron-down", "xs"));
		}
		const click = guarded(on_click, fallback);
		$anchor.on("click", click).on("keydown", (event) => {
			if (event.key !== "Enter" && event.key !== " ") return;
			event.preventDefault();
			click();
		});
		$container.append($heading);
		return $heading;
	}

	// Another app on show, with Show Its Modules: its modules' bars, every one closed, in place of
	// the sidebar Frappe built for the page, until one is picked (`browse_app`).
	function draw_accordion_browsing(sidebar) {
		const app = browsing_app(sidebar);
		const $container = sidebar.$items_container;
		if (!app || !$container || !$container.length) return;
		open_sidebar(sidebar);
		sidebar.empty();
		if (app.frontend) {
			const visit = () => visit_frontend(app);
			accordion_heading($container, app.frontend.label, "external-link", null, visit, visit);
		}
		module_layout(app).forEach(({ shell, label, icon, starts_group }) => {
			accordion_heading(
				$container,
				label,
				icon,
				false,
				() => open_module(sidebar, shell),
				() => sidebar.open_module(shell)
			).toggleClass("opendesk-accordion-group", starts_group);
		});
		animate_rows(sidebar, "fade");
	}

	// The header names the app over the list of its modules, with the app's mark.
	function draw_accordion_header(sidebar, header) {
		const app = browsing_app(sidebar) || dock_app_of(sidebar.current_module);
		if (!app) return false;
		header.$header_title.text(__(app.title));
		header.$header_logo.html(app_mark(app));
		set_subtitle(header, "");
		return true;
	}

	// Module Menu: the header's own menu, opened on `app`'s modules rather than the open
	// module's app. The dock lights `app` while it is up, and the open app again once it closes.
	function open_picker(sidebar, app) {
		open_sidebar(sidebar);
		const header = sidebar.sidebar_header;
		if (header && !header.menu && typeof header.setup_menu === "function") header.setup_menu();
		const menu = header && header.menu;
		if (!menu) return;
		watch_picker(sidebar, menu);
		menu.close();
		sidebar.opendesk_picker_app = app;
		light_dock(sidebar);
		draw_picker_header(header, app);
		// After the click that asked for it has finished, or the menu takes that click for one
		// outside itself and closes again.
		setTimeout(
			guarded(() => {
				if (sidebar.opendesk_picker_app === app) menu.open();
			})
		);
	}

	// The header the menu hangs from names the app being picked from, until it closes -- again
	// whenever Frappe redraws the header meanwhile, as it does when a page settles (`refresh_header`).
	function draw_picker_header(header, app) {
		header.$header_title.text(__(app.title));
		header.$header_logo.html(app_mark(app));
		set_subtitle(header, __("Choose a module"));
	}

	// The header's menu is made once, by Frappe; its close is chained onto here, once, so the
	// picker forgets the app it was opened on whichever way it closes.
	function watch_picker(sidebar, menu) {
		if (menu.opendesk_watched) return;
		const on_close = menu.opts.on_close;
		const forget = guarded(() => {
			if (!sidebar.opendesk_picker_app) return;
			sidebar.opendesk_picker_app = null;
			sidebar.refresh_header();
			light_dock(sidebar);
		});
		menu.opts.on_close = (reason) => {
			if (on_close) on_close(reason);
			forget();
		};
		menu.opendesk_watched = true;
	}

	// Sliding Sidebar: the list is drawn into the sidebar Frappe has built for the page, and
	// remembers the route it was opened on: once the route moves on, the list is put away. `quiet`
	// is a redraw no one clicked for (an editor's save), which does not slide.
	function show_module_list(sidebar, app, { quiet = false } = {}) {
		open_sidebar(sidebar);
		sidebar.opendesk_module_list = { app, route: frappe.get_route_str() };
		draw_module_rows(sidebar, app);
		draw_list_header(sidebar);
		draw_edit_button(sidebar);
		light_dock(sidebar);
		if (!quiet) animate_rows(sidebar, "back");
	}

	function leave_module_list(sidebar) {
		if (!sidebar.opendesk_module_list) return;
		sidebar.opendesk_module_list = null;
		if (sidebar.current_module) sidebar.setup(sidebar.current_module);
		light_dock(sidebar);
	}

	// Beside a pinned dock a collapsed sidebar is hidden altogether, header and all, so a picker
	// that shows something in it opens it first, as Frappe opens it for a Dock entry.
	function open_sidebar(sidebar) {
		if (!sidebar.sidebar_expanded && typeof sidebar.open === "function") sidebar.open();
	}

	function redraw_dock(sidebar) {
		if (!sidebar.dock) return;
		sidebar.dock.rendered = null;
		sidebar.dock.render_entries();
	}

	// The app the dock lights: the one a picker or the column is showing, else the open module's.
	function lit_app(sidebar) {
		const list = sidebar.opendesk_module_list;
		return (
			sidebar.opendesk_picker_app ||
			browsing_app(sidebar) ||
			(list ? list.app : dock_app_of(sidebar.current_module))
		);
	}

	// Moves the light without redrawing the tiles. The Module Menu and the module column change
	// what is lit on a pointerdown -- a menu closing, the column going back -- and a tile redrawn
	// between that pointerdown and its click is not there to take the click, so picking another app
	// while either is open would take two clicks.
	function light_dock(sidebar) {
		if (!sidebar.dock || !sidebar.dock.$items) return;
		const current = lit_app(sidebar);
		sidebar.dock.$items.find(".opendesk-dock-app").each((_, tile) => {
			const is_active = !!current && tile.dataset.appKey === current.key;
			$(tile).toggleClass("active", is_active);
			if (is_active) tile.setAttribute("aria-current", "page");
			else tile.removeAttribute("aria-current");
		});
	}

	// Sliding Sidebar: above a module's content, a row naming its app that slides back to the app's
	// module list (one level up, so the list comes in from the left). Not for an app with nothing
	// else to pick.
	function add_back_row(sidebar) {
		const app = dock_app_of(sidebar.current_module);
		const $container = sidebar.$items_container;
		if (!app || choice_count(app) < 2 || !$container || !$container.length) return;
		sidebar.add_item($container, {
			type: "Button",
			standard: true,
			class: "sidebar-item-container opendesk-back-row",
			label: frappe.utils.escape_html(__(app.title)),
			icon: "chevron-left",
			onClick: guarded(() => show_module_list(sidebar, app)),
		});
		$container
			.children()
			.last()
			.attr("title", __("Back to the {0} modules", [__(app.title)]))
			.prependTo($container);
	}

	function draw_module_rows(sidebar, app) {
		sidebar.empty();
		const $container = sidebar.$items_container;
		const add_row = (item) =>
			sidebar.add_item($container, {
				type: "Button",
				// A row with no link is only drawn when it is `standard`, as Frappe's own Search
				// and Notification rows are.
				standard: true,
				// `TypeButton` replaces the row's classes with these, so the class every
				// sidebar row is styled by is named again.
				class: "sidebar-item-container opendesk-module-row",
				...item,
			});

		if (app.frontend) {
			// Frappe's row template prints its label as HTML, and these are typed by whoever edits
			// a Desk App: escaped here, as every label this hands it is.
			add_row({
				label: frappe.utils.escape_html(app.frontend.label),
				icon: "external-link",
				onClick: () => visit_frontend(app),
			});
			sidebar.add_item($container, { type: "Spacer", label: "" });
		}

		module_layout(app).forEach(({ entry, label, icon, category, spacer }) => {
			if (category) {
				$(`<div class="sidebar-item-container opendesk-module-category">
					<div class="standard-sidebar-item">
						<div class="item-anchor section-break">
							<span class="sidebar-item-label"></span>
						</div>
					</div>
				</div>`)
					.find(".sidebar-item-label")
					.text(category)
					.end()
					.appendTo($container);
			} else if (spacer) {
				sidebar.add_item($container, { type: "Spacer", label: "" });
			}
			add_row({
				label: frappe.utils.escape_html(label),
				icon,
				onClick: module_opener(sidebar, entry.shell, "forward"),
			});
			// The module the page is in, lit the way Frappe lights the current row.
			if (entry.shell === sidebar.current_module) {
				$container
					.find(".opendesk-module-row")
					.last()
					.find(".standard-sidebar-item")
					.addClass("active-sidebar");
			}
		});
	}

	// The header shows the app over its list: its mark, its name, and its module count under the
	// name in Frappe's own subtitle style. Its menu belongs to the module Frappe thinks it is
	// showing, which is not this list, so while the list is up a click on the header never reaches
	// it. For someone who may arrange the dock, the click opens Manage Modules for this app
	// instead -- the list's own editor, from the list itself. For everyone else the header is a
	// label. No chevron either way: it opens no menu.
	function draw_list_header(sidebar) {
		const header = sidebar.sidebar_header;
		const list = sidebar.opendesk_module_list;
		if (!header || !list) return;
		header.$header_title.text(__(list.app.title));
		header.$header_logo.html(app_mark(list.app));
		const count = modules_of(list.app).length;
		set_subtitle(header, count === 1 ? __("1 module") : __("{0} modules", [count]));
		const manageable = can_manage();
		header.wrapper
			.removeClass("opendesk-header-plain")
			.addClass("opendesk-module-list-header")
			.toggleClass("opendesk-module-list-header--manageable", manageable)
			.attr("title", manageable ? __("Manage {0} Modules", [__(list.app.title)]) : null);
		header.$drop_icon && header.$drop_icon.addClass("hidden");
		if (!header.opendesk_list_guard) {
			// Capture phase, so it runs before the menu's own listener on this element.
			header.wrapper.get(0).addEventListener(
				"click",
				guarded((event) => {
					const shown = sidebar.opendesk_module_list;
					if (!shown) return;
					event.stopImmediatePropagation();
					event.preventDefault();
					if (can_manage()) opendesk.dock.manage_modules(shown.app.key);
				}),
				true
			);
			header.opendesk_list_guard = true;
		}
	}

	function app_mark(app) {
		if (app.logo) {
			return frappe.utils.app_logo({ app_title: app.title, app_logo_url: app.logo }).icon;
		}
		if (app.icon) return frappe.utils.icon(app.icon, "md");
		return frappe.utils.desktop_icon(app.title, "gray", "md");
	}

	// Below 768px Frappe hides the Dock, and with it every way to another app but the header's
	// menu. With "Show Dock on Mobile" the dock stays: it is a column in the sidebar's drawer, left
	// of the sidebar, shown while the drawer is open (`scss/dock.scss`). That is the pinned dock --
	// a full column, avatar at its foot -- whatever the user's Dock preference, since nothing
	// brings a floating one out there.
	if (features.mobile_dock && typeof Dock.prototype.should_pin === "function") {
		patch(Dock.prototype, "should_pin", function (should_pin) {
			return (this.enabled && frappe.is_mobile()) || should_pin();
		});
		// The drawer can close with a pointer resting on a tile (a pick that goes into an app closes
		// it), and a tile that is hidden gets no pointerleave: its tooltip would stay on the page.
		$(document).on(
			"sidebar-expand.opendesk",
			guarded((event, state) => {
				const dock = frappe.app && frappe.app.sidebar && frappe.app.sidebar.dock;
				if (!frappe.is_mobile() || (state && state.sidebar_expand) || !dock) return;
				const group_tips = dock.$items
					? dock.$items
							.find(".opendesk-dock-group")
							.toArray()
							.flatMap((group) => $(group).data("tips") || [])
					: [];
				[
					...(dock.tooltips || []),
					dock.header_tooltip,
					...(dock.utility_tooltips || []),
					...group_tips,
				].forEach((tip) => tip && tip.hide());
			})
		);
	}

	// Phones, from Frappe 16.60. There is no drawer: a tab bar runs along the bottom, and the page's
	// title opens a sheet over the page, with a row of the open app's dock entries across its top
	// and the module's sidebar under it (`frappe.ui.MobileNav`). With "Show Dock on Mobile" that row
	// is the dock's: a tile for the app you are in, then its frontend and modules. The app's tile
	// turns the row into the dock's apps; picking one shows its modules, and picking a module shows
	// its sidebar below, as Frappe's row does. Nothing navigates until a sidebar row is picked.
	// Without the setting, Frappe's own row lists the open app's modules, from the Dock rows
	// `js/boot_arrangement.js` gives the dock's own apps.
	//
	// `MobileNav` comes in a bundle of its own once the screen is phone-sized, after this script,
	// and makes its one instance as it loads; so its methods are patched as the class arrives,
	// before that instance is made.
	if (features.mobile_dock) {
		when_defined(frappe.ui, "MobileNav", (MobileNav) => {
			const proto = MobileNav && MobileNav.prototype;
			if (
				!proto ||
				["render_dock", "open_navigation"].some((m) => typeof proto[m] !== "function")
			) {
				return;
			}
			patch(proto, "open_navigation", function (open_navigation) {
				// Each sheet starts on the app you are in.
				this.opendesk_sheet = null;
				return open_navigation();
			});
			patch(proto, "render_dock", function (render_dock, [$dock]) {
				draw_sheet_dock(this, $dock);
			});
		});
	}

	// Run `run` with `owner[key]` once it is set: now, or when it is first assigned.
	function when_defined(owner, key, run) {
		const ready = guarded(run);
		if (owner[key]) {
			ready(owner[key]);
			return;
		}
		const descriptor = Object.getOwnPropertyDescriptor(owner, key);
		if (descriptor && !descriptor.configurable) return;
		Object.defineProperty(owner, key, {
			configurable: true,
			enumerable: true,
			get: () => undefined,
			set(value) {
				Object.defineProperty(owner, key, {
					value,
					writable: true,
					configurable: true,
					enumerable: true,
				});
				ready(value);
			},
		});
	}

	// The sheet's row: the dock's apps, or one app's tile, frontend and modules. `nav.opendesk_sheet`
	// is what the row is showing: `{apps}` while it lists the apps, `{app}` once one was picked.
	function draw_sheet_dock(nav, $dock) {
		const sidebar = frappe.app.sidebar;
		const state = nav.opendesk_sheet || (nav.opendesk_sheet = { apps: false, app: null });
		const here = dock_app_of(sidebar.current_module);
		const app = state.app || here;
		$dock.empty();
		if (state.apps || !app) {
			dock_apps
				.filter((each) => choice_count(each))
				.forEach((each) =>
					sheet_tile($dock, {
						label: __(each.title),
						mark: app_mark(each),
						active: each === here,
						on_click: () => pick_sheet_app(nav, $dock, each),
					})
				);
			return;
		}
		sheet_tile($dock, {
			label: __(app.title),
			mark: app_mark(app),
			css_class: "opendesk-sheet-app",
			on_click: () => {
				state.apps = true;
				draw_sheet_dock(nav, $dock);
				$dock.find(".desk-mobile-sheet-dock-item").first().trigger("focus");
			},
		});
		if (app.frontend) {
			sheet_tile($dock, {
				label: app.frontend.label,
				mark: frappe.utils.icon("external-link", "md"),
				on_click: () => {
					nav.close_sheet();
					visit_frontend(app);
				},
			});
		}
		module_layout(app).forEach(({ shell, label, icon }) =>
			sheet_tile($dock, {
				label,
				mark: frappe.utils.icon(icon, "md"),
				active: shell === sidebar.current_module,
				on_click: () => browse_sheet_module(nav, $dock, shell),
			})
		);
	}

	// A tile drawn as Frappe draws the row's own (`MobileNav.render_dock`).
	function sheet_tile($dock, { label, mark, active = false, css_class = "", on_click }) {
		const $tile = $(`<button type="button" class="desk-mobile-sheet-dock-item">
			<span class="dock-item-icon"></span>
			<span class="dock-item-label"></span>
		</button>`)
			.addClass(css_class)
			.toggleClass("active", active)
			.on("click", guarded(on_click));
		$tile.find(".dock-item-icon").html(mark);
		$tile.find(".dock-item-label").text(label);
		return $tile.appendTo($dock);
	}

	// An app picked in the sheet: its modules in the row, under its name. One with a single module
	// shows that module's sidebar at once; one with only a frontend opens it.
	function pick_sheet_app(nav, $dock, app) {
		const modules = modules_of(app);
		if (!modules.length) {
			nav.close_sheet();
			if (app.frontend) visit_frontend(app);
			return;
		}
		nav.opendesk_sheet = { apps: false, app };
		if (modules.length === 1 && !app.frontend) {
			browse_sheet_module(nav, $dock, modules[0].shell);
			return;
		}
		if (nav.sheet) nav.sheet.set_title(__(app.title));
		draw_sheet_dock(nav, $dock);
		$dock.find(".desk-mobile-sheet-dock-item").first().trigger("focus");
	}

	// A module picked in the sheet: its sidebar under the row, as Frappe's `browse_dock_entry` does.
	function browse_sheet_module(nav, $dock, shell) {
		frappe.app.sidebar.select_shell(shell);
		nav.opendesk_sheet = { apps: false, app: dock_app_of(shell) };
		if (nav.sheet) nav.sheet.set_title(nav.module_label(shell));
		draw_sheet_dock(nav, $dock);
		// The tapped tile was just rebuilt; focus left on <body> would miss the sheet's Escape.
		$dock.find(".active").trigger("focus");
	}

	// Other apps' tiles, on the dock under Frappe's Search and Notifications, which Frappe puts at
	// its top (`Dock.render_utilities`) while it is pinned or the page has no sidebar. Made with
	// Frappe's own `make_utility`, they come and go with that pair. Built once, with the Dock.
	patch(Dock.prototype, "make", function (make_dock) {
		const result = make_dock();
		const $utilities = this.$dock.find(".dock-utilities");
		// All of them at the bottom of the dock, over the user menu: the slot itself moves, so
		// Frappe's showing and hiding of it, and what it holds, are unchanged.
		if (features.dock_tools_bottom) $utilities.insertBefore(this.$dock.find(".dock-user"));
		// Off, other apps' tiles stay at the top of the sidebar, where their apps put them.
		if (!dock_tools) return result;
		// Their tips, among the Dock's `utility_tooltips`, taken out again if the dock gives up.
		this.opendesk_tool_tips = [];
		opendesk.dock.tools.forEach((spec) => {
			let $button = null;
			try {
				if (!spec || !spec.name || (spec.condition && !spec.condition())) return;
				const badge = spec.badge_class
					? `<span class="${frappe.utils.escape_html(
							spec.badge_class
					  )} opendesk-dock-count hidden" aria-live="polite"></span>`
					: "";
				const tips = this.utility_tooltips.length;
				$button = this.make_utility({
					label: spec.label || spec.name,
					icon: spec.icon || "square",
					css_class: `opendesk-dock-tool ${frappe.utils.escape_html(spec.class || "")}`,
					badge,
				})
					.attr("data-tool", spec.name)
					.appendTo($utilities);
				this.opendesk_tool_tips.push(...this.utility_tooltips.slice(tips));
				// Another app's handler: its failure is that app's, and leaves the dock on.
				if (spec.on_click) {
					$button.on("click", () => {
						try {
							spec.on_click($button);
						} catch (e) {
							console.error(`opendesk: the dock tile ${spec.name} failed`, e);
						}
					});
				}
				if (spec.on_draw) spec.on_draw($button);
			} catch (e) {
				// Left out even when it was already drawn, before its `on_draw` threw.
				if ($button) $button.remove();
				console.error(`opendesk: left the dock tile ${spec && spec.name} out`, e);
			}
		});
		return result;
	});

	// Whether this user may arrange the dock: the editors in `js/arrange.js` say.
	function can_manage() {
		const editors = window.opendesk && opendesk.dock;
		return !!(editors && editors.can_manage && editors.can_manage());
	}

	// The user menu: Manage Dock out, Manage Desk Apps in, where it was (`public/js/user_menu_rows.js`).
	// Manage Modules opens from the module list's header (`draw_list_header`), or is the header
	// menu's last row with the Module Menu picker (`picker_groups`).
	// Both rows stay in the menu, which is built once: Manage Desk Apps while the dock is on,
	// Frappe's own row again once it has given up.
	const manage_dock = {
		name: "opendesk-manage-desk-apps",
		// Read when the menu is drawn: Frappe may load the translations after this script runs.
		get label() {
			return __("Manage Desk Apps");
		},
		icon: "monitor",
		condition: () => !broken && can_manage(),
		onclick: () => opendesk.dock.manage_dock(),
		// Not on the phone's Profile page, which leaves Frappe's Manage Dock out too: a phone has no
		// dock to arrange (`public/js/user_menu_rows.js`).
		menu_only: true,
	};
	opendesk.user_menu.add((groups) =>
		groups.map((group) =>
			group && Array.isArray(group.options)
				? {
						...group,
						options: group.options.flatMap((row) =>
							row && row.name === "workspace-selector"
								? [
										manage_dock,
										{
											...row,
											condition: () =>
												broken && (!row.condition || row.condition()),
										},
								  ]
								: [row]
						),
				  }
				: group
		)
	);

	// After an editor saves: the dock, each module's dock app, and the app entries Frappe's header
	// reads, as the server now resolves them -- then everything drawn from them.
	frappe.provide("opendesk.dock");
	opendesk.dock.apply = guarded(function ({ desk_apps, app_data, module_sidebars }) {
		dock_apps.splice(0, dock_apps.length, ...(desk_apps || []));
		// With any module the editor just made, which the page's copy has never seen. Placed in
		// its dock app as it arrives (`js/boot_arrangement.js`).
		if (module_sidebars) frappe.boot.module_sidebars = module_sidebars;
		opendesk.boot_arrangement.adopt(app_data);
		opendesk.boot_arrangement.place(dock_apps);

		const sidebar = frappe.app && frappe.app.sidebar;
		if (!sidebar) return;
		// What a picker or the column is showing is an app of the old dock: the same app on the
		// new one, or nothing if it is gone.
		const fresh = (app) => (app && dock_apps.find((a) => a.key === app.key)) || null;
		if (sidebar.opendesk_picker_app) {
			sidebar.opendesk_picker_app = fresh(sidebar.opendesk_picker_app);
		}
		leave_browsing(sidebar);
		const list = sidebar.opendesk_module_list;
		if (list) {
			const app = fresh(list.app);
			app ? show_module_list(sidebar, app, { quiet: true }) : leave_module_list(sidebar);
		} else if ((sidebar_accordion || picker === "sidebar") && sidebar.current_module) {
			// The modules' headings, and the back row's app, are drawn into the sidebar itself.
			sidebar.setup(sidebar.current_module);
		} else {
			sidebar.refresh_header();
		}
		// Drawn afresh: the apps' names and marks may have changed, which a redraw in place keeps.
		if (sidebar.dock && sidebar.dock.$items) clear_dock(sidebar.dock);
		redraw_dock(sidebar);
	}, adopt_saved);

	// After the dock has given up, a save still reaches the boot, as without the dock.
	function adopt_saved({ app_data, module_sidebars }) {
		if (module_sidebars) frappe.boot.module_sidebars = module_sidebars;
		opendesk.boot_arrangement.adopt(app_data);
	}

	// Every page can switch apps, so the dock is drawn wherever the page lets Frappe draw a Dock,
	// whether or not the app on screen ships one.
	patch(Sidebar.prototype, "dock_enabled", () => true);

	// The site's mark at the top, leading where Frappe's app mark leads: the Apps screen. Only a
	// logo the site has set (`desk_apps.site_logo`); without one, the home icon rather than the
	// Frappe logo Frappe would fall back to.
	//
	// This and `render_entries` replace Frappe's methods rather than wrapping them: what they draw
	// is not Frappe's with something added, it is something else. So what Frappe adds to either
	// later is lost here without an error -- `test_frappe_seams` fingerprints both, and fails
	// when Frappe's change, so the change is read before it ships.
	patch(Dock.prototype, "render_logo", function () {
		// With App Menu, the mark is the app's, and opens the menu of apps.
		if (app_menu) {
			draw_app_logo(this);
			return;
		}
		const logo = frappe.boot.opendesk_site_logo;
		const title = __("Home");
		this.$header_logo.html(
			logo
				? frappe.utils.app_logo({ app_title: title, app_logo_url: logo }).icon
				: frappe.utils.icon("house", "md")
		);
		this.$header_title.text(title);
		this.$header.attr("aria-label", __("All apps"));
		if (!this.header_tooltip) {
			this.header_tooltip = new frappe.ui.Tooltip(this.$header[0], {
				text: __("All apps"),
				side: "right",
				delay: 0,
				offset: 10,
				class: "es-tooltip--plain",
			});
		}
	});

	// Apps instead of the open app's modules. Frappe calls this whenever what it would draw
	// changes, which includes moving to another module, so the lit app follows.
	patch(Dock.prototype, "render_entries", function () {
		const sidebar = this.sidebar;
		// With Accordion Dock, a redraw for the same apps keeps the tiles, so the trays can slide.
		if (dock_accordion && redraw_dock_in_place(this, sidebar)) {
			draw_beside(sidebar);
			return;
		}
		this.tooltips.forEach((tip) => tip.destroy());
		this.tooltips = [];
		clear_dock(this);
		// With App Menu, the app's modules, under its mark.
		if (app_menu) {
			draw_module_tiles(this, sidebar);
			this.render_logo();
			draw_beside(sidebar);
			return;
		}

		const current = lit_app(sidebar);

		dock_apps.forEach((app) => {
			if (!choice_count(app)) return;
			const is_active = !!current && app.key === current.key;
			const label = __(app.title);
			const $item = $(`<button
				class="dock-item opendesk-dock-app ${is_active ? "active" : ""}"
				data-app-key="${frappe.utils.escape_html(app.key)}"
				aria-label="${frappe.utils.escape_html(label)}"
				${is_active ? 'aria-current="page"' : ""}
			>
				<span class="dock-item-icon">${app_mark(app)}</span>
				<span class="dock-item-label">${frappe.utils.escape_html(label)}</span>
			</button>`);
			this.name_tile($item, label);
			$item.on(
				"click",
				guarded(
					() => {
						// The open app's tile, with its modules under it, folds them instead. Read
						// on the click: the tiles outlive the redraws that move the open app.
						if (
							app === dock_app_of(sidebar.current_module) &&
							$item.attr("aria-expanded")
						) {
							fold_dock_group(sidebar, app);
							return;
						}
						this.close();
						open_app(sidebar, app);
					},
					() => frappe_open_app(sidebar, app)
				)
			);
			this.$items.append($item);
		});
		arrange_dock_groups(sidebar, true);
		// The module column, or the band of tabs, follows the dock: it is drawn whenever the dock is.
		draw_beside(sidebar);
	});

	// And whenever a page shows or hides the sidebar, which takes the column or the band with it;
	// and when the window crosses 768px, where the column and the band give way to the header menu
	// and come back, and the dock moves into the drawer and out, the header with them, since it
	// names the app only where they do not.
	{
		let resize_timer = null;
		let was_mobile = frappe.is_mobile();
		$(window).on("resize.opendesk-beside", () => {
			clearTimeout(resize_timer);
			resize_timer = setTimeout(
				guarded(() => {
					const sidebar = frappe.app && frappe.app.sidebar;
					if (!sidebar || !sidebar.wrapper) return;
					const mobile = frappe.is_mobile();
					const crossed = mobile !== was_mobile;
					was_mobile = mobile;
					// The drawer's dock is pinned and a floating one out of it is not: what the
					// dock draws (App Menu, Accordion Dock) follows its reach.
					if (crossed && sidebar.dock && typeof sidebar.dock.apply_pin === "function") {
						sidebar.dock.apply_pin();
						redraw_dock(sidebar);
					}
					draw_beside(sidebar);
					// Crossing 768px changes whatever the header's menu holds (the Sliding
					// Sidebar's plain header, say), modules moving or not.
					if (crossed) sidebar.refresh_header();
				}),
				150
			);
		});
		["apply_page_visibility", "toggle"].forEach((method) => {
			if (typeof Sidebar.prototype[method] !== "function") return;
			patch(Sidebar.prototype, method, function (original) {
				const before = shown_state(this);
				const draws = beside_draws;
				const result = original();
				// Frappe shows or hides the sidebar, then refreshes the Dock, which redraws
				// through `render_entries` when the dock changed -- by then with the sidebar as
				// it now is. Drawn here only when what shows the column or band changed and that
				// redraw did not happen.
				if (shown_state(this) !== before && beside_draws === draws) draw_beside(this);
				// The page is on screen now, with its sidebar or without.
				if (method === "apply_page_visibility") run_after_page();
				return result;
			});
		});
	}

	// Any rebuild of the sidebar is the real sidebar again.
	patch(Sidebar.prototype, "setup", function (setup) {
		this.opendesk_module_list = null;
		this.opendesk_browsing = null;
		if (this.sidebar_header) clear_list_header(this.sidebar_header);
		return setup();
	});

	// Below 768px Frappe shuts the drawer whenever it rebuilds the sidebar, which it does on every
	// move into another module. A module picked in the drawer -- from the header's menu, the dock or
	// the sidebar's own list -- is a step on the way to the module's content, not the content: the
	// drawer stays open on the new module's rows. Picking one of those closes it, as Frappe closes
	// it (its click on a row that leads somewhere, before the route changes), and a rebuild with
	// the drawer already shut leaves it shut.
	if (typeof Sidebar.prototype.restore_expanded_state === "function") {
		patch(Sidebar.prototype, "restore_expanded_state", function (restore) {
			const keep_open = this.panel_can_close() && this.sidebar_expanded;
			const result = restore();
			if (keep_open && !this.sidebar_expanded) this.open();
			return result;
		});
	}

	// The same pick would then shut the drawer all the same, as its click reaches the document:
	// Frappe closes the drawer on a click outside it, and a row the pick rebuilt away, or one in
	// the header's menu (drawn over the page, outside the drawer), looks outside. Frappe's
	// click-away, with those two let through. (`test_frappe_seams` keeps the copy level with
	// Frappe's.)
	if (typeof Sidebar.prototype.setup_click_away === "function") {
		patch(Sidebar.prototype, "setup_click_away", function () {
			$(document)
				.off(".sidebar-click-away")
				.on("click.sidebar-click-away", (e) => {
					if (!this.sidebar_expanded || !this.panel_can_close()) return;
					if (
						$(e.target).closest(
							".body-sidebar, .dock, .sidebar-toggle-btn, .sidebar-panel, .sidebar-collapse-arrow"
						).length
					)
						return;
					if (
						!broken &&
						(!e.target.isConnected || $(e.target).closest("[role=menu]").length)
					)
						return;
					this.close();
				});
		});
	}

	// With the Sliding Sidebar, the rows Frappe draws for a module start with a way back to its
	// app's module list.
	if (picker === "sidebar" && typeof Sidebar.prototype.make_sidebar === "function") {
		patch(Sidebar.prototype, "make_sidebar", function (make_sidebar) {
			const result = make_sidebar();
			add_back_row(this);
			draw_edit_button(this);
			return result;
		});
	}

	// With Accordion Sidebar, the rows Frappe draws for the open module go under its heading. The
	// rows of the module being left are taken out first, before Frappe empties the sidebar, to
	// fold away under their own.
	if (sidebar_accordion && typeof Sidebar.prototype.make_sidebar === "function") {
		patch(Sidebar.prototype, "make_sidebar", function (make_sidebar) {
			const left = this.opendesk_accordion_shell;
			const $rows =
				left && left !== this.current_module && this.$items_container
					? this.$items_container.children(".opendesk-accordion-content").detach()
					: $();
			const result = make_sidebar();
			draw_accordion(this, left ? { shell: left, $content: $rows } : null);
			return result;
		});
	}

	// Frappe re-resolves the sidebar on every route change but rebuilds it only when the answer
	// is a different module, which the list never changed. So once the route has moved on from
	// where the list was opened, the list is put away here.
	patch(Sidebar.prototype, "set_workspace_sidebar", function (set_workspace_sidebar) {
		const result = set_workspace_sidebar();
		const list = this.opendesk_module_list;
		if (list && frappe.get_route_str() !== list.route) leave_module_list(this);
		// The same for an app the column, the band, the dock or the sidebar was showing.
		const browsing = this.opendesk_browsing;
		if (browsing && frappe.get_route_str() !== browsing.route) leave_browsing(this);
		// Frappe has lit the row for the page: noted as the one its app was left on -- once the
		// module's own rows are back, since over a module list or another app's modules no row is.
		if (!this.opendesk_module_list && !this.opendesk_browsing) {
			once_page_shows(() => note_item(this));
		}
		// A tile on the Apps screen was picked: its app's module list, once the page it opens is
		// on screen with its sidebar.
		if (from_apps_screen) {
			const app = from_apps_screen;
			from_apps_screen = null;
			remember_pick(null);
			once_page_shows(() => offer_modules(this, app));
		}
		return result;
	});

	// The Apps screen. Its tiles are links to each app's landing page, which Frappe takes to be
	// the app's first module (`Sidebar.app_landing_route`). The page is still that one, but for
	// an app with a choice to make, its modules are offered, as picking the app on the dock does
	// -- once the route has changed and the sidebar is built (`set_workspace_sidebar` above). A tile leading out of the desk, to a frontend, or for an
	// app with one thing to pick, is left alone.
	//
	// Some tiles link to `/app/...`, the desk's old address, which reloads the page on the way to
	// `/desk/...`. So the pick is also kept in this tab's session storage for a few seconds, and
	// the page it lands on takes it from there.
	//
	// With Open Last Module or Open Last Sidebar Item a tile does what picking the app on the dock
	// does (`enter_app`) rather than open the landing page, unless the click is one that opens the
	// link elsewhere (a new tab, say).
	const PICK = "opendesk-apps-screen-pick";
	let from_apps_screen = picked_before_reload();
	document.addEventListener(
		"click",
		guarded((event) => {
			from_apps_screen = null;
			if (!(event.target instanceof Element)) return;
			const link = event.target.closest(".desktop-container a[href]");
			if (!link) return;
			// A click that opens the tile elsewhere (a new tab, say) leaves this page where it is,
			// and nothing armed for the next page it shows.
			const plain_click =
				event.button === 0 &&
				!event.metaKey &&
				!event.ctrlKey &&
				!event.shiftKey &&
				!event.altKey &&
				link.getAttribute("target") !== "_blank";
			if (!plain_click) return;
			from_apps_screen = tile_app(link);
			if (enters_app && from_apps_screen) {
				const app = from_apps_screen;
				from_apps_screen = null;
				event.preventDefault();
				event.stopPropagation();
				enter_app(frappe.app.sidebar, app);
				return;
			}
			remember_pick(from_apps_screen);
		}),
		true
	);

	function remember_pick(app) {
		try {
			if (app)
				sessionStorage.setItem(PICK, JSON.stringify({ key: app.key, at: Date.now() }));
			else sessionStorage.removeItem(PICK);
		} catch (e) {
			// Storage refused (a private window, say): a reloading tile simply opens its module.
		}
	}

	function picked_before_reload() {
		try {
			const saved = JSON.parse(sessionStorage.getItem(PICK) || "null");
			sessionStorage.removeItem(PICK);
			if (!saved || Date.now() - saved.at > 15000) return null;
			return dock_apps.find((app) => app.key === saved.key) || null;
		} catch (e) {
			return null;
		}
	}

	// The dock app an Apps screen tile leads into, when it should open on the module list.
	function tile_app(link) {
		const sidebar = frappe.app && frappe.app.sidebar;
		if (!sidebar || typeof sidebar.app_landing_route !== "function") return null;
		const path = (url) => new URL(url, window.location.origin).pathname.replace(/\/$/, "");
		const target = path(link.href);
		if (!/^\/(desk|app)(\/|$)/.test(target)) return null;
		const entry = (frappe.boot.app_data || []).find((candidate) => {
			if (!candidate.on_apps_screen) return false;
			const route = sidebar.app_landing_route(candidate);
			return route && path(route) === target;
		});
		const app = entry && dock_apps.find((candidate) => candidate.app_name === entry.app_name);
		return app && choice_count(app) > 1 ? app : null;
	}

	// Frappe makes the header, and redraws it, as pages settle and modules change, always through
	// here. Over the Sliding Sidebar's list it is the app over its module count; over another app's
	// modules, that app; beside the module column, the module alone; inside a module otherwise, in
	// every picker, the app over its module, as the levels run -- the app's mark, and Frappe's title
	// moving to the line under.
	patch(Sidebar.prototype, "refresh_header", function (refresh_header) {
		const result = refresh_header();
		const header = this.sidebar_header;
		if (this.opendesk_module_list) {
			draw_list_header(this);
		} else if (header && this.opendesk_picker_app) {
			draw_picker_header(header, this.opendesk_picker_app);
		} else if (header) {
			clear_list_header(header);
			const app = dock_app_of(this.current_module);
			if (sidebar_accordion_shown(this) && browsing_app(this)) {
				// Over another app's module headings, that app alone.
				draw_accordion_header(this, header);
			} else if (column_shown(this)) {
				// The module column beside it names the app: the header names the module alone,
				// as Frappe draws it.
				set_subtitle(header, "");
			} else if (app) {
				const module_title = header.$header_title.text();
				header.$header_title.text(__(app.title));
				// With App Menu the dock's mark is the app's already: the header is words alone.
				header.$header_logo.html(app_menu_shown(this) ? "" : app_mark(app));
				header.wrapper.toggleClass("opendesk-header-no-mark", app_menu_shown(this));
				// A module called what its app is (Education's, say) is not named twice.
				set_subtitle(header, module_title === __(app.title) ? "" : module_title);
			} else {
				set_subtitle(header, "");
			}
			mark_lone_row(this, header);
			sliding_header(this, header);
			tabs_header(this, header);
		}
		return result;
	});

	// A header menu of one row is no menu -- Three Column or Module Tabs leaves only Edit Sidebar
	// in it, say. The header then does what that row does, on a click (Enter and Space arrive as
	// clicks too), without the chevron, and names the row in its tooltip. Taken in the capture
	// phase, so the menu's own listener on the header never opens a menu of one.
	//
	// Only beside the module column or the band: every other picker keeps the modules in this
	// menu, so it is never one row there, and the menu's rows are only read where they can be.
	// Reading them runs the site's own row conditions (Navbar Settings), and one that throws
	// means a menu, not a broken dock.
	function lone_row(header) {
		if (!modules_beside(header.sidebar)) return null;
		try {
			return only_visible_row(header);
		} catch (e) {
			return null;
		}
	}

	function only_visible_row(header) {
		const rows = visible_rows(header);
		return rows.length === 1 && !rows[0].submenu ? rows[0] : null;
	}

	// The rows the header's menu would show, as it would read them on opening.
	function visible_rows(header) {
		const rows = [];
		const take = (row) => {
			if (row && (!row.condition || row.condition())) rows.push(row);
		};
		(header.menu_items() || []).forEach((entry) => {
			if (entry && Array.isArray(entry.options)) entry.options.forEach(take);
			else take(entry);
		});
		return rows;
	}

	// Sliding Sidebar: a header whose menu would be empty -- the modules being the sidebar's own
	// list and Edit Sidebar its corner's button, which is so wherever the dock can be reached and
	// the site's rows have moved to the user menu -- is a plain label: no chevron, and a click or a
	// key on it opens nothing. Over the module list it keeps its own click (`draw_list_header`).
	// Reading the rows runs the site's own row conditions, and one that throws means a menu.
	function menu_is_empty(header) {
		try {
			return !visible_rows(header).length;
		} catch (e) {
			return false;
		}
	}

	function sliding_header(sidebar, header) {
		if (picker !== "sidebar") return;
		const plain = menu_is_empty(header);
		header.wrapper.toggleClass("opendesk-header-plain", plain);
		if (plain) header.$drop_icon && header.$drop_icon.addClass("hidden");
		if (header.opendesk_plain_guard) return;
		const swallow = guarded((event) => {
			if (
				event.type === "keydown" &&
				!["Enter", " ", "ArrowDown", "ArrowUp"].includes(event.key)
			) {
				return;
			}
			// As the header's last redraw found it (above), rather than reading the menu again.
			if (
				sidebar.opendesk_module_list ||
				!header.wrapper.hasClass("opendesk-header-plain")
			) {
				return;
			}
			event.stopImmediatePropagation();
			event.preventDefault();
		});
		// Capture phase, so it runs before the menu's own listeners on this element.
		header.wrapper.get(0).addEventListener("click", swallow, true);
		header.wrapper.get(0).addEventListener("keydown", swallow, true);
		header.opendesk_plain_guard = true;
	}

	// Sliding Sidebar, and Module Tabs beside the band: Edit Sidebar, a pencil in the sidebar's
	// lower right corner, while a module's content is shown (not over the Sliding Sidebar's module
	// list, which it does not edit). It does what Frappe's own Edit Sidebar row does: loads the
	// editor and opens it on the sidebar on screen.
	function draw_edit_button(sidebar) {
		if ((picker !== "sidebar" && !tabs_mode) || !sidebar.wrapper) return;
		let $button = sidebar.wrapper.find(".opendesk-edit-sidebar");
		if (!$button.length) {
			const label = __("Edit Sidebar");
			$button = $(`<button class="btn-reset opendesk-edit-sidebar" type="button">
				${frappe.utils.icon("pencil", "sm")}
			</button>`)
				.attr({ title: label, "aria-label": label })
				.appendTo(sidebar.wrapper.find(".body-sidebar"));
			$button.on(
				"click",
				guarded(() =>
					frappe
						.require("arrangement_editor.bundle.js")
						.then(() => new frappe.ui.SidebarManager())
						.catch((e) => {
							console.error("opendesk: could not open the sidebar editor", e);
							frappe.ui.toast({
								message: __(
									"Could not open the sidebar editor. Please refresh the page."
								),
								type: "error",
							});
						})
				)
			);
		}
		const wanted = picker === "sidebar" ? !sidebar.opendesk_module_list : tabs_shown(sidebar);
		$button.toggleClass("hidden", !wanted || !sidebar.current_module);
	}

	// Module Tabs: beside the band, which names the app and lists its modules, the sidebar's header
	// is not drawn at all -- when its menu would hold nothing else (`menu_is_empty`), Edit Sidebar
	// being the corner's button. Below 768px there is no band, and the header is back.
	function tabs_header(sidebar, header) {
		if (!tabs_mode) return;
		header.wrapper.toggleClass(
			"opendesk-header-hidden",
			tabs_shown(sidebar) && menu_is_empty(header)
		);
	}

	function mark_lone_row(sidebar, header) {
		if (!column_mode && !tabs_mode) return;
		const row = lone_row(header);
		header.$drop_icon && header.$drop_icon.toggleClass("hidden", !!row);
		header.wrapper.attr("title", row ? row.label : null);
		if (header.opendesk_lone_guard) return;
		header.wrapper.get(0).addEventListener(
			"click",
			guarded((event) => {
				// The module list and the picker draw headers of their own.
				if (sidebar.opendesk_module_list || sidebar.opendesk_picker_app) return;
				const only = lone_row(header);
				if (!only) return;
				event.stopImmediatePropagation();
				event.preventDefault();
				if (only.onclick) only.onclick(event);
				else if (only.href && only.target) window.open(only.href, only.target);
				else if (only.href) window.location.assign(only.href);
			}),
			true
		);
		header.opendesk_lone_guard = true;
	}

	// Back to the header Frappe draws for a module.
	function clear_list_header(header) {
		header.wrapper
			.removeClass(
				"opendesk-module-list-header opendesk-module-list-header--manageable opendesk-header-no-mark"
			)
			.removeAttr("title");
		header.$drop_icon && header.$drop_icon.removeClass("hidden");
	}

	// The line under the header's title, in Frappe's own `.header-subtitle` style. Frappe's header
	// has none of its own, so it is added the first time and dropped when there is nothing to say.
	function set_subtitle(header, text) {
		let $subtitle = header.wrapper.find(".title-container .header-subtitle");
		if (!text) {
			$subtitle.remove();
			return;
		}
		if (!$subtitle.length) {
			$subtitle = $('<div class="header-subtitle"></div>').appendTo(
				header.wrapper.find(".title-container")
			);
		}
		$subtitle.text(text);
	}

	// The header menu's switcher rows become the open app's module list: its frontend first, then
	// its modules under their Categories, a Spacer starting a new group.
	//
	// With the Module Menu picker the modules come under the app's name, then Manage Modules; and
	// opened from the dock on another app that is all it holds, since the rest of the menu
	// concerns the sidebar on screen, which is not that app's.
	patch(Header.prototype, "menu_items", function (menu_items) {
		const items = menu_items();
		const open_app = dock_app_of(this.sidebar.current_module);
		const app = this.sidebar.opendesk_picker_app || open_app;
		// A module no dock app holds (one its app's Dock hides, say) still gets the dock's apps
		// in place of Frappe's "Apps" row, which lists every `app_data` entry on the Apps screen
		// -- per-module tiles among them, when the Apps screen is arranged from the dock.
		if (!app) return without_app_switcher(items, app_switcher(this, this.sidebar));
		// The module column, the band or the accordion lists the modules, so the menu does not list
		// them again. The accordions have no button of their own for Manage Modules: it is here.
		if (modules_beside(this.sidebar)) {
			const rest = items.filter((group) => !is_switcher(group));
			return [
				...(app_menu || dock_accordion || sidebar_accordion ? manage_group(app) : []),
				...app_switcher(this, this.sidebar),
				// Beside the band, Edit Sidebar is the corner's button (`draw_edit_button`).
				...(tabs_mode ? without_rows(rest, ["edit-sidebar"]) : rest),
			];
		}
		// The Sliding Sidebar lists the modules itself, behind its back row, and Edit Sidebar is
		// its corner's button: what is left is the way to another app where the dock cannot be
		// reached, and the site's own rows (`sliding_header`).
		if (picker === "sidebar") {
			return [
				...app_switcher(this, this.sidebar),
				...without_rows(
					items.filter((group) => !is_switcher(group)),
					["edit-sidebar"]
				),
			];
		}
		const modules = menu_picker
			? picker_groups(this.sidebar, app)
			: module_groups(this.sidebar, app);
		if (app !== open_app) return modules;
		return [
			...modules,
			...app_switcher(this, this.sidebar),
			...items.filter((group) => !is_switcher(group)),
		];
	});

	// Menu groups less the rows named, and any group left with none.
	function without_rows(groups, names) {
		return groups
			.map((group) =>
				group && Array.isArray(group.options)
					? {
							...group,
							options: group.options.filter((row) => !names.includes(row?.name)),
					  }
					: group
			)
			.filter((group) => !group || !Array.isArray(group.options) || group.options.length);
	}

	// The app's modules under its name, then Manage Modules for whoever may arrange the dock.
	function picker_groups(sidebar, app) {
		const groups = module_groups(sidebar, app);
		if (groups.length && !groups[0].group) groups[0].group = __(app.title);
		else groups.unshift({ group: __(app.title), options: [] });
		groups.push(...manage_group(app));
		return groups;
	}

	// Manage Modules for `app`, for whoever may arrange the dock.
	function manage_group(app) {
		return [
			{
				group: "",
				options: [
					{
						name: "opendesk-manage-modules",
						label: __("Manage Modules"),
						icon: "settings-2",
						condition: can_manage,
						onclick: () => opendesk.dock.manage_modules(app.key),
					},
				],
			},
		];
	}

	// Frappe's rows less its "Apps" row -- and its way out to the Apps screen, when the dock's own
	// switcher carries one -- then the dock's switcher.
	function without_app_switcher(items, switcher) {
		const dropped = ["switch-app", ...(switcher.length ? ["all-apps"] : [])];
		return [...without_rows(items, dropped), ...switcher];
	}

	// Frappe's switcher group, known by its rows rather than by where it sits: Modules, Apps, and
	// the way out to the Apps screen (`SidebarHeader.switcher_items`). A group that holds nothing
	// else is the switcher, whatever else Frappe puts in the menu or in what order.
	const SWITCHER_ROWS = new Set(["switch-module", "switch-app", "all-apps"]);
	function is_switcher(group) {
		const rows = (group && Array.isArray(group.options) && group.options) || [];
		return rows.length > 0 && rows.every((row) => row && SWITCHER_ROWS.has(row.name));
	}

	// Where the dock cannot be reached -- a touch screen with the dock floating out of reach, or
	// a page that leaves the dock off -- the header menu is the only way to another app, as
	// Frappe's own switcher is there. So it carries the
	// dock's apps, then the way out to the Apps screen. Read on every open, as the menu's rows are.
	function app_switcher(header, sidebar) {
		if (dock_reachable(sidebar)) return [];
		const apps = dock_apps
			.filter((app) => choice_count(app))
			.map((app) => ({
				name: `opendesk-dock-app-${app.key}`,
				label: __(app.title),
				onclick: guarded(
					() => open_app(sidebar, app),
					() => frappe_open_app(sidebar, app)
				),
			}));
		return [
			{
				group: "",
				options: [
					{
						name: "opendesk-switch-app",
						label: __("Apps"),
						icon: "layout-dashboard",
						submenu: [
							{ group: "", options: apps },
							{
								group: "",
								options:
									typeof header.all_apps_item === "function"
										? [header.all_apps_item()]
										: [],
							},
						],
					},
				],
			},
		];
	}

	function module_groups(sidebar, app) {
		const groups = [];
		let group = null;
		const start = (label) => {
			group = { group: label || "", options: [] };
			groups.push(group);
		};

		if (app.frontend) {
			start();
			group.options.push({
				name: "opendesk-dock-frontend",
				label: app.frontend.label,
				icon: "external-link",
				href: app.frontend.url,
			});
		}

		module_layout(app).forEach(({ entry, label, icon, category, spacer }) => {
			if (category) {
				start(category);
			} else if (!group || spacer) {
				start();
			}
			group.options.push({
				name: `opendesk-dock-module-${entry.shell}`,
				label,
				icon,
				// The Module Menu's rows are the only place modules are listed, so the one on
				// screen is marked there.
				selected: menu_picker && entry.shell === sidebar.current_module,
				onclick: module_opener(sidebar, entry.shell, "fade"),
			});
		});
		return groups;
	}
})();
