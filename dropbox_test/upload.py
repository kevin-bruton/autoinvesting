import requests

token = 'sl.BLUtvDl8lFtDGXMa6lxyD5pdZ3ApwNSw-uu5Ib4h_qp1BlGjMr7RIjsblH8fDvQyWgjPuH8-eQYhGLOQCHbK0VjWIkIqRyNbK4xvW0R5mgNMPFcGrNzwKfY5CQL_Xc_W8og-YTk'
filepath = './sample_expenses.zip'
file_destination = '/mq4/my_strategy.zip'
url = 'https://content.dropboxapi.com/2/files/upload'
headers = {
  'Authorization': 'Bearer ' + token,
  'Dropbox-API-Arg': '{"autorename":false,"mode":"add","mute":false,"path":"' + file_destination + '","strict_conflict":false}',
  'Content-Type': 'application/octet-stream'
}

with open(filepath, 'rb') as f:
  data = f.read()
  res = requests.post(url=url, data=data, headers=headers)
  print(res.status_code)
  print(res.text)
