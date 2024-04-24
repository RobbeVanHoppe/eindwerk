import asyncio
import getpass
import json
import os
import subprocess
from typing import List, Optional, Union

import paramiko
import requests


class SetupReportPortal:
    """
    Represents a setup for interacting with ReportPortal.

    Methods:
        __init__: Initialize the setup with optional remote host IP.
        _create_client: Create an SSH client for the remote host.
        _close_client: Close the SSH client connection.
        _retrieve_api_key: Retrieve the API key for authentication.
        execute_ssh_command: Execute an SSH command on the remote host.
        copy_folder: Copy a folder to the remote host.
        copy_file: Copy a file to the remote host.
        create_api_call: Make an API call to the remote host.
        step_1_copy_required_files: Copy required files and SSH key.
        step_2_install_docker_compose: Install Docker Compose.
        step_3_pull_report_portal_image: Pull the ReportPortal Docker image.
        step_4_start_report_portal_stack: Start the ReportPortal stack.
        step_5_create_OBS_test_project: Create a test project.
        step_6_create_qcify_user: Create a user for QCify.
        step_7_assign_user_to_project: Assign a user to a project.
        main: Execute the setup steps in sequence.
    """

    
    def __init__(self, remote_host_ip: Optional[str] = None):
        self._ssh_client: Optional[paramiko.SSHClient] = None
        self._remote_host = '10.10.0.10' if remote_host_ip is None else remote_host_ip
        self._remote_user = 'qcify'
        self._remote_password = 'Qc1fyT3st'
        self.remote_home = f'/home/{self._remote_user}'
        self.host_home = f'{os.environ["HOME"]}'
        self.host_rsa_pub_key = f'{self.host_home}/.ssh/id_rsa.pub'
        self.host_rsa_priv_key = f'{self.host_home}/.ssh/id_rsa'
        self.host_reportportal_dir = f'{self.host_home}/qcify/test_dashboard/reportportal'

    def _create_client(self, user: Optional[str] = None, password: Optional[str] = None) -> None:
        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if user and password is not None:
            self._ssh_client.connect(hostname=self._remote_host, username=user, password=password)
        else:
            self._ssh_client.connect(hostname=self._remote_host, username=self._remote_user, key_filename=self.host_rsa_priv_key)

    def _close_client(self):
        self._ssh_client.close() # type: ignore

    async def _retrieve_api_key(self) -> str:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "password",
                "username": "superadmin",
                "password": "erebus"}
        auth = ("ui", "uiman")
        result = setup.create_api_call('POST', '/uat/sso/oauth/token', headers=headers, data=data, auth=auth)
        return result.json().get('access_token')

    def execute_ssh_command(self, command: str, user: Optional[str] = None, password: Optional[str] = None) -> str:
        self._create_client(user=user, password=password)
        full_cmd = command

        if command.startswith("sudo") and not self._remote_password:
            self._remote_password = getpass.getpass(prompt="Enter remote sudo password: ")
            # Add -S option to sudo command and pass the password through stdin
            full_cmd = f'echo "{self._remote_password}" | sudo -S {command}'

        stdin, stdout, stderr = self._ssh_client.exec_command(full_cmd) # type: ignore
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
        self.execute_ssh_command(
            f"mkdir -p {dst_folder}",
            user=self._remote_user,
            password=self._remote_password,
        )
        print(subprocess.run(['scp', '-r', src_folder, f'{self._remote_user}@{self._remote_host}:{dst_folder}']))

    def copy_file(self, src_file: str, dst_file: str):
        print(subprocess.run(['scp', '-r', src_file, f'{self._remote_user}@{self._remote_host}:{dst_file}']))

    def create_api_call(self, method: str, url: str, headers: dict[str, str], data: Union[str, dict[str, str]], auth: Optional[tuple[str, str]] = None) -> requests.Response:
        if method == 'POST':
            return requests.post(url=f'http://{self._remote_host}:8080{url}', headers=headers, data=data, auth=auth)
        if method == 'PUT':
            return requests.put(url=f'http://{self._remote_host}:8080{url}', headers=headers, data=data, auth=auth)
        return requests.Response()

    def step_1_copy_required_files(self):
        """
        Copy files and SSH key.
        """
        setup.copy_folder(setup.host_reportportal_dir, setup.remote_home)
        setup.copy_file(setup.host_rsa_pub_key, f'{setup.remote_home}/.ssh/authorized_keys')

    def step_2_install_docker_compose(self):
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

    def step_3_pull_report_portal_image(self):
        print(setup.execute_ssh_command(f'docker compose -f {setup.remote_home}/reportportal/provisioning/docker-compose.yml pull'))

    def step_4_start_report_portal_stack(self):
        print(setup.execute_ssh_command(f'docker compose -f {setup.remote_home}/reportportal/provisioning/docker-compose.yml up -d'))

    async def step_5_create_OBS_test_project(self):
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {await self._retrieve_api_key()}"}
        data = {
            "entryType": "INTERNAL",
            "projectName": "OBS_test"
        }
        result = setup.create_api_call('POST', '/api/v1/project', headers=headers, data=json.dumps(data))
        print(result.content)

    async def step_6_create_qcify_user(self):
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {await self._retrieve_api_key()}"}
        data = {"accountRole": "USER",
                "defaultProject": "OBS_test",
                "email": "rvanhoppe@qcify.com",
                "fullName": "qcify",
                "login": "qcify",
                "password": "qcify",
                "projectRole": "PROJECT_MANAGER"}

        result = setup.create_api_call('POST', '/api/users', headers=headers, data=json.dumps(data))

        print(result.content)

    async def main(self):
        self.step_1_copy_required_files()
        self.step_2_install_docker_compose()
        self.step_3_pull_report_portal_image()
        self.step_4_start_report_portal_stack()
        await self.step_5_create_OBS_test_project()
        await self.step_6_create_qcify_user()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    setup = SetupReportPortal()
    loop.run_until_complete(setup.main())
