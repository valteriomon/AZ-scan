import cv2 as cv
import numpy as np

class AutoCrop:
    def __init__(self, input_image, output_image):
        pass

    def method(self):
        pass

    def colorspace(self, image):
        pass

    def blur(self, image):
        pass

    def threshold(self, image):
        pass

    def morph(self, image):
        pass

    def crop(self, image):
        pass






def show(img, leave=False, winname="img", wait_time=0):
    scale = 0.3
    disp_img = cv.resize(img, None, fx=scale, fy=scale)
    cv.imshow(winname, disp_img)
    cv.waitKey(wait_time)
    if leave:
        exit()

original_image_0 = cv.imdecode(np.fromfile("files/imageC.png", dtype=np.uint8), cv.IMREAD_UNCHANGED)
original_image_0 = cv.cvtColor(original_image_0, cv.COLOR_BGR2RGB)

#COLOR - Colorspace
colorspace_mode = 6
colorspace_1 = cv.cvtColor(original_image_0, colorspace_mode)


#BLUR - Gaussian
# kernel_size = 31
kernel_size = 3
gaussian_2 = cv.GaussianBlur(colorspace_1, (kernel_size, kernel_size), 0)

#THRESH - Simple
# thresh_value = 240
thresh_value = 228
max_value = 255
thresh_type = 1
simple_3 = cv.threshold(gaussian_2, thresh_value, max_value, thresh_type)[1]


#BLUR - Gaussian
kernel_size = 59
gaussian_4 = cv.GaussianBlur(simple_3, (kernel_size, kernel_size), 0)


#THRESH - Simple
thresh_value = 117
max_value = 255
thresh_type = 0
simple_5 = cv.threshold(gaussian_4, thresh_value, max_value, thresh_type)[1]

#MORPH
# kernel_size = 7
kernel_size = 3
# kernel_size = 1
iterations = 1
operation_type = 0
morph_type = 0
morph_4 = cv.morphologyEx(simple_5, operation_type, cv.getStructuringElement(morph_type, (kernel_size, kernel_size)), iterations=iterations)
# Operation type, kernel size combos:
# Erode 1 ksize 7
# Dilate 2 ksize 1
# Open 3 ksize 11/15 > performs erode and then dilate
# Close 4 ksize > performs dilate and then erode (not working too well)
# hitmiss 7 ksize 1 to 21

#Contours (Thresh)
contour_luminosity = 255
contour_thickness = 1
contour_mode = 0
contour_approximation = 1
# thresh_5 = cv.drawContours(np.zeros(morph_4.shape).astype("uint8"), cv.findContours(morph_4, contour_mode, contour_approximation)[0], -1, contour_luminosity, contour_thickness)

# Find contours
contours, _ = cv.findContours(morph_4, contour_mode, contour_approximation)

if contours:
    largest_contour = max(contours, key=cv.contourArea)

    # Get rotated bounding box
    rect = cv.minAreaRect(largest_contour)  # returns (center, (width, height), angle)
    box = cv.boxPoints(rect)                # convert to 4 corner points
    box = np.intp(box)                      # convert to integer

    # Draw it on the original image
    image_with_rotated_rect = original_image_0.copy()
    cv.drawContours(image_with_rotated_rect, [box], 0, (255, 0, 0), 2)
    # show(image_with_rotated_rect, True)
    # Show image
    # show(cv.cvtColor(image_with_rotated_rect, cv.COLOR_RGB2BGR))
    # cv.waitKey(0)
    # cv.destroyAllWindows()
    # Step 1: Get the rotation matrix to deskew

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
    rotated_image = cv.warpAffine(original_image_0, rotation_matrix, (original_image_0.shape[1], original_image_0.shape[0]))
    # show(rotated_image, True)

    # Step 3: Crop the rotated rectangle
    padding = 20  # pixels
    expanded_width = width + 2 * padding
    expanded_height = height + 2 * padding

    cropped = cv.getRectSubPix(rotated_image, (expanded_width, expanded_height), center)
    # show(cropped, True)

    # Show the result
    show(cv.cvtColor(cropped, cv.COLOR_RGB2BGR))
    cv.waitKey(0)
    cv.destroyAllWindows()

else:
    print("No contours found.")

#
# blur slider
# thresh val, type?
# padding

