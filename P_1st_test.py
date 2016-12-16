from flask import *
from mongoengine import *
from os import *
from werkzeug.utils import secure_filename

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login')
@app.route('/signup')
def register():
    return url_for()


if __name__ == '__main__':
    app.run()
