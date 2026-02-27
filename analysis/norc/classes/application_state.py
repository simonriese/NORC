"""
Global state management for the analysis application.

Copyright (c) 2026 TU Darmstadt, Germany
Version: v0.2
Date: 2025-08-08

Licensed under the BSD 3-Clause License.
For more information, see the LICENSE file in the project root:
https://github.com/tuda-parallel/NORC/blob/main/LICENSE
"""

import os

from norc.core.plotmanager import PlotManager


class ApplicationState:
    def __init__(self, loader):
        script_location = os.path.dirname(os.path.abspath(__file__))
        self.ui_dir = os.path.join(script_location, "..", "ui")
        self.ui_dir = os.path.abspath(self.ui_dir)

        self.loader = loader
        self.plt_mgr = PlotManager()

    def load_ui(self, fname):
        """Load a .ui file from the UI directory."""
        return self.loader.load(os.path.join(self.ui_dir, fname), None)
