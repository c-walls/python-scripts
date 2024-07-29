import os
from PyPDF2 import PdfReader
import sys
from tqdm import tqdm
import re

### This script extracts text from all PDF files in a directory and saves it to a single text file. ###

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    text = re.sub(r'(?<![.!?])\n', ' ', text)
    return text

def main(input_folder):
    output_file = os.path.join(input_folder, os.path.basename(input_folder) + ".txt")
    with open(output_file, "w", encoding="utf-8") as out_file:
        for root, dirs, files in os.walk(input_folder):
            for file in tqdm(files, desc="Processing files"):
                if file.endswith(".pdf"):
                    pdf_path = os.path.join(root, file)
                    text = extract_text_from_pdf(pdf_path)
                    out_file.write(f"\n\n--- Start of {file} ---\n\n")
                    out_file.write(text)
                    out_file.write(f"\n\n--- End of {file} ---\n\n")

if len(sys.argv) != 2:
    print("Usage: python script.py <input_folder>")
    sys.exit(1)
else:
    input_folder = sys.argv[1]
    main(input_folder)
    print("Text extracted and saved to", os.path.basename(input_folder) + ".txt")