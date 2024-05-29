import asyncio
import getpass
import json
import os
import subprocess
from asyncio import sleep
import sys
from typing import List, Optional, Union

import paramiko
import requests


async def _retrieve_api_key() -> str:
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "password",
            "username": "superadmin",
            "password": "erebus"}
    auth = ("ui", "uiman")
    result = setup.create_api_call('POST', '/uat/sso/oauth/token', headers=headers, data=data, auth=auth)
    return result.json().get('access_token')


class SetupReportPortal:
    """
    Represents an automated basic setup for interacting with ReportPortal.
    It does the Docker setup on a fresh Ubuntu server, then installs reportportal.
    After installation, we provision reportportal with a qcify user and OBS_Test dashboard.
    """

    def __init__(self):
        self._widget_ids: List[int] = []
        self._OBS_DashBoard_id: Optional[str] = None
        self._OBS_Test_project_name: str = "OBS_Test"
        self._ssh_client: Optional[paramiko.SSHClient] = None
        self._remote_host = '127.0.0.1' # sys.argv[0] or '127.0.0.1'  
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
        self._ssh_client.close()  # type: ignore

    def execute_ssh_command(self, command: str, user: Optional[str] = None, password: Optional[str] = None) -> str:
        self._create_client(user=user, password=password)
        full_cmd = command

        if command.startswith("sudo") and not self._remote_password:
            self._remote_password = getpass.getpass(prompt="Enter remote sudo password: ")
            # Add -S option to sudo command and pass the password through stdin
            full_cmd = f'echo "{self._remote_password}" | sudo -S {command}'

        stdin, stdout, stderr = self._ssh_client.exec_command(full_cmd)  # type: ignore
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

    def create_api_call(self, method: str,
                        url: str,
                        headers: Optional[dict[str, str]] = None,
                        data: Optional[Union[str, dict[str, str]]] = None,
                        auth: Optional[tuple[str, str]] = None) -> requests.Response:
        if method == 'GET':
            return requests.get(url=f'http://{self._remote_host}:8080{url}', headers=headers)
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

    async def step_5_wait_for_stack_to_be_online(self):
        # while setup.create_api_call('GET', '/api/v1/settings').status_code != 400:
        print("Waiting for stack to be ready")
        #     await sleep(5)
        await sleep(30)
    async def step_6_create_OBS_test_project(self):
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {await _retrieve_api_key()}"}
        data = {
            "entryType": "INTERNAL",
            "projectName": f"{self._OBS_Test_project_name}"
        }
        result = setup.create_api_call('POST', '/api/v1/project', headers=headers, data=json.dumps(data))
        print(result.content)

    async def step_7_create_qcify_user(self):
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {await _retrieve_api_key()}"}
        with open(f'{os.getcwd()}/provisioning/users/qcify_user.json') as user:
            data = json.load(user)
            result = setup.create_api_call('POST', '/api/users', headers=headers, data=json.dumps(data))
            print(f'{user.name} {result.content}')

    async def step_8_create_dashboard(self):
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {await _retrieve_api_key()}"}
        data = {"description": "OBS_All demo dashboard",
                "name": "OBS_All Demo"}

        result = setup.create_api_call('POST', f'/api/v1/{self._OBS_Test_project_name}/dashboard', headers=headers, data=json.dumps(data))
        print(result.content)
        self._OBS_DashBoard_id = json.loads(result.content.decode('utf-8'))['id']

    async def step_9_create_filters(self):
        # TODO: Add system test filter
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {await _retrieve_api_key()}"}

        with open(f'{os.getcwd()}/provisioning/dashboards/filters/demo_filter.json') as filter:
            data = json.load(filter)
            result = setup.create_api_call('POST', f'/api/v1/{self._OBS_Test_project_name}/filter', headers=headers, data=json.dumps(data))
            print(f'{filter.name} {result.content}')

        with open(f'{os.getcwd()}/provisioning/dashboards/filters/python_unit_test_filter.json') as filter:
            data = json.load(filter)
            result = setup.create_api_call('POST', f'/api/v1/{self._OBS_Test_project_name}/filter', headers=headers, data=json.dumps(data))
            print(f'{filter.name} {result.content}')

        with open(f'{os.getcwd()}/provisioning/dashboards/filters/ctest_filter.json') as filter:
            data = json.load(filter)
            result = setup.create_api_call('POST', f'/api/v1/{self._OBS_Test_project_name}/filter', headers=headers, data=json.dumps(data))
            print(f'{filter.name} {result.content}')

    async def step_10_create_widget(self):
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {await _retrieve_api_key()}"}
        with open(f'{os.getcwd()}/provisioning/dashboards/widgets/launch_statistics.json') as widget:
            data = json.load(widget)
            result = setup.create_api_call('POST', f'/api/v1/{self._OBS_Test_project_name}/widget', headers=headers, data=json.dumps(data))
            self._widget_ids.append(json.loads(result.content.decode('utf-8'))['id'])
            print(f'{widget.name} {result.content}')

        with open(f'{os.getcwd()}/provisioning/dashboards/widgets/time_consumption.json') as widget:
            data = json.load(widget)
            result = setup.create_api_call('POST', f'/api/v1/{self._OBS_Test_project_name}/widget', headers=headers, data=json.dumps(data))
            self._widget_ids.append(json.loads(result.content.decode('utf-8'))['id'])
            print(f'{widget.name} {result.content}')

    async def step_11_add_widgets(self):
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {await _retrieve_api_key()}"}
        with open(f'{os.getcwd()}/provisioning/dashboards/widgets/add_to_dashboard.json') as add_widget:
            data = json.load(add_widget)
            data['addWidget']['widgetId'] = self._widget_ids[0]
            result = setup.create_api_call('PUT', f'/api/v1/{self._OBS_Test_project_name}/dashboard/{self._OBS_DashBoard_id}/add', headers=headers, data=json.dumps(data))
            print(f'{add_widget.name} {result.content}')
            
    async def step_12_get_qcify_user_key(self) -> str:
        qcify_user_id = 3 # TODO: Get the qcify user id via the API
        
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {await _retrieve_api_key()}"}
        result = setup.create_api_call('GET', f'/api/users/{qcify_user_id}/api-keys', headers=headers)
        api_key = json.loads(result.content.decode('utf-8'))
        return api_key
        
    async def main(self):
        # self.step_1_copy_required_files()
        # self.step_2_install_docker_compose()
        # self.step_3_pull_report_portal_image()
        # self.step_4_start_report_portal_stack()
        # await self.step_5_wait_for_stack_to_be_online()
        # await self.step_6_create_OBS_test_project()
        # await self.step_7_create_qcify_user()
        # await self.step_8_create_dashboard()
        # await self.step_9_create_filters()
        # await self.step_10_create_widget()
        # await self.step_11_add_widgets()
        # print( await _retrieve_api_key())
        print( await self.step_12_get_qcify_user_key())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    setup = SetupReportPortal()
    loop.run_until_complete(setup.main())
