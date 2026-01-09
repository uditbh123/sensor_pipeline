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