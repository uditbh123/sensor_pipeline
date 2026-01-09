import os
import requests
import zipfile
import io
import shutil

# Stable link to the entire repository zip (Head of Master)
REPO_URL = "https://github.com/ros2/rosbag2_sample_data/archive/refs/heads/master.zip"
DATA_DIR = "data"
EXTRACT_PATH = os.path.join(DATA_DIR, "temp_extract")
FINAL_BAG_DIR = os.path.join(DATA_DIR, "rosbag2_2020_03_20-11_23_34")

def setup():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # 1. Download
    print(f"Downloading repo from {REPO_URL}...")
    try:
        r = requests.get(REPO_URL)
        r.raise_for_status()
    except Exception as e:
        print(f"Download failed: {e}")
        return

    # 2. Extract
    print("Unzipping...")
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        z.extractall(EXTRACT_PATH)

    # 3. Move the specific bag folder out
    # The zip usually creates a top-level folder like 'rosbag2_sample_data-master'
    inner_folder = os.path.join(EXTRACT_PATH, "rosbag2_sample_data-master", "rosbag2_2020_03_20-11_23_34")
    
    if os.path.exists(FINAL_BAG_DIR):
        shutil.rmtree(FINAL_BAG_DIR) # Clear old attempts
        
    shutil.move(inner_folder, FINAL_BAG_DIR)

    # 4. Cleanup
    shutil.rmtree(EXTRACT_PATH)
    
    print("\nSUCCESS: Real robot data is ready!")
    print(f"Location: {FINAL_BAG_DIR}")

if __name__ == "__main__":
    setup()