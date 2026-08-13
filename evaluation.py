"""
PII Anonymization Performance & Evaluation Suite
=================================================
Automated ground-truth validation runner. Calculates Confusion Matrix (TP, FP, FN, TN),
Recall, Precision, Accuracy, and F1-Scores for PII detection engines.
"""

import json
import os
from tabulate import tabulate
from pii_redactor import PIIAnonymizerEngine
from dataset_generator import AUDIT_CORPUS_BLOCKS


class RedactionEvaluator:
    """Evaluates anonymization engine performance against ground-truth datasets."""

    def __init__(self):
        self.engine = PIIAnonymizerEngine()
        self.categories = ["NAME", "EMAIL", "PHONE", "COMPANY", "ADDRESS", "SSN", "CREDIT_CARD", "DOB", "IP_ADDRESS"]

    def execute_evaluation(self):
        """Runs validation against annotations and computes statistical metrics."""
        work_dir = os.path.dirname(os.path.abspath(__file__))
        gt_path = os.path.join(work_dir, "ground_truth.json")

        with open(gt_path, "r", encoding="utf-8") as f:
            annotations = json.load(f)

        confusion_table = {c: {"TP": 0, "FP": 0, "FN": 0, "TN": 0} for c in self.categories}
        confusion_table["NON_PII"] = {"TP": 0, "FP": 0, "FN": 0, "TN": 0}

        for block in AUDIT_CORPUS_BLOCKS:
            if "ticket_id" not in block:
                continue

            t_id = block["ticket_id"]
            raw_text = block["text"]

            gt_pii_items = [a for a in annotations if a["ticket_id"] == t_id and a["type"] != "NON_PII"]
            gt_non_pii_items = [a for a in annotations if a["ticket_id"] == t_id and a["type"] == "NON_PII"]

            detected_spans = self.engine.locate_pii_entities(raw_text)
            detected_vals = [sp.raw_value.strip() for sp in detected_spans]

            # 1. Evaluate PII Detection (Recall & True Positives)
            for item in gt_pii_items:
                val = item["value"].strip()
                cat = item["type"]

                is_detected = any(val.lower() in d.lower() or d.lower() in val.lower() for d in detected_vals)
                if is_detected:
                    confusion_table[cat]["TP"] += 1
                else:
                    confusion_table[cat]["FN"] += 1

            # 2. Evaluate Non-PII Technical ID Guarding (Precision & False Positives)
            for non_item in gt_non_pii_items:
                non_val = non_item["value"].strip()
                erroneously_masked = any(non_val.lower() in d.lower() for d in detected_vals)
                if erroneously_masked:
                    confusion_table["NON_PII"]["FP"] += 1
                else:
                    confusion_table["NON_PII"]["TN"] += 1

        # Calculate metrics
        row_records = []
        tot_tp = tot_fp = tot_fn = 0
        tot_tn = sum(confusion_table[c]["TN"] for c in confusion_table)

        for c in self.categories:
            tp = confusion_table[c]["TP"]
            fp = confusion_table[c]["FP"]
            fn = confusion_table[c]["FN"]
            tn = confusion_table[c]["TN"]

            prec = tp / (tp + fp) if (tp + fp) > 0 else 1.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 1.0
            f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
            acc = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 1.0

            tot_tp += tp
            tot_fp += fp
            tot_fn += fn

            row_records.append([
                c, tp, fp, fn,
                f"{prec:.4f}", f"{rec:.4f}", f"{f1:.4f}", f"{acc * 100:.2f}%"
            ])

        overall_prec = tot_tp / (tot_tp + tot_fp) if (tot_tp + tot_fp) > 0 else 1.0
        overall_rec = tot_tp / (tot_tp + tot_fn) if (tot_tp + tot_fn) > 0 else 1.0
        overall_f1 = (2 * overall_prec * overall_rec) / (overall_prec + overall_rec) if (overall_prec + overall_rec) > 0 else 0.0
        overall_acc = (tot_tp + tot_tn) / (tot_tp + tot_tn + tot_fp + tot_fn) if (tot_tp + tot_tn + tot_fp + tot_fn) > 0 else 1.0

        row_records.append([
            "--- OVERALL SUMMARY ---", tot_tp, tot_fp, tot_fn,
            f"{overall_prec:.4f}", f"{overall_rec:.4f}", f"{overall_f1:.4f}", f"{overall_acc * 100:.2f}%"
        ])

        headers = ["PII Category", "TP", "FP", "FN", "Precision", "Recall", "F1-Score", "Accuracy"]
        formatted_table = tabulate(row_records, headers=headers, tablefmt="github")

        print("\n" + "=" * 65)
        print("         PII REDACTION ENGINE - PERFORMANCE EVALUATION         ")
        print("=" * 65 + "\n")
        print(formatted_table)
        print("\n" + "-" * 65)
        non_pii_total = confusion_table['NON_PII']['TN'] + confusion_table['NON_PII']['FP']
        guard_prec = (confusion_table['NON_PII']['TN'] / non_pii_total) * 100 if non_pii_total > 0 else 100.0
        print(f"Technical Identifier Guarding Precision (Preserved Non-PII):")
        print(f"  True Negatives (Preserved intact): {confusion_table['NON_PII']['TN']}")
        print(f"  False Positives (Mistakenly redacted): {confusion_table['NON_PII']['FP']}")
        print(f"  Guard Clause Precision: {guard_prec:.2f}%")
        print("-" * 65 + "\n")

        # Save markdown report
        md_report_path = os.path.join(work_dir, "evaluation_report.md")
        with open(md_report_path, "w", encoding="utf-8") as f:
            f.write("# PII Redaction Tool - Evaluation Report\n\n")
            f.write("## Executive Summary\n")
            f.write("Quantitative performance analysis evaluating the hybrid PII Redaction Engine against ground-truth annotations.\n\n")
            f.write(f"- **Overall Recall**: `{overall_rec:.4f}` ({overall_rec * 100:.2f}%)\n")
            f.write(f"- **Overall Precision**: `{overall_prec:.4f}` ({overall_prec * 100:.2f}%)\n")
            f.write(f"- **Overall F1-Score**: `{overall_f1:.4f}` ({overall_f1 * 100:.2f}%)\n")
            f.write(f"- **Overall Accuracy**: `{overall_acc * 100:.2f}%`\n\n")
            f.write("## Category Breakdown\n\n")
            f.write(formatted_table)
            f.write("\n\n## Precision Guarding Results\n")
            f.write(f"- Non-PII Technical Identifier Preservation: **{confusion_table['NON_PII']['TN']}/{non_pii_total}** (`{guard_prec:.2f}%` Precision).\n")

        print(f"Evaluation report generated -> {md_report_path}")


if __name__ == "__main__":
    evaluator = RedactionEvaluator()
    evaluator.execute_evaluation()
