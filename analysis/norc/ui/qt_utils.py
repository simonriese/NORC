"""
User interface utilities for the NORC analysis tool.

Copyright (c) 2026 TU Darmstadt, Germany
Version: v0.2
Date: 2025-08-08

Licensed under the BSD 3-Clause License.
For more information, see the LICENSE file in the project root:
https://github.com/tuda-parallel/NORC/blob/main/LICENSE
"""

from PySide6.QtWidgets import QComboBox, QTableWidget


def update_choices(cb: QComboBox, choices):
    block = cb.blockSignals(True)
    prev_choice = cb.currentText()

    cb.clear()
    cb.addItems(sorted(choices))

    idx = cb.findText(prev_choice)
    if idx >= 0:
        cb.setCurrentIndex(idx)

    cb.blockSignals(block)


def table_dimensions(table: QTableWidget, min_it_w=0, min_it_h=0):
    hhead = table.horizontalHeader()
    vhead = table.verticalHeader()
    w = vhead.width()
    h = hhead.height()
    for i in range(hhead.count()):
        w += max(hhead.sectionSize(i), min_it_w)

    for i in range(vhead.count()):
        h += max(vhead.sectionSize(i), min_it_h)

    return w, h
