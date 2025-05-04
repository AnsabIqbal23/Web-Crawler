import subprocess
import os
import socket
import time

def is_mongo_running():
    # Check if port 27017 is already in use
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(("localhost", 27017))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close()

def start_mongodb_server():
    if is_mongo_running():
        print("✅ MongoDB is already running. Skipping startup.")
        return None  # No need to start again!

    mongodb_bin_path = r"C:\Program Files\MongoDB\Server\8.0\bin"  # UPDATE this if needed
    mongod_path = os.path.join(mongodb_bin_path, "mongod.exe")
    dbpath = r"C:\data\db"

    process = subprocess.Popen(
        [mongod_path, f"--dbpath={dbpath}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    print("✅ MongoDB server started.")
    return process