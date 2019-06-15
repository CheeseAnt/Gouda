from flask import Flask, render_template, request, redirect, Response
from base64 import b64decode
from hashlib import md5
from mobilenet import MobileNet
from os import remove as remove_file

app =  Flask(__name__)
mb = MobileNet()
TEMP_FILENAME = "infer_input.jpg"

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/infer", methods=["POST"])
def infer_image():
    for value in request.values:
        f = open(TEMP_FILENAME, "wb")

        base64encoded = value.replace('@', '=').replace('*', '+')
        base64decoded = b64decode(base64encoded)

        f.write(base64decoded)
        f.close()

    print("Received image, performing inference...")

    prediction, accuracy = mb.infer(TEMP_FILENAME)

    remove_file(TEMP_FILENAME)
    
    resp = Response()
    resp.headers['prediction'] = prediction
    resp.headers['accuracy'] = accuracy

    return resp
#    return redirect("/")

@app.route("/results", methods=["GET"])
def get_results():
    prediction, accuracy = mb.results()

    resp = Response()
    resp.headers['prediction'] = prediction
    resp.headers['accuracy'] = accuracy

    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

