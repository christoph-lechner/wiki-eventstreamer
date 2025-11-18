cmake_minimum_required(VERSION 3.12)
project(analyze_timeseries)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(analyze_timeseries
	analyze_timeseries.cc
)

