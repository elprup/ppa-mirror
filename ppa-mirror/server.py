from flask import Flask, request, send_from_directory
app = Flask(__name__)

@app.route('/ubuntu/<path:path>')
def static_files(path):
    return send_from_directory('repo', path)
    