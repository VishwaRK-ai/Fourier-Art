import cv2
import numpy as np


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
    low_thresh=100,
    high_thresh=200,
    morph_kernel=5,
    adaptive_thresh=True,
):
    # greyscale imgea
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Image not found")

    #minimize noise
    img = cv2.GaussianBlur(img, (blur_ksize, blur_ksize), 0)

    if adaptive_thresh:
        img = cv2.adaptiveThreshold(
            img,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            11,
            2
        )
    else:
        _,img = cv2.threshold(
            img,
            0,
            255,
            cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU
        )
    #morph close
    kernel = np.ones((morph_kernel,morph_kernel),np.uint8)
    img = cv2.morphologyEx(img,cv2.MORPH_CLOSE,kernel)

    #edges
    edges = cv2.Canny(img,low_thresh,high_thresh)

    #skeltonize
    skel = thin_edges(edges)

    return skel