from flask_cors import CORS

from utils import my_config

cors = CORS(
    resources={r'/*': {'origins': my_config('cors', 'origins')}},
    supports_credentials=True
)
