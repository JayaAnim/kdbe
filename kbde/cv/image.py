from kbde.data import serialize

import cv2
import numpy as np
import os, io
import base64
import PIL
import piexif


DIR_PATH = os.path.dirname(os.path.abspath(__file__))
FACE_CASCADE_FILE = os.path.join(DIR_PATH, "haarcascade_frontalface_default.xml")
FACE_CASCADE = cv2.CascadeClassifier(FACE_CASCADE_FILE)


class Image(serialize.Serializable):

    @classmethod
    def from_opencv_image(cls, opencv_image, image_box=None):
        _, buf = cv2.imencode(".jpg", opencv_image)
        buf = bytes(buf)
        return cls(buf, image_box)

    def __init__(self, image, image_box=None):
        """
        Takes an image as bytes and an optional ImageBox object describing the source coordinates of
            the image relative to any parent/source image
        """
        assert isinstance(image, bytes), "image was passed as {} but should be bytes".format(
                                                                                        type(image))
        self.image = image
        self.image_box = image_box

    def serialize(self):
        data = {
            "image": self.get_string(),
            "image_box": self.image_box,
            }
        return data

    def get_string(self):
        return base64.b64encode(self.image).decode("latin1")

    def get_cropped(self, image_box):
        """
        Creates a subset of self.image cropped to the given `image_box`
        Creates a new `Image` object with the subset
        Returns the `Image` object
        """
        cropped_opencv_image = self.get_opencv_image()[image_box.y:image_box.y+image_box.h,
                                                       image_box.x:image_box.x+image_box.w]

        return Image.from_opencv_image(cropped_opencv_image, image_box)

    def get_largest_face_box(self, margin_amount=None, margin_percent=None):
        face_boxes = self.get_face_boxes()

        face_boxes.sort(key=lambda x: x.get_area(), reverse=True)

        if not face_boxes:
            return None

        face_box = face_boxes[0]

        if margin_amount or margin_percent:
            face_box = face_box.get_adjusted(self, margin_amount, margin_percent)

        return face_box

    def get_faces(self, margin_amount=None, margin_percent=None):
        """
        Returns a list of new image instances based on where faces were found in this image
        """
        # Get all of the faces that are in this image
        face_boxes = self.get_face_boxes()

        if margin_amount or margin_percent:
            face_boxes = [face_box.get_adjusted(self, margin_amount, margin_percent)]

        # Get the image that is largest/closest to the camera
        face_boxes.sort(key=lambda fb: fb.get_area(), reverse=True)

        return [self.get_cropped(face_box) for face_box in face_boxes]

    def get_face_boxes(self):
        """
        Checks self.image for faces
        Creates a list of `ImageBox` objects, one for each face found
        Returns the list of `ImageBox` objects
        """
        gray = cv2.cvtColor(self.get_opencv_image(), cv2.COLOR_BGR2GRAY)
        face_boxes = FACE_CASCADE.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        face_boxes = [ImageBox(*face_box) for face_box in face_boxes]

        return face_boxes

    def get_opencv_image(self, gray_scale=False):
        """
        Returns a version of self.image which can be used by opencv
        """
        #handling for imdecode
        nparr = np.fromstring(self.image, np.uint8)

        #load the image
        if gray_scale:
            image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        else:
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        return image

    def get_quality(self):
        im = self.get_opencv_image(gray_scale=True)

        #compute the focus measure of the image using Variance of Laplacian method
        fm = cv2.Laplacian(im, cv2.CV_64F).var()

        return fm

    def remove_ios_orientation_exif(self):
        """
        Checks self.image exif data for iOS orientation data
        If found: removes from image, returns `True`
        Else: does nothing, returns false
        """

        img = PIL.Image.open(io.BytesIO(self.image))
        if "exif" in img.info:
            exif_dict = piexif.load(img.info['exif'])

            if piexif.ImageIFD.Orientation in exif_dict["0th"]:
                img_format = img.format

                orientation = exif_dict["0th"][piexif.ImageIFD.Orientation]

                if orientation == 1:
                    return False
                elif orientation == 2:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 3:
                    img = img.rotate(180)
                elif orientation == 4:
                    img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 5:
                    img = img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 6:
                    img = img.rotate(-90, expand=True)
                elif orientation == 7:
                    img = img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)

                exif_dict["0th"][piexif.ImageIFD.Orientation] = 1
                exif_bytes = piexif.dump(exif_dict)

                output_file = io.BytesIO()
                img.save(output_file, format=img_format, exif=exif_bytes)

                self.image = output_file
                return True

        return False


class ImageBox(serialize.Serializable):
    
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __str__(self):
        return str(self.get_coordinates())

    def serialize(self):
        return self.get_coordinates()

    def get_coordinates(self):
        return [int(self.x), int(self.y), int(self.w), int(self.h)]

    def get_adjusted(self, image, amount=None, percent=None):
        """
        Takes amount or percent
        Adjusts the dimensions of this `ImageBox` accordingly
        """

        assert amount is not None or percent is not None, "must provide amount or percent"

        if percent is not None:
            # Calculate amount to adjust by based on size of w and h
            l = max([self.w, self.h])
            amount = int(l * (percent / 100.0))

        new_w = self.w + amount * 2
        new_h = self.h + amount * 2
        new_x = self.x - amount
        new_y = self.y - amount

        new_image_box = ImageBox(new_x, new_y, new_w, new_h)
        new_image_box.validate(image)

        return new_image_box

    def validate(self, image):
        """
        Takes an `image` object
        Checks to make sure that this `ImageBox` is completely within the given image
        Adjusts the x, y, w, and h if they are out of bounds
        """
        height, width, channels = image.get_opencv_image().shape

        if self.x < 0:
            self.x = 0

        if self.y < 0:
            self.y = 0

        error = (self.w + self.x) - width
        if error > 0:
            self.w -= error

        error = (self.h + self.y) - height
        if error > 0:
            self.h -= error

    def get_area(self):
        return self.w * self.h