# cv.imshow('Result', thresh_5)
# cv.waitKey()



















# # Step 1: Grayscale
#     # color light contrast? test
# # Step 2: Gaussian Blur > Kernel size: 3 (can be adjusted slightly upwards)
# # Step 3: Threshold > Binary inverted (could be set to binary), max: 255, value: 228 (can be adjusted slightly)
# Optional, another blur +threshold?
# # Step 4: Morph~
#     # Kernel size
#     # Morph type: 0 (erode), 1 (dilate), 2 (open), 3 (close), 4 (gradient)
# # Step 5: Contours + extra padding > Adjust padding, contour thickness




# kernel_size = 9

# thresh_type = 0
# thresh_value = 228

# operation_type = 4
# kernel_size = 9




# # blur slider
# # thresh val, type?
# # padding

# #BLUR - Gaussian
# # kernel_size = 31
# kernel_size = 5
# gaussian_2 = cv.GaussianBlur(colorspace_1, (kernel_size, kernel_size), 0)

# #THRESH - Simple
# # thresh_value = 240
# thresh_value = 228
# max_value = 255
# thresh_type = 1
# simple_3 = cv.threshold(gaussian_2, thresh_value, max_value, thresh_type)[1]

# #MORPH
# # kernel_size = 7
# kernel_size = 9
# # kernel_size = 1
# iterations = 1
# operation_type = 4
# morph_type = 0
# morph_4 = cv.morphologyEx(simple_3, operation_type, cv.getStructuringElement(morph_type, (kernel_size, kernel_size)), iterations=iterations)







# #BLUR - Gaussian
# # kernel_size = 31
# kernel_size = 5
# gaussian_2 = cv.GaussianBlur(colorspace_1, (kernel_size, kernel_size), 0)

# #THRESH - Simple
# # thresh_value = 240
# thresh_value = 228
# max_value = 255
# thresh_type = 1
# simple_3 = cv.threshold(gaussian_2, thresh_value, max_value, thresh_type)[1]

# #MORPH
# # kernel_size = 7
# kernel_size = 3
# kernel_size = 1
# iterations = 1
# operation_type = 0
# morph_type = 0
# morph_4 = cv.morphologyEx(simple_3, operation_type, cv.getStructuringElement(morph_type, (kernel_size, kernel_size)), iterations=iterations)


# #BLUR - Gaussian
# # kernel_size = 31
# kernel_size = 5
# gaussian_2 = cv.GaussianBlur(colorspace_1, (kernel_size, kernel_size), 0)

# #THRESH - Simple
# # thresh_value = 240
# thresh_value = 228
# max_value = 255
# thresh_type = 1
# simple_3 = cv.threshold(gaussian_2, thresh_value, max_value, thresh_type)[1]

# #MORPH
# # kernel_size = 7
# kernel_size = 3
# kernel_size = 1
# iterations = 1
# operation_type = 3
# morph_type = 0
# morph_4 = cv.morphologyEx(simple_3, operation_type, cv.getStructuringElement(morph_type, (kernel_size, kernel_size)), iterations=iterations)





# #COLOR - Colorspace
# colorspace_mode = 6
# colorspace_1 = cv.cvtColor(original_image_0, colorspace_mode)


# #BLUR - Gaussian
# # kernel_size = 31
# kernel_size = 3
# gaussian_2 = cv.GaussianBlur(colorspace_1, (kernel_size, kernel_size), 0)

# #THRESH - Simple
# # thresh_value = 240
# thresh_value = 228
# max_value = 255
# thresh_type = 1
# simple_3 = cv.threshold(gaussian_2, thresh_value, max_value, thresh_type)[1]

# #MORPH
# # kernel_size = 7
# kernel_size = 3
# # kernel_size = 1
# iterations = 1
# operation_type = 0
# morph_type = 0
# morph_4 = cv.morphologyEx(simple_3, operation_type, cv.getStructuringElement(morph_type, (kernel_size, kernel_size)), iterations=iterations)

# #Contours (Thresh)
# contour_luminosity = 255
# contour_thickness = 6
# contour_mode = 0
# contour_approximation = 1
# # thresh_5 = cv.drawContours(np.zeros(morph_4.shape).astype("uint8"), cv.findContours(morph_4, contour_mode, contour_approximation)[0], -1, contour_luminosity, contour_thickness)


