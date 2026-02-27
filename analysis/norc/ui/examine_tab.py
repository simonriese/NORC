"""
User interface component for the examine_tab.py part of the NORC analysis tool.

Copyright (c) 2026 TU Darmstadt, Germany
Version: v0.2
Date: 2025-08-08

Licensed under the BSD 3-Clause License.
For more information, see the LICENSE file in the project root:
https://github.com/tuda-parallel/NORC/blob/main/LICENSE
"""

from PySide6.QtGui import Qt
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from norc.ui.chart import chart


class examine_tab(QWidget):
    def __init__(self, appstate):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.appstate = appstate
        self.ui = appstate.load_ui("examine_tab.ui")
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)

        self.chart_splitter = QSplitter(orientation=Qt.Vertical)
        self.ui.sa_charts.setWidget(self.chart_splitter)

        self.ui.pb_addchart.clicked.connect(self.add_chart)

    def add_chart(self):
        self.chart_splitter.addWidget(chart(self.appstate))
