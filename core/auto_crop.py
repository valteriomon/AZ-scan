import cv2 as cv
import numpy as np
from PIL import Image

class AutoCrop:

    def __init__(self, input):
        self.input = input
        self.output = self.input

    def method(self):
        self.original()
        original_rgb = self.input.copy()
        self.colorspace(cv.COLOR_BGR2GRAY)
        self.blur(kernel_size=3)
        self.threshold(228, 255, cv.THRESH_BINARY_INV)
        self.blur(kernel_size=59)
        self.threshold(117, 255, cv.THRESH_BINARY)
        self.morph(kernel_size=3, iterations=1, operation_type=0, morph_type=0)
        # self.morph(7)
        rect = self.countours(contour_luminosity=255, contour_thickness=1, contour_mode=0, contour_approximation=1)
        self.output = original_rgb
        self.show("output", wait_time=0)
        self.crop(rect)
        return self.output

        # ###
        # self.scale(0.5)
        # self.show()

    def original(self):
        # self.input = cv.imdecode(np.fromfile(self.input, dtype=np.uint8), cv.IMREAD_UNCHANGED)
        # self.input = cv.cvtColor(self.input, cv.COLOR_BGR2RGB)
        # self.output = self.input
        if isinstance(self.input, str):  # it's a file path
            self.input = cv.imdecode(np.fromfile(self.input, dtype=np.uint8), cv.IMREAD_UNCHANGED)
            self.input = cv.cvtColor(self.input, cv.COLOR_BGR2RGB)
        elif isinstance(self.input, Image.Image):  # it's a PIL image
            self.input = cv.cvtColor(np.array(self.input), cv.COLOR_RGB2BGR)
        else:
            raise TypeError("Unsupported input type. Must be file path or PIL.Image")

        self.output = self.input
    def steps(self):
        pass

    def colorspace(self, mode):
        self.output = cv.cvtColor(self.output, mode)

    def blur(self, kernel_size):
        self.output = cv.GaussianBlur(self.output, (kernel_size, kernel_size), 0)

    def threshold(self, value, max_value, type):
        self.output = cv.threshold(self.output, value, max_value, type)[1]

    def morph(self, kernel_size, iterations, operation_type, morph_type):
        self.output = cv.morphologyEx(self.output, operation_type, cv.getStructuringElement(morph_type, (kernel_size, kernel_size)), iterations=iterations)

    def countours(self,contour_luminosity, contour_thickness, contour_mode, contour_approximation):
        contours, _ = cv.findContours(self.output, contour_mode, contour_approximation)
        if contours:
            largest_contour = max(contours, key=cv.contourArea)
            # Get rotated bounding box
            rect = cv.minAreaRect(largest_contour)  # returns (center, (width, height), angle)
            box = cv.boxPoints(rect)                # convert to 4 corner points
            box = np.intp(box)                      # convert to integer
            image_with_rotated_rect = self.input.copy()
            cv.drawContours(image_with_rotated_rect, [box], 0, (255, 0, 0), 2)
            return rect
        return None

    def crop(self, rect):
        center, size, angle = rect
        width, height = int(size[0]), int(size[1])
        print(angle)
        if angle > 10:
            angle = angle - 90 # or angle = 90 + angle warning if very high angle (far from 0 or 90)
            width, height = height, width

        # add option to adjust size easily on 4 sides

        if width == 0 or height == 0:
            raise ValueError("Detected bounding box has zero width or height.")

        # OpenCV rotates counter-clockwise by default, so negate the angle
        rotation_matrix = cv.getRotationMatrix2D(center, angle, 1.0)

        # Step 2: Rotate the entire image
        rotated_image = cv.warpAffine(self.input, rotation_matrix, (self.input.shape[1], self.input.shape[0]), flags=cv.INTER_CUBIC)
        # show(rotated_image, True)

        # Step 3: Crop the rotated rectangle
        padding = 20  # pixels
        expanded_width = width + 2 * padding
        expanded_height = height + 2 * padding

        cropped = cv.getRectSubPix(rotated_image, (expanded_width, expanded_height), center)

        self.output = cv.cvtColor(cropped, cv.COLOR_RGB2BGR)

    def scale(self, scale):
        self.output = cv.resize(self.output, None, fx=scale, fy=scale)

    def show(self, title=None, wait_time=0):
        cv.imshow(title, self.output)
        cv.waitKey(wait_time)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Autocroper.")
    parser.add_argument("image", help="Path to the image file.")
    args = parser.parse_args()

    autocrop = AutoCrop(args.image)
    autocrop.method()

# 'Grayscale' : cv.COLOR_BGR2GRAY,
# 'RGB to BGR': cv.COLOR_RGB2BGR,
# 'RGB to HSV': cv.COLOR_RGB2HSV,
# 'RGB to YUV': cv.COLOR_RGB2YUV,
# 'RGB to LAB': cv.COLOR_RGB2LAB,
# 'BGR to RGB': cv.COLOR_BGR2RGB,
# 'BGR to HSV': cv.COLOR_BGR2HSV,
# 'BGR to YUV': cv.COLOR_BGR2YUV,
# 'BGR to LAB': cv.COLOR_BGR2LAB,
# 'HSV to RGB': cv.COLOR_HSV2RGB,
# 'HSV to BGR': cv.COLOR_HSV2BGR,
# 'HSV to BGR': cv.COLOR_HSV2BGR,
# 'YUV to RGB': cv.COLOR_YUV2RGB,
# 'YUV to BGR': cv.COLOR_YUV2BGR,
# 'LAB to RGB': cv.COLOR_LAB2RGB,
# 'LAB to BGR': cv.COLOR_LAB2BGR

# 'Binary' : cv.THRESH_BINARY,
# 'Binary Inverted': cv.THRESH_BINARY_INV,
# 'Truncate': cv.THRESH_TRUNC,
# 'To Zero': cv.THRESH_TOZERO,
# 'To Zero Inverted': cv.THRESH_TOZERO_INV,
# 'Otsu': cv.THRESH_OTSU

# 'Erode' : cv.MORPH_ERODE,
# 'Dilate': cv.MORPH_DILATE,
# 'Open': cv.MORPH_OPEN,
# 'Close': cv.MORPH_CLOSE,
# 'Gradient': cv.MORPH_GRADIENT,
# 'Top Hat': cv.MORPH_TOPHAT,
# 'Black Hat': cv.MORPH_BLACKHAT,
# 'Hit Miss': cv.MORPH_HITMISS

# 'Rectangle' : cv.MORPH_RECT,
# 'Cross': cv.MORPH_CROSS,
# 'Ellipse': cv.MORPH_ELLIPSE