# @packages
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from google.cloud import vision
import time
import os
import os.path
import requests
import os
import io

BASE_PATH = os.getcwd()
UPLOAD_PATH = os.path.join(BASE_PATH, 'static/upload')

def readAPI(filename):
    # Azure 3.2 Read API Config
    subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")
    endpoint = os.getenv("AZURE_ENDPOINT")
    computervision_client = ComputerVisionClient(
        endpoint, CognitiveServicesCredentials(subscription_key))
    read_image_path = os.path.join(UPLOAD_PATH, filename)
    read_image = open(read_image_path, "rb")

    # Call API with img and raw response to get OperationID
    read_response = computervision_client.read_in_stream(
        read_image, raw=True)
    # Get the operation location (URL with ID as last appendage)
    read_operation_location = read_response.headers["Operation-Location"]
    # Extract ID for results
    operation_id = read_operation_location.split("/")[-1]

    waitingOnAPI = True
    # 'GET' results
    while waitingOnAPI:
        read_result = computervision_client.get_read_result(
            operation_id)
        if read_result.status.lower() not in ['notstarted', 'running']:
            waitingOnAPI = False
            break
        time.sleep(.5)

    if read_result.status == OperationStatusCodes.succeeded:

        return read_result


def azureAPI(filename):
    # send image to Azure OCR API
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

    return analysis


def googleAPI(path_save):
    # Google Vision API
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ServiceToken.json'
    client = vision.ImageAnnotatorClient()
    with io.open(path_save, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    response = client.text_detection(image=image)

    return response

