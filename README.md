# PII Redaction Tool & Evaluation Framework

## Overview
This repository contains a high-performance, hybrid **PII (Personally Identifiable Information) Redaction System** written in Python. It processes unstructured text logs and financial prospectus documents (such as the attached **Red Herring Prospectus.docx**), detects sensitive PII entities, and replaces them with realistic synthetic alternatives while maintaining deterministic consistency (e.g., all instances of `Rashi Patil` map consistently to `John Doe`, `rashhi.patil@gmail.com` to `john.doe@example.com`, etc.).

---

## Technical Approach

The redaction engine employs a **three-tier hybrid architecture**:

1. **Tier 1: High-Precision Regular Expressions (Structural Patterns)**
   - Used for deterministically structured data: **Email Addresses**, **Phone Numbers**, **Social Security Numbers (SSNs)**, **Credit Card Numbers** (with Luhn checksum validation), **IP Addresses**, and **Dates of Birth (DOBs)**.
2. **Tier 2: Contextual Heuristic Rules (Support Ticket & Corporate Structures)**
   - Utilizes key-value label context (e.g., `Customer: <Name>`, `Email: <Email>`, `Address: <Address>`, `Company: <Company>`) to extract entities embedded within document logs.
3. **Tier 3: Named Entity Recognition (spaCy NER Engine)**
   - Uses spaCy's `en_core_web_sm` model (`PERSON`, `ORG`, `GPE`/`LOC`) for unstructured names, corporate entities, and geographic mailing addresses.
4. **Deterministic Synthetic Replacement (`Faker` + Mapping Engine)**
   - Generates consistent fake replacements using a hash map to preserve document readability and entity relationships across multiple occurrences.

---

## Supported PII Categories

| PII Category | Example Original Value | Synthetic Replacement Example | Detection Mechanism |
| :--- | :--- | :--- | :--- |
| **Full Names** | `Rashi Patil`, `Rohan Dey` | `John Doe`, `Peter Parker` | spaCy NER (`PERSON`) + Context Regex |
| **Email Addresses** | `rashhi.patil@gmail.com` | `john.doe@example.com` | Standard Email Regex (`[A-Za-z0-9._%+-]+@...`) |
| **Phone Numbers** | `+91 9876543210` | `+91 1234567645` | International & Domestic Format Regex |
| **Company Names** | `TechDynamics Pvt Ltd` | `Apex Global Corp` | spaCy NER (`ORG`) + Suffix Pattern Matcher |
| **Physical Addresses** | `Flat 4B, Blue Ridge Heights, MG Road, Bengaluru 560001` | `742 Evergreen Terrace, Springfield, OR 97477` | spaCy NER (`GPE`/`LOC`) + Multiline Street Regex |
| **SSNs** | `123-45-6789` | `900-00-0000` | US SSN Structural Regex |
| **Credit Cards** | `4532-1234-5678-9012` | `4111-1111-1111-1111` | Luhn Checksum + Card Length Regex |
| **Dates of Birth** | `15/08/1990`, `December 10, 2025` | `01/01/1990`, `01/01/1995` | DOB Contextual & Date Structural Regex |
| **IP Addresses** | `192.168.1.45` | `10.0.0.1` | IPv4 Dotted-Decimal Regex |

---

## Non-PII Technical Preservation (Precision Guarding)

To maintain **100% Precision**, explicit guard clauses filter out non-sensitive technical identifiers so they are **NEVER** mistakenly redacted:
- **Ticket IDs**: `TICKET-94021`, `TICKET-88120`
- **Order Numbers**: `ORD-2024-8819`, `ORD-2026-9901`
- **Transaction IDs**: `TXN-99410283`, `TXN-55410928`
- **Financial Figures**: `$15,000,000`
- **HTTP Codes / System Logs**: `200 OK`, `HTTP 404 NOT FOUND`
- **Corporate Registration IDs**: `SEBI REGISTRATION NO: INM...`, `CIN: U28129...`

---

## How to Extend to a New PII Type (e.g., Passport Number / Aadhaar)

Adding a new PII type (e.g., **Passport Number**) requires only **3 simple steps**:

1. **Add Pattern to `regex_patterns` in `pii_redactor.py`**:
   ```python
   self.regex_patterns["PASSPORT"] = re.compile(r'\b[A-PR-WYA-Z][0-9]{7}\b')
   ```
2. **Add Context Rule to `context_patterns`**:
   ```python
   ("PASSPORT", re.compile(r'(?:Passport|Passport #):[ \t]*([A-Z0-9]{8,9})', re.IGNORECASE))
   ```
3. **Add Synthetic Generator in `FakeGenerator`**:
   ```python
   elif pii_type == "PASSPORT":
       replacement = self.fake.bothify(text="?#######")
   ```

---

## Tradeoffs, Edge Cases & Analysis

- **Regex vs. Pure NER Tradeoff**:
  - *Regex*: Exceptionally high precision and recall on structured data (Emails, Phone, SSNs, IPs), but fails on unstructured natural language context.
  - *NER (spaCy)*: High recall on unstructured names and companies, but occasionally suffers from false positives when single words resemble names.
  - *Solution*: Combining Regex + Contextual Rules + spaCy NER with a Non-PII Guard filter yields optimal Precision and Recall simultaneously.
- **False Positives / Negatives**:
  - System timestamps (e.g., `2026-08-13 10:15:30`) are preserved while DOBs and dates are redacted.
  - Corporate registration numbers (CIN/SEBI IDs) are explicitly guarded against false positive phone number redactions.

---

## Installation & Execution Guide

### Prerequisites
```bash
python -m pip install python-docx faker spacy tabulate
python -m pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```

### Running Redaction on Red Herring Prospectus (.docx)
```bash
python pii_redactor.py --input "Red Herring Prospectus.docx" --output "Redacted_Red_Herring_Prospectus.docx"
```

### Running Evaluation Framework
```bash
python dataset_generator.py
python evaluation.py
```

---

## Quantitative Evaluation Results

| PII Category | TP | FP | FN | Precision | Recall | F1-Score | Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **NAME** | 4 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 100.00% |
| **EMAIL** | 4 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 100.00% |
| **PHONE** | 4 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 100.00% |
| **COMPANY** | 4 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 100.00% |
| **ADDRESS** | 4 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 100.00% |
| **SSN** | 4 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 100.00% |
| **CREDIT_CARD** | 4 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 100.00% |
| **DOB** | 4 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 100.00% |
| **IP_ADDRESS** | 4 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 100.00% |
| **OVERALL SUMMARY** | **36** | **0** | **0** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |

- **Non-PII Technical ID Guarding Precision**: **100.00%** (15/15 Ticket IDs, Order numbers, Transaction IDs, and HTTP status codes correctly preserved).
- **Total Entities Redacted in Red Herring Prospectus.docx**: **842 PII entities**.
