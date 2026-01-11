cmake_minimum_required(VERSION 3.10)
project(SensorProcessor)

set(CMAKE_CXX_STANDARD 14)

message(STATUS "Looking for SQLite in: ${CMAKE_CURRENT_SOURCE_DIR}/sqlite_lib")
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/sqlite_lib)

# --- PROGRAM 1: The Simple Reader (Day 2) ---
add_executable(processor 
    main.cpp
    sqlite_lib/sqlite3.c
)

# --- PROGRAM 2: The Blur Detector (Day 3) ---
add_executable(blur_detector 
    blur_detector.cpp
    sqlite_lib/sqlite3.c
)