#!/usr/bin/env python3
import os
import sys
import time
import json
import zipfile
import argparse
import requests

# -------------------------
# CONFIG - use your values
# -------------------------
MOBSF_URL = "http://129.219.60.5:8000"   # MobSF host
API_KEY   = "f510bd5ddf94a5244b34990348df020fbf98913da7583da06213ffc03294fb3f"
APK_DIR   = "/mnt/data/projects/HealthApps/android/base_apks"
REPORT_DIR= "/mnt/data/projects/HealthApps/mobsf_reports"
HEADERS   = {"Authorization": API_KEY}

# -------------------------
# Helpers
# -------------------------
def is_valid_apk(path):
    """Return True if file is a valid ZIP-like APK containing AndroidManifest.xml"""
    try:
        with zipfile.ZipFile(path, 'r') as z:
            return "AndroidManifest.xml" in z.namelist()
    except Exception:
        return False

def upload_apk(path):
    print(f"[+] Uploading {path}")
    try:
        with open(path, "rb") as f:
            files = {"file": (os.path.basename(path), f, "application/vnd.android.package-archive")}
            r = requests.post(f"{MOBSF_URL}/api/v1/upload", files=files, headers=HEADERS, timeout=60)
    except Exception as e:
        print(f"    -> HTTP error during upload: {e}")
        return None, None

    print(f"    -> HTTP {r.status_code}")
    # try parse JSON to see exact error
    try:
        rj = r.json()
    except Exception:
        print("    -> Non-JSON response (first 400 chars):")
        print(r.text[:400])
        return None, None

    if r.status_code != 200:
        print("    -> Upload returned non-200:", rj)
        return None, rj

    if "error" in rj:
        print("    -> Upload returned error:", rj)
        return None, rj

    # expected: { "analyzer": "...", "status":"success", "hash":"<hash>" ...}
    scan_hash = rj.get("hash")
    return scan_hash, rj

def start_scan(scan_hash):
    print("    -> Starting scan...")
    try:
        r = requests.post(f"{MOBSF_URL}/api/v1/scan", headers=HEADERS, data={"hash": scan_hash, "scan_type":"apk"}, timeout=120)
        print("    -> scan HTTP", r.status_code)
        return r.status_code == 200
    except Exception as e:
        print("    -> scan request failed:", e)
        return False

def fetch_report(scan_hash, out_json, out_pdf, tries=30, sleep_s=3):
    for i in range(tries):
        try:
            r = requests.post(f"{MOBSF_URL}/api/v1/report_json", headers=HEADERS, data={"hash": scan_hash}, timeout=60)
        except Exception as e:
            print("    -> report_json HTTP error:", e)
            time.sleep(sleep_s)
            continue

        if r.status_code != 200:
            print(f"    -> report_json returned HTTP {r.status_code} (try {i+1}/{tries})")
            print("       body:", (r.text[:400] + "...") if r.text else "<no body>")
            time.sleep(sleep_s)
            continue

        # parse JSON
        try:
            jr = r.json()
        except Exception:
            print("    -> report_json returned non-json (try {}/{}).".format(i+1, tries))
            time.sleep(sleep_s)
            continue

        # MobSF often replies {"report":"Report not Found"} while processing
        if isinstance(jr, dict) and jr.get("report") == "Report not Found":
            print(f"    -> report not ready (try {i+1}/{tries})")
            time.sleep(sleep_s)
            continue

        # Looks good — save JSON
        with open(out_json, "w") as fh:
            json.dump(jr, fh, indent=2)
        print("    -> JSON saved:", out_json)

        # attempt PDF
        try:
            rp = requests.post(f"{MOBSF_URL}/api/v1/download_pdf", headers=HEADERS, data={"hash": scan_hash}, timeout=120)
            if rp.status_code == 200 and rp.content:
                with open(out_pdf, "wb") as pf:
                    pf.write(rp.content)
                print("    -> PDF saved:", out_pdf)
            else:
                print("    -> PDF not available (HTTP", rp.status_code, ")")
        except Exception as e:
            print("    -> download_pdf error:", e)
        return True

    return False

def process_apk(path):
    print("\n=== PROCESS ===")
    print("File:", path)
    if not os.path.isfile(path):
        print(" -> SKIP: not a file.")
        return

    if not path.endswith(".apk"):
        print(" -> SKIP: not .apk")
        return

    if not is_valid_apk(path):
        print(" -> SKIP: not a valid APK (not ZIP or missing AndroidManifest.xml)")
        return

    scan_hash, upload_info = upload_apk(path)
    if not scan_hash:
        print(" -> Upload failed; server response:")
        print(json.dumps(upload_info, indent=2) if upload_info else "<no json>")
        return

    # start scan
    ok = start_scan(scan_hash)
    if not ok:
        print(" -> Scan kickoff failed (but will still attempt to fetch report).")

    # fetch report (poll)
    base = os.path.basename(path)
    json_out = os.path.join(REPORT_DIR, base + ".json")
    pdf_out  = os.path.join(REPORT_DIR, base + ".pdf")
    ok = fetch_report(scan_hash, json_out, pdf_out)
    if not ok:
        print(" -> Report not retrieved after retries for hash", scan_hash)

# -------------------------
# MAIN
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="MobSF scanner helper")
    parser.add_argument("--apk-dir", default=APK_DIR)
    parser.add_argument("--report-dir", default=REPORT_DIR)
    parser.add_argument("--single", help="path to single apk to scan (for testing)")
    args = parser.parse_args()

    # create report dir if possible
    os.makedirs(args.report_dir, exist_ok=True)

    if args.single:
        process_apk(args.single)
        return

    if not os.path.isdir(args.apk_dir):
        print("APK directory not found:", args.apk_dir)
        return

    files = sorted(os.listdir(args.apk_dir))
    for fn in files:
        if fn.endswith(".apk"):
            process_apk(os.path.join(args.apk_dir, fn))

if __name__ == "__main__":
    main()
