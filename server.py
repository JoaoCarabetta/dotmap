from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/")
def serve_index():
    # Serve the main index.html file when accessing the root URL
    return send_from_directory(".", "index.html")


@app.route("/<path:filename>")
def serve_file(filename):
    # Serve any other requested files from the current directory
    return send_from_directory(".", filename)


if __name__ == "__main__":
    app.run(port=8000)
