# @packages
from flask import Flask
from dotenv import load_dotenv
import cv2
import os
import os.path
import sys
# @scripts
from services.apiServices import azureAPI, googleAPI, readAPI
from helpers.image_processing import img_preprocessing

load_dotenv()
app = Flask(__name__)

BASE_PATH = os.getcwd()
UPLOAD_PATH = os.path.join(BASE_PATH, 'static/upload')


def azure_read_service(image_file, preprocessing_level):
    textResults = []
    try: 
        filename = image_file.filename
        path_save = os.path.join(UPLOAD_PATH, filename)
        image_file.save(path_save)
        textBoundingBox = []
        boundingBoxNumbers = []

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

        return textResults

    except: 
        textResults.append("INTERNAL SERVER ERROR @ azure-read-service: ", sys.exc_info()[0])
        return textResults


def azure_service(image_file, preprocessing_level):
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

    for line_words in words:
        for lw in line_words:
            w = lw["text"]
            textResults.append(w)
            # Search for the text "ingredient"
            if "ingredient" in lw["text"].lower():
                textResults.clear()
                textBoxNumbers.append(lw["boundingBox"])
                for num in textBoxNumbers[0].split(","):
                    boundingBoxNumbers.append(int(num))
                # upper left edge x-coordinate
                x1 = boundingBoxNumbers[0]
                # y-coordinate of top edge after auto-rotation
                y1 = boundingBoxNumbers[1]
                # width
                w = boundingBoxNumbers[2]
                # height
                h = boundingBoxNumbers[3]

                highestVertex = y1

                img = cv2.imread(path_save)
                height, width, _channel = img.shape
                # crop image height to where text is found
                cropped_image1 = img[highestVertex -
                                     5:height, 0:width]
                # save the preprocessed image
                cv2.imwrite(path_save, cropped_image1)
                # find bounding box if present

                img_preprocessing(4, path_save)

                # Send area of interest to Azure API
                new_analysis = azureAPI(filename)
                new_regions = new_analysis["regions"]
                new_lines = [region["lines"] for region in new_regions][0]
                new_words = [line["words"] for line in new_lines]
                for line_items in new_words:
                    for lw2 in line_items:
                        word = lw2["text"]
                        textResults.append(word)
                return textResults

    if len(textResults) == 0:
        textResults.append("No text was discovered")

    return textResults


def vision_service(image_file, preprocessing_level):
    filename = image_file.filename
    path_save = os.path.join(UPLOAD_PATH, filename)
    image_file.save(path_save)
    boundingBoxNumbers = []

    img_preprocessing(preprocessing_level, path_save)

    # call Google Vision API
    response = googleAPI(path_save)

    texts = response.text_annotations

    # process results
    textResults = []
    for index, text in enumerate(texts, start=0):
        if index != 0:
            textResults.append(text.description)
            textResults.pop(0)
            if "ingredient" in text.description.lower():
                for vertex in text.bounding_poly.vertices:
                    boundingBoxNumbers.append(int(vertex.x))
                    boundingBoxNumbers.append(int(vertex.y))
                # bounding Box from where text was found
                # upper left vertex
                x1 = boundingBoxNumbers[0]
                y1 = boundingBoxNumbers[1]
                # upper right vertex
                x2 = boundingBoxNumbers[2]
                y2 = boundingBoxNumbers[3]
                # bottom right vertex
                x3 = boundingBoxNumbers[2]
                y3 = boundingBoxNumbers[3]

                # get highest vertex
                if (y1 < y2):
                    highestVertex = y1
                else:
                    highestVertex = y2
                img = cv2.imread(path_save)
                height, width, _channel = img.shape
                # crop image height to where text is found
                cropped_image = img[highestVertex - 5:height, 0:width]
                # save the preprocessed image
                cv2.imwrite(path_save, cropped_image)
                # find bounding box if present
                img_preprocessing(4, path_save)
                # Send area of interest to Google API
                del textResults[:]
                response2 = googleAPI(path_save)
                texts2 = response2.text_annotations
                # process results
                for index, text in enumerate(texts2):
                    textResults.append(text.description)
                    if index == 0:
                        textResults.pop(0)
                break

    if len(textResults) <= 1:
        textResults.append("No text was discovered")

    return textResults
