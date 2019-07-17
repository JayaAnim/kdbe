from django.db import models
from imutils import paths

import argparse
import cv2
import io
import numpy as np


class Image(models.Model):

	def check_quality(self, image, threshold):
		###image should be a django image file

		#convert to bytes
		bytes_image = image.read()

		#handling for imdecode
		byte_wrap = io.BytesIO(bytes_image)
		img_str = byte_wrap.read()
		nparr = np.fromstring(img_str, np.uint8)

		#load the image in greyscale
		im = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

		#compute the focus measure of the image using Variance of Laplacian method
		fm = cv2.Laplacian(im, cv2.CV_64F).var()
		text = "Not Blurry"

		#if focus measure is less than supplied threshold, image should be considered "blurry"
		if fm < threshold:
    		text = "Blurry"

		return (text, fm)

    