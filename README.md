<div align="center" markdown="1">

<img src="https://www.probytes.net/wp-content/uploads/2018/10/flask-logo-png-transparent.png" height="160" alt="FlaskApp">
<br/>

# Flask OCR Back-end

</div>

This server-side application is the back-end to a mobile application providing Optical Character Recognition (OCR) image processing

---

## Project Details

- Developed in Python with Flask micro-framework
- Image preprocessing via OpenCV
- Utilizes Azure Computer Vision and Google Vision APIs
- Deployed to [Heroku](https://www.heroku.com/)

---

## Deployed URL for API services

- https://computer-vision-api.herokuapp.com/{endpoint}

---

#### This application utilizes a .env file to host environment variables. For utilization configure the following keys:

- ##### AZURE_SUBSCRIPTION_KEY
- ##### AZURE_ENDPOINT
- ##### ServiceToken.json via Google Vision
