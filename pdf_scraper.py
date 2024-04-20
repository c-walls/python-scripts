#!/usr/bin/env python3

import os
import sys
import re
import unicodedata
from PyPDF4 import PdfFileReader
from pdf2jpg import pdf2jpg
import pytesseract
from tqdm import tqdm

# Setting the Tesseract path
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Update this path if necessary

input_file = sys.argv[1]
if not input_file.endswith((".pdf")):
    print("Please provide a PDF file as input.")
    sys.exit()

# Get the base name of the file without the extension
base_name = os.path.splitext(os.path.basename(input_file))[0]

def pdf_to_txt(input_file):

    # Opening the PDF file and creating a reader object
    pdf_file = open(input_file, "rb")
    pdf_reader = PdfFileReader(pdf_file)

    # Initialize tqdm with the total number of pages
    progress_bar = tqdm(total=pdf_reader.getNumPages(), desc="Converting PDF to Text")

    # Convert the PDF to a list of images
    outputpath = "temp_images"
    result = pdf2jpg.convert_pdf2jpg(input_file, outputpath, dpi=300, pages="ALL")

    # Get the directory containing the images
    image_dir = result[0]["output_pdfpath"]

    # Get the list of image files and sort them
    image_files = sorted(os.listdir(image_dir), key=lambda x: int(x.split('_')[0]))

    # Loop through the images and process them with Tesseract
    text = ""
    for image_file in image_files:
        # Construct the path to the image file
        image_path = os.path.join(image_dir, image_file)
        # Extract the text from the image using Tesseract
        page_text = pytesseract.image_to_string(image_path)
        # Append the text to the final text
        text += page_text.strip() + " \n\n###@@@###"

        # Update the progress bar
        progress_bar.update(1)

    # Clean the completed text
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    text = re.sub('###@@@###.{0,40}\n', '', text)
    text = re.sub('###@@@###.{0,40}(\d{1,4})', '', text)
    text = text.replace('\r', '').replace('\n', ' ')
    text = text.replace('- ', '')
    text = re.sub('\s{3,}', '.  ', text)
    text = re.sub('###@@@###$', '', text)
    text = re.sub(r'([.!?])  ', r'\1\n\n', text)
    text = text.replace('\ne ', '\n- ')
    text = text.replace('  ', ' ')
    text = text.replace('..', '.')

    # Close the tqdm progress bar
    progress_bar.close()

    # Closing the PDF file
    pdf_file.close()

    # Saving the text to a .txt file
    text_file = base_name + ".txt"
    with open(text_file, "w") as f:
        f.write(text)

    # Clean up the temporary image files
    for image_file in image_files:
        os.remove(os.path.join(image_dir, image_file))
    os.rmdir(image_dir)

    print("Temporary image files deleted")
    print(f"Text file saved as {text_file}")

    return text_file

pdf_to_txt(input_file)