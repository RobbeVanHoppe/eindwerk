# How does it work?

The setup script makes sure docker is installed and then pulls the images for the reportportal stack. 

Reportportal works via a Java API to easily set up projects, users, dashboards, etc.
To make the setup repeatable, the script can be run on a server or VM via ssh, the IP and username of the target should be provided in the __init__ function.

## Python pytest

The integration with pytest is pretty easy, the pytest_example_data/ has a basic implementation showing the essentials.

First, the necessary packages need to be installed, for Python this is:
- reportportal-client
- pytest-reportportal

There needs to be a pytest.ini which contains the endpoint and API key (which can be found in the reportportal GUI).
The test themselves don't need any change, which is a plus. 


## GTest

We need to save the results in xml format and then post them to the reportportal stack. to save the output, all that is needed is adding `--gtest_output=xml:test_results/results.xml` to the GTest run arguments.



To launch the reportportal stack, you can just execute the docker-compose. 

For a first time setup, use the reportportal/setup.py script (mind that you may have to comment/uncomment some steps based on your needs). 



## What needs to be improved?

There is no checking in the methods to know if the user/project/dashboard has already been made. This works fine when setting up a server for the first time, but when the steps need to be executed individually, errors may occur when trying to add a duplicate user.
