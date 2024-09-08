from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# Load Haar cascades for face, eyes, and smile detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

def enhance_image(img):
    # Image Enhancement Techniques
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (5, 5), 0)
    img = cv2.equalizeHist(img)
    return img

def detect_expression(img):
    enhanced_img = enhance_image(img)
    
    faces = face_cascade.detectMultiScale(enhanced_img, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
    for (x, y, w, h) in faces:
        roi_gray = enhanced_img[y:y+h, x:x+w]
        
        # Apply more advanced image processing techniques
        # 1. Morphological Processing
        kernel = np.ones((5, 5), np.uint8)
        roi_gray = cv2.morphologyEx(roi_gray, cv2.MORPH_CLOSE, kernel)
        
        # 2. Segmentation - Thresholding
        _, roi_thresh = cv2.threshold(roi_gray, 120, 255, cv2.THRESH_BINARY)
        
        # Detect eyes and smiles
        eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=10, minSize=(30, 30))
        smiles = smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.8, minNeighbors=20, minSize=(25, 25))
        
        # Expression Logic
        if len(smiles) > 0:
            return "Happy"
        elif len(eyes) == 2:
            if np.mean(roi_gray) > 150:
                return "Surprised"
            else:
                return "Neutral"
        elif len(eyes) == 1:
            return "Sleepy"
        else:
            if np.mean(roi_gray) < 100:
                return "Sad"
            else:
                return "Angry"
    return "No face detected"

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    img = Image.open(io.BytesIO(file.read()))
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    expression = detect_expression(img)
    _, buffer = cv2.imencode('.jpg', img)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return jsonify({'expression': expression, 'image': img_str})


@app.route('/process', methods=['POST'])
def process_image():
    file = request.files['file']
    action = request.form['action']
    img = Image.open(io.BytesIO(file.read()))
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    if action == 'canny':
        img = cv2.Canny(img, 100, 200)
    elif action == 'gaussian':
        img = cv2.GaussianBlur(img, (15, 15), 0)
    elif action == 'equalize':
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.equalizeHist(gray)
    elif action == 'rotate':
        angle = int(request.form['angle'])
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        img = cv2.warpAffine(img, M, (w, h))
    elif action == 'dilate':
        kernel = np.ones((5, 5), np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)
    elif action == 'hsv':
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    _, buffer = cv2.imencode('.jpg', img)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return jsonify({'image': img_str})

if __name__ == '__main__':
    app.run(debug=True)
