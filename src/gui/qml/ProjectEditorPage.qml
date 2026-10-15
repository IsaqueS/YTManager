import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.kirigamiaddons.formcard as FormCard

Kirigami.ScrollablePage {
    id: editorRoot

    property var project: (backend && backend.activeProject) ? backend.activeProject : ({})

    title: (project && project.id) ? ("Edit Project: " + project.id) : "Edit Project"

    // Form model properties bound to active project
    property string editTitle: project ? (project.title || "") : ""
    property bool editUploaded: project ? (project.videoUploaded || false) : false
    property string editPreDesc: project ? (project.preDescription || "") : ""
    property string editDesc: project ? (project.description || "") : ""
    property string editPosDesc: project ? (project.posDescription || "") : ""
    property string editPreWebSite: project ? (project.preWebSite || "") : ""
    property string editWebSite: project ? (project.webSite || "") : ""
    property string editVideoPath: project ? (project.videoPath || "Export/Video") : "Export/Video"
    property string editThumbPath: project ? (project.thumbPath || "Export/Thumb") : "Export/Thumb"

    function syncFromProject() {
        if (!backend || !backend.activeProject) return;
        var p = backend.activeProject;
        editTitle = p.title || "";
        editUploaded = p.videoUploaded || false;
        editPreDesc = p.preDescription || "";
        editDesc = p.description || "";
        editPosDesc = p.posDescription || "";
        editPreWebSite = p.preWebSite || "";
        editWebSite = p.webSite || "";
        editVideoPath = p.videoPath || "Export/Video";
        editThumbPath = p.thumbPath || "Export/Thumb";
    }

    Connections {
        target: backend
        function onActiveProjectChanged() {
            editorRoot.syncFromProject();
        }
    }

    Component.onCompleted: {
        syncFromProject();
    }

    function doSave() {
        if (!project || !project.id) return;
        var ok = backend.saveProject(
            project.id,
            editTitle,
            editDesc,
            editPreDesc,
            editPosDesc,
            editPreWebSite,
            editWebSite,
            editUploaded,
            editVideoPath,
            editThumbPath
        );
        if (ok) {
            saveMsg.visible = true;
            saveTimer.restart();
        }
    }

    Timer {
        id: saveTimer
        interval: 3500
        onTriggered: saveMsg.visible = false
    }

    actions: [
        Kirigami.Action {
            text: "Save"
            icon.name: "document-save"
            tooltip: "Save changes to project.toml"
            displayHint: Kirigami.DisplayHint.AlwaysHide
            onTriggered: editorRoot.doSave()
        },
        Kirigami.Action {
            text: "Open Folder"
            icon.name: "folder-open"
            tooltip: "Open project folder in Dolphin"
            onTriggered: {
                if (project && project.id) {
                    backend.openProjectFolder(project.id);
                }
            }
        },
        Kirigami.Action {
            text: "Copy YouTube Info"
            icon.name: "edit-copy"
            tooltip: "Copy formatted YouTube description to clipboard"
            onTriggered: {
                if (project) {
                    var formatted = "";
                    if (editTitle.trim().length > 0) formatted += editTitle.trim() + "\n\n";
                    if (editPreDesc.trim().length > 0) formatted += editPreDesc.trim() + "\n\n";
                    if (editDesc.trim().length > 0) formatted += editDesc.trim() + "\n\n";
                    if (editPosDesc.trim().length > 0) formatted += editPosDesc.trim() + "\n\n";
                    if (editWebSite.trim().length > 0) {
                        var link = (editPreWebSite ? editPreWebSite : "") + editWebSite.trim();
                        formatted += link;
                    }
                    backend.copyToClipboard(formatted.trim());
                }
            }
        }
    ]

    ColumnLayout {
        id: mainColumn
        Layout.fillWidth: true
        Layout.maximumWidth: Kirigami.Units.gridUnit * 55
        Layout.alignment: Qt.AlignHCenter
        spacing: Kirigami.Units.largeSpacing

        // Notification Inline Message
        Kirigami.InlineMessage {
            id: saveMsg
            Layout.fillWidth: true
            type: Kirigami.MessageType.Positive
            text: "Project saved successfully to project.toml!"
            visible: false
            showCloseButton: true
        }

        // --- 16:9 Thumbnail Preview ---
        FormCard.FormHeader {
            title: "Thumbnail Preview (16:9)"
        }

        FormCard.FormCard {
            Layout.fillWidth: true

            Item {
                Layout.fillWidth: true
                implicitHeight: Math.round(width * 9.0 / 16.0)
                clip: true

                Rectangle {
                    anchors.fill: parent
                    color: Kirigami.Theme.alternateBackgroundColor
                    radius: 4

                    Image {
                        id: editorThumbImg
                        anchors.fill: parent
                        source: (project && project.thumbnailUrl) ? project.thumbnailUrl : ""
                        sourceSize.width: 1280
                        sourceSize.height: 720
                        fillMode: Image.PreserveAspectCrop
                        visible: status === Image.Ready
                        asynchronous: true
                    }

                    Item {
                        anchors.fill: parent
                        visible: editorThumbImg.status !== Image.Ready

                        Kirigami.Icon {
                            anchors.centerIn: parent
                            width: 64
                            height: 64
                            source: "video-x-generic"
                            opacity: 0.4
                        }
                    }
                }
            }
        }

        // --- SECTION 1: Status & Project Overview ---
        FormCard.FormHeader {
            title: "Project Status & Identity"
        }

        FormCard.FormCard {
            Layout.fillWidth: true

            FormCard.FormTextDelegate {
                text: "Project ID / Folder"
                description: project ? project.id : ""
            }

            FormCard.FormDelegateSeparator {}

            FormCard.FormSwitchDelegate {
                id: uploadSwitch
                text: "Video Uploaded to YouTube"
                description: checked ? "Video has been uploaded and published" : "Video is still in progress / pending upload"
                checked: editorRoot.editUploaded
                onCheckedChanged: editorRoot.editUploaded = checked
            }

            FormCard.FormDelegateSeparator {}

            FormCard.FormTextDelegate {
                text: "Date Created"
                description: (project && project.dateOfCreation) ? project.dateOfCreation : "Unknown"
            }

            FormCard.FormDelegateSeparator {}

            FormCard.FormTextDelegate {
                text: "Last Update"
                description: (project && project.lastUpdate) ? project.lastUpdate : "Unknown"
            }
        }

        // --- SECTION 2: Video Metadata ---
        FormCard.FormHeader {
            title: "Video Metadata"
        }

        FormCard.FormCard {
            Layout.fillWidth: true

            FormCard.FormTextFieldDelegate {
                id: titleInput
                label: "Video Title"
                text: editorRoot.editTitle
                maximumLength: 100
                placeholderText: "YouTube video title (max 100 chars)"
                onTextChanged: editorRoot.editTitle = text
            }

            FormCard.FormDelegateSeparator {}

            FormCard.FormTextFieldDelegate {
                id: preDescInput
                label: "Pre-Description (optional)"
                text: editorRoot.editPreDesc
                maximumLength: 45
                placeholderText: "Text placed before main description (max 45 chars)"
                onTextChanged: editorRoot.editPreDesc = text
            }

            FormCard.FormDelegateSeparator {}

            FormCard.FormTextAreaDelegate {
                id: descInput
                label: "Main Description"
                text: editorRoot.editDesc
                maximumLength: 4900
                placeholderText: "Write the full video description here (max 4900 chars)"
                onTextChanged: editorRoot.editDesc = text
            }

            FormCard.FormDelegateSeparator {}

            FormCard.FormTextFieldDelegate {
                id: posDescInput
                label: "Post-Description (optional)"
                text: editorRoot.editPosDesc
                maximumLength: 45
                placeholderText: "Text placed after main description (max 45 chars)"
                onTextChanged: editorRoot.editPosDesc = text
            }
        }

        // --- SECTION 3: Website & Links ---
        FormCard.FormHeader {
            title: "Website & Link"
        }

        FormCard.FormCard {
            Layout.fillWidth: true

            FormCard.FormTextFieldDelegate {
                id: preWebInput
                label: "Link Prefix"
                text: editorRoot.editPreWebSite
                placeholderText: "e.g. 'Saiba mais: '"
                onTextChanged: editorRoot.editPreWebSite = text
            }

            FormCard.FormDelegateSeparator {}

            FormCard.FormTextFieldDelegate {
                id: webInput
                label: "Website URL"
                text: editorRoot.editWebSite
                placeholderText: "https://example.com/item"
                onTextChanged: editorRoot.editWebSite = text
            }
        }

        // --- SECTION 4: Paths & Folders ---
        FormCard.FormHeader {
            title: "Paths & Organization"
        }

        FormCard.FormCard {
            Layout.fillWidth: true

            FormCard.FormTextFieldDelegate {
                id: videoPathInput
                label: "Video Export Path"
                text: editorRoot.editVideoPath
                placeholderText: "e.g. Export/Video"
                onTextChanged: editorRoot.editVideoPath = text
            }

            FormCard.FormButtonDelegate {
                text: "Open Video Export Folder"
                icon.name: "folder-videos"
                onClicked: {
                    if (project && project.id) backend.openVideoFolder(project.id);
                }
            }

            FormCard.FormDelegateSeparator {}

            FormCard.FormTextFieldDelegate {
                id: thumbPathInput
                label: "Thumbnail Path"
                text: editorRoot.editThumbPath
                placeholderText: "e.g. Export/Thumb"
                onTextChanged: editorRoot.editThumbPath = text
            }

            FormCard.FormButtonDelegate {
                text: "Open Thumbnail Folder"
                icon.name: "folder-pictures"
                onClicked: {
                    if (project && project.id) backend.openThumbFolder(project.id);
                }
            }
        }

        // --- SECTION 5: YouTube Copy Preview ---
        FormCard.FormHeader {
            title: "YouTube Description Preview"
        }

        FormCard.FormCard {
            Layout.fillWidth: true

            Item {
                implicitHeight: previewContent.implicitHeight + Kirigami.Units.largeSpacing * 2
                Layout.fillWidth: true

                ColumnLayout {
                    id: previewContent
                    anchors.fill: parent
                    anchors.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.smallSpacing

                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: previewText.implicitHeight + Kirigami.Units.largeSpacing * 2
                        radius: 6
                        color: Kirigami.Theme.alternateBackgroundColor
                        border.color: Kirigami.ColorUtils.linearInterpolation(Kirigami.Theme.backgroundColor, Kirigami.Theme.textColor, 0.2)
                        border.width: 1

                        Controls.TextArea {
                            id: previewText
                            anchors.fill: parent
                            anchors.margins: Kirigami.Units.smallSpacing
                            readOnly: true
                            wrapMode: TextEdit.Wrap
                            font: Kirigami.Theme.smallFont
                            text: {
                                var out = "";
                                if (editorRoot.editTitle.trim().length > 0) out += editorRoot.editTitle.trim() + "\n\n";
                                if (editorRoot.editPreDesc.trim().length > 0) out += editorRoot.editPreDesc.trim() + "\n\n";
                                if (editorRoot.editDesc.trim().length > 0) out += editorRoot.editDesc.trim() + "\n\n";
                                if (editorRoot.editPosDesc.trim().length > 0) out += editorRoot.editPosDesc.trim() + "\n\n";
                                if (editorRoot.editWebSite.trim().length > 0) {
                                    out += (editorRoot.editPreWebSite ? editorRoot.editPreWebSite : "") + editorRoot.editWebSite.trim();
                                }
                                return out.trim();
                            }
                        }
                    }

                    Controls.Button {
                        Layout.alignment: Qt.AlignRight
                        icon.name: "edit-copy"
                        text: "Copy Preview to Clipboard"
                        onClicked: {
                            backend.copyToClipboard(previewText.text);
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
                text: "Save project.toml"
                icon.name: "document-save"
                highlighted: true
                onClicked: editorRoot.doSave()
            }
        }
    }
}
