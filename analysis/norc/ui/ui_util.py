"""
User interface component for the ui_util.py part of the NORC analysis tool.

Copyright (c) 2026 TU Darmstadt, Germany
Version: v0.2
Date: 2025-08-08

Licensed under the BSD 3-Clause License.
For more information, see the LICENSE file in the project root:
https://github.com/tuda-parallel/NORC/blob/main/LICENSE
"""

import matplotlib
from PySide6.QtWidgets import QSizePolicy, QWidget


def score_color(score):
    return matplotlib.colormaps["turbo"](0.5 + (1.0 - score) * 0.5)


def add_v_spacer(target):
    spacer = QWidget(target)
    spacer.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
    target.layout().addWidget(spacer)


def clear_widget(w):
    if w is None or w.layout() is None:
        return
    layout = w.layout()
    for i in range(layout.count()):
        if layout.itemAt(i) is None:
            continue
        layout.itemAt(i).widget().setParent(None)
