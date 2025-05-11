#MORPH
# Operation type, kernel size combos:
# Erode 1 ksize 7
# Dilate 2 ksize 1
# Open 3 ksize 11/15 > performs erode and then dilate
# Close 4 ksize > performs dilate and then erode (not working too well)
# hitmiss 7 ksize 1 to 21

#Contours (Thresh)

# thresh_5 = cv.drawContours(np.zeros(morph_4.shape).astype("uint8"), cv.findContours(morph_4, contour_mode, contour_approximation)[0], -1, contour_luminosity, contour_thickness)


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