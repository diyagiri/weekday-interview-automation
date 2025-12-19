import os
import requests
from datetime import datetime, timezone

AIRTABLE_PAT = os.environ["AIRTABLE_PAT"]
BASE_ID = os.environ["AIRTABLE_BASE_ID"]
TABLE = os.environ.get("AIRTABLE_TABLE_NAME", "Interview_Rounds")

MAILERSEND_API_KEY = os.environ["MAILERSEND_API_KEY"]
FROM_EMAIL = os.environ["FROM_EMAIL"]
FROM_NAME = os.environ.get("FROM_NAME", "Weekday Interviews")

AIRTABLE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE}"

def airtable_headers():
    return {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json",
    }

def mailersend_headers():
    return {
        "Authorization": f"Bearer {MAILERSEND_API_KEY}",
        "Content-Type": "application/json",
    }

def fetch_pending_records(max_records=25):
    params = {
        "filterByFormula": "{Mail Status}='Pending'",
        "maxRecords": max_records
    }
    r = requests.get(AIRTABLE_URL, headers=airtable_headers(), params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("records", [])

def update_record(record_id, fields):
    r = requests.patch(
        f"{AIRTABLE_URL}/{record_id}",
        headers=airtable_headers(),
        json={"fields": fields},
        timeout=30
    )
    r.raise_for_status()

def send_email(to_email, to_name, round_name, calendly_link):
    subject = f"Interview Invitation – {round_name}"
    body = (
        f"Hi {to_name or 'there'},\n\n"
        f"You have been invited for {round_name}.\n\n"
        f"Please book a suitable slot using the Calendly link below:\n"
        f"{calendly_link}\n\n"
        f"Best regards,\n{FROM_NAME}"
    )

    payload = {
        "from": {"email": FROM_EMAIL, "name": FROM_NAME},
        "to": [{"email": to_email, "name": to_name}],
        "subject": subject,
        "text": body,
    }

    return requests.post(
        "https://api.mailersend.com/v1/email",
        headers=mailersend_headers(),
        json=payload,
        timeout=30
    )

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def main():
    records = fetch_pending_records()
    if not records:
        print("No pending emails.")
        return

    for rec in records:
        rid = rec["id"]
        f = rec.get("fields", {})

        email = (f.get("Candidate Email") or "").strip()
        name = (f.get("Candidate") or "").strip()
        round_name = (f.get("Rounds") or "").strip()
        link = (f.get("Calendly Link") or "").strip()

        if not email or not link:
            update_record(rid, {
                "Mail Status": "Failed",
                "Error": "Missing email or Calendly link"
            })
            continue

        try:
            resp = send_email(email, name, round_name, link)
            if resp.ok:
                update_record(rid, {
                    "Mail Status": "Sent",
                    "Mail Sent Time": now_iso(),
                    "Error": ""
                })
                print(f"Sent → {email}")
            else:
                update_record(rid, {
                    "Mail Status": "Failed",
                    "Error": f"{resp.status_code}: {resp.text[:300]}"
                })
        except Exception as e:
            update_record(rid, {
                "Mail Status": "Failed",
                "Error": str(e)[:300]
            })

if __name__ == "__main__":
    main()
