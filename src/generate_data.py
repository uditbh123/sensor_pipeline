import os
import shutil
import numpy as np
from rosbags.rosbag2 import Writer
from rosbags.typesys import get_typestore, Stores

# 1. Setup path
BAG_PATH = 'data/synthetic_bag'

# Auto-delete old folder if it exists
if os.path.exists(BAG_PATH):
    shutil.rmtree(BAG_PATH)

os.makedirs(os.path.dirname(BAG_PATH), exist_ok=True)
print(f"Generating synthetic data at {BAG_PATH}...")

# 2. Load Types
typestore = get_typestore(Stores.LATEST)
Image = typestore.types['sensor_msgs/msg/Image']
Header = typestore.types['std_msgs/msg/Header']
Time = typestore.types['builtin_interfaces/msg/Time']

# 3. Create the Writer
with Writer(BAG_PATH) as writer:
    topic = '/camera/image_raw'
    msgtype = Image.__msgtype__
    connection = writer.add_connection(topic, msgtype, typestore=typestore)
    
    for i in range(10):
        timestamp_nanos = i * 1_000_000_000
        
        # Header
        my_header = Header(
            stamp=Time(sec=i, nanosec=0),
            frame_id='camera_optical_frame'
        )
        
        # Noise Image (100x100x3)
        noise = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # FIX: Keep as uint8 numpy array, flatten to 1D with correct dtype
        image_data = noise.flatten().astype(np.uint8)
        
        msg = Image(
            header=my_header,
            height=100, 
            width=100, 
            encoding='rgb8',
            is_bigendian=0, 
            step=300,  # width * channels (100 * 3)
            data=image_data  # Pass numpy array directly
        )
        
        writer.write(connection, timestamp_nanos, typestore.serialize_cdr(msg, msgtype))
        
        if (i + 1) % 5 == 0:
            print(f"  Written {i + 1}/10 images...")

print("SUCCESS: Synthetic data created successfully!")
print(f"Output: {os.path.abspath(BAG_PATH)}")
print("\nTo read this bag, use:")
print(f"  python src/read_data.py")