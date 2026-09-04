from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS

ROOT = Path(__file__).resolve().parent
app = Flask(__name__)
CORS(app)


@app.route("/")
def serve_index():
    return send_from_directory(ROOT, "index.html")


@app.route("/<path:filename>")
def serve_file(filename):
    # PMTiles is read with HTTP Range. Gzip of the whole archive breaks 206
    # and the browser cannot seek inside the hilbert directory.
    kwargs = {"conditional": True}
    if filename.endswith(".pmtiles"):
        kwargs["mimetype"] = "application/vnd.pmtiles"
    response = send_from_directory(ROOT, filename, **kwargs)
    if filename.endswith(".pmtiles"):
        response.headers["Accept-Ranges"] = "bytes"
    return response


if __name__ == "__main__":
    import os

    # Threaded so the map can issue overlapping Range reads on one archive.
    port = int(os.environ.get("PORT", "8000"))
    app.run(port=port, threaded=True)
