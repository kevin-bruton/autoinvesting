from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from os import getenv
from flask_cors import CORS
from auth import generate_user_token, validate_token, token_required, admin_only
from upload_file import upload_file
import db
from utils import get_kpis
from strategies_csv import save_strategies_csv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": getenv('ORIGIN')}})
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

@app.route('/')
def hello_world():
    return 'Auto Investing API'


@app.route('/api/authenticate', methods=['POST']) 
def authenticate_request():
  req = request.get_json()
  host = request.environ['HTTP_HOST']

  if not req or not req['username'] or not req['passwd']:
    return (jsonify({'error': 'Credentials not provided'}), 401)

  try:
    token = generate_user_token(req['username'], req['passwd'], host)
    return (jsonify({'t' : token}), 200)
  except Exception as e:
    print('CAUGHT ERROR: ', e)
    return (jsonify({'error': str(e)}), 401)

@app.route('/api/validate', methods=['GET'])
def validate_request():
  try:
    validate_token(request.headers)
    return (jsonify({'message': 'OK'}), 200)
  except Exception as e:
    return (jsonify({'error': str(e)}), 401)

@app.route('/api/strategies', methods=['GET'])
@token_required
def get_strategies_request(user):
  return (jsonify({'success': True, 'data': db.get_strategies()}), 200)

@app.route('/api/strategies/<strategy_id>', methods=['GET'])
@token_required
def get_strategy_request(user, strategy_id):
  try:
    strategy = db.get_strategy_detail(strategy_id)
    return (jsonify(strategy), 200)
  except Exception as e:
    return (jsonify({ 'error': repr(e) }), 200)

@app.route('/api/strategies', methods=['POST'])
@admin_only
def save_strategy_request(user):
  try:
    db.save_strategy(request.get_json())
    return (jsonify({'message': 'Saved strategy successfully'}), 200)
  except Exception as e:
    error_msg = repr(e)
    if 'Duplicate entry' in error_msg:
      error_msg = error_msg[error_msg.find('Duplicate entry') : error_msg.find(' for key')]
    return (jsonify({'error': error_msg}), 200)

@app.route('/api/strategies-csv', methods=['POST'])
@admin_only
def save_strategies_csv_request(user):
  results = save_strategies_csv(request.get_data(as_text=True))
  return (jsonify(results), 200)

@app.route('/api/files', methods=['POST'])
@admin_only
def upload_file_request(user):
  try:
    upload_file(user, request)
    return (jsonify({'message': 'File uploaded successfully'}))
  except Exception as e:
    return (jsonify({'error': repr(e)}), 200)

@app.route('/api/backtest', methods=['POST'])
@admin_only
def save_backtest_request(user):
  try:
    data = request.get_json()
    # add kpis to data ?
    db.save_backtest(data)
    return (jsonify({'message': 'Saved backtest successfully'}), 200)
  except Exception as e:
    print(repr(e))
    return(jsonify({'error': repr(e)}), 200)


if __name__ == '__main__':
    app.run()

