#!/bin/bash

run_python_tests() {
    (
        python -m pip install -r requirements.txt
        python -m pytest --junitxml=/app/test_results/run$(date +%Y%m%d-%H%M).xml
        exit_status=0
        return $exit_status
    )
}

main() {
    run_python_tests
    exit $?
}

main
