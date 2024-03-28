#######################################
#### Setup script for ReportPortal ####
#######################################

import os
import subprocess


class SetupReportPortal:
    def __init__(self, remote_host_ip: str = None):
        self.remote_host = '10.10.0.59'
        self.remote_user = 'qcify'
        self.remote_home = f'/home/{self.remote_user}/reportportal'
        self.ssh_key = f'{os.environ["HOME"]}/.ssh/id_rsa'
        self.host_home = f'{os.environ["HOME"]}'
        self.reportportal_dir = f'{self.host_home}/qcify/test_dashboard/reportportal'


    def execute_ssh_command(self, command):
        ssh_command = f'ssh -i {self.ssh_key} {self.remote_user}@{self.remote_host}'
        subprocess.run(f'{ssh_command} {command}', shell=True, check=True)
        

    def copy_files(self, src_folder, dst_folder):
        command = f'scp -i {self.ssh_key} -r {src_folder}/ {self.remote_user}@{self.remote_host}:{dst_folder}'
        subprocess.run(f'{command}', shell=True, check=True)
        
        
if __name__ == '__main__':
    setup = SetupReportPortal()
    def copy_required_files():
        setup.copy_files(setup.reportportal_dir, setup.remote_home)
        
    # step 1: copy required files into container
    copy_required_files()
    
