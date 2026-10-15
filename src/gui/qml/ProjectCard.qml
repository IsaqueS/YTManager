import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Kirigami.AbstractCard {
    id: cardRoot

    property var projectData: ({})
    signal openEditorRequested(string projectId)

    Layout.fillWidth: true
    showClickFeedback: true

    onClicked: {
        if (projectData && projectData.id) {
            cardRoot.openEditorRequested(projectData.id)
        }
    }

    // 16:9 Aspect Ratio Preview Header
    header: Rectangle {
        id: bannerBox
        Layout.fillWidth: true
        implicitHeight: Math.round((width > 0 ? width : (cardRoot.width > 0 ? cardRoot.width : 320)) * 9.0 / 16.0)
        height: implicitHeight
        color: Kirigami.Theme.alternateBackgroundColor
        clip: true

        // Thumbnail Image in 16:9 aspect ratio
        Image {
            id: thumbImg
            anchors.fill: parent
            source: (projectData && projectData.thumbnailUrl) ? projectData.thumbnailUrl : ""
            sourceSize.width: 640
            sourceSize.height: 360
            fillMode: Image.PreserveAspectCrop
            visible: status === Image.Ready
            asynchronous: true
        }

        // Fallback when no thumbnail image exists
        Item {
            anchors.fill: parent
            visible: thumbImg.status !== Image.Ready

            Rectangle {
                anchors.fill: parent
                color: Kirigami.Theme.alternateBackgroundColor

                Kirigami.Icon {
                    anchors.centerIn: parent
                    width: 48
                    height: 48
                    source: "video-x-generic"
                    opacity: 0.5
                }
            }
        }

        // Top Gradient for badge readability
        Rectangle {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 44
            gradient: Gradient {
                GradientStop { position: 0.0; color: Qt.rgba(0, 0, 0, 0.45) }
                GradientStop { position: 1.0; color: "transparent" }
            }
        }

        // Top Row Badges
        RowLayout {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: Kirigami.Units.smallSpacing
            spacing: Kirigami.Units.smallSpacing

            // Project ID Chip
            Rectangle {
                implicitWidth: idText.implicitWidth + Kirigami.Units.smallSpacing * 2
                implicitHeight: idText.implicitHeight + Kirigami.Units.smallSpacing
                radius: 4
                color: Qt.rgba(0, 0, 0, 0.7)

                Controls.Label {
                    id: idText
                    anchors.centerIn: parent
                    text: projectData ? projectData.id : ""
                    font.bold: true
                    font.pointSize: Kirigami.Theme.smallFont.pointSize
                    color: "white"
                }
            }

            Item { Layout.fillWidth: true }

            // Export Video Indicator Badge
            Rectangle {
                visible: projectData && projectData.hasVideoExport
                implicitWidth: exportRow.implicitWidth + Kirigami.Units.smallSpacing * 2
                implicitHeight: idText.implicitHeight + Kirigami.Units.smallSpacing
                radius: 4
                color: Qt.rgba(0.15, 0.45, 0.85, 0.85)

                RowLayout {
                    id: exportRow
                    anchors.centerIn: parent
                    spacing: 3
                    Kirigami.Icon {
                        source: "media-playback-start"
                        implicitWidth: 11
                        implicitHeight: 11
                        color: "white"
                    }
                    Controls.Label {
                        text: "Exported"
                        font.pointSize: Kirigami.Theme.smallFont.pointSize - 1
                        color: "white"
                    }
                }
            }

            // Upload Status Badge
            Rectangle {
                id: statusBadge
                readonly property bool isUploaded: Boolean(cardRoot.projectData && cardRoot.projectData.videoUploaded)

                implicitWidth: statusRow.implicitWidth + Kirigami.Units.smallSpacing * 2
                implicitHeight: idText.implicitHeight + Kirigami.Units.smallSpacing
                radius: 4
                color: statusBadge.isUploaded ? Qt.rgba(0.12, 0.6, 0.25, 0.9) : Qt.rgba(0.85, 0.45, 0.05, 0.9)

                RowLayout {
                    id: statusRow
                    anchors.centerIn: parent
                    spacing: 3

                    Kirigami.Icon {
                        source: statusBadge.isUploaded ? "checkmark" : "chronometer"
                        implicitWidth: 12
                        implicitHeight: 12
                        color: "white"
                    }

                    Controls.Label {
                        text: statusBadge.isUploaded ? "Uploaded" : "In Progress"
                        font.bold: true
                        font.pointSize: Kirigami.Theme.smallFont.pointSize
                        color: "white"
                    }
                }
            }
        }
    }

    contentItem: ColumnLayout {
        spacing: Kirigami.Units.smallSpacing

        // Video Title
        Kirigami.Heading {
            text: (projectData && projectData.title && projectData.title.trim().length > 0)
                  ? projectData.title
                  : (projectData ? "Project " + projectData.id : "")
            level: 4
            wrapMode: Text.Wrap
            maximumLineCount: 2
            elide: Text.ElideRight
            Layout.fillWidth: true
        }

        // Subtitle / Date info
        RowLayout {
            spacing: Kirigami.Units.smallSpacing
            Layout.fillWidth: true

            Kirigami.Icon {
                source: "view-calendar"
                implicitWidth: 13
                implicitHeight: 13
                opacity: 0.6
            }

            Controls.Label {
                text: projectData ? "Updated: " + projectData.formattedDate : ""
                font: Kirigami.Theme.smallFont
                color: Kirigami.Theme.disabledTextColor
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
        }

        // Excerpt or Website
        Controls.Label {
            text: {
                if (!projectData) return ""
                if (projectData.webSite && projectData.webSite.length > 0) return projectData.webSite
                if (projectData.description && projectData.description.length > 0) return projectData.description
                return "No description set"
            }
            font: Kirigami.Theme.smallFont
            opacity: 0.75
            elide: Text.ElideRight
            maximumLineCount: 1
            Layout.fillWidth: true
        }
    }

    footer: Kirigami.ActionToolBar {
        alignment: Qt.AlignRight

        actions: [
            Kirigami.Action {
                text: "Edit"
                icon.name: "document-edit"
                tooltip: "Edit project.toml"
                onTriggered: {
                    if (projectData && projectData.id) {
                        cardRoot.openEditorRequested(projectData.id)
                    }
                }
            },
            Kirigami.Action {
                text: "Folder"
                icon.name: "folder-open"
                tooltip: "Open project folder in Dolphin"
                onTriggered: {
                    if (projectData && projectData.id) {
                        backend.openProjectFolder(projectData.id)
                    }
                }
            },
            Kirigami.Action {
                text: (projectData && projectData.videoUploaded) ? "Mark In Progress" : "Mark Uploaded"
                icon.name: (projectData && projectData.videoUploaded) ? "edit-undo" : "task-complete"
                tooltip: (projectData && projectData.videoUploaded) ? "Mark video as in progress" : "Mark video as uploaded"
                onTriggered: {
                    if (projectData && projectData.id) {
                        backend.setUploaded(projectData.id, !projectData.videoUploaded)
                    }
                }
            }
        ]
    }
}
