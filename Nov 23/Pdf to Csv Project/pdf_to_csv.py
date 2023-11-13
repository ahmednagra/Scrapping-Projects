import re
import csv
import sys
from io import StringIO

from pypdf import PdfReader

pdf_file = "input/demo_Extrait.pdf"


# Create a CSV output buffer
csv_output = StringIO()
csv_writer = csv.writer(csv_output)

# Open the PDF file
pdf_reader = PdfReader(pdf_file)

# Loop through all pages in the PDF
for page in pdf_reader.pages:
    text = page.extract_text()

    # Remove Headers Part
    formatted_text = text.split('!Date compta')[1].strip()
    full_text = '!Date compta' + formatted_text

    # Split the text into lines
    lines = full_text.strip().split('\n')

    # Write the header (assuming it's the first line in the text)
    pagenumber = page.page_number
    if pagenumber == 0:
        header = [re.sub(r'\s+', ' ', column.strip()) for column in lines[0].split('!') if column.strip()]
        csv_writer.writerow(header)

    # Iterate through the rest of the lines and write them to the CSV
    for line in lines[2:]:
        line = line.strip('!').strip()
        row = [re.sub(r'\s+', ' ', column.strip()) for column in line.split('!')]
        if any(row) and '------------------------------------------------------------------------------------------------------------------------------------' not in row:
            csv_writer.writerow(row)

# Get the CSV content as a string
csv_content = csv_output.getvalue()

# Optionally, save the CSV content to a file
with open('Bank Statement.csv', 'w', newline='') as csv_file:
    csv_file.write(csv_content)
