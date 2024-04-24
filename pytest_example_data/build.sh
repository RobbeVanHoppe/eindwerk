#!/bin/bash

run_python_tests() {
    (
        python3 -m pip install -r requirements.txt

        python3 -m pytest ./example_tests --reportportal
        exit_status=0
        return $exit_status
    )
}

main() {
    run_python_tests
    exit $?
}

main
