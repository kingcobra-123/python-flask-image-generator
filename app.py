from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io
import random
import string
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
import os

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

@app.route('/')
def home():
    return "Flask app is running!"

@app.route('/generate-image', methods=['POST'])
def generate_image(text):
    # data = request.json
    # text = data['text']
    
    # Define the image size and background color
    width, height = 1080, 1920
    background_color = (247, 167, 11)  # #F7A70B in RGB

    # Create the image
    image = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(image)
    
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "Roboto_Slab", "RobotoSlab-VariableFont_wght.ttf")
    font_size = 100  # Change this to the desired font size
    font_size = 100 
    font = ImageFont.truetype(font_path, font_size)

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Calculate the position to center the text
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Add text to image
    draw.text((x, y), text, font=font, fill=(0, 0, 0))  # Black text color
    
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
    return {"image_url": blob_url}

if __name__ == '__main__':
    # sample_text = "Hello, World!"
    # generate_image(sample_text)
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=8000, debug=True)
