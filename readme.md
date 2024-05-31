# How does it work?

The setup script makes sure docker is installed and then pulls the images for the reportportal stack.

Reportportal works via a Java API to easily set up projects, users, dashboards, etc.
To make the setup repeatable, the script can be run on a server or VM via ssh, the IP and username of the target should
be provided in the __init__ function.

## Running the stack

To launch the reportportal stack, you can just execute

`cd reportportal/provisioning/docker-compose.yaml && docker compose up`

For a first time setup, use the **reportportal/setup.py** script (mind that you may have to comment/uncomment some steps
based on your needs).

## Python pytest

The integration with pytest is pretty easy, the **pytest_example_data/** has a basic implementation showing the
essentials.

First, the necessary packages need to be installed, for Python this is:

- reportportal-client
- pytest-reportportal

There needs to be a pytest.ini which contains the endpoint and API key (which can be found in the reportportal GUI).
Preferably, the API key should be stored in a more secure way, but for now, it is hardcoded in the pytest.ini file.
The test themselves don't need any change, which is a plus.

To run the tests, execute `python -m pytest --reportportal`

## GTest

We need to save the results in xml format and then post them to the reportportal stack. to save the output, all that is
needed is adding `--output-junit` to the CTest run arguments.

For example `ctest --output-junit "${OBS_ALL_DIR}"/test_results/ctest/result-"${current_date_time}".xml`

For getting the results into the reportportal stack, we need to use the **reportportal/reportportal_uploader.py**
script.
This script will read the xml files and post them to the reportportal stack. This script can be improved by reading
different xml tags and then adding them to the properties.

## What needs to be improved?

There is no checking in the methods to know if the user/project/dashboard has already been made. This works fine when
setting up a server for the first time,
but when the steps need to be executed individually, errors may occur for example when trying to add a duplicate user.
The API key for uploading test results needs to be hardcoded in the pytest.ini file, this is not ideal and should be
changed to a more secure method.
The same goes for the CTest uploader script. I have tried writing a GET for the keys of the user, but I failed to get
that working in time.
