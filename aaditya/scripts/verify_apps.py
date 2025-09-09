import os
import re

# Paths
input_file = "/home/local/ASURITE/amodi22/apps_lists/apps_list.txt"   # raw list
output_file = "/home/local/ASURITE/amodi22/apps_lists/verified_apps.txt"  # clean list
download_dir = "/home/local/ASURITE/amodi22/apks"  # where APKs/XAPKs are saved

# Create download folder if it doesn't exist
os.makedirs(download_dir, exist_ok=True)

# Read input list
with open(input_file, "r") as infile:
    apps = infile.readlines()

clean_apps = []

for app in apps:
    app = app.strip()
    # Remove trailing underscores/numbers after APK names like _123.apk or _v1.apk
    app = re.sub(r'_[0-9]+(\.apk|\.xapk)?$', '', app)
    # Replace invalid characters/spaces with dots
    app = re.sub(r'[^a-zA-Z0-9\.]', '.', app)
    
    # Check if the app is already downloaded (skip if file exists and >0 bytes)
    apk_file_xapk = os.path.join(download_dir, f"{app}.xapk")
    apk_file_apk = os.path.join(download_dir, f"{app}.apk")
    if os.path.exists(apk_file_xapk) and os.path.getsize(apk_file_xapk) > 0:
        continue
    if os.path.exists(apk_file_apk) and os.path.getsize(apk_file_apk) > 0:
        continue

    clean_apps.append(app)

# Save verified clean list
with open(output_file, "w") as outfile:
    for app in clean_apps:
        outfile.write(app + "\n")

print(f"✅ Clean list ready with {len(clean_apps)} apps at {output_file}")

