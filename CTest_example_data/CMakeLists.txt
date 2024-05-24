cmake_minimum_required(VERSION 3.28)
project(RP_TestProject LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED True)

if(DEFINED ENV{VCPKG_ROOT} AND EXISTS "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake")
    set(CMAKE_TOOLCHAIN_FILE "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake" CACHE STRING "")
endif()

find_package(GTest CONFIG REQUIRED)
enable_testing()

add_executable(RP_TestProject src/main.cpp)

add_executable(RP_ExampleProjectTests tests/test_main.cpp)
target_link_libraries(RP_ExampleProjectTests PRIVATE GTest::gtest GTest::gtest_main)

include(GoogleTest)
gtest_discover_tests(RP_ExampleProjectTests)

# Set the output directory for test results
file(MAKE_DIRECTORY ${PROJECT_SOURCE_DIR}/test_results)

# setup python venv
set(VENV_DIR ${CMAKE_BINARY_DIR}/.venv)

add_custom_target(setup_venv ALL
        COMMAND python3 -m venv ${VENV_DIR}
        COMMAND ${VENV_DIR}/bin/pip install --upgrade pip
        COMMAND ${VENV_DIR}/bin/pip install -r ${CMAKE_SOURCE_DIR}/requirements.txt
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
)

# Configure CTest to output results in JUnit XML format
set(CMAKE_COMMAND cmake)
set(CTEST_OUTPUT_ON_FAILURE ON)
set(CTEST_CUSTOM_POST_TEST "${CMAKE_COMMAND} -E copy ${CMAKE_BINARY_DIR}/Testing/Temporary/LastTest.log ${PROJECT_SOURCE_DIR}/test_results/results.xml")

# Add a custom target to run tests and generate JUnit XML output
#add_custom_target(run_reportportal ALL
#        COMMAND ${CMAKE_COMMAND} -E echo "Running ReportPortal client script..."
#        COMMAND ${CMAKE_COMMAND} -E env PYTHONPATH=${CMAKE_SOURCE_DIR} python3 ${CMAKE_SOURCE_DIR}/reportportal_uploader.py
#        DEPENDS RP_ExampleProjectTests
#        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
#)