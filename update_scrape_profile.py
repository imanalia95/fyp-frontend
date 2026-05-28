import requests
import pandas as pd
import time
import os
from config import INPUT_CSV

csv_file = INPUT_CSV

# ----------------------------
# LOAD CSV
# ----------------------------
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    print(f"Loaded dataset: {len(df)} lecturers")
else:
    raise Exception("CSV file not found!")

# ----------------------------
# ENSURE EMAIL COLUMN EXISTS
# ----------------------------
if "email" not in df.columns:
    df["email"] = ""

failed_staff = []

# ----------------------------
# RETRY FUNCTION
# ----------------------------
def fetch_with_retry(url, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Retry {attempt + 1} failed: {e}")
            time.sleep(delay)
    return None

# ----------------------------
# EMAIL FETCH FUNCTION
# ----------------------------
def fetch_email(staff_no):
    try:
        url = f"https://staffcloud.unimas.my/api/v1/public/personDetail/DTO-V2?staffNo={staff_no}"
        response = fetch_with_retry(url)

        if not response:
            return None

        data = response.json()

        # correct nested extraction
        person = data.get("psPersonDetail", {})
        return person.get("email")

    except Exception as e:
        print(f"Email fetch error for {staff_no}: {e}")
        return None

# ----------------------------
# UPDATE LOOP
# ----------------------------
for idx, row in df.iterrows():

    staff_no = str(row["staff_no"])
    existing_email = row["email"]

    # Skip if email already exists
    if isinstance(existing_email, str) and existing_email.strip() != "":
        print("Skipping (already has email):", staff_no)
        continue

    print("Fetching email for:", staff_no)

    email = fetch_email(staff_no)

    if email:
        df.at[idx, "email"] = email
    else:
        failed_staff.append(staff_no)

    time.sleep(0.3)

# ----------------------------
# SAVE CSV
# ----------------------------
df.to_csv(csv_file, index=False)

print("Email update completed!")

# ----------------------------
# LOG FAILURES
# ----------------------------
if failed_staff:
    with open("failed_email.txt", "w") as f:
        for s in failed_staff:
            f.write(s + "\n")

    print("Some emails failed and were saved.")