import rosbags
import os

print(f"INSTALLED VERSION: {rosbags.__version__}")
print(f"FILE LOCATION: {os.path.dirname(rosbags.__file__)}")

try:
    from rosbags.typesys import get_typestore
    print("SUCCESS: get_typestore found!")
except ImportError:
    print("FAILURE: get_typestore is MISSING.")
    import rosbags.typesys
    print(f"Available contents in typesys: {dir(rosbags.typesys)}")