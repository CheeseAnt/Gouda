## Flask application to act as a REST service for android app, dummy frontend

from flask import Flask, render_template, request, redirect, Response
from base64 import b64decode
from hashlib import md5
from mobilenet import MobileNet
from os import remove as remove_file

app =  Flask(__name__)
mb = MobileNet()
TEMP_FILENAME = "infer_input.jpg"

# dummy frontend to make sure server is up
@app.route("/")
def main():
    return render_template("index.html")

# inference POST route
@app.route("/infer", methods=["POST"])
def infer_image():
    # find the contents and save the image from them
    for value in request.values:
        f = open(TEMP_FILENAME, "wb")

        # first replace all special characters then decode the base64 encoding
        base64encoded = value.replace('@', '=').replace('*', '+')
        base64decoded = b64decode(base64encoded)

        # write the image to a temporary file
        f.write(base64decoded)
        f.close()

    print("Received image, performing inference...")

    # perform classification
    prediction, accuracy = mb.infer(TEMP_FILENAME)

    # remove the temporary file
    remove_file(TEMP_FILENAME)
    
    # create a response in the headers with the predicted object and the accuracy of the prediction
    resp = Response()
    resp.headers['prediction'] = prediction
    resp.headers['accuracy'] = accuracy

    return resp

# run on external IP on port 5k
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

