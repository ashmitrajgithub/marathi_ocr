from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import pytesseract
import pdf2image
import os
import cv2

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def preprocess_image(image_path, save_as):
    """Grayscale → Denoise → Threshold → Save and return path"""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.fastNlMeansDenoising(img, h=30)
    _, img_bw = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite(save_as, img_bw)
    return save_as

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filename = file.filename

    if filename == '':
        return jsonify({'error': 'No file selected'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    text_output = ""

    try:
        if filename.lower().endswith('.pdf'):
            images = pdf2image.convert_from_path(file_path)
            for i, image in enumerate(images):
                page_path = os.path.join(PROCESSED_FOLDER, f'page_{i}.png')
                image.save(page_path)

                bw_path = os.path.join(PROCESSED_FOLDER, f'page_{i}_bw.png')
                preprocessed_path = preprocess_image(page_path, bw_path)

                pil_img = Image.open(preprocessed_path)
                text = pytesseract.image_to_string(pil_img, lang='mar')
                text_output += text + "\n"
        else:
            img = Image.open(file_path)
            img_path = os.path.join(PROCESSED_FOLDER, 'image_input.png')
            img.save(img_path)

            bw_path = os.path.join(PROCESSED_FOLDER, 'image_input_bw.png')
            preprocessed_path = preprocess_image(img_path, bw_path)

            pil_img = Image.open(preprocessed_path)
            text_output = pytesseract.image_to_string(pil_img, lang='mar')

        return jsonify({'extracted_text': text_output.strip()})

    except Exception as e:
        return jsonify({'error': f'OCR processing failed: {str(e)}'}), 500

if __name__ == '__main__':
    print("🔵 Marathi OCR Flask server running at http://127.0.0.1:5001")
    app.run(debug=True, port=5001)
