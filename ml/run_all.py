"""Run the whole data + ML pipeline in dependency order. Works on Windows, macOS and Linux.
From the project root:   python ml/run_all.py
Steps that need the raw files (cleaning) are skipped automatically when datasets/raw/ has no data - the processed CSVs shipped
in datasets/processed/ are used instead. Prophet is skipped automatically when it is not installed."""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "datasets" / "raw"

STEPS = [  # (script, working dir, needs raw store file, needs raw online file)
    ("datasets/data_cleaning.py", ROOT, "retail_store_inventory.csv", None),
    ("datasets/data_cleaning_segmentation.py", ROOT, None, ("online_retail_II.xlsx", "OnlineRetail.csv")),
    ("datasets/data_quality_report.py", ROOT, None, None),
    ("segmentation.py", ROOT / "ml", None, None),            # must run before churn_models / generate_reports
    ("forecasting_prophet.py", ROOT / "ml", None, None),     # optional: skips itself if prophet is missing
    ("forecasting_models.py", ROOT / "ml", None, None),
    ("recommendations_complete.py", ROOT / "ml", None, None),  # must run before recommendations_combined
    ("recommendations_combined.py", ROOT / "ml", None, None),
    ("churn_setup.py", ROOT / "ml", None, None),
    ("churn_models.py", ROOT / "ml", None, None),
    ("anomaly_detection.py", ROOT / "ml", None, None),
    ("generate_reports.py", ROOT / "ml", None, None),
    ("test_models.py", ROOT / "ml", None, None),
]


def main():
    failed = []
    for script, cwd, raw1, raw2 in STEPS:
        if raw1 and not (RAW / raw1).exists():
            print(f"-- skip {script}: raw/{raw1} not present (using datasets/processed)"); continue
        if raw2 and not any((RAW / f).exists() for f in raw2):
            print(f"-- skip {script}: none of raw/{', '.join(raw2)} present (using datasets/processed)"); continue
        path = ROOT / script if script.startswith("datasets") else cwd / script
        print(f"\n=== {script} ===", flush=True)
        t = time.time()
        rc = subprocess.call([sys.executable, str(path)], cwd=str(cwd))
        print(f"[{'ok' if rc == 0 else 'FAILED'}] {script} ({time.time() - t:.0f}s)")
        if rc != 0:
            failed.append(script)
            if script in ("segmentation.py", "forecasting_models.py"):
                break           # later steps depend on these
    print("\nPipeline finished." if not failed else f"\nFailed steps: {failed}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
