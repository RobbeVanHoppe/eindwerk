from datetime import datetime
from pathlib import Path
import threading
from prometheus_client import start_http_server, Gauge
import time
import xml.etree.ElementTree as ET

class Exporter:
    def __init__(self) -> None:
        self.timestamp = Gauge('timestamp', 'Timestamp of the test run')
        self.total_tests = Gauge('total_tests', 'Total number of tests')
        self.total_run_time = Gauge('total_run_time', 'Total time taken to run tests')
        self.test_failed = Gauge('test_failed', 'Number of tests failed')
        threading.Thread(target=self.update_metrics_periodically).start()
    
    def process_data(self):
        xml_files = Path('/app/test_results').glob('*.xml')
        for run in xml_files:
            tree = ET.parse(run)
            root = tree.getroot()  
            
            # Extract data and update metrics
            testsuite = root.find('testsuite')
            self.total_tests.set(float(testsuite.attrib['tests']))
            self.total_run_time.set(float(testsuite.attrib['time']))
            
            # We need the timestamp in a float format
            date_time_obj = datetime.fromisoformat(testsuite.attrib['timestamp'])
            timestamp = date_time_obj.timestamp()
            self.timestamp.set(float(timestamp))
            self.test_failed.set(float(testsuite.attrib['failures']))
            
    def update_metrics_periodically(self):
        while True:
            self.process_data()
            time.sleep(5)
        
    

if __name__ == '__main__':
    start_http_server(8000)
    Exporter().update_metrics_periodically()
