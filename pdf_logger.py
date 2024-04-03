import os
import datetime
import sys
from PyPDF2 import PdfFileReader

def create_pdf_log(directory):
    # Get the current date
    current_date = datetime.datetime.now().strftime("%m-%d-%Y")
    
    # Create the log file name
    log_file_name = f"pdf_log_{current_date}.txt"
    
    # Create the log file path
    log_file_path = os.path.join(directory, log_file_name)
    
    # Get the list of PDF files in the directory
    pdf_files = [file for file in os.listdir(directory) if file.endswith(".pdf")]
    
    # Open the log file in write mode
    with open(log_file_path, "w") as log_file:
        # Iterate over the PDF files
        for pdf_file in pdf_files:
            # Get the title of the PDF file
            title = os.path.splitext(pdf_file)[0].replace("_", " ")
            
            # Get the number of pages in the PDF file
            pdf_path = os.path.join(directory, pdf_file)
            with open(pdf_path, "rb") as file:
                pdf = PdfFileReader(file)
                num_pages = pdf.getNumPages()
            
            # Write the title and number of pages to the log file
            log_file.write(f"{title} ({num_pages} pages)\n")

if len(sys.argv) > 1:
    directory_path = sys.argv[1]
    # Call the function to create the PDF log
    create_pdf_log(directory_path)
else:
    print("Please provide a directory path as a command-line argument.")