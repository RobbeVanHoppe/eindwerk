import xml.etree.ElementTree as ET
from reportportal_client import RP, create_client, ClientType
from reportportal_client.helpers import get_launch_sys_attrs
import time
import os
import asyncio

def parse_test_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    results = []
    for testcase in root.iter('testcase'):
        result = {
            'name': testcase.get('name'),
            'status': 'PASSED' if testcase.find('failure') is None else 'FAILED',
            'time': testcase.get('time'),
            'system_out': testcase.find('system-out').text if testcase.find('system-out') is not None else '',
        }
        results.append(result)
    return results

async def send_results_to_report_portal(results):
    client: RP | None = create_client(
        client_type=ClientType.ASYNC,
        endpoint="http://localhost:8080",
        project="obs_test",
        api_key="ctest-key_9FTz5jnOTHO8kB6Jb6ps1rL1DvpATboZPWVJY2duuS63eXGYkwaOHpP8BSHY5xP-"
    )
    
    if client is None:
        print("Failed to create client")
        return
    else: print("Client created")

    launch_name = "ctest_launch_" + str(int(time.time()))
    
    launch_id = await client.start_launch(
        name=launch_name,
        start_time=str(int(time.time() * 1000)),
        attributes=get_launch_sys_attrs(),
        description="OBS C++ Unit Tests"
    )
    
    if launch_id is None:
        print("Failed to start launch")
    else: print("Launch started with UUID: ", launch_id)


    for result in results:
        item_id = await client.start_test_item(
            name=result['name'],
            start_time=str(int(time.time() * 1000)),
            item_type="STEP"
        )

        if item_id is not None:
            description = f"System Out:\n{result['system_out']}" if result['system_out'] else "No system out available."
            await client.finish_test_item(
                item_id=item_id,
                end_time=str(int(time.time() * 1000)),
                status=result['status'],
                description=description
            )

    await client.finish_launch(
        launch_id=launch_id,
        end_time=str(int(time.time() * 1000))
    )


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_xml_path = os.path.join(base_dir, "test_results", "results.xml")
    
    results = parse_test_xml(test_xml_path)
    
    asyncio.run(send_results_to_report_portal(results))