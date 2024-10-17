from datetime import datetime
from db.common import query_one, mutate_one

def register_mt_trades_update (account_id):
  now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
  evName = 'mt_trades_updated'
  sql = 'SELECT eventName from Updates where eventName = ? AND filename = ?'
  exists = query_one(sql, (evName, account_id))
  if not exists:
    sql = 'INSERT INTO Updates (eventName, eventDatetime, filename) VALUES (?, ?, ?)'
    return mutate_one(sql, (evName, now, account_id))
  else:
    sql = 'UPDATE Updates SET eventDatetime=? WHERE eventName=? AND filename=?'
    return mutate_one(sql, (now, evName, account_id))

def get_last_mt_trades_update (account_id):
  evName = 'mt_trades_updated'
  sql = 'SELECT eventDatetime FROM Updates WHERE eventName = ? AND filename = ?;'
  return query_one(sql, (evName, account_id))

def register_mc_logfile_modified_ts (logfilepath, modified_ts):
  prev_modified_ts = get_mc_logfile_modified_ts(logfilepath)
  evName = 'mc_logfile_modified'
  if prev_modified_ts:
    sql = ''' UPDATE Updates
              SET eventDatetime=?
              WHERE eventName = ? AND filename=?'''
    return mutate_one(sql, (modified_ts, evName, logfilepath))
  else:
    sql = '''INSERT INTO Updates (eventName, eventDatetime, filename) VALUES (?, ?, ?)'''
    return mutate_one(sql, (evName, modified_ts, logfilepath))

def get_mc_logfile_modified_ts (logfilepath):
  evName = 'mc_logfile_modified'
  sql = '''
    SELECT eventDatetime
    FROM Updates
    WHERE eventName = ? AND filename = ?
    '''
  result = query_one(sql, (evName,logfilepath))
  if not result: return ''
  return result['eventDatetime']

def register_mc_logfile_entry_read_ts (logfilepath, logentry_ts):
  prev_logentry_ts = get_mc_logfile_entry_read_ts(logfilepath)
  evName = 'mc_logfile_entry_read'
  if prev_logentry_ts:
    sql = ''' UPDATE Updates
              SET eventDatetime=?
              WHERE eventName=? AND filename=?'''
    return mutate_one(sql, (logentry_ts, evName, logfilepath))
  else:
    sql = '''INSERT INTO Updates (eventName, eventDatetime, filename) VALUES (?,?,?)'''
    return mutate_one(sql, (evName, logentry_ts, logfilepath))

def get_mc_logfile_entry_read_ts (logfilepath):
  evName = 'mc_logfile_entry_read'
  sql = '''
    SELECT eventDatetime FROM Updates
    WHERE eventName = ? AND filename = ?
    '''
  result = query_one(sql, (evName,logfilepath))
  if not result: return ''
  return result['eventDatetime']
