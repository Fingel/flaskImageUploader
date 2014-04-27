import os

UPLOAD_FOLDER = '/uploads'  # empty this directory every few minutes
ALLOWED_EXTENSIONS = set(['png', 'jpg'])
PROFILE_IMAGE_SIZE = 128  # width and height

try:
    ACCESS_KEY = os.environ["ACCESS_KEY"]
    SECRET_KEY = os.environ["SECRET_KEY"]
    BUCKET = 'whatsgoodaustin/images'
    BASE_URL = 'https://s3-us-west-1.amazonaws.com'
except KeyError:
    pass

try:
    from local_settings import *
except ImportError:
    pass
