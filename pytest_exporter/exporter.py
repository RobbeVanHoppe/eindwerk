import glob
import threading
from prometheus_client import Info, start_http_server, Gauge
import time
import xml.etree.ElementTree as ET



class Exporter:
    def __init__(self) -> None:
        self.unit_tests_total_tests = Gauge('total_tests', 'Total number of tests')
        self.unit_tests_total_run_time = Gauge('total_run_time', 'Total time taken to run tests')
        self.unit_tests_failed_tests = Gauge('failed_tests', 'Number of tests failed')
        self.unit_tests_skipped_tests = Gauge('skipped_tests', 'Number of tests skipped')
        self.unit_tests_errored_tests = Gauge('errored_tests', 'Number of tests errored')
        threading.Thread(target=self.update_metrics_periodically).start()
    
    def process_data(self, test_type = 'unit'):
        if test_type == 'unit':
            xml_files = glob.glob('/app/pytest_test_results/unit_test_results/*.xml')
            testsuite = self.unit_tests
        elif test_type == 'telemetry':
            xml_files = glob.glob('/app/telemetry_test_results/telemetry_test_results/*.xml')
            testsuite = self.telemetry_tests
        elif test_type == 'system':
            xml_files = glob.glob('/app/system_test_results/*.xml')
            testsuite = self.system_tests
            
        if len(xml_files) > 0:
            last_run = xml_files[-1]
            tree = ET.parse(last_run)
            root = tree.getroot()  
            
            # Extract data and update metrics for dirrefent test suites
            testsuite = root.find('testsuite')
            self.unit_tests_total_tests.set(float(testsuite.attrib['tests']))
            self.unit_tests_total_run_time.set(float(testsuite.attrib['time']))
            testsuite.failed_tests.set(float(testsuite.attrib['failures']))
            testsuite.skipped_tests.set(float(testsuite.attrib['skipped']))
            testsuite.errored_tests.set(float(testsuite.attrib['errors']))
            
    def update_metrics_periodically(self):
        while True:
            self.process_data(test_type='unit')
            self.process_data(test_type='system')
            self.process_data(test_type='telemetry')
            time.sleep(5)
        
    

if __name__ == '__main__':
    start_http_server(8000)
    Exporter().update_metrics_periodically()
