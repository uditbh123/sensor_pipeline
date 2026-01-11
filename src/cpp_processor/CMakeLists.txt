# --- Python ---
__pycache__/
*.pyc

# --- Virtual Environments ---
venv/
env/
.env

# --- IDE Settings ---
.vscode/
.idea/

# --- Data (CRITICAL) ---
# We generate this or download it. Never upload to GitHub.
data/
*.db3

# --- C++ Build Artifacts (NEW) ---
# Ignore the build folder where CMake does its work
build/
src/cpp_processor/build/

# Ignore compiled executables and objects
*.exe
*.o
*.obj
*.dll
*.dylib
*.so

# --- CMake Temporary Files ---
CMakeCache.txt
CMakeFiles/
cmake_install.cmake
Makefile

# --- OS System Files ---
.DS_Store
Thumbs.db