import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Kirigami.ScrollablePage {
    id: pageRoot

    title: "YouTube Video Projects"

    property string searchQuery: ""
    property string statusFilter: "all" // "all", "in_progress", "uploaded"
    property string sortBy: "last_update" // "last_update", "creation_date", "id", "title"
    property var filteredProjects: []

    signal newProjectRequested()
    signal openSettingsRequested()
    signal openEditorRequested(string projectId)

    onStatusFilterChanged: {
        if (typeof statusCombo !== "undefined" && statusCombo) {
            var idx = statusCombo.indexOfValue(statusFilter);
            if (idx >= 0 && statusCombo.currentIndex !== idx) {
                statusCombo.currentIndex = idx;
            }
        }
    }

    function updateFilteredList() {
        if (!backend) return;
        var list = backend.projects || [];
        var query = searchQuery.trim().toLowerCase();
        var status = statusFilter;
        var res = [];

        for (var i = 0; i < list.length; i++) {
            var p = list[i];
            if (status === "in_progress" && p.videoUploaded) continue;
            if (status === "uploaded" && !p.videoUploaded) continue;

            if (query.length > 0) {
                var idMatch = (p.id || "").toLowerCase().indexOf(query) !== -1;
                var titleMatch = (p.title || "").toLowerCase().indexOf(query) !== -1;
                var descMatch = (p.description || "").toLowerCase().indexOf(query) !== -1;
                var webMatch = (p.webSite || "").toLowerCase().indexOf(query) !== -1;
                if (!idMatch && !titleMatch && !descMatch && !webMatch) continue;
            }
            res.push(p);
        }

        res.sort(function(a, b) {
            if (pageRoot.sortBy === "id") {
                return (a.id || "").localeCompare(b.id || "", undefined, { numeric: true, sensitivity: "base" });
            } else if (pageRoot.sortBy === "title") {
                return (a.title || "").localeCompare(b.title || "", undefined, { sensitivity: "base" });
            } else if (pageRoot.sortBy === "creation_date") {
                return (b.dateOfCreation || "").localeCompare(a.dateOfCreation || "");
            } else {
                return (b.lastUpdate || "").localeCompare(a.lastUpdate || "");
            }
        });

        filteredProjects = res;
    }

    Connections {
        target: backend
        function onProjectsChanged() {
            pageRoot.updateFilteredList();
        }
    }

    Component.onCompleted: {
        updateFilteredList();
    }

    // Page Actions (Header Toolbar)
    actions: [
        Kirigami.Action {
            text: "New Project"
            icon.name: "list-add"
            tooltip: "Create a new video project"
            displayHint: Kirigami.DisplayHint.AlwaysHide
            onTriggered: pageRoot.newProjectRequested()
        },
        Kirigami.Action {
            text: "Settings"
            icon.name: "settings-configure"
            tooltip: "Configure projects folder and default templates"
            onTriggered: pageRoot.openSettingsRequested()
        },
        Kirigami.Action {
            text: "Reload"
            icon.name: "view-refresh"
            tooltip: "Rescan projects folder"
            onTriggered: {
                if (backend) backend.reloadProjects();
            }
        }
    ]

    // Top Header: Search and Filter Bar
    header: ColumnLayout {
        id: headerLayout
        spacing: Kirigami.Units.smallSpacing

        // Search Field Row
        RowLayout {
            Layout.fillWidth: true
            Layout.margins: Kirigami.Units.smallSpacing
            spacing: Kirigami.Units.smallSpacing

            Kirigami.SearchField {
                id: searchInput
                Layout.fillWidth: true
                placeholderText: "Search projects by ID, video title, description, or link..."

                onTextChanged: {
                    pageRoot.searchQuery = text;
                    pageRoot.updateFilteredList();
                }
            }

            Controls.Button {
                icon.name: "list-add"
                text: "New Project"
                highlighted: true
                onClicked: pageRoot.newProjectRequested()
            }
        }

        // Filter and Sort Row
        RowLayout {
            Layout.fillWidth: true
            Layout.leftMargin: Kirigami.Units.smallSpacing
            Layout.rightMargin: Kirigami.Units.smallSpacing
            Layout.bottomMargin: Kirigami.Units.smallSpacing
            spacing: Kirigami.Units.smallSpacing

            // Status Filter Dropdown
            Controls.Label {
                text: "Status:"
                font: Kirigami.Theme.smallFont
                opacity: 0.7
            }

            Controls.ComboBox {
                id: statusCombo

                FontMetrics {
                    id: statusFontMetrics
                    font: statusCombo.font
                }

                implicitWidth: Math.max(
                    Kirigami.Units.gridUnit * 11,
                    statusFontMetrics.advanceWidth("In Progress (" + (backend ? backend.inProgressCount : 0) + ")") + Kirigami.Units.gridUnit * 4
                )
                Layout.preferredWidth: implicitWidth
                popup.width: Math.max(statusCombo.width, Kirigami.Units.gridUnit * 11)

                model: [
                    { text: "All (" + (backend ? backend.totalCount : 0) + ")", value: "all" },
                    { text: "In Progress (" + (backend ? backend.inProgressCount : 0) + ")", value: "in_progress" },
                    { text: "Uploaded (" + (backend ? backend.uploadedCount : 0) + ")", value: "uploaded" }
                ]
                textRole: "text"
                valueRole: "value"
                currentIndex: 0
                onActivated: {
                    pageRoot.statusFilter = currentValue;
                    pageRoot.updateFilteredList();
                }
                onModelChanged: {
                    var idx = indexOfValue(pageRoot.statusFilter);
                    if (idx >= 0) {
                        currentIndex = idx;
                    }
                }
            }

            Item { Layout.fillWidth: true }

            // Sort Dropdown
            Controls.Label {
                text: "Sort:"
                font: Kirigami.Theme.smallFont
                opacity: 0.7
            }

            Controls.ComboBox {
                id: sortCombo
                implicitWidth: Kirigami.Units.gridUnit * 9
                Layout.preferredWidth: implicitWidth
                popup.width: Math.max(sortCombo.width, Kirigami.Units.gridUnit * 9)

                model: [
                    { text: "Last Updated", value: "last_update" },
                    { text: "Creation Date", value: "creation_date" },
                    { text: "Project ID", value: "id" },
                    { text: "Video Title", value: "title" }
                ]
                textRole: "text"
                valueRole: "value"
                currentIndex: 0
                onActivated: {
                    pageRoot.sortBy = currentValue;
                    pageRoot.updateFilteredList();
                }
            }
        }

        // Separator
        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: Kirigami.ColorUtils.linearInterpolation(Kirigami.Theme.backgroundColor, Kirigami.Theme.textColor, 0.15)
        }
    }

    // Projects Grid Content: Dynamically scales tiles on X axis with 320px minimum size (reduced by half)
    GridLayout {
        id: gridLayout
        Layout.fillWidth: true
        width: pageRoot.width - (pageRoot.leftPadding + pageRoot.rightPadding)

        // Reduced by half: 320px width (180px height in 16:9)
        readonly property real minTileWidth: 320
        readonly property real availWidth: Math.max(minTileWidth, width)

        // Number of tiles on X axis automatically scales with window width (e.g. 4-5 on 1080p, 6-7 on 1440p)
        columns: Math.max(1, Math.floor((availWidth + columnSpacing) / (minTileWidth + columnSpacing)))
        columnSpacing: Kirigami.Units.largeSpacing
        rowSpacing: Kirigami.Units.largeSpacing

        visible: pageRoot.filteredProjects.length > 0

        Repeater {
            model: pageRoot.filteredProjects

            ProjectCard {
                projectData: modelData
                Layout.fillWidth: true
                Layout.preferredWidth: 0
                Layout.fillHeight: true
                onOpenEditorRequested: function(projId) {
                    pageRoot.openEditorRequested(projId);
                }
            }
        }
    }

    // Empty Search / Filter State
    Kirigami.PlaceholderMessage {
        anchors.centerIn: parent
        width: parent.width - (Kirigami.Units.largeSpacing * 4)
        visible: pageRoot.filteredProjects.length === 0
        icon.name: pageRoot.searchQuery.length > 0 ? "edit-find" : "folder-videos"
        text: pageRoot.searchQuery.length > 0
              ? "No projects match '" + pageRoot.searchQuery + "'"
              : "No video projects found in folder"
        explanation: pageRoot.searchQuery.length > 0
                     ? "Try searching for a different keyword or check the status filter."
                     : "Current path: " + (backend ? backend.projectsFolder : "")

        helpfulAction: pageRoot.searchQuery.length > 0 ? clearSearchAction : newProjectAction

        Kirigami.Action {
            id: clearSearchAction
            text: "Clear Search"
            icon.name: "edit-clear"
            onTriggered: {
                searchInput.text = "";
                pageRoot.searchQuery = "";
                pageRoot.statusFilter = "all";
                pageRoot.updateFilteredList();
            }
        }

        Kirigami.Action {
            id: newProjectAction
            text: "Create First Project"
            icon.name: "list-add"
            onTriggered: pageRoot.newProjectRequested()
        }
    }
}
