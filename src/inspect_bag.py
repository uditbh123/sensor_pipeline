from rosbags.rosbag2 import Reader

# 1. POINT TO YOUR NEW DATA
BAG_PATH = 'data/synthetic_bag'

print(f"Opening bag: {BAG_PATH}...")

try: 
    # 2. Open the bag
    with Reader(BAG_PATH) as reader:
        # Print high-level info
        print(f"\n--- Metadata ---")
        print(f"Duration: {reader.duration / 1e9:.2f} seconds")
        print(f"Message Count: {reader.message_count}")

        print("\n--- Topics Found ---")
        for connection in reader.connections:
            print(f" - {connection.topic} ({connection.msgtype})")

        # 3. Read the first few messages
        print("\n--- Reading Streams ---")
        count = 0
        for connection, timestamp, rawdata in reader.messages():
            # FIX: Print the first 5, THEN stop.
            if count < 5:
                print(f"Msg: {connection.topic} | Time: {timestamp}")
                count += 1
            else:
                break 

    print("\nSUCCESS: You have successfully ingested robotics data!")

except FileNotFoundError:
    print(f"ERROR: Could not find folder at {BAG_PATH}")
except Exception as e:
    print(f"An error occurred: {e}")