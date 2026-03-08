import cv2
import numpy as np

def extract_skeleton(
    image_path,
    blur_ksize=9,
    morph_kernel=3,
):
    # greyscale imgea
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Image not found")

    # minimize noise
    img = cv2.GaussianBlur(img, (blur_ksize, blur_ksize), 0)

    # binarize (eyes become solid white blobs)
    bw = np.zeros_like(img, np.uint8)
    bw[img < 90] = 255

    # clean small noise but keep eyes
    kernel = np.ones((morph_kernel, morph_kernel), np.uint8)
    bw = cv2.morphologyEx(bw, cv2.MORPH_OPEN, kernel)

    # skeletonization (OpenCV-only thinning)
    skel = np.zeros(bw.shape, np.uint8)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
    temp = bw.copy()

    while True:
        eroded = cv2.erode(temp, element)
        opened = cv2.dilate(eroded, element)
        subset = cv2.subtract(temp, opened)
        skel = cv2.bitwise_or(skel, subset)
        temp = eroded.copy()

        if cv2.countNonZero(temp) == 0:
            break

    return skel