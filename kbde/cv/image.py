from django.db import models
from imutils import paths

import argparse
import cv2
import io
import numpy as np


class Image():

    def __init__(self, image):
        self.image = image

    def check_quality(self):
        #convert self.image to bytes
        bytes_image = self.image.read()

        #handling for imdecode
        nparr = np.fromstring(bytes_image, np.uint8)

        #load the image in greyscale
        im = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        #compute the focus measure of the image using Variance of Laplacian method
        fm = cv2.Laplacian(im, cv2.CV_64F).var()

        return fm

    
