### Open Desk

Desk navigation for Frappe 16.50 and later, each part behind its own switch in
Open Desk Settings:

- **Override Dock.** Frappe's Dock lists apps instead of the open
  app's modules. A site groups modules into apps of its own, or rearranges an
  installed app's, with **Desk App** records (or Manage Desk Apps and Manage Modules
  from the user menu). Modules no Desk App claims stay under their installed
  app; those of apps Frappe lists nowhere are under Other.
- **Move Other Apps' Tiles to Dock.** Frappe puts Search and Notifications on
  a pinned dock; with this, the tiles other apps add beside them (such as
  Commons' To Do) move from the top of the sidebar onto the dock with them.
- **Move Search and Notifications to Bottom of Dock.** All of those tiles at
  the bottom of the dock, above the user menu, rather than under the logo.
- **Override Desktop Icons.** Frappe's Apps screen (`/desk`) arranged in dock
  order: Frappe's default, one icon, an icon per module, the app and its
  modules, or none -- set per app in Manage Desk Apps (also in the Apps screen's
  avatar menu). A module tile shows its row's Apps Screen Image, else the
  module's own icon on a tile in the Desk App's Color (else the app's colour).
  Only where Desktop Settings shows the Apps screen; Frappe's
  older Desktop Icons grid, which it is retiring, is left as Frappe draws it.
- **Move Help and Site Tools to User Menu.** The site's Navbar Settings rows and
  Help move from the sidebar header's menu into the user menu.

Other apps can add tiles to the dock through `opendesk.dock.tools`;
see `opendesk/open_desk/js/dock.js`.

### Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch main
bench install-app opendesk
```

### Tests

A browser smoke test against a running site: the dock, its module list, the user menu, Manage
Desk Apps and Manage Modules, and the Apps screen. It only reads, checks whatever the site has
switched on, and logs out at the end. It drives your installed Chrome; Playwright is installed
once into `~/.cache/opendesk-smoke`.

```bash
OPENDESK_SMOKE_PASSWORD=admin tests/smoke/run.sh http://demo.localhost:8000
```

Before pulling a new Frappe: the names, classes, icons and boot data Open Desk leans on, looked
for in the Frappe it would pull (any ref `apps/frappe` has fetched; the checkout is not touched).
A failure is a list of what to read in Frappe's diff, not a broken desk:

```bash
git -C apps/frappe fetch upstream
apps/opendesk/tests/check_frappe.sh upstream/version-16-hotfix   # or upstream/develop
```

Site-less, over Frappe's source and plain data:

```bash
cd sites && ../env/bin/python -m unittest opendesk.open_desk.test_frappe_seams \
  opendesk.open_desk.test_desk_apps opendesk.open_desk.test_apps_screen \
  opendesk.open_desk.test_module_tiles
```

### License

MIT
