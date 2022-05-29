
from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for, send_file
import flask
import os
from werkzeug.utils import secure_filename
from swap import swap_img

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = "SecretKey"

upload_folder = "static/uploaded_files/"
if not os.path.exists(upload_folder):
    os.mkdir(upload_folder)

app.config['UPLOAD_FOLDER'] = upload_folder

@app.route('/')
def home():
    return render_template('index.html')

allowed_extension = ['jpg', 'png']
global fname, path

@app.route('/swap', methods = ['POST', 'GET'])
def swap():
    global fname, path
    if request.method == 'POST':
        images = request.files.to_dict()
        image_names = []
        for image in images:
            img_name = images[image].filename
            temp = img_name
            if img_name == "":
                flash("Please Upload file")
                return redirect(url_for('home'))
            extension = img_name.split('.')[1]
            if extension not in allowed_extension:
                flash("file format not supported")
                return redirect(url_for('home'))
            image_names.append(temp)
            images[image].save(os.path.join(app.config['UPLOAD_FOLDER'], images[image].filename))
        try:
            path, fname = swap_img(image_names)
        except:
            flash("Image may contain more than one or no face")
            return redirect(url_for('home')) 
        print(fname)
        return render_template('swap.html',filepath = path, filename = fname, image1 = image_names[0], image2 = image_names[1])
    if request.method == 'GET':
        return redirect(url_for('home'))

@app.route('/download_file/<path:filename>')
def download_file(filename):
    file_location = app.static_folder + '/' + 'output_files'
    print(file_location)
    print(filename)
    return send_from_directory(directory = file_location, path = filename, as_attachment=True)

@app.route('/instructions')
def instructions():
    return render_template('instructions.html')

@app.route('/compare', methods = ["POST", "GET"])
def compare():
    if request.method == 'POST':
        image1 = request.form['img1']
        image2 = request.form['img2']
        result = request.form['result']
        return render_template('compare.html', img1 = image1, img2 = image2, result = result)
    else:
        return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)


# <!-- <img src= "{{ url_for('static', filename = '/output_files/'+final_name) }}" alt="image 1 not found"/> -->
 