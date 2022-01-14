# @packages
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from flask import Flask, request, Response, render_template, send_file
from dotenv import load_dotenv
from google.cloud import vision
import json
import time
import cv2
import os
import os.path
import requests
import os
import io
# @scripts
from services import azureAPI, readAPI

load_dotenv()
app = Flask(__name__)

BASE_PATH = os.getcwd()
UPLOAD_PATH = os.path.join(BASE_PATH, 'static/upload')


@app.route('/', methods=["GET"])
def home():
    return "Hello from Computer Vision"


@app.route('/sift-read', methods=["POST", "GET"])
def sift_read():
    if request.method == "POST":
        try:
            image_file = request.files['image']
            preprocessing_level = int(request.form['preprocessing'])
            filename = image_file.filename
            path_save = os.path.join(UPLOAD_PATH, filename)
            image_file.save(path_save)
            textBoundingBox = []
            boundingBoxNumbers = []
            textResults = []

            img_preprocessing(preprocessing_level, path_save)

            read_result = readAPI(filename)

            for text_result in read_result.analyze_result.read_results:
                for line in text_result.lines:
                    textResults.append(line.text)
                    # filter for text "ingredient"
                    if "ingredient" in line.text.lower():
                        textBoundingBox.append(line.bounding_box)
                        for pixel_nums in textBoundingBox[0]:
                            boundingBoxNumbers.append(pixel_nums)
                        # upper left coordinate bounding box
                        x1 = int(boundingBoxNumbers[0])
                        y1 = int(boundingBoxNumbers[1])
                        # upper right coordinate of bounding box
                        x2 = int(boundingBoxNumbers[2])
                        y2 = int(boundingBoxNumbers[3])
                        # get highest vertex
                        if (y1 < y2):
                            highestVertex = y1
                        else:
                            highestVertex = y2

                        img = cv2.imread(path_save)
                        height, width, _channel = img.shape
                        # crop image height to where text is found
                        cropped_image1 = img[highestVertex -
                                             4:height, 0:width]
                        # save the preprocessed image
                        cv2.imwrite(path_save, cropped_image1)
                        # find bounding box if present
                        img_preprocessing(4, path_save)
                        # Send area of interest to Read API
                        textResults = []
                        read_result2 = readAPI(filename)
                        for text_result in read_result2.analyze_result.read_results:
                            for line in text_result.lines:
                                textResults.append(line.text)
                        break

            if len(textResults) == 0:
                textResults.append("No text was discovered")

            analysis_res = json.dumps(textResults)
            return Response(response=analysis_res, status=200, mimetype="application/json")

        except:
            return Response(response="An error occurred", status=500, mimetype="application/json")

    return render_template('layout.html', upload=False)


@app.route('/sift-ocr', methods=["POST", "GET"])
def sift_ocr():
    if request.method == "POST":
        try:
            image_file = request.files['image']
            preprocessing_level = int(request.form['preprocessing'])
            filename = image_file.filename
            path_save = os.path.join(UPLOAD_PATH, filename)
            image_file.save(path_save)
            textBoxNumbers = []
            boundingBoxNumbers = []
            textResults = []

            img_preprocessing(preprocessing_level, path_save)

            # send image to Azure v2.0 OCR API
            analysis = azureAPI(filename)

            regions = analysis["regions"]
            lines = [region["lines"] for region in regions][0]
            words = [line["words"] for line in lines]

            lines_words = []
            for line_words in words:
                for lw in line_words:
                    w = lw["text"]
                    lines_words.append(w)
                    # Search for the text "ingredient"
                    if "ingredient" in lw["text"].lower():
                        textBoxNumbers.append(lw["boundingBox"])
                        for num in textBoxNumbers[0].split(","):
                            boundingBoxNumbers.append(int(num))

                        # upper left edge x coordinate
                        x1 = boundingBoxNumbers[0]
                        # y-coordinate of top edge after auto-rotation
                        y1 = boundingBoxNumbers[1]
                        # width
                        w = boundingBoxNumbers[2]
                        # height
                        h = boundingBoxNumbers[3]

                        highestVertex = x1

                        img = cv2.imread(path_save)
                        height, width, _channel = img.shape
                        # crop image height to where text is found
                        cropped_image1 = img[highestVertex -
                                             8:height, 0:width]
                        # save the preprocessed image
                        cv2.imwrite(path_save, cropped_image1)
                        # find bounding box if present
                        img_preprocessing(4, path_save)
                        # Send area of interest to Azure API
                        textResults = []
                        analysis = azureAPI(filename)
                        regions = analysis["regions"]
                        lines = [region["lines"] for region in regions][0]
                        words = [line["words"] for line in lines]

                        lines_words = []
                        for line_words in words:
                            w = [lw["text"] for lw in line_words]
                            lines_words.append(w)
                        break

            textResults = lines_words

            if len(textResults) == 0:
                textResults.append("No text was discovered")

            analysis_res = json.dumps(textResults)
            return Response(response=analysis_res, status=200, mimetype="application/json")

        except:
            return Response(response="An error occurred", status=500, mimetype="application/json")

    return render_template('layout.html', upload=False)


@app.route('/sift-vision', methods=["POST", "GET"])
def sift_vision():
    if request.method == "POST":
        try:
            image_file = request.files['image']
            preprocessing_level = int(request.form['preprocessing'])
            filename = image_file.filename
            path_save = os.path.join(UPLOAD_PATH, filename)
            image_file.save(path_save)

            img_preprocessing(preprocessing_level, path_save)

            # call Google Vision API
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ServiceToken.json'
            client = vision.ImageAnnotatorClient()
            with io.open(path_save, 'rb') as image_file:
                content = image_file.read()
            image = vision.Image(content=content)

            response = client.text_detection(image=image)
            texts = response.text_annotations

            # process results
            textResults = []
            result_str = "Analysis Results: Preprocessing Level " + \
                str(preprocessing_level)
            textResults.append(result_str)

            for text in texts:
                textResults.append(text.description)
            # remove lines of text
            textResults.pop(1)

            if len(textResults) <= 1:
                textResults.append("No text was discovered")

            analysis_res = json.dumps(textResults)
            return Response(response=analysis_res, status=200, mimetype="application/json")

        except:
            return Response(response="An error occurred", status=500, mimetype="application/json")

    return render_template('layout.html', upload=False)


@app.route('/sift-contours', methods=["POST"])
def sift_contours():
    if request.method == "POST":
        try:
            image_file = request.files['image']
            filename = image_file.filename
            path_save = os.path.join(UPLOAD_PATH, filename)
            image_file.save(path_save)

            result = assess_contours(path_save)

            imagePass = result
            if (imagePass):
                responseMsg = "The results were a success"
                img_preprocessing(4, path_save)
                try:
                    return send_file(path_save, attachment_filename=filename)
                except:
                    return Response(response="Assesment success, an error occurred sending the file", status=500, mimetype="apllication/json")
            else:
                responseMsg = "The image failed contour assessment"
                response = {"msg": responseMsg, "success": result}
                analysis_res = json.dumps(response)
                return Response(response=analysis_res, status=400, mimetype="application/json")

        except:
            return Response(response="An exception occured processing the image", status=500, mimetype="application/json")

    return render_template('layout.html', upload=False)


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


if __name__ == "__main__":
    app.run(debug=True)
