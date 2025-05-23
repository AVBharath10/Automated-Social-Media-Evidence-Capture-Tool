import sys
import os
from fpdf import FPDF
import datetime

# Get credentials from arguments
if len(sys.argv) != 3:
    print("Usage: python twitter_viewer.py <username> <password>")
    sys.exit(1)

username = sys.argv[1]
password = sys.argv[2]

# Simulate fetching Twitter data (replace with real logic or automation later)
tweets = [
    {
        "date": "2023-05-01",
        "text": "Just setting up my twttr"
    },
    {
        "date": "2023-05-02",
        "text": "Learning Python automation!"
    },
    {
        "date": "2023-05-03",
        "text": "Excited to build cool projects."
    }
]

# Create PDF
output_folder = "output"
os.makedirs(output_folder, exist_ok=True)
output_path = os.path.join(output_folder, "Twitter_Report.pdf")

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=14)
pdf.cell(200, 10, txt=f"Twitter Report for @{username}", ln=True, align="C")
pdf.set_font("Arial", size=10)
pdf.cell(200, 10, txt=f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
pdf.ln(10)

pdf.set_font("Arial", size=12)
for idx, tweet in enumerate(tweets, 1):
    pdf.multi_cell(0, 10, txt=f"{idx}. ({tweet['date']}) {tweet['text']}")

pdf.output(output_path)
print(f"✅ Report generated: {output_path}")
