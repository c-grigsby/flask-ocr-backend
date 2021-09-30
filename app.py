from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from flask import Flask, request, Response, render_template
from dotenv import load_dotenv
import json
import time
import cv2
import os
import os.path

load_dotenv()
app = Flask(__name__)

BASE_PATH = os.getcwd()
UPLOAD_PATH = os.path.join(BASE_PATH, 'static/upload')

@app.route('/', methods=["GET"])
def home():
  return "Hello from Computer Vision"

@app.route('/sift-ocr', methods=["POST", "GET"])
def sift_ocr():
  if request.method == "POST":
    image_file = request.files['image']
    filename = image_file.filename
    path_save = os.path.join(UPLOAD_PATH, filename)
    image_file.save(path_save)

    image_to_ocr = cv2.imread(path_save)
    # preprocess Step1: Convert to Gray
    preprocessed_img = cv2.cvtColor(image_to_ocr, cv2.COLOR_BGR2GRAY)
    # preprocess Step2: Binary and Otsu Thresholding 
    _, preprocessed_img = cv2.threshold(preprocessed_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # preprocess Step3: Median Blur to rm noise in img
    preprocessed_img = cv2.medianBlur(preprocessed_img, 3)
    # save the preprocessed image
    cv2.imwrite(path_save, preprocessed_img)

    # Send img to Azure Read API
    subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")
    endpoint = os.getenv("AZURE_ENDPOINT")
    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    print("===== Read File - local =====")
    read_image_path = os.path.join(UPLOAD_PATH, filename)         
    read_image = open(read_image_path, "rb")

    # Call API with image and raw response to get OperationID
    read_response = computervision_client.read_in_stream(read_image, raw=True)
    # Get the operation location (URL with ID as last appendage)
    read_operation_location = read_response.headers["Operation-Location"]
    # Extract ID for results
    operation_id = read_operation_location.split("/")[-1]

    textResults = []
    waitingOnAPI = True
    # 'GET' API results
    while waitingOnAPI:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status.lower () not in ['notstarted', 'running']:
           waitingOnAPI = False
           break
        print ('Waiting for result...')
        time.sleep(10)

    if read_result.status == OperationStatusCodes.succeeded:
        textResults.append("Results from the Read API are a success.")
        textResults.append("Analysis Results:")
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                textResults.append(line.text)
                
    if len(textResults) < 3:
      textResults.append("No text was discovered")
    
    analysis_res = json.dumps(textResults)

    return Response(response=analysis_res, status=200, mimetype="application/json")

  return render_template('layout.html',upload=False)

if __name__ == "__main__":
        app.run()