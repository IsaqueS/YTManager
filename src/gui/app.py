import os
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

from .backend import ProjectBackend


def run_gui() -> int:
    # Set application metadata
    app = QApplication(sys.argv)
    app.setApplicationName("YTManager")
    app.setApplicationDisplayName("YTManager - Video Project Manager")
    app.setOrganizationName("IsaqueS")
    app.setDesktopFileName("ytmanager")

    # Ensure system icon theme works well
    if not QIcon.themeName():
        QIcon.setThemeName("breeze")

    engine = QQmlApplicationEngine()

    # Add standard Kirigami and Qt6 QML paths
    standard_paths = [
        "/usr/lib64/qt6/qml",
        "/usr/share/qt6/qml",
        "/usr/lib/qt6/qml",
    ]
    for p in standard_paths:
        if os.path.exists(p) and p not in engine.importPathList():
            engine.addImportPath(p)

    qml_dir = Path(__file__).parent / "qml"
    engine.addImportPath(str(qml_dir))

    # Instantiate backend
    backend = ProjectBackend()
    engine.rootContext().setContextProperty("backend", backend)

    main_qml_path = qml_dir / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(main_qml_path)))

    if not engine.rootObjects():
        print("Error: Could not load Main.qml", file=sys.stderr)
        return 1

    return app.exec()


if __name__ == "__main__":
    sys.exit(run_gui())
