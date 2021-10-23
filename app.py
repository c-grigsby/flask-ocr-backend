from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from flask import Flask, request, Response, render_template
from dotenv import load_dotenv
from google.cloud import vision     
import json
import time
import cv2
import os
import os.path
import requests
import os, io
import requests
import io 

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
    image_file = request.files['image']
    preprocessing_level = int(request.form['preprocessing'])
    filename = image_file.filename
    path_save = os.path.join(UPLOAD_PATH, filename)
    image_file.save(path_save)

    img_preprocessing(preprocessing_level, path_save)

    # Send img to Azure Read API
    subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")
    endpoint = os.getenv("AZURE_ENDPOINT")
    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    read_image_path = os.path.join(UPLOAD_PATH, filename)         
    read_image = open(read_image_path, "rb")

    # Call API with img and raw response to get OperationID
    read_response = computervision_client.read_in_stream(read_image, raw=True)
    # Get the operation location (URL with ID as last appendage)
    read_operation_location = read_response.headers["Operation-Location"]
    # Extract ID for results
    operation_id = read_operation_location.split("/")[-1]

    textResults = []
    waitingOnAPI = True
    # 'GET' results
    while waitingOnAPI:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status.lower () not in ['notstarted', 'running']:
           waitingOnAPI = False
           break
        time.sleep(1)

    if read_result.status == OperationStatusCodes.succeeded:
        result_str = "Analysis Results: Preprocessing Level " + str(preprocessing_level)
        textResults.append(result_str)
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                textResults.append(line.text)
                
    if len(textResults) < 2:
      textResults.append("No text was discovered")
    
    analysis_res = json.dumps(textResults)
    return Response(response=analysis_res, status=200, mimetype="application/json")

  return render_template('layout.html',upload=False)

@app.route('/sift-ocr', methods=["POST", "GET"])
def sift_ocr():
  if request.method == "POST":
    image_file = request.files['image']
    preprocessing_level = int(request.form['preprocessing'])
    filename = image_file.filename
    path_save = os.path.join(UPLOAD_PATH, filename)
    image_file.save(path_save)

    img_preprocessing(preprocessing_level, path_save)
    
    # Send image to Azure OCR API
    subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY_2")
    vision_base_url = "https://westus.api.cognitive.microsoft.com/vision/v2.0/"
    ocr_url = vision_base_url + "ocr"

    read_image_path = os.path.join(UPLOAD_PATH, filename)         
    image_data = open(read_image_path, "rb").read()

    headers = {'Ocp-Apim-Subscription-Key': subscription_key,
               'Content-Type': 'application/octet-stream'}
    response = requests.post(ocr_url, headers=headers, data=image_data)
    response.raise_for_status()
    analysis = response.json()

    textResults = []
    regions = analysis["regions"]
    lines = [region["lines"] for region in regions][0]
    words = [line["words"] for line in lines]

    lines_words = []
    for line_words in words:
        w = [lw["text"] for lw in line_words]
        lines_words.append(w)

    textResults = lines_words
    result_str = ["Analysis Results: Preprocessing Level " + str(preprocessing_level)]
    textResults.insert(0,result_str)

    if len(textResults) <= 1:
      textResults.append("No text was discovered")
    
    analysis_res = json.dumps(textResults)
    return Response(response=analysis_res, status=200, mimetype="application/json")

  return render_template('layout.html',upload=False)

@app.route('/sift-vision', methods=["POST", "GET"])
def sift_vision():
  if request.method == "POST":
    image_file = request.files['image']
    preprocessing_level = int(request.form['preprocessing'])
    filename = image_file.filename
    path_save = os.path.join(UPLOAD_PATH, filename)
    image_file.save(path_save)

    img_preprocessing(preprocessing_level, path_save)

    # Call Google Vision API
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ServiceToken.json'
    client = vision.ImageAnnotatorClient()    
    with io.open(path_save, 'rb') as image_file:        
    	content = image_file.read()    
    image = vision.Image(content=content)    
    
    response = client.text_detection(image=image)    
    texts = response.text_annotations

    # Process results
    textResults = [] 
    result_str = "Analysis Results: Preprocessing Level " + str(preprocessing_level)
    textResults.append(result_str)

    for text in texts:        
        textResults.append(text.description)  
    # Remove lines of text
    textResults.pop(1)

    if len(textResults) <= 1:
      textResults.append("No text was discovered")

    analysis_res = json.dumps(textResults)
    return Response(response=analysis_res, status=200, mimetype="application/json")

  return render_template('layout.html',upload=False)

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
      _, preprocessed_img = cv2.threshold(preprocessed_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
      # save the preprocessed image
      cv2.imwrite(path_save, preprocessed_img)

  elif (preprocessing_level == 3):
      image_to_ocr = cv2.imread(path_save)
      # preprocess Step1: Convert to Gray
      preprocessed_img = cv2.cvtColor(image_to_ocr, cv2.COLOR_BGR2GRAY)
      # preprocess Step2: Binary and Otsu Thresholding 
      _, preprocessed_img = cv2.threshold(preprocessed_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
      # preprocess Step3: Median Blur to rm noise in img
      preprocessed_img = cv2.medianBlur(preprocessed_img, 3)
      # save the preprocessed image
      cv2.imwrite(path_save, preprocessed_img)
    
  elif (preprocessing_level == 4):
      img = cv2.imread(path_save)
      # preprocess Step4: Crop Image - get bounding box
      gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    
      dst = cv2.Canny(gray, 0, 150)
      blured = cv2.blur(dst, (5,5), 0) 
      # estimate min contour by size of the image    
      MIN_CONTOUR_AREA=40000
      img_thresh = cv2.adaptiveThreshold(blured, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
      Contours,imgContours = cv2.findContours(img_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

      for contour in Contours:
        if cv2.contourArea(contour) > MIN_CONTOUR_AREA:
          [X, Y, W, H] = cv2.boundingRect(contour)
          box=cv2.rectangle(img, (X, Y), (X + W, Y + H), (0,0,255), 2)
      # Crop Image
      cropped_image = img[Y:Y+H, X:X+W]
      # save the preprocessed image
      cv2.imwrite(path_save, cropped_image) 

if __name__ == "__main__":
        app.run(debug=True)