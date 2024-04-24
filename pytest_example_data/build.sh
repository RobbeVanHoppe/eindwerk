#!/bin/bash

run_python_tests() {
    (
        python3 -m pip install -r requirements.txt

        py.test . --reportportal
        exit_status=0
        return $exit_status
    )
}

main() {
    run_python_tests
    exit $?
}

main
