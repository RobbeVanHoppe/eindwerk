import getpass
import os
import subprocess
from typing import List

import paramiko


class SetupReportPortal:
    def __init__(self, remote_host_ip: str = None):
        self._ssh_client = None
        self._remote_host = '10.10.0.8' if remote_host_ip is None else remote_host_ip
        self._remote_user = 'qcify'
        self._remote_password = 'Qc1fyT3st'
        self.remote_home = f'/home/{self._remote_user}'
        self.host_home = f'{os.environ["HOME"]}'
        self.host_rsa_pub_key = f'{self.host_home}/.ssh/id_rsa.pub'
        self.host_rsa_priv_key = f'{self.host_home}/.ssh/id_rsa'
        self.host_reportportal_dir = f'{self.host_home}/qcify/test_dashboard/reportportal'

    def _create_client(self, user: str = None, password: str = None) -> None:
        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if user and password is not None:
            self._ssh_client.connect(hostname=self._remote_host, username=user, password=password)
        else:
            self._ssh_client.connect(hostname=self._remote_host, username=self._remote_user, key_filename=self.host_rsa_priv_key)

    def _close_client(self):
        self._ssh_client.close()

    def execute_ssh_command(self, command: str, user: str = None, password: str = None) -> str:
        self._create_client(user=user, password=password)
        full_cmd = command

        if command.startswith("sudo"):
            # Prompt for password securely
            # sudo_password = getpass.getpass(prompt="Enter sudo password: ")
            sudo_password = self._remote_password
            # Add -S option to sudo command and pass the password through stdin
            full_cmd = f'echo "{sudo_password}" | sudo -S {command}'

        stdin, stdout, stderr = self._ssh_client.exec_command(full_cmd)
        exit_status: int = stdout.channel.recv_exit_status()
        output: str = stdout.read().decode('utf-8')
        error: str = stderr.read().decode('utf-8')
        self._close_client()

        newline = '\n'
        return (f'Command: {command or newline}\n'
                f'Exitcode: {exit_status}\n'
                f'Output: {output or newline}'
                f'Error: {error or newline}\n')

    def copy_folder(self, src_folder: str, dst_folder: str):
        self.execute_ssh_command("mkdir -p " + dst_folder, user=self._remote_user, password=self._remote_password)
        print(subprocess.run(['scp', '-r', src_folder, f'{self._remote_user}@{self._remote_host}:{dst_folder}']))

    def copy_file(self, src_file: str, dst_file: str):
        print(subprocess.run(['scp', '-r', src_file, f'{self._remote_user}@{self._remote_host}:{dst_file}']))



if __name__ == '__main__':
    setup = SetupReportPortal()


    def step_1_copy_required_files():
        """
        Copy files and SSH key.
        """
        setup.copy_folder(setup.host_reportportal_dir, setup.remote_home)
        setup.copy_file(setup.host_rsa_pub_key, f'{setup.remote_home}/.ssh/authorized_keys')


    def step_2_install_docker_compose():
        """
        First log in as root user and install docker compose
        """
        apt_repo_install_commands: List[str] = [
            "sudo apt-get update",
            "sudo apt-get install -y ca-certificates curl",
            "sudo install -m 0755 -d /etc/apt/keyrings",
            "sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc",
            "sudo chmod a+r /etc/apt/keyrings/docker.asc",
            "sudo sh -c 'echo \"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable\" > /etc/apt/sources.list.d/docker.list'",
            "sudo apt-get update",
            "sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin"
        ]
        for command in apt_repo_install_commands:
            print(setup.execute_ssh_command(command))

        post_install_command = "sudo usermod -aG docker $USER"
        print(setup.execute_ssh_command(post_install_command))

    def step_3_pull_report_portal_image():
        print(setup.execute_ssh_command(f'docker compose -f {setup.remote_home}/reportportal/provisioning/docker-compose.yml pull'))


    def step_4_start_report_portal_stack():
        print(setup.execute_ssh_command(f'docker compose -f {setup.remote_home}/reportportal/provisioning/docker-compose.yml up -d'))


    step_1_copy_required_files()
    step_2_install_docker_compose()
    step_3_pull_report_portal_image()
    step_4_start_report_portal_stack()
