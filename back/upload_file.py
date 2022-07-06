from werkzeug.utils import secure_filename
from os.path import join, exists

ALLOWED_EXTENTIONS = {'mq4', 'sqx'}

def upload_file(user, request):
  if 'file' not in request.files:
    raise Exception('File not provided')
  file = request.files['file']
  if file.filename == '':
    raise Exception('File not provided')
  if '.' not in file.filename:
    raise Exception('File does not have an exception')
  file_extension = file.filename.rsplit('.', 1)[1].lower()
  if file_extension not in ALLOWED_EXTENTIONS:
    raise Exception('File type not allowed')
  if user['accountType'] != 'admin':
    raise Exception('User does not have permission')
  filename = secure_filename(file.filename)
  upload_folder = './back/files/mq4' if file_extension == 'mq4' else './back/files/sqx'
  filepath = join(upload_folder, filename)
  if exists(filepath):
    raise Exception('File already exists')
  try:
    file.save(join(upload_folder, filename))
  except Exception as e:
    raise Exception('Error saving file: ' + repr(e))


