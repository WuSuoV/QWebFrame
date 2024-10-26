from flask import Flask

from config import database, cors
from utils import my_response
from views import blueprints

app = Flask(__name__)

database.init_app(app)
database.migrate.init_app(app)
cors.init_app(app)

for blueprint in blueprints:
    app.register_blueprint(blueprint)


@app.route('/')
def index():
    return my_response(msg='首页')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
