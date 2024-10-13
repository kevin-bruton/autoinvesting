from datetime import datetime
from db.common import query_one, mutate_one

def register_mt_trades_update ():
  now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
  evName = 'mt_trades_updated'
  sql = 'SELECT eventName from Updates where eventName = ?'
  exists = query_one(sql, (evName,))
  if not exists:
    sql = 'INSERT INTO Updates (eventName, eventDatetime) VALUES (?, ?)'
    return mutate_one(sql, (evName, now))
  else:
    sql = 'UPDATE Updates SET eventDatetime=? WHERE eventName=?'
    return mutate_one(sql, (now, evName))

def get_last_mt_trades_update ():
  evName = 'mt_trades_updated'
  sql = 'SELECT eventDatetime FROM Updates WHERE eventName = ?;'
  return query_one(sql, (evName,))

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
