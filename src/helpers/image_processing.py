# @packages
import cv2


def img_preprocessing(preprocessing_level, path_save):

    if (preprocessing_level == 0):
        return

    if (preprocessing_level == 1):
        image_to_ocr = cv2.imread(path_save)
        # preprocess Step1: Convert to Gray
        preprocessed_img = cv2.cvtColor(image_to_ocr, cv2.COLOR_BGR2GRAY)
        # save the preprocessed image
        cv2.imwrite(path_save, preprocessed_img)

    elif (preprocessing_level == 2):
        image_to_ocr = cv2.imread(path_save)
        # preprocess Step1: Convert to Gray
        preprocessed_img = cv2.cvtColor(image_to_ocr, cv2.COLOR_BGR2GRAY)
        # preprocess Step2: Binary and Otsu Thresholding
        _, preprocessed_img = cv2.threshold(
            preprocessed_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        # save the preprocessed image
        cv2.imwrite(path_save, preprocessed_img)

    elif (preprocessing_level == 3):
        image_to_ocr = cv2.imread(path_save)
        # preprocess Step1: Convert to Gray
        preprocessed_img = cv2.cvtColor(image_to_ocr, cv2.COLOR_BGR2GRAY)
        # preprocess Step2: Binary and Otsu Thresholding
        _, preprocessed_img = cv2.threshold(
            preprocessed_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        # preprocess Step3: Median Blur to rm noise in img
        preprocessed_img = cv2.medianBlur(preprocessed_img, 3)
        # save the preprocessed image
        cv2.imwrite(path_save, preprocessed_img)

    elif (preprocessing_level == 4):
        img = cv2.imread(path_save)
        # preprocess Step4: Crop Image - get bounding box
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        dst = cv2.Canny(gray, 0, 150)
        blured = cv2.blur(dst, (5, 5), 0)
        # estimate min contour by size of the image
        MIN_CONTOUR_AREA = 100000
        img_thresh = cv2.adaptiveThreshold(
            blured, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        Contours, imgContours = cv2.findContours(
            img_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        for contour in Contours:
            if cv2.contourArea(contour) > MIN_CONTOUR_AREA:
                [X, Y, W, H] = cv2.boundingRect(contour)
                box = cv2.rectangle(
                    img, (X, Y), (X + W, Y + H), (0, 0, 255), 2)
                # crop image
                cropped_image = img[Y:Y+H, X:X+W]
                # save the preprocessed image
                cv2.imwrite(path_save, cropped_image)


def assess_contours(path_save):
    # detect boundaries of the largest bounding box, reject cut-off image
    img = cv2.imread(path_save)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dst = cv2.Canny(gray, 0, 150)
    blured = cv2.blur(dst, (5, 5), 0)
    # estimate min contour by size of the image
    MIN_CONTOUR_AREA = 90000
    img_thresh = cv2.adaptiveThreshold(
        blured, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    Contours, imgContours = cv2.findContours(
        img_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in Contours:
        if cv2.contourArea(contour) > MIN_CONTOUR_AREA:
            # get bounding rectangle of largest contour
            [X, Y, W, H] = cv2.boundingRect(contour)
            box = cv2.rectangle(img, (X, Y), (X + W, Y + H), (0, 0, 255), 2)
            print('X Value of BoundingBox Left Coordinate:', X)
            print('X Value of BoundingBox Right Coordinate:', W)
            # compare against image dimensions
            _h, w, _c = img.shape
            print('Width of Image:', w)
            if X <= 50 or W >= w-50:
                return False
            else:
                return True
