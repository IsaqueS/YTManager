import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.kirigami.layouts as KirigamiLayouts

Kirigami.ApplicationWindow {
    id: appWindow

    title: "YTManager"
    width: 1024
    height: 720
    minimumWidth: 640
    minimumHeight: 480

    // Component templates for dynamic navigation
    Component {
        id: settingsPageComponent
        SettingsPage {}
    }

    Component {
        id: editorPageComponent
        ProjectEditorPage {}
    }

    NewProjectDialog {
        id: newProjectDialog
        onProjectCreated: function(projectId) {
            backend.selectProject(projectId);
            appWindow.pageStack.push(editorPageComponent);
        }
    }

    // Connect to backend notifications
    Connections {
        target: backend
        function onNotification(message, isError) {
            appWindow.showPassiveNotification(message, 3000);
        }
    }

    Binding {
        target: appWindow.pageStack.columnView
        property: "columnResizeMode"
        value: appWindow.pageStack.wideMode ? KirigamiLayouts.ColumnView.DynamicColumns : KirigamiLayouts.ColumnView.SingleColumn
    }

    pageStack.initialPage: ProjectsPage {
        id: mainProjectsPage

        onOpenSettingsRequested: {
            appWindow.pageStack.push(settingsPageComponent);
        }

        onOpenEditorRequested: function(projectId) {
            backend.selectProject(projectId);
            appWindow.pageStack.push(editorPageComponent);
        }

        onNewProjectRequested: {
            newProjectDialog.open();
        }
    }
}
