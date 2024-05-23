cmake_minimum_required(VERSION 3.28)
project(TestProject LANGUAGES CXX)


set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED True)


if(DEFINED ENV{VCPKG_ROOT} AND EXISTS "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake")
    set(CMAKE_TOOLCHAIN_FILE "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake" CACHE STRING "")
endif()

find_package(GTest CONFIG REQUIRED)
enable_testing()

add_executable(TestProject src/main.cpp)

add_executable(ExampleProjectTests tests/test_main.cpp)
target_link_libraries(ExampleProjectTests PRIVATE GTest::gtest GTest::gtest_main)

# Enable tests
include(GoogleTest)
file(MAKE_DIRECTORY ${PROJECT_SOURCE_DIR}/test_results)
gtest_discover_tests(ExampleProjectTests)
add_custom_target(
        reportportal_ctest
        COMMAND ExampleProjectTests --gtest_output=xml:${PROJECT_SOURCE_DIR}/test_results/results.xml
        DEPENDS ExampleProjectTests
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
)
