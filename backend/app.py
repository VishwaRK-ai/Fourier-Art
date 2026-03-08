import os
import tempfile
import cv2                 
import numpy as np         
import base64              
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import your custom modules
from src.image_processing.edges_1 import extract_contours
from src.geometry.stitch_1 import stitch_contours
from src.Fourier.signal import to_complex_signal, resample_by_arclength

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_IMAGE_PATH = os.path.join(BASE_DIR, "data", "Images", "input1.jpg")

# GLOBAL VARIABLE: Stores the full ABSOLUTE path to the current image
current_image_path = DEFAULT_IMAGE_PATH

@app.route("/upload", methods=["POST"])
def upload_file():
    global current_image_path
    
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        temp_dir = tempfile.gettempdir()
        save_path = os.path.join(temp_dir, filename)
        file.save(save_path)
        current_image_path = save_path
        print(f"Image saved to temp: {current_image_path}")
        return jsonify({"message": "File uploaded successfully", "filename": filename})

@app.route("/coords")
def get_coords():
    global current_image_path
    
    if not os.path.exists(current_image_path):
        print(f"File not found at {current_image_path}, reverting to default.")
        current_path_to_use = DEFAULT_IMAGE_PATH
    else:
        current_path_to_use = current_image_path

    try:
        print("Processing image:", current_path_to_use)

        # 1. EXTRACT RAW CONTOURS
        contours = extract_contours(current_path_to_use)
        
        if not contours:
             return jsonify({"error": "No contours found"}), 400

        # 2. STITCH CONTOURS (Connect them into one path)
        stitched = stitch_contours(contours)

        if stitched is None or stitched.size == 0:
            return jsonify({"error": "Stitching failed"}), 400

        # 3. GENERATE VISUALIZATION (Now using the STITCHED path)
        # We use the stitched points to determine canvas size
        max_x = int(np.max(stitched[:, 0]))
        max_y = int(np.max(stitched[:, 1]))
        
        vis_h, vis_w = max_y + 10, max_x + 10
        vis_img = np.ones((vis_h, vis_w, 3), dtype=np.uint8) * 255
        
        # Draw the Single Continuous Stitched Line
        # reshape is needed for cv2.polylines (N, 1, 2)
        points_to_draw = stitched.astype(np.int32).reshape((-1, 1, 2))
        
        # False = Don't close the loop explicitly (though it usually is closed)
        # Color = Black (0,0,0), Thickness = 1
        cv2.polylines(vis_img, [points_to_draw], False, (0, 0, 0), 1)
        
        _, buffer = cv2.imencode('.png', vis_img)
        img_str = base64.b64encode(buffer).decode('utf-8')
        contour_data_url = f"data:image/png;base64,{img_str}"
        # -----------------------------------------

        # 4. FOURIER PROCESSING
        z = to_complex_signal(stitched)
        z = resample_by_arclength(z, num_samples=2000)

        coords = [{"re": float(c.real), "im": float(c.imag)} for c in z]
        
        return jsonify({
            "coords": coords,
            "contour_image": contour_data_url
        })

    except Exception as e:
        print(f"Error processing image: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)