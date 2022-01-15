# @packages
from flask import Flask, request, Response, render_template, send_file
from dotenv import load_dotenv
import json
import os
import os.path
# @scripts
from helpers.image_processing import assess_contours, img_preprocessing
from services.ocrServices import azure_read_service, azure_service, vision_service

load_dotenv()
app = Flask(__name__)

BASE_PATH = os.getcwd()
UPLOAD_PATH = os.path.join(BASE_PATH, 'static/upload')


@app.route('/', methods=["GET"])
def home():
    return "Hello from Computer Vision"


@app.route('/ocr/azure-read', methods=["POST", "GET"])
def sift_read():
    if request.method == "POST":
        try:
            image_file = request.files['image']
            preprocessing_level = int(request.form['preprocessing'])

            textResults = azure_read_service(image_file, preprocessing_level)

            analysis_res = json.dumps(textResults)
            return Response(response=analysis_res, status=200, mimetype="application/json")

        except:
            return Response(response="An error occurred", status=500, mimetype="application/json")

    return render_template('layout.html', upload=False)


@app.route('/ocr/azure', methods=["POST", "GET"])
def sift_ocr():
    if request.method == "POST":
        try:
            image_file = request.files['image']
            preprocessing_level = int(request.form['preprocessing'])

            textResults = azure_service(image_file, preprocessing_level)

            analysis_res = json.dumps(textResults)

            return Response(response=analysis_res, status=200, mimetype="application/json")

        except:
            return Response(response="An error occurred", status=500, mimetype="application/json")

    return render_template('layout.html', upload=False)


@app.route('/ocr/vision', methods=["POST", "GET"])
def sift_vision():
    if request.method == "POST":
        try:
            image_file = request.files['image']
            preprocessing_level = int(request.form['preprocessing'])

            textResults = vision_service(image_file, preprocessing_level)

            analysis_res = json.dumps(textResults)
            return Response(response=analysis_res, status=200, mimetype="application/json")

        except:
            return Response(response="An error occurred", status=500, mimetype="application/json")

    return render_template('layout.html', upload=False)


@app.route('/assess-contours', methods=["POST"])
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


if __name__ == "__main__":
    app.run(debug=True)
