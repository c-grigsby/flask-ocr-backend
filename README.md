<div align="center" markdown="1">

<img src="https://www.educative.io/api/page/6196871006519296/image/download/6316021754363904" height="165" alt="FlaskApp">

<br/>

# Flask OCR Back-end

</div>

This server-side application is the back-end to a mobile application providing Optical Character Recognition (OCR) image processing

---

## Project Details

- Developed in Python with Flask micro-framework
- Image preprocessing via OpenCV
- Utilizes Azure Computer Vision and Google Vision APIs
- Image files via requests stored locally
- Deployed to [Heroku](https://www.heroku.com/)

---

## Deployed URL for API services

- https://computer-vision-api.herokuapp.com/{endpoint}

---

## API References

- URL: https://computer-vision-api.herokuapp.com/sift-read

  - Method: POST
  - Body: image: _the image file_, preprocessing: _a number from 0 - 4_
  - Response: OCR Analysis via Azure Read v3.0 API

- URL: https://computer-vision-api.herokuapp.com/sift-ocr

  - Method: POST
  - Body: image: _the image file_, preprocessing: _a number from 0 - 4_
  - Response: OCR Analysis via Azure OCR v2.1 API

- URL: https://computer-vision-api.herokuapp.com/sift-vision

  - Method: POST
  - Body: image: _the image file_, preprocessing: _a number from 0 - 4_
  - Response: OCR Analysis via Google Vision API

- URL: https://computer-vision-api.herokuapp.com/sift-contour

  - Method: POST
  - Body: image: _the image file_
  - Response: Successful if the contours of the largest bounding box discovered within the image is assessed to have been contained within the images width

---

## Getting Started

- Ensure Python is installed locally on your machine
- To initialize a virtual enviroment, navigate to the directory of the application in the terminal and execute:

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
  $ pip install -r requirements.txt
  ```

---

#### This application utilizes a .env file to host environment variables. For utilization configure the following keys:

- ##### AZURE_SUBSCRIPTION_KEY
- ##### AZURE_ENDPOINT
- ##### ServiceToken.json via Google Vision
