from django.test.client import Client
c = Client()
resp = c.post('/spotlight/sensor/', {'sensorid': '1', 'values': 'this is just a test 1', 'locationstamp': '324.21321321,454.2342432,NULL', 'timestamp': '2009-11-04 01:35:00'})
resp = c.post('/spotlight/sensor/', {'sensorid': '4', 'values': 'this is just a test 2', 'locationstamp': '323.21321321,454.2342432,NULL', 'timestamp': '2009-11-04 01:34:00'})
resp = c.post('/spotlight/sensor/', {'sensorid': '1', 'values': 'this is just a test 3', 'locationstamp': '325.21321321,454.2342432,NULL', 'timestamp': '2009-11-04 01:33:00'})
resp = c.post('/spotlight/sensor/', {'sensorid': '4', 'values': 'this is just a test 4', 'locationstamp': '326.21321321,454.2342432,NULL', 'timestamp': '2009-11-04 01:32:00'})

