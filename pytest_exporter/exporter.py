import glob
import threading
from prometheus_client import start_http_server, Gauge
import time
import xml.etree.ElementTree as ET

class Exporter:
    def __init__(self) -> None:
        self.total_tests = Gauge('total_tests', 'Total number of tests')
        self.total_run_time = Gauge('total_run_time', 'Total time taken to run tests')
        self.failed_tests = Gauge('failed_tests', 'Number of tests failed')
        self.skipped_tests = Gauge('skipped_tests', 'Number of tests skipped')
        self.errored_tests = Gauge('errored_tests', 'Number of tests errored')
        threading.Thread(target=self.update_metrics_periodically).start()
    
    def process_data(self):
        # xml_files = glob.glob('pytest_example_data/test_results/*.xml')
        xml_files = glob.glob('/app/test_results/*.xml')
        if len(xml_files) > 0:
            last_run = xml_files[-1]
            tree = ET.parse(last_run)
            root = tree.getroot()  
            
            # Extract data and update metrics
            testsuite = root.find('testsuite')
            self.total_tests.set(float(testsuite.attrib['tests']))
            self.total_run_time.set(float(testsuite.attrib['time']))
            self.failed_tests.set(float(testsuite.attrib['failures']))
            self.skipped_tests.set(float(testsuite.attrib['skipped']))
            self.errored_tests.set(float(testsuite.attrib['errors']))
            
    def update_metrics_periodically(self):
        while True:
            self.process_data()
            time.sleep(5)
        
    

if __name__ == '__main__':
    start_http_server(8000)
    Exporter().update_metrics_periodically()
