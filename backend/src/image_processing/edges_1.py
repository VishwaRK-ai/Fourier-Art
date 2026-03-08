import cv2
import numpy as np

def smooth_contour(contour):
    if len(contour) < 3: return contour
    smoothed = np.copy(contour)
    # Simple averaging
    for i in range(1, len(contour)-1):
        smoothed[i] = (contour[i-1] + contour[i] + contour[i+1]) / 3.0
    return smoothed

def get_sketch(img_gray, blur_ksize=21):
    """
    Applies the Dodge Blend (Pencil Sketch) effect.
    """
    inv = 255 - img_gray
    # Ensure odd kernel size
    if blur_ksize % 2 == 0: blur_ksize += 1
    
    blur = cv2.GaussianBlur(inv, (blur_ksize, blur_ksize), 0)
    sketch = cv2.divide(img_gray, 255 - blur, scale=256)
    return sketch

# ADDED PARAMETERS HERE: min_length and min_area
def extract_contours(image_path, min_length=10, min_area=10.0):
    img = cv2.imread(image_path)
    if img is None: raise ValueError("Image not found")

    # 1. Resize (Standardize)
    h, w = img.shape[:2]
    if max(h, w) > 1000:
        scale = 1000 / max(h, w)
        img = cv2.resize(img, (0,0), fx=scale, fy=scale)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # -------------------------------------------------------------
    # STEP 1: HYBRID PREPARATION (Face vs Body)
    # -------------------------------------------------------------
    
    # Sharp version for Face
    src_sharp = gray
    
    # Flat version for Body (Heavy Median Blur to kill texture)
    src_flat = cv2.medianBlur(gray, 21)

    # -------------------------------------------------------------
    # STEP 2: GENERATE SKETCHES
    # -------------------------------------------------------------
    
    sketch_sharp = get_sketch(src_sharp, blur_ksize=21)
    sketch_flat = get_sketch(src_flat, blur_ksize=45) 

    # -------------------------------------------------------------
    # STEP 3: MERGE
    # -------------------------------------------------------------
    
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
    
    final_sketch = sketch_flat.copy()
    
    if len(faces) > 0:
        fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])
        
        # Shrink face box slightly to keep messy hair outlines out
        pad = int(fw * 0.05)
        y1, y2 = fy + pad, fy + fh - pad
        x1, x2 = fx + pad, fx + fw - pad
        
        # Paste sharp face into flat body
        final_sketch[y1:y2, x1:x2] = sketch_sharp[y1:y2, x1:x2]

    # -------------------------------------------------------------
    # STEP 4: THRESHOLD AND CLEAN
    # -------------------------------------------------------------
    
    _, binary = cv2.threshold(final_sketch, 240, 255, cv2.THRESH_BINARY_INV)
    
    # Remove tiny dots (pores) using morphology
    kernel = np.ones((2,2), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
    edges = cv2.ximgproc.thinning(binary) if hasattr(cv2, 'ximgproc') else binary

    # -------------------------------------------------------------
    # STEP 5: STRICT CONTOUR FILTERING
    # -------------------------------------------------------------
    
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    
    good_contours = []
    
    # Hardcoded variables removed; now using function arguments min_length and min_area

    for c in contours:
        # Check Length (ArcLength)
        length = cv2.arcLength(c, False)
        
        # Check Area (ContourArea) - mostly for small closed blobs
        area = cv2.contourArea(c)
        
        # Filter Logic: Must be long enough OR big enough
        if length > min_length or area > min_area:
            c = c.squeeze()
            if c.ndim < 2: continue
            
            # Close loops
            if np.linalg.norm(c[0] - c[-1]) < 10.0:
                c = np.vstack([c[1:], c[:1]])
            
            c = smooth_contour(c)
            good_contours.append(c)
            
    return good_contours