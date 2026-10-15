import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.kirigami.layouts as KirigamiLayouts
import org.kde.kirigamiaddons.formcard as FormCard

Kirigami.ScrollablePage {
    id: settingsRoot

    title: "Settings"

    KirigamiLayouts.ColumnView.fillWidth: true
    KirigamiLayouts.ColumnView.interactiveResizeEnabled: true
    KirigamiLayouts.ColumnView.minimumWidth: Kirigami.Units.gridUnit * 18
    KirigamiLayouts.ColumnView.maximumWidth: (typeof appWindow !== "undefined") ? (appWindow.width - Kirigami.Units.gridUnit * 18) : (Kirigami.Units.gridUnit * 60)

    property var st: backend.settingsData || ({})

    property string editFolder: st ? (st.videoProjectsFolder || "") : ""
    property string editFileName: st ? (st.fileName || "project.toml") : "project.toml"
    property string editVideoPath: st ? (st.defaultVideoPath || "Export/Video") : "Export/Video"
    property string editThumbPath: st ? (st.defaultThumbPath || "Export/Thumb") : "Export/Thumb"
    property string editPreLink: st ? (st.defaultPreLink || "Saiba mais: ") : "Saiba mais: "
    property var editFoldersList: (st && st.folders) ? JSON.parse(JSON.stringify(st.folders)) : []

    function syncFromBackend() {
        var s = backend.settingsData;
        if (!s) return;
        editFolder = s.videoProjectsFolder || "";
        editFileName = s.fileName || "project.toml";
        editVideoPath = s.defaultVideoPath || "Export/Video";
        editThumbPath = s.defaultThumbPath || "Export/Thumb";
        editPreLink = s.defaultPreLink || "Saiba mais: ";
        editFoldersList = s.folders ? JSON.parse(JSON.stringify(s.folders)) : [];
    }

    Connections {
        target: backend
        function onSettingsChanged() {
            settingsRoot.syncFromBackend();
        }
    }

    Component.onCompleted: {
        syncFromBackend();
    }

    function doSave() {
        var ok = backend.saveSettings(
            editFolder,
            editFileName,
            editVideoPath,
            editThumbPath,
            editPreLink,
            editFoldersList
        );
        if (ok) {
            savedMsg.visible = true;
            saveTimer.restart();
        }
    }

    Timer {
        id: saveTimer
        interval: 3500
        onTriggered: savedMsg.visible = false
    }

    actions: [
        Kirigami.Action {
            text: "Save Settings"
            icon.name: "document-save"
            tooltip: "Save settings to settings.toml"
            displayHint: Kirigami.DisplayHint.AlwaysHide
            onTriggered: settingsRoot.doSave()
        }
    ]

    ColumnLayout {
        Layout.fillWidth: true
        Layout.maximumWidth: Kirigami.Units.gridUnit * 50
        Layout.alignment: Qt.AlignHCenter
        spacing: Kirigami.Units.largeSpacing

        // Notification
        Kirigami.InlineMessage {
            id: savedMsg
            Layout.fillWidth: true
            type: Kirigami.MessageType.Positive
            text: "Settings saved successfully to settings.toml!"
            visible: false
            showCloseButton: true
        }

        // --- SECTION 1: Projects Folder ---
        FormCard.FormHeader {
            title: "Projects Location"
        }

        FormCard.FormCard {
            Layout.fillWidth: true

            FormCard.FormTextFieldDelegate {
                id: folderField
                label: "Projects Directory"
                text: settingsRoot.editFolder
                placeholderText: "/home/user/Vídeos/VideosEvolução"
                onTextChanged: settingsRoot.editFolder = text
            }

            FormCard.FormButtonDelegate {
                text: "Browse Folder..."
                icon.name: "folder-open"
                onClicked: {
                    var picked = backend.chooseFolder(settingsRoot.editFolder);
                    if (picked && picked.length > 0) {
                        settingsRoot.editFolder = picked;
                    }
                }
            }

            FormCard.FormDelegateSeparator {}

            FormCard.FormTextFieldDelegate {
                id: fileField
                label: "Project File Name"
                text: settingsRoot.editFileName
                placeholderText: "project.toml"
                onTextChanged: settingsRoot.editFileName = text
            }
        }

        // --- SECTION 2: Defaults ---
        FormCard.FormHeader {
            title: "Default Paths & Description"
        }

        FormCard.FormCard {
            Layout.fillWidth: true

            FormCard.FormTextFieldDelegate {
                label: "Default Video Path"
                text: settingsRoot.editVideoPath
                placeholderText: "Export/Video"
                onTextChanged: settingsRoot.editVideoPath = text
            }

            FormCard.FormDelegateSeparator {}

            FormCard.FormTextFieldDelegate {
                label: "Default Thumbnail Path"
                text: settingsRoot.editThumbPath
                placeholderText: "Export/Thumb"
                onTextChanged: settingsRoot.editThumbPath = text
            }

            FormCard.FormDelegateSeparator {}

            FormCard.FormTextFieldDelegate {
                label: "Default Description Pre-Link"
                text: settingsRoot.editPreLink
                placeholderText: "Saiba mais: "
                onTextChanged: settingsRoot.editPreLink = text
            }
        }

        // --- SECTION 3: Template Folders ---
        FormCard.FormHeader {
            title: "New Project Template Folders"
        }

        FormCard.FormCard {
            Layout.fillWidth: true

            Item {
                implicitHeight: foldersLayout.implicitHeight + Kirigami.Units.largeSpacing * 2
                Layout.fillWidth: true

                ColumnLayout {
                    id: foldersLayout
                    anchors.fill: parent
                    anchors.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.smallSpacing

                    Controls.Label {
                        text: "Folders created inside each new video project:"
                        font: Kirigami.Theme.smallFont
                        color: Kirigami.Theme.disabledTextColor
                    }

                    // List of current template folders
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Kirigami.Units.smallSpacing

                        Repeater {
                            model: settingsRoot.editFoldersList

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: Kirigami.Units.smallSpacing

                                Kirigami.Icon {
                                    source: "folder"
                                    implicitWidth: 16
                                    implicitHeight: 16
                                    opacity: 0.7
                                }

                                Controls.Label {
                                    text: modelData
                                    Layout.fillWidth: true
                                    font.bold: true
                                }

                                Controls.ToolButton {
                                    icon.name: "list-remove"
                                    Controls.ToolTip.visible: hovered
                                    Controls.ToolTip.text: "Remove folder"
                                    onClicked: {
                                        var arr = settingsRoot.editFoldersList.slice();
                                        arr.splice(index, 1);
                                        settingsRoot.editFoldersList = arr;
                                    }
                                }
                            }
                        }
                    }

                    // Add folder input row
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.topMargin: Kirigami.Units.smallSpacing
                        spacing: Kirigami.Units.smallSpacing

                        Controls.TextField {
                            id: newFolderInput
                            Layout.fillWidth: true
                            placeholderText: "e.g. Export/Subtitles or Raw/Audio"
                            onAccepted: addFolderBtn.clicked()
                        }

                        Controls.Button {
                            id: addFolderBtn
                            icon.name: "list-add"
                            text: "Add Folder"
                            onClicked: {
                                var val = newFolderInput.text.trim();
                                if (val.length > 0) {
                                    var arr = settingsRoot.editFoldersList.slice();
                                    if (arr.indexOf(val) === -1) {
                                        arr.push(val);
                                        settingsRoot.editFoldersList = arr;
                                    }
                                    newFolderInput.text = "";
                                }
                            }
                        }
                    }

                    // Reset Defaults button
                    Controls.Button {
                        text: "Reset Folders to Defaults"
                        icon.name: "edit-undo"
                        onClicked: {
                            settingsRoot.editFoldersList = [
                                "Videos", "Images", "Audio", "Project",
                                "Export", "Export/Thumb", "Export/Video", "Images/Slides"
                            ];
                        }
                    }
                }
            }
        }

        // Bottom Save Action Bar
        RowLayout {
            Layout.fillWidth: true
            Layout.topMargin: Kirigami.Units.largeSpacing
            Layout.bottomMargin: Kirigami.Units.gridUnit * 2
            spacing: Kirigami.Units.largeSpacing

            Item { Layout.fillWidth: true }

            Controls.Button {
                text: "Cancel"
                icon.name: "dialog-cancel"
                onClicked: applicationWindow().pageStack.pop()
            }

            Controls.Button {
                text: "Save Settings"
                icon.name: "document-save"
                highlighted: true
                onClicked: settingsRoot.doSave()
            }
        }
    }
}
