import os
import datetime
import sys
from tqdm import tqdm
from PyPDF2 import PdfReader

### This script generates a log file containing the titles and number of pages of all PDF files in a directory. ###

def create_pdf_log(directory):
    total_files = 0
    total_pages = 0
    current_date = datetime.datetime.now().strftime("%m-%d-%Y")
    log_file_name = f"pdf_log_{current_date}.txt"
    log_file_path = os.path.join(directory, log_file_name)
    
    # Get the list of PDF files in the directory
    pdf_files = [file for file in os.listdir(directory) if file.endswith(".pdf")]
    
    with open(log_file_path, "w", encoding="utf-8") as log_file:
        for pdf_file in tqdm(pdf_files, desc="Processing PDF files"):
            # Get the title of the PDF file
            title = os.path.splitext(pdf_file)[0].replace("_", " ")
            
            # Get the number of pages in the PDF file
            pdf_path = os.path.join(directory, pdf_file)
            with open(pdf_path, "rb") as file:
                pdf = PdfReader(file)
                num_pages = len(pdf.pages)
            
            # Write the title and number of pages to the log file
            log_file.write(f"{title} ({num_pages} pages)\n")

            # Update counters
            total_files += 1
            total_pages += num_pages
        
        # Calculate average number of pages
        avg_pages = total_pages / total_files if total_files > 0 else 0

        # Write summary to the log file
        log_file.write("\n\n")
        log_file.write(f"Total number of files: {total_files}\n")
        log_file.write(f"Total number of pages: {total_pages}\n")
        log_file.write(f"Average number of pages: {avg_pages:.2f}\n")

        print("PDF log created successfully.")

if len(sys.argv) > 1:
    directory_path = sys.argv[1]
    create_pdf_log(directory_path)
else:
    print("Please provide a directory path as a command-line argument.")