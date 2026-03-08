import cv2
import numpy as np

def is_closed(contour, eps=2.0):
    return np.linalg.norm(contour[0]-contour[-1])<eps

def break_loop(contour):
    return np.vstack([contour[1:],contour[:1]])

def smooth_contour(contour, window=5,sigma = 2.0):
    
    smoothed = np.copy(contour)
    N = len(contour)

    offset = np.arange(-window,window+1)
    weights = np.exp(-0.5*(offset/sigma)**2)
    weights /= weights.sum()

    for i in range(N):
        indices = [(i + j) % N for j in range(-window, window + 1)]
        smoothed[i] = np.sum(contour[indices]*weights[:,None],axis=0)
    return smoothed


def thin_edges(edges):
    skel = np.zeros(edges.shape,np.uint8)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))

    temp = edges.copy()

    while True:
        eroded = cv2.erode(temp,element)
        opened = cv2.dilate(eroded,element)
        subset = cv2.subtract(temp,opened)
        skel = cv2.bitwise_or(skel,subset)
        temp = eroded.copy()

        if cv2.countNonZero(temp)==0:
            break
    return skel


# def remove_junctions(skel):
#     h,w = skel.shape
#     cleaned = skel.copy()
#     for y in range(1,h-1):
#         for x in range(1,w-1):
#             if skel[y,x]==0:
#                 continue

#             neighbors = skel[y-1:y+2, x-1:x+2]
#             count = np.count_nonzero(neighbors)-1

#             if count >=6:
#                 cleaned[y,x]=0
#     return cleaned

def extract_contours(
    image_path,
    blur_ksize=15,
    low_thresh=30,
    high_thresh=120,
    morph_kernel=5,
    adaptive_thresh=True,
    smooth_window=3,
    smooth_sigma=2.0,
    min_length=0,
):
    # greyscale imgea
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Image not found")

    #minimize noise
    img = cv2.GaussianBlur(img, (blur_ksize, blur_ksize), 0)

    #binarize image
    if adaptive_thresh:
        img = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 9, 2
        )
    else:
        _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    #morphological closing
    kernel = np.ones((morph_kernel, morph_kernel), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    #edges detection
    edges = cv2.Canny(img, low_thresh, high_thresh)
    edges = thin_edges(edges)
    # edges = remove_junctions(edges)

    #extenal contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # filter
    good_contours = []
    for c in contours:
        if len(c) >= min_length and cv2.arcLength(c.astype(np.float32),False)>2*min_length:
            c = c.squeeze()
            if c.ndim == 1:
                c = np.expand_dims(c, axis=0)
            if is_closed(c):
                c = break_loop(c)
            c = smooth_contour(c, window=smooth_window,sigma = smooth_sigma)
            good_contours.append(c)

    if len(good_contours) == 0:
        raise ValueError("No contours found above the minimum length")

    return good_contours