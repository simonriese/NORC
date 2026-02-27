"""
Implementation of the ratings and rankings tab in the GUI.

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
from norc.ui.dimension_picker import dimension_picker
from norc.ui.score_table import score_table


class ratings_tab(QWidget):
    def __init__(self, appstate):
        super().__init__()
        self.appstate = appstate
        self.setLayout(QVBoxLayout())
        # self.ui = appstate.load_ui("ratings_tab.ui")

        vsplit = QSplitter(orientation=Qt.Vertical)
        table_hsplit = QSplitter(orientation=Qt.Horizontal)
        self.layout().addWidget(vsplit)

        # self.layout().addWidget(self.ui)

        table = score_table(self, appstate.plt_mgr)
        dimpik = dimension_picker(appstate, "System", "Benchmark", "Noise", "Counter")
        chrt = chart(appstate)

        table.info_selected.connect(chrt.controls.set_measurement_info)
        dimpik.dimensions_changed.connect(table.set_dimensions)

        table_hsplit.addWidget(table)
        table_hsplit.addWidget(dimpik)
        vsplit.addWidget(table_hsplit)
        vsplit.addWidget(chrt)
