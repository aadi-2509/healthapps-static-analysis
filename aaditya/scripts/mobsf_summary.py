import os
import json
import pandas as pd
import matplotlib.pyplot as plt

# Paths
REPORTS_DIR = "/mnt/data/projects/HealthApps/women_health_apps/"
OUTPUT_DIR = "/mnt/data/projects/HealthApps/summary_reports_women_apps/"

# Create output dir if not exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize storage
permissions_data = []
trackers_data = []
third_party_data = []

# Loop through JSON reports
json_files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".json")]
total_files = len(json_files)
for idx, file in enumerate(json_files, start=1):
    try:
        with open(os.path.join(REPORTS_DIR, file), "r", encoding="utf-8") as f:
            data = json.load(f)

        app_name = data.get("app_name", file.replace(".json", ""))

        # Extract Permissions
        perms = data.get("permissions", {}).keys()
        for p in perms:
            permissions_data.append({"App": app_name, "Permission": p})

        # Extract Trackers
        trackers = data.get("trackers", [])
        for t in trackers:
            trackers_data.append({"App": app_name, "Tracker": t})

        # Extract Third-Party Libraries
        third_party = data.get("third_party_libraries", [])
        for tp in third_party:
            third_party_data.append({"App": app_name, "ThirdParty": tp})

        print(f"Processed {idx}/{total_files}: {app_name}")

    except Exception as e:
        print(f"Error processing {file}: {e}")

# Convert to DataFrames
df_permissions = pd.DataFrame(permissions_data)
df_trackers = pd.DataFrame(trackers_data)
df_third_party = pd.DataFrame(third_party_data)

# ====== 1. Permissions Report ======
if not df_permissions.empty:
    perm_summary = df_permissions["Permission"].value_counts()
    perm_summary.to_csv(os.path.join(OUTPUT_DIR, "permissions_summary.csv"))

    plt.figure(figsize=(12,6))
    perm_summary.head(20).plot(kind="bar")
    plt.title("Top 20 Permissions Used Across Apps")
    plt.ylabel("Number of Apps")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "permissions_summary.png"))
    plt.close()
else:
    print("⚠️ No permissions data found in JSON reports.")

# ====== 2. Trackers Report ======
if not df_trackers.empty:
    tracker_summary = df_trackers["Tracker"].value_counts()
    tracker_summary.to_csv(os.path.join(OUTPUT_DIR, "trackers_summary.csv"))

    plt.figure(figsize=(12,6))
    tracker_summary.head(20).plot(kind="bar")
    plt.title("Top 20 Trackers Used Across Apps")
    plt.ylabel("Number of Apps")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "trackers_summary.png"))
    plt.close()
else:
    print("⚠️ No trackers data found in JSON reports.")

# ====== 3. Third-Party Access Report ======
if not df_third_party.empty:
    third_party_summary = df_third_party["ThirdParty"].value_counts()
    third_party_summary.to_csv(os.path.join(OUTPUT_DIR, "third_party_summary.csv"))

    plt.figure(figsize=(12,6))
    third_party_summary.head(20).plot(kind="bar")
    plt.title("Top 20 Third-Party Libraries Used Across Apps")
    plt.ylabel("Number of Apps")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "third_party_summary.png"))
    plt.close()
else:
    print("⚠️ No third-party library data found in JSON reports.")

print("✅ Summary reports generated successfully in:", OUTPUT_DIR)

