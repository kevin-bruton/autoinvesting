from os import getenv

import db
from auth import (admin_only, generate_user_token, token_required,
                  validate_token)
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from strategies_csv import save_strategies_csv, save_all_strategy_data
from werkzeug.middleware.proxy_fix import ProxyFix
from utils import get_upload_folders
from controllers import save_new_strategies, get_account_logs

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

@app.route('/api/users', methods=['GET'])
@token_required
def get_users_request(user):
  return (jsonify({'success': True, 'data': db.get_users()}), 200)

@app.route('/api/strategies', methods=['GET'])
@token_required
def get_strategies_request(user):
  return (jsonify({'success': True, 'data': db.get_strategies()}), 200)

@app.route('/api/subscriptions', methods=['GET'])
@token_required
def get_subscriptions_request(user):
  return (jsonify({'success': True, 'data': db.get_subscriptions()}), 200)

@app.route('/api/orders', methods=['GET'])
@token_required
def get_orders_request(user):
  return (jsonify({'success': True, 'data': db.get_orders()}), 200)

@app.route('/api/strategies/summary', methods=['GET'])
@token_required
def get_strategies_summaries_request(user):
  return (jsonify({'success': True, 'data': db.get_strategy_summaries()}), 200)

@app.route('/api/strategies/<strategy_id>', methods=['GET'])
@token_required
def get_strategy_request(user, strategy_id):
  if strategy_id == 'all':
    try:
      strategies = db.get_all_strategy_data_as_csv()
      return (strategies, 200)
    except Exception as e:
      return (jsonify({ 'error': repr(e) }), 200)
  else:
    try:
      strategy = db.get_strategy_detail(strategy_id)
      return (jsonify(strategy), 200)
    except Exception as e:
      return (jsonify({ 'error': repr(e) }), 200)

@app.route('/api/accounts', methods=['GET'])
@token_required
def get_accounts_request(user):
  return (jsonify({'success': True, 'data': db.get_accounts()}), 200)

@app.route('/api/trades', methods=['GET'])
@token_required
def get_trades(user):
  return (jsonify({'success': True, 'data': db.get_trades()}), 200)

@app.route('/api/user/accounts', methods=['GET'])
@token_required
def get_users_accounts_request(user):
  account_ids = db.get_users_account_ids(user['username'])
  return (jsonify({'success': True, 'data': account_ids }), 200)

@app.route('/api/account/<account_id>/orders', methods=['GET'])
@token_required
def get_account_orders_request(user, account_id):
  orders = db.get_account_orders(account_id)
  return (jsonify({'success': True, 'data': orders}))

@app.route('/api/account/<account_id>/trades', methods=['GET'])
@token_required
def get_accounts_trades(user, account_id):
  trades = db.get_account_trades(account_id)
  return (jsonify({'success': True, 'data': trades}), 200)

@app.route('/api/account/<account_id>/logs', methods= ['GET'])
@token_required
def get_account_logs_request(user, account_id):
  log = get_account_logs(account_id)
  return log

@app.route('/api/account/<account_id>/connection-status', methods=['GET'])
@token_required
def get_account_connection_status(user, account_id):
  status = db.get_account_connection_status(account_id)
  return (jsonify({'success': True, 'data': status}), 200)

@app.route('/api/account/<account_id>/subscribe', methods=['POST'])
@token_required
def subscribe_to_strategies(user, account_id):
  magics = request.get_json()
  try:
    db.update_subscriptions(account_id, magics)
    return (jsonify({'success': True}))
  except Exception as e:
    return (jsonify({'error': repr(e)}), 200)

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

@app.route('/api/strategies-json', methods=['POST'])
@admin_only
def save_all_strategy_data_request(user):
  results = save_all_strategy_data(request.get_data(as_text=True))
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

@app.route('/api/save-new-strategies', methods=['POST'])
@admin_only
def save_new_strategies_request(user):
  try:
    data = request.get_json()
    result = save_new_strategies(data['uploadFolder'])
    return (jsonify({'message': 'Saved new strategies successfully'}), 200)
  except Exception as e:
    print(repr(e))
    return(jsonify({'error': repr(e)}), 200)

@app.route('/api/upload-folders', methods=['GET'])
@admin_only
def get_upload_folders_request(user):
  try:
    folders = get_upload_folders()
    return (jsonify({'succes': True, 'data': folders}))
  except Exception as e:
    print(repr(e))
    return(jsonify({'error': repr(e)}), 200)

@app.route('/api/updates/last', methods=['GET'])
@token_required
def get_last_update_request(user):
  try: 
    last_update = db.get_last_update()
    return (jsonify({ 'success': True, 'data': last_update }))
  except Exception as e:
    return (jsonify({ 'error': repr(e) }), 200)

if __name__ == '__main__':
    app.run()

