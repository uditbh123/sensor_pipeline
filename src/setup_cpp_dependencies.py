import os 
import urllib.request
import zipfile 
import io

# Configuration
# We use the "Amalgamation" version of SQLite 
# This means the entire database engine is combined into a single C file.
# It makes it incredibly easy to add to a project (no complex installation required).
SQLITE_URL = "https://www.sqlite.org/2023/sqlite-amalgamation-3420000.zip"

# Where I want to save the C++ library files 
# path: scr/cpp_processor/sqlite_lib
DEST_DIR = os.path.join("src", "cpp_processor", "sqlite_lib")

def setup_sqlite():
    """
    Downloads the SQLite source code and extracts the necessary .c and .h files 
    into the project folder so c++ can use them
    """
    # 1. Create the destination folder if it doesn't exist
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    print(f"Downloading SQLite from {SQLITE_URL}...")

    try:
        # 2. Download the file into memory (RAM)
        # I use 'io.BytesIO' so I don't have to save the temporary zip file to disk.
        with urllib.request.urlopen(SQLITE_URL) as response:
            zip_data_in_memory = response.read()

        print("Download complete. Extracting files...")

        # 3. Open the download data as a Zip file 
        with zipfile.ZipFile(io.BytesIO(zip_data_in_memory)) as z:

            # 4. Look for the specific files it needs
            # I filter the list because the zip contains many files I don't want.
            for file_path in z.namelist():

                # Check if the file is the Source Code (.c) or Header (.h)
                if "sqlite3.c" in file_path or "sqlite3.h" in file_path:

                    # Get just the filename (remove folders inside the zip)
                    filename = os.path.basename(file_path)

                    # Define where this specific file should go
                    target_path = os.path.join(DEST_DIR, filename)

                    # Write the file content to out project folder
                    with open(target_path, "wb") as f:
                        f.write(z.read(file_path))

                    print(f"  - Extracted: {filename}")

        print(f"\nSUCCESS: SQLite source code saved to {DEST_DIR}")
        print("You can now include 'sqlite3.h' in your C++ project")

    except Exception as e:
        print(f"FAILED: An error occured: {e}")

if __name__ == "__main__":
    setup_sqlite()
 
