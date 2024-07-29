#!/usr/bin/env python3
import sys
import io
import re
import pytesseract
from PyPDF4 import PdfFileReader
import gtts
import os
import unicodedata
from tqdm import tqdm
from pydub import AudioSegment
from pdf2jpg import pdf2jpg
from google.cloud import texttospeech

### This script converts a PDF or TXT file to an MP3 audio file using Google Cloud Text-to-Speech API

# Setting the Tesseract path
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

input_file = sys.argv[1]
base_name = os.path.splitext(os.path.basename(input_file))[0]

def pdf_to_txt(input_file, base_name):
    pdf_file = open(input_file, "rb")
    pdf_reader = PdfFileReader(pdf_file)
    progress_bar = tqdm(total=pdf_reader.getNumPages(), desc="Converting PDF to Text")

    outputpath = "temp_images"
    result = pdf2jpg.convert_pdf2jpg(input_file, outputpath, dpi=300, pages="ALL")

    # Create a list of image files
    image_dir = result[0]["output_pdfpath"]
    image_files = sorted(os.listdir(image_dir), key=lambda x: int(x.split('_')[0]))

    # Loop through the images and process them with Tesseract
    text = ""
    for image_file in image_files:
        # Construct the path to the image file
        image_path = os.path.join(image_dir, image_file)
        # Extract the text from the images using Tesseract and join them together
        page_text = pytesseract.image_to_string(image_path)
        text += page_text.strip() + " \n\n###@@@###"
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

    # Close the progress bar and PDF file
    progress_bar.close()
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
    
    return text


def txt_to_audio(text, base_name):
    print(f"Beginning Audio Conversion...")
    
    def split_text_into_chunks(text, max_sentence_length=200, max_bytes=4800):
        sentences = re.split(r'(?<=[.!?]) +', text)
        print(text)
        print(f"Total number of sentences: {len(sentences)}")

        # Split long sentences into smaller ones
        short_sentences = []
        for sentence in sentences:
            while len(sentence) > max_sentence_length:
                # Find the last space within the limit
                space_index = sentence.rfind(' ', 0, max_sentence_length)
                short_sentences.append(sentence[:space_index] + '.')
                sentence = sentence[space_index:]
            short_sentences.append(sentence)

        # Recombine the short sentences into chunks
        chunks = []
        current_chunk = ""

        for sentence in short_sentences:
            # Check if adding the sentence to the current chunk will exceed the limit
            if len((current_chunk + sentence).encode('utf-8')) > max_bytes:
                # If so, add the current chunk to the list and start a new one
                chunks.append(current_chunk)
                current_chunk = sentence + " "
            else:
                current_chunk += sentence + " "

        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    chunks = split_text_into_chunks(text)

    # Authenticate the Google Cloud Text-to-Speech API (Path to your service account key)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_key.json"
    client = texttospeech.TextToSpeechClient()

    # Build the voice request, select the language code ("en-US") and the neural voice
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.MALE, name='en-US-Journey-D')

    # Select the type of audio file you want
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3)

    # Perform the text-to-speech request on each chunk
    audio_chunks = []
    for i in tqdm(range(len(chunks)), desc="Converting text to speech"):
        chunk = chunks[i]
        synthesis_input = texttospeech.SynthesisInput(text=chunk)
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config)

        # Convert the response to an AudioSegment
        audio = AudioSegment.from_file(io.BytesIO(response.audio_content), format="mp3")
        audio_chunks.append(audio)

    # Concatenate the audio chunks into a single file
    combined = sum(audio_chunks, AudioSegment.empty())
    combined.export(f"{base_name}.mp3", format="mp3")
    print(f'Audio content written to file "{base_name}.mp3"')


if not input_file.endswith((".pdf", ".txt")):
    print("Please provide a PDF or TXT file as input.")
    sys.exit()
if input_file.endswith(".pdf"):
    text = pdf_to_txt(input_file, base_name)
elif input_file.endswith(".txt"):
    with open(input_file, "r") as f:
        text = f.read()

    # Clean the text
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    text = re.sub('###@@@###.{0,40}\n', '', text)
    text = re.sub('###@@@###.{0,40}(\d{1,4})', '', text)
    text = text.replace('\r', '').replace('\n', ' ')
    text = text.replace('- ', '')
    text = re.sub('\s{3,}', '  ', text)
    text = re.sub('###@@@###', '', text)
    text = re.sub(r'([.!?])  ', r'\1\n\n', text)
    text = text.replace('  ', ' ')
    text = text.replace('..', '.')

txt_to_audio(text, base_name)
print("All done!")