# https://github.com/murniox/ScanCropper/blob/master/scan_cropper.py
# https://github.com/z80z80z80/autocrop/blob/master/autocrop.py
# https://github.com/Claytorpedo/scan-cropper/blob/master/scan_cropper.py
# https://github.com/kosenina/ScannedImageMultiCrop/blob/master/src/scan_cropper.py













# #BLUR - Gaussian
# # kernel_size = 31
# kernel_size = 3
# gaussian_2 = cv.GaussianBlur(colorspace_1, (kernel_size, kernel_size), 0)

# #THRESH - Simple
# # thresh_value = 240
# thresh_value = 228
# max_value = 255
# thresh_type = 1
# simple_3 = cv.threshold(gaussian_2, thresh_value, max_value, thresh_type)[1]


# #BLUR - Gaussian
# kernel_size = 469
# gaussian_4 = cv.GaussianBlur(simple_3, (kernel_size, kernel_size), 0)


# #THRESH - Simple
# thresh_value = 214
# max_value = 255
# thresh_type = 0
# simple_5 = cv.threshold(gaussian_4, thresh_value, max_value, thresh_type)[1]

# #MORPH
# # kernel_size = 7
# kernel_size = 3
# # kernel_size = 1
# iterations = 1
# operation_type = 2
# morph_type = 0
# morph_4 = cv.morphologyEx(simple_5, operation_type, cv.getStructuringElement(morph_type, (kernel_size, kernel_size)), iterations=iterations)
# # Operation type, kernel size combos:
# # Erode 1 ksize 7
# # Dilate 2 ksize 1
# # Open 3 ksize 11/15 > performs erode and then dilate
# # Close 4 ksize > performs dilate and then erode (not working too well)
# # hitmiss 7 ksize 1 to 21

# #Contours (Thresh)
# contour_luminosity = 255
# contour_thickness = 1
# contour_mode = 0
# contour_approximation = 1
# # thresh_5 = cv.drawContours(np.zeros(morph_4.shape).astype("uint8"), cv.findContours(morph_4, contour_mode, contour_approximation)[0], -1, contour_luminosity, contour_thickness)











original_image_0 = cv.imdecode(np.fromfile("files/imageC.png", dtype=np.uint8), cv.IMREAD_UNCHANGED)
original_image_0 = cv.cvtColor(original_image_0, cv.COLOR_BGR2RGB)

#COLOR - Colorspace
colorspace_mode = 6
colorspace_1 = cv.cvtColor(original_image_0, colorspace_mode)


# #BLUR - Gaussian
# # kernel_size = 31
# kernel_size = 3
# gaussian_2 = cv.GaussianBlur(colorspace_1, (kernel_size, kernel_size), 0)

# #THRESH - Simple
# # thresh_value = 240
# thresh_value = 228
# max_value = 255
# thresh_type = 1
# simple_3 = cv.threshold(gaussian_2, thresh_value, max_value, thresh_type)[1]


# #BLUR - Gaussian
# kernel_size = 59
# gaussian_4 = cv.GaussianBlur(simple_3, (kernel_size, kernel_size), 0)


# #THRESH - Simple
# thresh_value = 117
# max_value = 255
# thresh_type = 0
# simple_5 = cv.threshold(gaussian_4, thresh_value, max_value, thresh_type)[1]

# #MORPH
# # kernel_size = 7
# kernel_size = 3
# # kernel_size = 1
# iterations = 1
# operation_type = 0
# morph_type = 0
# morph_4 = cv.morphologyEx(simple_5, operation_type, cv.getStructuringElement(morph_type, (kernel_size, kernel_size)), iterations=iterations)
# # Operation type, kernel size combos:
# # Erode 1 ksize 7
# # Dilate 2 ksize 1
# # Open 3 ksize 11/15 > performs erode and then dilate
# # Close 4 ksize > performs dilate and then erode (not working too well)
# # hitmiss 7 ksize 1 to 21

# #Contours (Thresh)
# contour_luminosity = 255
# contour_thickness = 1
# contour_mode = 0
# contour_approximation = 1
# # thresh_5 = cv.drawContours(np.zeros(morph_4.shape).astype("uint8"), cv.findContours(morph_4, contour_mode, contour_approximation)[0], -1, contour_luminosity, contour_thickness)

# # Find contours