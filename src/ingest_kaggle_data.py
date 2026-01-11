import os 
import cv2 
import glob
import shutil
import numpy as np
from rosbags.rosbag2 import Writer
from rosbags.typesys import get_typestore, Stores 

# Configuration 
SOURCE_ROOT = 'data/kaggle_blur_dataset'
OUTPUT_BAG = 'data/real_world_bag'

# standarlize all input images to 640x480 for consistent processing
TARGET_W, TARGET_H = 640, 480

def get_image_paths():
    """Gathers file paths and assigns Ground Truth (GT) Labels."""
    dataset = []

    # 1. Get Sharp Images 
    path_sharp = os.path.join(SOURCE_ROOT, 'sharp')
    files_sharp = glob.glob(os.path.join(path_sharp, '*.*'))
    # Take first 50 to keep the bag files size manageable 
    for f in files_sharp[:50]:
        dataset.append((f, "SHARP_GT"))

    # 2. Get defocused blurred images 
    path_blur = os.path.join(SOURCE_ROOT, 'defocsed_blurred')
    files_blur = glob.glob(os.path.join(path_blur, '*.*'))
    for f in files_blur[:50]:
        dataset.append((f, "BLUR_GT"))

    # 3. Get motion blurred
    path_motion = os.path.join(SOURCE_ROOT, 'motion_blurred')
    files_motion = glob.glob(os.path.join(path_motion, '*.*'))
    for f in files_motion[:20]:
        dataset.append((f, "BLUR_GT")) #Treat motion blur as BLUR too 

    return dataset

def resize_with_padding(img):
    """Resizes image to 640x480, padding with black if aspect ration differs."""
    h, w = img.shape[:2]
    scale = min(TARGET_W / w, TARGET_H / h)
    new_w, new_h = int(w * scale), int(h * scale)

    resized = cv2.resize(img, (new_w, new_h))

    # Create black canvas 
    canvas = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.uint8)

    # Center the image 
    y_off = (TARGET_H - new_h) // 2
    x_off = (TARGET_W - new_w) // 2
    canvas[y_off:y_off+new_h, x_off:x_off+new_w] = resized

    return canvas 

def main():
    # 1. Prepare Output 
    if os.path.exists(OUTPUT_BAG):
        shutil.rmtree(OUTPUT_BAG)
    os.makedirs(os.path.dirname(OUTPUT_BAG), exist_ok=True)

    # 2. Load data 
    print(f"Scanning {SOURCE_ROOT}...")
    dataset = get_image_paths()
    print(f"Found {len(dataset)} images to ingest.")

    # 3. Setup Rosbags 
    typestore = get_typestore(Stores.LATEST)
    Image = typestore.types['sensor_msgs/msg/Image']
    Header = typestore.types['std_msgs/msg/Header']
    Time = typestore.types['builtin_interfaces/msg/Time']

    with Writer(OUTPUT_BAG) as writer:
        topic = '/camera/image_raw'
        msgtype = Image.__msgtype__
        conn = writer.add_connection(topic, msgtype, typestore=typestore)

        print("Starting ingestion.. (this might take a moment)")

        for i, (filepath, label) in enumerate(dataset):
            # Read with OpenCV
            img = cv2.imread(filepath)
            if img is None:
                print(f"Warning: Could not read {filepath}")
                continue

            # Process
            processed_img = resize_with_padding(img)
            flattened = processed_img.flatten().astype(np.uint8)

            # Create Message 
            # TRICK: WE store the 'label' (SHARP_GT / BLUR_GT) in the frame_id!
            header = Header(
                stamp=Time(sec=i, nanosec=0),
                frame_id=label
            )

            msg = Image(
                header=header,
                height=TARGET_H,
                width=TARGET_W,
                encoding='bgr8', # OpenCV uses BGR by default
                is_bigendian=0,
                step=TARGET_W * 3,
                data=flattened
            )

            # Write 
            timestamp = i * 100_000_000 # simulated 10 FPS 
            writer.write(conn, timestamp, typestore.serialize_cdr(msg, msgtype))

            if (i+1) % 20 == 0:
                print(f"  Ingested {i+1} frames...")

    print(f"\nSUCCESS: Real-world bag created at {os.path.abspath(OUTPUT_BAG)}")

if __name__ == "__main__":
    main()
