cmake_minimum_required(VERSION 3.10)
project(SensorProcessor)

set(CMAKE_CXX_STANDARD 14)

# DEBUG: Confirm path
message(STATUS "Looking for SQLite in: ${CMAKE_CURRENT_SOURCE_DIR}/sqlite_lib")

# 1. Include the folder so main.cpp finds "sqlite3.h"
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/sqlite_lib)

# 2. Compile BOTH files into one executable
add_executable(processor 
    main.cpp
    sqlite_lib/sqlite3.c
)