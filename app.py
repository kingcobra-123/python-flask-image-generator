from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask app is running!"

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

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=8000, debug=True)
