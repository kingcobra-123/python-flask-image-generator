from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io
import random
import string
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
import os
import textwrap

# Load the environment variables
load_dotenv()

app = Flask(__name__)

connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
container_name = os.getenv('AZURE_CONTAINER_NAME')

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

def generate_random_name(length=12):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

# Function to wrap text to fit within a given width when rendered.
def wrap_text(text, font, max_width, draw):
    lines = []
    # Use textwrap to split the text into lines
    for line in text.splitlines():
        # Wrap the text according to the actual rendered size
        words = line.split()
        current_line = []
        for word in words:
            # Append word to current line and check width
            current_line.append(word)
            # Calculate the width of the current line
            text_bbox = draw.textbbox((0, 0), ' '.join(current_line), font=font)
            width = text_bbox[2] - text_bbox[0]
            if width > max_width:
                # If width exceeds max, store current line without the last word
                lines.append(' '.join(current_line[:-1]))
                # Start a new line with the last word
                current_line = [word]
        # Add the last line of words
        if current_line:
            lines.append(' '.join(current_line))
    return lines



@app.route('/')
def home():
    return "Conbuy Python Flask API"

@app.route('/generate-image', methods=['POST'])

def generate_image():
    data = request.json
    text = data['text']
    
    # Define the image size and background color
    width, height = 1080, 1920
    background_color = (247, 167, 11)  # #F7A70B in RGB

    # Create the image
    image = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(image)
    
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "Roboto_Slab", "RobotoSlab-VariableFont_wght.ttf")
    font_size = 100  
    font_size = 100 
    font = ImageFont.truetype(font_path, font_size)

    # Calculate max width for text
    max_text_width = width * 0.9 

    # Wrap the text
    wrapped_text = wrap_text(text, font, max_text_width, draw)

    # Calculate total height of wrapped text lines
    total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in wrapped_text)

    # Calculate vertical starting point to center text
    y = (height - total_text_height) // 2  


    # Add wrapped text to image
    for line in wrapped_text:
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        line_height = text_bbox[3] - text_bbox[1]
        x = (width - text_width) // 2  
        draw.text((x, y), line, font=font, fill=(0, 0, 0)) 
        y += line_height
    
    # Save the image to a BytesIO object
    img_io = io.BytesIO()
    image.save(img_io, 'JPEG')
    img_io.seek(0)

    # Generate a random name for the image
    image_name = generate_random_name() + '.jpg'

    #create the blob client
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=image_name)

    #upload the image to the blob
    blob_client.upload_blob(img_io, blob_type="BlockBlob")

    # Save the image locally
    # local_path = os.path.join('local_images', image_name)
    # os.makedirs('local_images', exist_ok=True)
    # image.save(local_path)

    # return local_path


    # Return the URL of the image uploaded
    blob_url = blob_client.url
    print(blob_url)
    return {"image_url": blob_url}

if __name__ == '__main__':
    # sample_text = "Hello, World! "
    # generate_image(sample_text)
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=8000, debug=True)
