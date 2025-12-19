# Weekday – Interview Scheduling Automation

This repository contains an end-to-end automated workflow designed to streamline interview scheduling and communication for candidates, as part of the Weekday (YC W21) coding assignment.

The solution integrates **Airtable**, **MailerSend**, and **automation scripts** to handle data cleaning, interview invite emails, and turnaround time (TAT) calculation.

---

## 📌 Project Overview

The workflow performs the following:

1. Cleans and normalizes interview scheduling data  
2. Splits multiple interview rounds into individual records  
3. Sends interview invitation emails with round-specific Calendly links  
4. Logs email send timestamps  
5. Computes Turnaround Time (TAT) for interview scheduling  

---

## 🧩 Tasks & Implementation

### **Task 1 – Data Splitting (Airtable Script)**

**Problem:**  
Some candidates have multiple interview rounds stored in a single row.

**Solution:**  
An Airtable Scripting Extension script:
- Parses the “Scheduling method” field  
- Splits each interview round into a **separate row**  
- Preserves all candidate and interviewer metadata  
- Associates the correct Calendly link with each round  

📁 Script location:
```
/task1_split_interview_rounds.js
```

> ⚠️ Note: This script is designed to run **inside Airtable’s Scripting Extension**, not locally.

---

### **Task 2 – MailerSend Integration (Automation Script)**

**Problem:**  
Automate interview invitation emails with round-specific details.

**Solution:**  
A Python script integrated with:
- Airtable REST API (to fetch pending records)
- MailerSend API (to send emails)

Each email includes:
- Company name  
- Interview round  
- Interviewer name and email  
- Calendly scheduling link  

The script:
- Processes records in **bounded batches**
- Updates `Mail Status` and `Mail Sent Time`
- Avoids duplicate sends by filtering on record state (`Pending` → `Sent`)

📁 Script location:
```
send_invites.py
```

---

### **Why Only 5 Emails Were Sent**

MailerSend trial accounts enforce strict sending limits.

To ensure:
- Ethical handling of candidate data  
- No unintended mass outreach  
- Compliance with trial constraints  

The automation was **validated on a small batch (5 records)**.

> The workflow is fully scalable and can be re-run iteratively in batches until no `Pending` records remain.

---

### **Task 3 – TAT (Turnaround Time) Calculation**

**Definition:**
```
TAT = Mail Sent Time – Added On Time
```

**Implementation:**
- `Mail Sent Time` is written automatically when an email is sent
- TAT is calculated using an Airtable **Formula field**

#### TAT Formula (minutes):
```text
IF(
  AND({Mail Sent Time}, {Added On}),
  DATETIME_DIFF({Mail Sent Time}, {Added On}, "minutes"),
  BLANK()
)
```

---

## 🔎 How to View TAT in Airtable

1. Open the `Interview_Rounds` table  
2. Apply a filter:
```
TAT (minutes) → is not empty
```
3. This view shows **only successfully sent interview invites**
4. Records without a successful send intentionally remain blank

---

## 🏗️ Architecture Summary

| Component | Responsibility |
|---------|----------------|
| Airtable | Data storage, formula-based TAT |
| Airtable Script | Data normalization & splitting |
| Python Script | Email automation & timestamps |
| MailerSend | Email delivery |
| GitHub Actions | Automation runner |

---

## ✅ Deliverables Covered

- ✔ Airtable base with split and cleaned data  
- ✔ Airtable script for interview round splitting  
- ✔ MailerSend automation script  
- ✔ TAT calculation field  

---

## 📝 Notes

This solution demonstrates safe, scalable automation practices suitable for real-world recruiting operations.  
Bulk execution can be enabled by increasing batch size and removing trial constraints.
