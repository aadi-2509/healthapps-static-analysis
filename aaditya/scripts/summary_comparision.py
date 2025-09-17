import os
import pandas as pd
import matplotlib.pyplot as plt

# Paths
old_dir = "/mnt/data/projects/HealthApps/summary_reports"
new_dir = "/mnt/data/projects/HealthApps/summary_reports_new_apps"
output_dir = "/mnt/data/projects/HealthApps/summary_comparison"

# Ensure output folder exists
os.makedirs(output_dir, exist_ok=True)

def compare_reports(file_name, key_col):
    """Compare old vs new summary CSVs based on a key column (Permission, Tracker, Library)."""
    old_path = os.path.join(old_dir, file_name)
    new_path = os.path.join(new_dir, file_name)

    if not (os.path.exists(old_path) and os.path.exists(new_path)):
        print(f"Skipping {file_name}, not found in both directories")
        return None

    # Load CSVs
    old_df = pd.read_csv(old_path)
    new_df = pd.read_csv(new_path)

    # Rename count columns
    old_df.rename(columns={"count": "old_count"}, inplace=True)
    new_df.rename(columns={"count": "new_count"}, inplace=True)

    # Merge on the key column
    merged = pd.merge(old_df, new_df, on=key_col, how="outer").fillna(0)

    # Save comparison CSV
    out_csv = os.path.join(output_dir, f"{file_name.replace('.csv','')}_comparison.csv")
    merged.to_csv(out_csv, index=False)
    print(f"Comparison saved: {out_csv}")

    # Plot histogram
    plt.figure(figsize=(12,6))
    x = range(len(merged[key_col]))
    plt.bar([i - 0.2 for i in x], merged["old_count"], width=0.4, label="Old")
    plt.bar([i + 0.2 for i in x], merged["new_count"], width=0.4, label="New")
    plt.xticks(x, merged[key_col], rotation=90)
    plt.xlabel(key_col)
    plt.ylabel("Count")
    plt.title(f"{key_col} Comparison (Old vs New)")
    plt.legend()
    plt.tight_layout()

    out_png = os.path.join(output_dir, f"{file_name.replace('.csv','')}_comparison.png")
    plt.savefig(out_png)
    plt.close()
    print(f"Histogram saved: {out_png}")

# Run comparisons
compare_reports("permissions_summary.csv", "Permission")
compare_reports("trackers_summary.csv", "Tracker")
compare_reports("thirdparty_summary.csv", "Library")  # adjust key_col if needed

