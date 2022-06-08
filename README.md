<div align="center" markdown="1">

<img src="https://www.educative.io/api/page/6196871006519296/image/download/6316021754363904" height="165" alt="FlaskApp">

<br/>

# Flask OCR Back-end

</div>

This server-side application is the back-end to a mobile application providing Optical Character Recognition (OCR) for image processing. This machine learning technology enables the API to read the text found within an uploaded image, and returns a response with the text results from the OCR analysis. 

---

## Project Details

- Developed in Python with Flask micro-framework
- Automated image cropping to a region of interest via text recognition
- Image preprocessing via OpenCV
- Utilizes Azure Computer Vision and Google Vision APIs
- Image files via requests stored locally
- Deployed to [Heroku](https://www.heroku.com/)

---

## Deployed URL for API services

- https://computer-vision-api.herokuapp.com/{endpoint}

---

## API References

_Note: For general use a preprocessing level of 0 for API calls will be the most effective_

- URL: https://computer-vision-api.herokuapp.com/ocr/azure-read

  - Method: POST
  - Body: image: _the image file_, preprocessing: _a number from 0 - 4_
  - Response: OCR Analysis via Azure Read v3.0 API

- URL: https://computer-vision-api.herokuapp.com/ocr/azure

  - Method: POST
  - Body: image: _the image file_, preprocessing: _a number from 0 - 4_
  - Response: OCR Analysis via Azure OCR v2.1 API

- URL: https://computer-vision-api.herokuapp.com/ocr/vision

  - Method: POST
  - Body: image: _the image file_, preprocessing: _a number from 0 - 4_
  - Response: OCR Analysis via Google Vision API

- URL: https://computer-vision-api.herokuapp.com/ocr/sift-contour

  - Method: POST
  - Body: image: _the image file_
  - Response: Successful if the contours of a largest bounding box are discovered to be contained within the images maximum width. Returns an image file auto-cropped to the region of interest.

---

## Getting Started

- Ensure Python is installed locally on your machine
- To initialize a virtual enviroment, navigate to the 'src' directory of the application in the terminal and execute:

  ##### _Note: "python3" will depend on your version of Python_

  ```
  $ python3 -m venv venv
  ```

- Activate the virtual environment:

  ```
  $ source venv/bin/activate
  ```

- Install dependencies:

  ```
  $ pip3 install -r requirements.txt
  ```

---

## Run the Development Server

Navigate to the 'src' directory in the terminal

- Activate the virtual environment:

  ```
  $ source venv/bin/activate
  ```

- Run the Development Server:

  ```
  $ python -m flask run
  ```

---

### This application utilizes a .env file to host environment variables. For utilization configure the following keys:

- #### AZURE_SUBSCRIPTION_KEY
- #### AZURE_SUBSCRIPTION_KEY_2 (for Azure OCR v2.0)
- #### AZURE_ENDPOINT
- #### ServiceToken.json via Google Vision
