# This file is part of the NORC software
#
# Copyright (c) 2024-2025, Technical University of Darmstadt, Germany
#
# This software may be modified and distributed under the terms of a BSD-style license.
# See the LICENSE file in the base directory for details.

from PySide6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QFileDialog
from PySide6.QtCore import QProcess

import subprocess
import os
import threading
from norc.ui.ssh_util import SSHConnectionWorker
from norc.ui.ssh_util import get_repo_base

from mpl_toolkits.axisartist import floating_axes


class acquisition_tab(QWidget):
    def __init__(self, appstate):
        super().__init__()
        self.appstate = appstate

        self.setLayout(QVBoxLayout())
        self.ui = appstate.load_ui("acquisition_tab.ui")
        self.layout().addWidget(self.ui)

        # Action Buttons
        self.ui.run_setup_button.clicked.connect(self.setup)
        self.ui.run_acquisition_button.clicked.connect(self.acquisiton)
        # Connection enable toggle
        self.ui.connectionOptions.currentIndexChanged.connect(self.toggle_fields)
        self.toggle_fields()
        # SSH
        self.ui.sshPathButton.clicked.connect(self.open_file_browser)
        self.ui.connectButton.clicked.connect(self.on_connect_button_clicked)
        self.ssh_worker = None
        self.successfulConnection = False
        # Subprocess for Installion and Aquasition
        self.process = QProcess()
        self.process.setStandardOutputFile("app_output.log")
        self.process.setStandardErrorFile("app_output.log")

    def closeEvent(self, event):
        if self.ssh_worker:
            try:
                self.ssh_worker.close()
                print("SSH Connection closed on exit.")
            except Exception as e:
                print(f"Error closing SSH connection: {e}")
        if self.process.state() == QProcess.ProcessState.Running:
            print("Terminating background subprocess...")
            self.process.terminate()
            if not self.process.waitForFinished(2000):
                self.process.kill()
        event.accept()

    def open_file_browser(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if file_path:
            self.ui.keyPathField.setText(file_path)

    def is_localhost(self):
        return self.ui.connectionOptions.currentText() == "localhost"

    def get_destination(self) -> str:
        destination = self.ui.destinationPathField.text()
        if not destination:
            destination = "NORC"
        return destination

    def setup(self):
        #Run Remote Code download
        if not self.is_localhost() and self.ssh_worker and self.successfulConnection:
            destination = self.get_destination()
            self.ssh_worker.run_setup(destination)
        elif not self.is_localhost():
            print("[Error] Invalid SSH Session")
            return

        #Run Install.py
        if self.is_localhost():
            if self.process.state() == QProcess.ProcessState.NotRunning:
                self.process.start("python3",[str(get_repo_base()/"acquisition"/"install.py"),"-f", "-q"])
            else :
                print("[Error] Process is all ready running.")
                return
        elif self.ssh_worker and self.successfulConnection :
            destination = self.get_destination()
            self.ssh_worker.run_installation(destination)


    def acquisiton(self):
        print("acquisiton test beep boop")




    def on_connect_button_clicked(self):
        self.ui.connectButton.setEnabled(False)
        self.ui.connectButton.setText("Connecting...")

        host = self.ui.ipField.text()
        port = int(self.ui.portField.text())
        username = self.ui.userNameField.text()
        password = None
        key_path = None
        passphrase = None

        auth_method = self.ui.authOptions.currentText()
        if auth_method == "Password":
            password = self.ui.passwordField.text()
        elif auth_method == "SSH Key":
            key_path = self.ui.keyPathField.text()
            passphrase = self.ui.passphraseField.text()
            if not passphrase:
                passphrase = None

        self.ssh_worker = SSHConnectionWorker(
            host,
            port,
            username,
            password=password,
            key_path=key_path,
            passphrase=passphrase
        )
        def connection_success():
            self.ui.connectButton.setText("Connected")
            self.successfulConnection = True
        def connection_failed(str):
            self.ui.connectButton.setEnabled(True)
            self.successfulConnection = False
            self.ui.connectButton.setText("Connect to remote device")
            print(str)
        self.ssh_worker.connection_success.connect(connection_success)
        self.ssh_worker.connection_failed.connect(connection_failed)
        self.ssh_worker.start()

    def toggle_fields(self):
        should_enable = not self.is_localhost()

        target_widgets = [
            self.ui.ipLabel,
            self.ui.ipField,
            self.ui.portLabel,
            self.ui.portField,
            self.ui.userNameLabel,
            self.ui.userNameField,
            self.ui.authOptions,
            self.ui.passwordPage,
            self.ui.keyPage,
            self.ui.connectButton
        ]
        for widget in target_widgets:
            widget.setEnabled(should_enable)
