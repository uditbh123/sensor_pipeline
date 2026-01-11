# Robotics Sensor Pipeline

## Project Overview
This project builds a pipeline to process robot sensor data.
Currently, it focuses on **Synthetic Data Generation** and **Data Ingestion** using ROS 2 formats (sqlite3 `.db3` files).

## What We Have Built (Day 1)
1.  **Environment Setup**: A robust Conda environment (`rosbag_test`) handling complex Python dependencies.
2.  **Synthetic Data Generator**: A Python script that creates valid ROS 2 bag files from scratch without needing a full ROS installation. It generates "static noise" images to simulate a camera feed.
3.  **Data Inspector**: A verification tool that reads the bag file, decodes the messages, and proves the data pipeline is working.

## Technical Challenges & Solutions (Day 1)

### 1. "Dependency Hell" (rosbags vs. numpy)
* **Problem:** The `rosbags` library had conflicting version requirements with `numpy` (v2.0+ vs v1.26), causing `ImportError` and `AttributeError: module has no attribute`.
* **Solution:** We created a fresh Conda environment (`rosbag_test`) and strictly controlled the installation order to ensure `rosbags 0.10+` and `numpy` were compatible.

### 2. Broken Public Data Links
* **Problem:** The official ROS 2 sample data repositories returned 404 errors due to structural changes on GitHub.
* **Solution:** Instead of relying on external downloads, we engineered a **Synthetic Data Generator** (`generate_data.py`). This script manually constructs ROS 2 CDR-serialized messages and writes them to a standard SQLite database, making the project self-contained and robust.

### 3. Serialization Conflicts
* **Problem:** The library threw `AttributeError: 'bytes' object has no attribute 'view'` because it expected a specific Numpy array format for image data.
* **Solution:** We refactored the generator to pass flattened Numpy arrays with specific `dtype=uint8` instead of raw bytes, satisfying the serializer's requirements.

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
* **Solution:** Configured `CMakeLists.txt` to include the `sqlite_lib` directory and explicitly link the `sqlite3.c` source file into the final executable, treating it as part of our own code ("Amalgamation").

---

# Day 2: Building the C++ Data Ingestion Engine

## 🚀 What We Accomplished
Today, we shifted from Python prototyping to high-performance C++ development. We successfully built the "Ingestion Layer" that reads raw sensor data directly from the storage database.

### 1. Set Up the C++ Toolchain (Windows)
* **Action:** Installed `cmake`, `make`, and the `g++` compiler (MinGW) via Conda.
* **Result:** Created a portable, isolated C++ development environment without needing a heavy Visual Studio installation.

### 2. Automated Dependency Management
* **Action:** Wrote `src/setup_cpp_dependencies.py` to automatically download and extract the SQLite "Amalgamation" source code.
* **Result:** We eliminated external library installation steps. Anyone cloning the repo can just run the script to get the dependencies.

### 3. Integrated SQLite into CMake
* **Action:** Configured `CMakeLists.txt` to compile `sqlite3.c` alongside our own code.
* **Result:** We achieved a "Static Build" where the database engine is built directly into our executable, preventing version conflicts.

### 4. Built the Data Reader (`processor.exe`)
* **Action:** Wrote `main.cpp` using raw SQL queries (`SELECT timestamp, data FROM messages`) to access the ROS 2 bag file.
* **Result:** Successfully verified the pipeline by printing the timestamps and byte sizes of all 10 synthetic frames.

---

## 🛠️ Technical Challenges & Solutions

### Challenge 1: The Missing Compiler
* **Issue:** Windows does not have native C++ tools. Running `cmake` initially returned "Command not found".
* **Solution:** We installed the `m2w64-toolchain` from `conda-forge`. This gave us a Unix-like build environment directly inside PowerShell.

### Challenge 2: The "Ghost" Build Path
* **Issue:** After adding the SQLite library, the compiler complained `fatal error: sqlite3.h: No such file`. This persisted even after we fixed the code.
* **Solution:** We learned that CMake "caches" old paths. We fixed it by using the absolute path variable `${CMAKE_CURRENT_SOURCE_DIR}` in the recipe and performing a clean build (deleting the `build` folder).

### Challenge 3: Linking Errors
* **Issue:** The build failed at the final step with `cannot find -lstatic`.
* **Solution:** We identified an unnecessary flag in `CMakeLists.txt`. Since we were compiling the source code directly (Amalgamation), we didn't need to link against a pre-built "static" library file.

