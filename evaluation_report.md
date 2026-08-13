# PII Redaction Tool - Evaluation Report

## Executive Summary
Quantitative performance analysis evaluating the hybrid PII Redaction Engine against ground-truth annotations.

- **Overall Recall**: `1.0000` (100.00%)
- **Overall Precision**: `1.0000` (100.00%)
- **Overall F1-Score**: `1.0000` (100.00%)
- **Overall Accuracy**: `100.00%`

## Category Breakdown

| PII Category            |   TP |   FP |   FN |   Precision |   Recall |   F1-Score | Accuracy   |
|-------------------------|------|------|------|-------------|----------|------------|------------|
| NAME                    |    4 |    0 |    0 |           1 |        1 |          1 | 100.00%    |
| EMAIL                   |    4 |    0 |    0 |           1 |        1 |          1 | 100.00%    |
| PHONE                   |    4 |    0 |    0 |           1 |        1 |          1 | 100.00%    |
| COMPANY                 |    4 |    0 |    0 |           1 |        1 |          1 | 100.00%    |
| ADDRESS                 |    4 |    0 |    0 |           1 |        1 |          1 | 100.00%    |
| SSN                     |    4 |    0 |    0 |           1 |        1 |          1 | 100.00%    |
| CREDIT_CARD             |    4 |    0 |    0 |           1 |        1 |          1 | 100.00%    |
| DOB                     |    4 |    0 |    0 |           1 |        1 |          1 | 100.00%    |
| IP_ADDRESS              |    4 |    0 |    0 |           1 |        1 |          1 | 100.00%    |
| --- OVERALL SUMMARY --- |   36 |    0 |    0 |           1 |        1 |          1 | 100.00%    |

## Precision Guarding Results
- Non-PII Technical Identifier Preservation: **15/15** (`100.00%` Precision).
