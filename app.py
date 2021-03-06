from flask import Flask
from flask import render_template, request, make_response
from werkzeug.utils import secure_filename
from PIL import Image, ExifTags
import uuid
from simples3 import S3Bucket
import StringIO

app = Flask(__name__)
app.config.from_object('settings')


@app.route('/')
def home():
    return render_template('upload.html')


@app.route('/upload/profile/user/', methods=['POST', 'OPTIONS'])
def upload_profile_image():
    if request.method == "OPTIONS":
        response = make_response("")
        response.headers['Access-Control-Allow-Origin'] = "*"
        response.headers['Access-Control-Allow-Method'] = "GET, POST"
        response.headers['Access-Control-Allow-Headers'] = "X-Custom-Header"
        return response
    else:
        file = request.files['file']
        url = ''
        if file and allowed_file(file.filename):
            filename = secure_filename(str(uuid.uuid4()) + ".jpg")
            temp = StringIO.StringIO()
            try:
                im = Image.open(file)
                if im.mode != "RGB":
                    im = im.convert("RGB")
                if hasattr(im, '_getexif'): # only present in JPEGs
                    for orientation in ExifTags.TAGS.keys():
                        if ExifTags.TAGS[orientation] == 'Orientation':
                            break
                    e = im._getexif()       # returns None if no EXIF data
                    if e is not None:
                        exif = dict(e.items())
                        orientation = exif[orientation]

                        if orientation == 3:   im = im.transpose(Image.ROTATE_180)
                        elif orientation == 6: im = im.transpose(Image.ROTATE_270)
                        elif orientation == 8: im = im.transpose(Image.ROTATE_90)
                im.thumbnail((app.config['PROFILE_IMAGE_SIZE'], app.config['PROFILE_IMAGE_SIZE']), Image.ANTIALIAS)
                im.save(temp, "JPEG")
                url = upload_to_s3(temp.getvalue(), filename)
            except IOError as e:
                return "{error: '" + str(e) + "' }"
            response = make_response(url)
            response.headers['Access-Control-Allow-Origin'] = "*"
            return response
        else:
            return "{error: 'Could not upload file.'}"


def upload_to_s3(file, filename):
    """
    upload contents to s3, and return the url
    """
    s = S3Bucket(app.config['BUCKET'], access_key=app.config['ACCESS_KEY'],
                secret_key=app.config['SECRET_KEY'], base_url=app.config['BASE_URL'] + '/' + app.config['BUCKET'])
    s.put(filename, file)
    return app.config['BASE_URL'] + '/' + app.config['BUCKET'] + '/' + filename


def allowed_file(filename):
    return '.' in filename and \
           get_extension(filename) in app.config['ALLOWED_EXTENSIONS']


def get_extension(filename):
    return filename.rsplit('.', 1)[1]


if __name__ == '__main__':
    app.run(port=8000, debug=True)
