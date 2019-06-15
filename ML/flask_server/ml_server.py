from flask import Flask, render_template, request, redirect
from base64 import b64decode
from hashlib import md5

app =  Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/infer", methods=["POST"])
def infer_image():
    for value in request.values:
        f = open("tempfile.jpg", "wb")

        base64encoded = value.replace('@', '=').replace('*', '+')
        base64decoded = b64decode(base64encoded)

        f.write(base64decoded)
        f.close()

    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

