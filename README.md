# Robotics Sensor Pipeline

## Project Overview
This project builds a pipeline to process robot sensor data.
Currently, it focuses on **Synthetic Data Generation** and **Data Ingestion** using ROS 2 formats (sqlite3 `.db3` files).

## What We Have Built (Day 1)
1.  **Environment Setup**: A robust Conda environment (`rosbag_test`) handling complex Python dependencies.
2.  **Synthetic Data Generator**: A Python script that creates valid ROS 2 bag files from scratch without needing a full ROS installation. It generates "static noise" images to simulate a camera feed.
3.  **Data Inspector**: A verification tool that reads the bag file, decodes the messages, and proves the data pipeline is working.

## Technical Challenges & Solutions
During the initial setup, we encountered several critical issues:

### 1. "Dependency Hell" (rosbags vs. numpy)
* **Problem:** The `rosbags` library had conflicting version requirements with `numpy` (v2.0+ vs v1.26), causing `ImportError` and `AttributeError: module has no attribute`.
* **Solution:** We created a fresh Conda environment (`rosbag_test`) and strictly controlled the installation order to ensure `rosbags 0.10+` and `numpy` were compatible.

### 2. Broken Public Data Links
* **Problem:** The official ROS 2 sample data repositories returned 404 errors due to structural changes on GitHub.
* **Solution:** instead of relying on external downloads, we engineered a **Synthetic Data Generator** (`generate_data.py`). This script manually constructs ROS 2 CDR-serialized messages and writes them to a standard SQLite database, making the project self-contained and robust.

### 3. Serialization Conflicts
* **Problem:** The library threw `AttributeError: 'bytes' object has no attribute 'view'` because it expected a specific Numpy array format for image data.
* **Solution:** We refactored the generator to pass flattened Numpy arrays with specific `dtype=uint8` instead of raw bytes, satisfying the serializer's requirements.

## How to Run

### 1. Prerequisites
- Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
- Open your terminal.

### 2. Setup Environment
```bash
conda create -n rosbag_test python=3.10 -y
conda activate rosbag_test
pip install rosbags numpy matplotlib


---


---

## What We Have Built (Day 2)
1.  **C++ Processing Engine**: Initialized a C++ project structure to process high-performance sensor data.
2.  **Automated Dependency Management**: Created a Python script (`setup_cpp_dependencies.py`) to automatically fetch and configure external C++ libraries.
3.  **Database Integration**: Successfully integrated the SQLite "Amalgamation" source code directly into the C++ build tree, allowing us to read ROS 2 `.db3` files natively without requiring the full ROS 2 SDK.

## Technical Challenges & Solutions (Day 2)

### 1. Missing C++ Tools on Windows
* **Problem:** Windows does not ship with standard C++ build tools (Make, G++, CMake), usually requiring a heavy Visual Studio installation (4GB+).
* **Solution:** We leveraged the existing Conda environment to install the `m2w64-toolchain` and `cmake` from `conda-forge`. This kept the environment lightweight and isolated.

### 2. "Why didn't we just download the SQLite Zip manually?"
* **Decision:** Instead of manually downloading the SQLite zip file, extracting it, and placing it in the folder, we wrote `src/setup_cpp_dependencies.py`.
* **Reasoning:**
    * **Reproducibility:** A manual process is error-prone. If another developer clones this repo, they shouldn't have to read a long instruction manual to find the right website and buttons.
    * **Automation:** By scripting the download, anyone can set up the entire C++ environment with a single command (`python src/setup_cpp_dependencies.py`). This is a best practice known as **"Infrastructure as Code."**

### 3. Build System Configuration
* **Problem:** Connecting a raw C library (SQLite) to a C++ project in CMake requires specific linking instructions.
* **Solution:** configured `CMakeLists.txt` to include the `sqlite_lib` directory and explicitly link the `sqlite3.c` source file into the final executable, treating it as part of our own code ("Amalgamation").