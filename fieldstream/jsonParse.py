import json

class WaveSegObject:
    def __init__(self, waveseg_json):
        self.start_time = waveseg_json['StartTime']
        self.sampling_interval = waveseg_json['SamplingInterval']
        self.static_location = waveseg_json['StaticLocation']
        self.value_blob_format = waveseg_json['ValueBlobFormat']
        self.value_blob = waveseg_json['ValueBlob']
        self.value_blob_statistics = { 'MIN': [], 'MAX': [], 'MEAN': [], 'MEDIAN': [], 'STD': [] }
        
class WaveSegSeriesObject:
    def __init__(self, waveseg_series_json):
      self.waveseg_series = waveseg_series_json['WaveSegSeries']
      if 'APIKey' in waveseg_series_json:
				self.apiKey = waveseg_series_json['APIKey']
      self.waveseg = []
      waveseg_list = waveseg_series_json['WaveSeg']
      for waveseg in waveseg_list:
          self.waveseg.append(WaveSegObject(waveseg))

def JSONtoDB(json_input):
    #json_input = json_input.strip('\t\n')
    json_input = json_input.replace("\n", '')
    json_input = json_input.replace("\t", '')
    
    json_obj = json.loads(json_input)

    #TODO This is a hack! - for some reason plus signs get stripped out of key? 
    json_obj['APIKey'] = json_obj['APIKey'].replace(' ', '+')
    for i in range(3):
      keyList = list(json_obj['APIKey'])
      first = json_obj['APIKey'].find('+')
      last = json_obj['APIKey'].rfind('+')
      keyList[first] = ' '
      keyList[last] = ' '
      json_obj['APIKey'] = "".join(keyList)

    t =  WaveSegSeriesObject(json_obj)
    return t

def DBtoJSON(waveseg_series):
    json_obj = {}
    json_obj['WaveSegSeries'] = waveseg_series.waveseg_series
    if hasattr(waveseg_series, 'apiKey'):
	    json_obj['APIKey'] = waveseg_series.apiKey 
    json_obj['WaveSeg'] = []

    for waveseg in waveseg_series.waveseg:
        waveseg_dict = {}
        waveseg_dict['StartTime'] = waveseg.start_time
        waveseg_dict['SamplingInterval'] = waveseg.sampling_interval
        waveseg_dict['StaticLocation'] = waveseg.static_location
        waveseg_dict['ValueBlobFormat'] = waveseg.value_blob_format
        waveseg_dict['ValueBlob'] = waveseg.value_blob
        waveseg_dict['ValueBlobStatistics'] = waveseg.value_blob_statistics
        json_obj['WaveSeg'].append(waveseg_dict)

    #return json.dumps(json_obj, sort_keys=True, indent=2)
    return json.dumps(json_obj)

def cleanJSON(json_input):
    #json_input = json_input.strip('\t\n')
    json_input = json_input.replace("\n", '')
    json_input = json_input.replace("\t", '')
    
    json_obj = json.loads(json_input)

    #TODO This is a hack! - for some reason plus signs get stripped out of key? 
    json_obj['APIKey'] = json_obj['APIKey'].replace(' ', '+')
    for i in range(3):
      keyList = list(json_obj['APIKey'])
      first = json_obj['APIKey'].find('+')
      last = json_obj['APIKey'].rfind('+')
      keyList[first] = ' '
      keyList[last] = ' '
      json_obj['APIKey'] = "".join(keyList)

    return json_obj
'''
# test script
filename = 'example_upload.json'
fp = open(filename, 'r')
json_string = fp.read()

waveseg_series = JSONtoDB(json_string)

fp.close()

print waveseg_series.waveseg_series

print waveseg_series.waveseg[0].start_time
print waveseg_series.waveseg[0].sampling_interval
print waveseg_series.waveseg[0].static_location
print waveseg_series.waveseg[0].value_blob_format
print waveseg_series.waveseg[0].value_blob
#print waveseg_series.waveseg[0].value_blob_statistics

print waveseg_series.waveseg[1].start_time
print waveseg_series.waveseg[1].sampling_interval
print waveseg_series.waveseg[1].static_location
print waveseg_series.waveseg[1].value_blob_format
print waveseg_series.waveseg[1].value_blob
#print waveseg_series.waveseg[1].value_blob_statistics

json_string = DBtoJSON(waveseg_series)
print json_string
'''
