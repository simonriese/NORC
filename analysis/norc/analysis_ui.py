"""
Entry point for the NORC analysis graphical user interface.

Copyright (c) 2026 TU Darmstadt, Germany
Version: v0.2
Date: 2025-08-08

Licensed under the BSD 3-Clause License.
For more information, see the LICENSE file in the project root:
https://github.com/tuda-parallel/NORC/blob/main/LICENSE
"""

import sys

from PySide6.QtGui import QColor
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication

from norc.classes.application_state import ApplicationState
from norc.ui.mainwindow import main_window


def main() -> None:
    loader = QUiLoader()
    app = QApplication(sys.argv)
    # app.setStyle("Windows")
    app.setPalette(QColor(255, 255, 255, 255))
    appstate = ApplicationState(loader)

    if len(sys.argv) > 1:
        appstate.plt_mgr.open_experiment(sys.argv[1])

    main_window(appstate)

    app.exec()


if __name__ == "__main__":
    main()

