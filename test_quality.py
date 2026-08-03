"""
Contactless Fingerprint Quality Gate Evaluation Suite (test_quality.py)
CORE LAYER — Batch Testing & Performance Budget Verification
"""

import os
import sys
import glob
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from quality_assessment import quality_gate
from generate_test_dataset import main as generate_dataset

# Performance budget SLA targets (ms)
BUDGETS = {
    "blur": 10.0,
    "brightness": 5.0,
    "glare": 10.0,
    "roi": 100.0,
    "ridge": 150.0,
    "total": 300.0
}

def main():
    dataset_dir = "test_dataset"
    if not os.path.exists(dataset_dir) or len(glob.glob(os.path.join(dataset_dir, "*", "*.*"))) == 0:
        print("Dataset missing or incomplete. Auto-generating test dataset...")
        generate_dataset()

    image_files = sorted(glob.glob(os.path.join(dataset_dir, "*", "*.*")))
    if not image_files:
        image_files = sorted(glob.glob(os.path.join("test_images", "*", "*.*")))

    records = []
    cat_counts = {"good": 0, "blurry": 0, "dark": 0, "glare": 0}
    cat_correct = {"good": 0, "blurry": 0, "dark": 0, "glare": 0}
    budget_violations = 0

    for filepath in image_files:
        filename = os.path.basename(filepath)
        category = os.path.basename(os.path.dirname(filepath)).lower()

        res = quality_gate(filepath)
        t_ms = res["timing_ms"]

        is_latency_ok = t_ms["total"] <= BUDGETS["total"]
        if not is_latency_ok:
            budget_violations += 1

        records.append({
            "File Name": filename,
            "Category": category,
            "Passed": res["passed"],
            "Score": res["composite_score"],
            "Blur": res["blur"]["blur_score"],
            "Is Blurry": res["blur"]["is_blurry"],
            "Bright": res["brightness"]["brightness"],
            "Too Dark": res["brightness"]["too_dark"],
            "Too Bright": res["brightness"]["too_bright"],
            "Glare": res["glare"]["glare_fraction"],
            "Has Glare": res["glare"]["has_glare"],
            "ROI": res["roi"]["roi_fraction"],
            "ROI Complete": res["roi"]["roi_complete"],
            "Ridge": res["ridge"]["ridge_score"],
            "Ridges Clear": res["ridge"]["ridges_clear"],
            "Time (ms)": t_ms["total"],
            "SLA Compliant": is_latency_ok,
            "Guidance": res["guidance"]
        })

        if category in cat_counts:
            cat_counts[category] += 1
            if category == "good" and res["passed"]:
                cat_correct[category] += 1
            elif category == "blurry" and res["blur"]["is_blurry"]:
                cat_correct[category] += 1
            elif category == "dark" and (res["brightness"]["too_dark"] or res["brightness"]["too_bright"]):
                cat_correct[category] += 1
            elif category == "glare" and res["glare"]["has_glare"]:
                cat_correct[category] += 1

    df = pd.DataFrame(records)

    print("\n=========================================================================================================")
    print("                      FINGERVISION QUALITY GATE BATCH EVALUATION MATRIX                                  ")
    print("=========================================================================================================\n")
    print(df.to_string(index=False))
    print("\n=========================================================================================================\n")

    csv_path = "test_results.csv"
    df.to_csv(csv_path, index=False)
    print(f"Results exported to: {csv_path}\n")

    print("-------------------------------------------------------------------------")
    print("CATEGORY ACCURACY SUMMARY:")
    for cat in cat_counts:
        count = cat_counts[cat]
        correct = cat_correct[cat]
        pct = (correct / count * 100.0) if count > 0 else 0.0
        print(f"  {cat.upper():<8} : {correct}/{count} correctly identified ({pct:.1f}%)")
    print("-------------------------------------------------------------------------")
    print(f"PERFORMANCE BUDGET SLA (<300ms): {'COMPLIANT (0 violations)' if budget_violations == 0 else f'VIOLATIONS DETECTED ({budget_violations} files)'}")
    print("-------------------------------------------------------------------------\n")

if __name__ == "__main__":
    main()
