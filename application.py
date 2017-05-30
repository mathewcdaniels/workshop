import sys, os
from flask import Flask, flash, redirect, render_template, request, url_for, send_from_directory
from werkzeug.utils import secure_filename

from helpers import *

UPLOAD_FOLDER = '/home/ubuntu/workspace/ePubCreator/uploads'
ALLOWED_EXTENSIONS = set(['txt'])
DOWNLOAD_FOLDER = '/home/ubuntu/workspace/ePubCreator/downloads'

#configure application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET', 'POST'])
def index():
    """submit title/author/isbn & upload file"""

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('no file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            title = request.form['title']
            author = request.form['author']
            if title == None:
                return render_template("index.html")
            isbn = request.form['ISBN']
            epub_name = ePub(filename, title, author, isbn)
            return redirect(url_for("download_file", filename=epub_name))

    else:
        return render_template("index.html")
    
@app.route('/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)