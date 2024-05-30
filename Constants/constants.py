import cv2 as cv
from dataclasses import dataclass
from datetime import datetime
import os

# Indices of the iris points
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

L_H_LEFT = [33]     # Right eye reference point
L_H_RIGHT = [133]   # Left eye reference point


TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")