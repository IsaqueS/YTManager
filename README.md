# YTManager

Manage YouTube Video Projects with a modern KDE Kirigami GUI and CLI tool.

## GUI Application (Kirigami / KDE)

The application now features a KDE Kirigami GUI tailored for Linux / KDE Plasma desktops.

### Features
- **Project Search & Grid View**: Search videos by ID, title, description, or website link. Videos are displayed in a responsive grid format with real-time thumbnail previews, upload badges, and dates.
- **Visual `project.toml` Editor**:
  - Edit video title (with max 100 char limit)
  - Toggle upload status ("Video Uploaded")
  - Edit pre-description, main description (max 4900 chars), post-description, and website links
  - Configure video and thumbnail export paths
  - Live preview of formatted YouTube upload text with a single-click "Copy to Clipboard" button
  - Quick open actions for Dolphin (project folder, thumbnail folder, video folder)
- **Settings Screen**:
  - Change default projects folder directory with a native folder chooser
  - Edit project file name (`project.toml`)
  - Customize new project template folder hierarchy (add/remove subdirectories)
  - Configure default video/thumbnail export paths and description link prefix
- **New Project Creator**:
  - Create new projects directly from the GUI with automatic folder generation and metadata initialization.

### Running the GUI
```bash
# Launch GUI directly (default when no CLI argument is given)
python ytmanager.py

# Or explicitly
python ytmanager.py gui

# Or via desktop launcher
# An application entry 'YTManager' is installed in ~/.local/share/applications
```

---

## CLI Usage

### `ytmanager create <project_id> [project_id ...]`
Creates new video project structure and `project.toml` file defined in `save/settings.toml`.

### `ytmanager status [-p / --path]`
Prints all unfinished / in-progress video projects.

### `ytmanager done <project_id> [--all / -a]`
Marks projects as uploaded/done and updates the timestamp in `project.toml`.

### `ytmanager cat <project_id>`
Prints the formatted YouTube video title, description, and link.

### `ytmanager path <project_id> [-t / --toml]`
Prints the project path or the `project.toml` file path.