### Challenge 4: The "Empty Database" Trap
* **Issue:** The program ran but crashed with `no such table: messages`.
* **Root Cause:** We pointed the program to `bag.db3`, which didn't exist. SQLite silently created a new, empty file with that name instead of throwing an error.
* **Solution:** We inspected the directory, found the correct file (`synthetic_bag.db3`), and updated our command arguments.

---

## Day 3: Robotics Blur Detector Implementation

We successfully implemented a C++ based Blur Detector module to analyze frame sharpness in the sensor pipeline.

### What we have implemented:
* **Laplacian Variance Algorithm:** Utilized OpenCV's Laplacian operator to calculate the variance of pixels in each frame. High variance indicates sharp edges; low variance indicates blur.
* **Frame Scoring System:** Each frame is assigned a specific numeric score (e.g., ~48,000 range in current tests) to quantify clarity.
* **Status Classification:** Added logic to automatically classify frames as `SHARP` or `BLURRY` based on a definable threshold.
* **Console Logging:** Implemented clear, frame-by-frame status logging to the terminal for debugging and verification.

### Issues we faced & Resolution:
* **Issue (Threshold Sensitivity):** Determining the correct numeric cutoff for "Blurry" vs "Sharp" was difficult as it varies by lighting and scene texture.
    * **Resolution:** We monitored the raw Laplacian variance scores (averaging around 48k for sharp frames) to establish a baseline for our specific sensor data.
* **Issue (Environment Setup):** Getting the C++ processor build system running in the `rosbag_test` environment.
    * **Resolution:** Successfully configured the build in `src/cpp_processor/build` to compile and execute the blur detection logic.

### 🚀 Day 4: Real-World Data & Computer Vision (Current Status)
**Focus:** "The Reality Check" – Kaggle Datasets & Edge Detection.

**1. Data Ingestion Pipeline (`ingest_kaggle_data.py`)**
We moved away from synthetic noise and built a bridge to the real world.
* **Source:** Ingested the **Kaggle Blur Dataset** (Real photos: Sharp vs. Blurry).
* **Normalization:** Implemented a resizing logic to standardize all inputs to `640x480` to prevent buffer crashes.
* **Ground Truth Injection:** We "snuck" the answer key (Label: `SHARP_GT` or `BLURRY_GT`) into the message headers, allowing us to mathematically calculate pipeline accuracy.

**2. The "RGB Trap" & Grayscale Fix**
* **Problem:** Our initial detector gave blurry colorful images (e.g., a blurry red ball on green grass) *higher* scores than sharp gray images.
* **Root Cause:** The algorithm was calculating **Color Contrast** (Red vs. Green), not **Edge Sharpness**.
* **Solution:** We implemented a raw C++ `toGrayscale` function using the luminance formula ($0.299R + 0.587G + 0.114B$) to isolate structural edges from color data.

**3. Laplacian Edge Detection (From Scratch)**
* **Implementation:** Instead of importing OpenCV in C++, we wrote a raw **3x3 Convolution Kernel**:
  $$
  \begin{bmatrix}
  0 & 1 & 0 \\
  1 & -4 & 1 \\
  0 & 1 & 0
  \end{bmatrix}
  $$
* **Result:** This filter cancels out flat colors and only activates when it hits a sharp edge.
* **Metrics:** Achieved **~85.7% Accuracy** on real-world test data after tuning the rejection threshold to `200.0`.

**Expected Output:**
```text
--- ROBOTICS DATA PIPELINE ---
Pipeline: Raw RGB -> Grayscale -> Laplacian Edge Detection
----------------------------------------
Frame 0 | Score: 777 | Pred: SHARP | GT: SHARP [OK]
...
Frame 50 | Score: 60 | Pred: BLURRY | GT: BLURRY [OK]
----------------------------------------
FINAL ACCURACY: 85.71%
---

## 🛠️ How to Run

### 1. Prerequisites
* Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
* Ensure you have the `data/` folder (or run the ingest script).

### 2. Setup Environment
```bash
# Create and activate environment
conda create -n rosbag_test python=3.10 -y
conda activate rosbag_test

# Install Python dependencies
pip install rosbags numpy matplotlib opencv-python

# Install C++ Toolchain (Windows)
conda install -c conda-forge cmake m2w64-toolchain make