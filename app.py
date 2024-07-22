from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.json
    text = data['text']
    
    # Define the image size and background color
    width, height = 500, 200
    background_color = (247, 167, 11)  # #F7A70B in RGB

    # Create the image
    image = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(image)
    
    # Load the default font and calculate text size
    font = ImageFont.load_default()
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
    
    return send_file(img_io, mimetype='image/jpeg')

def create_sample_image():
    text = "Sample Text"
    
    image = Image.new('RGB', (500, 200), color=(247, 167, 11))  # #F7A70B background
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (500 - text_width) // 2
    y = (200 - text_height) // 2
    draw.text((x, y), text, font=font, fill=(0, 0, 0))  # Black text color
    
    image.save("sample_image.jpg")
    print("Sample image created and saved as sample_image.jpg")

if __name__ == '__main__':
    # create_sample_image()
    print("Starting Flask server...")
    app.run(debug=True)
