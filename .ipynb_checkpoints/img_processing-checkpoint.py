import io
import os

import numpy as np
import cv2
import matplotlib.pyplot as plt

from google.cloud import vision
from google.cloud.vision import types
from PIL import Image
import math

CLIENT = vision.ImageAnnotatorClient()

def get_ocr_response(img):
    img = adjust_image(img)
#     print(img.shape)
    buffer = io.BytesIO()
    pil_img = Image.fromarray(img)
    pil_img.save(buffer, "JPEG")
    image = types.Image(content=buffer.getvalue())
    return CLIENT.document_text_detection(image=image)

def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def adjust_image(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_edges = cv2.Canny(img_gray, 100, 100, apertureSize=3)
    lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5)

    angles = []

    for x1, y1, x2, y2 in lines[0]:
#         cv2.line(img_gray, (x1, y1), (x2, y2), (255, 0, 0), 3)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        angles.append(angle)

    median_angle = np.median(angles)
    if not median_angle<4:
        img = rotate_image(img,-(90-int(median_angle)))
    return img