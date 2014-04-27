from flask import Flask
from flask import render_template, request
from werkzeug.utils import secure_filename
from PIL import Image
import uuid
from simples3 import S3Bucket
from flask_cors import cross_origin

app = Flask(__name__)
app.config.from_object('settings')


@app.route('/')
def home():
    return render_template('upload.html')


@cross_origin()
@app.route('/upload/profile/user/', methods=['POST'])
def upload_profile_image():
    file = request.files['file']
    url = ''
    if file and allowed_file(file.filename):
        filename = secure_filename(str(uuid.uuid4()) + ".jpg")
        save_dir = app.root_path + app.config['UPLOAD_FOLDER'] + '/'
        image_path = save_dir + filename
        file.save(image_path)
        try:
            im = Image.open(image_path)
            if im.mode != "RGB":
                im = im.convert("RGB")
            im.thumbnail((app.config['PROFILE_IMAGE_SIZE'], app.config['PROFILE_IMAGE_SIZE']))
            im.save(image_path, "JPEG")
            url = upload_to_s3(image_path, filename)
        except IOError as e:
            return "{error: '" + str(e) + "' }"
        return url
    else:
        return "{error: 'Could not upload file.'}"


def upload_to_s3(file, filename):
    """
    upload a file to s3, and return the url
    """
    s = S3Bucket(app.config['BUCKET'], access_key=app.config['ACCESS_KEY'],
                secret_key=app.config['SECRET_KEY'], base_url=app.config['BASE_URL'] + '/' + app.config['BUCKET'])
    to_upload = open(file)
    s.put(filename, to_upload.read())
    return app.config['BASE_URL'] + '/' + app.config['BUCKET'] + '/' + filename


def allowed_file(filename):
    return '.' in filename and \
           get_extension(filename) in app.config['ALLOWED_EXTENSIONS']


def get_extension(filename):
    return filename.rsplit('.', 1)[1]


if __name__ == '__main__':
    app.run(port=8080, debug=True)