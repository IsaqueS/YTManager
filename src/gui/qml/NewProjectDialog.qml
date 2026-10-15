import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.kirigami.dialogs as KirigamiDialogs

KirigamiDialogs.Dialog {
    id: dialogRoot

    title: "Create New Video Project"
    preferredWidth: Kirigami.Units.gridUnit * 26

    signal projectCreated(string projectId)

    function resetForm() {
        idField.text = "";
        titleField.text = "";
        linkField.text = "";
        errorMsg.visible = false;
        errorMsg.text = "";
    }

    onOpened: {
        resetForm();
        idField.forceActiveFocus();
    }

    ColumnLayout {
        spacing: Kirigami.Units.largeSpacing
        Layout.fillWidth: true

        Kirigami.InlineMessage {
            id: errorMsg
            Layout.fillWidth: true
            type: Kirigami.MessageType.Error
            visible: false
            showCloseButton: true
        }

        Controls.Label {
            text: "Creates a new project folder, folder structure, and project.toml metadata file."
            wrapMode: Text.Wrap
            font: Kirigami.Theme.smallFont
            color: Kirigami.Theme.disabledTextColor
            Layout.fillWidth: true
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing

            Controls.Label {
                text: "Project ID / Folder Name: *"
                font.bold: true
            }

            Controls.TextField {
                id: idField
                Layout.fillWidth: true
                placeholderText: "e.g. 8036 or MyNewVideo"
                onTextChanged: errorMsg.visible = false
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing

            Controls.Label {
                text: "Initial Video Title: (optional)"
            }

            Controls.TextField {
                id: titleField
                Layout.fillWidth: true
                placeholderText: "e.g. Casa 3 Quartos - Bairro Nobre"
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing

            Controls.Label {
                text: "Website Link: (optional)"
            }

            Controls.TextField {
                id: linkField
                Layout.fillWidth: true
                placeholderText: "https://example.com/property/8036"
            }
        }

        Item {
            height: Kirigami.Units.smallSpacing
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing

            Item { Layout.fillWidth: true }

            Controls.Button {
                text: "Cancel"
                icon.name: "dialog-cancel"
                onClicked: dialogRoot.close()
            }

            Controls.Button {
                text: "Create Project"
                icon.name: "list-add"
                highlighted: true
                enabled: idField.text.trim().length > 0
                onClicked: {
                    var pId = idField.text.trim();
                    if (pId.length === 0) {
                        errorMsg.text = "Please enter a valid Project ID.";
                        errorMsg.visible = true;
                        return;
                    }
                    var success = backend.createProject(pId, titleField.text.trim(), linkField.text.trim());
                    if (success) {
                        dialogRoot.close();
                        dialogRoot.projectCreated(pId);
                    } else {
                        errorMsg.text = "Failed to create project. It may already exist.";
                        errorMsg.visible = true;
                    }
                }
            }
        }
    }
}
