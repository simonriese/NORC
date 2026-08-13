import os
import sys
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal


import paramiko
dev_mode = True
dev_file_list =[
    "acquisition/install.py",
    "acquisition/util/utils.py"
]


def get_repo_base() -> Path:
    cur_dir = Path(__file__).resolve().parent
    for path in list(cur_dir.parents):
        if (path/ ".git").is_dir():
            return path
    raise RuntimeError("[Error] Could not find the local git repository root.")


class SSHConnectionWorker(QThread):
    connection_success = pyqtSignal()
    connection_failed = pyqtSignal(str)
    update_progress = pyqtSignal(str)

    def __init__(self, host,port, username, password=None, key_path=None, passphrase=None):
        super().__init__()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_path = key_path
        self.passphrase = passphrase

        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def run(self):
        try:
            if self.key_path:
                self.ssh_client.connect(
                    self.host,
                    port=self.port,
                    username=self.username,
                    key_filename=self.key_path,
                    passphrase=self.passphrase,
                    timeout=5
                )
            else:
                self.ssh_client.connect(
                    self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=5
                )
            self.connection_success.emit()

        except paramiko.ssh_exception.AuthenticationException:
            self.connection_failed.emit("Authentication failed. Check your password, key, or passphrase.")
        except Exception as e:
            self.connection_failed.emit(f"Connection error: {str(e)}")

    def close(self):
        self.ssh_client.close()

    def run_cmd(self,command):
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        for line in stdout:
            print(line, end="")
            sys.stdout.flush()

        for line in stderr:
            print(line, end="", file=sys.stderr)
            sys.stderr.flush()

        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            print(f"\nProcess exited with error code: {exit_status}", file=sys.stderr)

    def run_setup(self,TARGET_DIR=str):
        REPO_URL ="https://github.com/simonriese/NORC.git"
        git_command = f"""
        if [ -d "{TARGET_DIR}/.git" ]; then
            echo "[Info] Repository exists. Updating..."
            git -C "{TARGET_DIR}" pull
        else
            echo "[Info] Repository not found. Cloning..."
            mkdir -p "$(dirname "{TARGET_DIR}")"
            git clone "{REPO_URL}" "{TARGET_DIR}"
        fi
        """
        self.run_cmd(git_command)

        if dev_file_list and dev_mode:
            print("[Info] Starting dev file transfers...")
            try:
                sftp = self.ssh_client.open_sftp()
                local_base = get_repo_base()
                for relative_path in dev_file_list:
                    local_path = (local_base / relative_path)
                    remote_path = f"{TARGET_DIR.rstrip('/')}/{relative_path}"
                    sftp.put(local_path, remote_path)
            except Exception as e:
                print(f"[Error]File transfer failed: {e}", file=sys.stderr)
            finally:
                if 'sftp' in locals():
                    sftp.close()
            print("[Info] Setup and transfers complete!")

    def run_installation(self,TARGET_DIR):
        command = f"""
        "python3 {TARGET_DIR}/acquisition/install.py -f -q]
        """
        self.run_cmd(command)