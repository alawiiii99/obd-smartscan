import csv
from datetime import datetime

with open("obd_data_version4_injected_clean.csv", "r") as infile, open("obd_data_fixed.csv", "w", newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for row in reader:
        if len(row) >= 28:
            try:
                # Parse U.S. style date (4/1/2024) and reformat
                dt = datetime.strptime(row[27].strip(), "%m/%d/%Y")
                row[27] = dt.strftime("%Y-%m-%d 00:00:00")
            except Exception as e:
                print(f"Row skipped or already OK: {row[27]} -> {e}")
        writer.writerow(row)
