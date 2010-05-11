from django.http import *
from spotlightdb.backend.models import *
from django.core.exceptions import *
from django.contrib.auth.decorators import *
import datetime
from matplotlib.dates import DateFormatter
from django.shortcuts import render_to_response

ROOTAPPDIR = "/home/max/spotlight/spotlightdb"

def index(request):
  return HttpResponse("Hello NESL, I'm watching you... BOO!")

def sensor_data_check(request, fieldsNeeded):
  
  #Ensure proper http request type
  if request.method != 'POST':
    return ['-1', 'FAIL: Request must be in the form of a POST...loser!']
  
  #Make sure all data is present in post
  for field in fieldsNeeded:
    if field not in request.POST:
      return ['-1', 'FAIL: Need a %s field...loser!' % field]

  #Make sure sensor exists in db
  try:
    #print "id = %s" % request.POST[fieldsNeeded[0]]
    s = Sensor.objects.get(id = int(request.POST[fieldsNeeded[0]]))
    #print 'sen_top = %s' % s
  except ObjectDoesNotExist: 
    return ['-1', 'FAIL: Sensor does not exist in DB']
  except MultipleObjectsReturned:
    return ['-1', 'FAIL: Query returned multiple vals not exist in DB']
  
  #It's all good...
  return ['0', 'No Error']

def loc_val_check(loc):
  for x in range(len(loc)):
    try:
      float(loc[x])
    except ValueError:
      loc[x] = '0'
  return loc

def calc_stats(str_data):
  #stats = min, max, avg
  stats = (0, 0, 0)

  return stats

def sensor_data(request):
  #print 'REQUEST == \n\n %s' % request
  #print 'TYPE = %s' % type(request)
  
  fieldsNeeded = ['sensorid', 'values', 'locationstamp', 'timestamp']

  #Make sure the post contains all necessary and valid params
  err = sensor_data_check(request, fieldsNeeded)
  if int(err[0]) is -1:
    #print "\n\nThere was an error found: %s " % err[1]
    return HttpResponse(err[1])

  #Create Location Entry
  locStamp = request.POST[fieldsNeeded[2]].replace(',', ' ')
  locStamp = loc_val_check(locStamp.split())
  loc = Location()
  loc.gpsX = locStamp[0]
  loc.gpsY = locStamp[1]
  loc.gpsH = locStamp[2]
  loc.gpsP = '0'
  loc.isMapping = False
  loc.save()

  #Get Sensor

  #Create Data Entry
  d = Data()
  d.location = loc
  d.timeStamp = request.POST[fieldsNeeded[3]]
  d.value = request.POST[fieldsNeeded[1]]
  (d.min, d.max, d.avg) = calc_stats(request.POST[fieldsNeeded[1]]) 

  #print 'req.POST[sensorID] = %s' % request.POST[fieldsNeeded[0]]
  #print 'Sensor = %s' %Sensor.objects.get(id = int(request.POST[fieldsNeeded[0]]))
  
  d.sensor = Sensor.objects.get(id = int(request.POST[fieldsNeeded[0]]))
  #print 'd.sensor = %s' % d.sensor
  d.save()

  if not int(err[0]):
    return HttpResponse("You just sent me data for a sensor %s, Max is no longer lazy..." % d.sensor.id)

def get_sensors(name):
  #Compile a list of sensors that name has any access to
  
  #Find out what groups name is a part of

  #Search all DataContributor XML files for name and groups it is apart of
  pass

#Currently if this Function returns no data there is an error!
def get_data(currSensor, name):
  #Get all Data for sensorID
  #Modify data based on name's access privleges
    #Find sensorID.owner's XML file and find rule for name and sensorID
    #Modify data of SensorID

  #But for now, we fake it.... ;)
  u = name
  data = ''
  ts = []
  allData = Data.objects.filter(sensor = currSensor)
  if (u == 'max') or (u == 'Haksoo') or (u == 'ContributorA'):
    #print "got the name right - %s" % currSensor.name
    if currSensor.sensorType.name == 'Accelerometer':
      for d in allData:
        timeStamp = d.timeStamp
        d = d.value
        d = d.replace(',', ' ')
        d = d.split()
        data += ("%s;%s;%s;%s\n" % (timeStamp, d[0], d[1], d[2]))
    
    elif currSensor.sensorType.name == 'ECG':
      for d in allData:
        timeStamp = d.timeStamp
        d = d.value
        d = d.replace(',', ' ')
        d = d.split()
        data += ("%s;%s;%s\n" % (timeStamp, d[0], d[1]))

  elif u == 'PersonA':
    if currSensor.sensorType.name == 'Accelerometer':
      for d in allData:
        if (d.timeStamp.hour > 9) and (d.timeStamp.hour < 18):
          timeStamp = d.timeStamp
          d = d.value
          d = d.replace(',', ' ')
          d = d.split()
          data += ("%s;%s;%s;%s\n" % (timeStamp, str(float(d[0])*2 + 10), str(float(d[1])*2 + 10), str(float(d[2])*2 + 10)))

    elif currSensor.sensorType.name == 'ECG':
      for d in allData:
        if (d.timeStamp.hour > 9) and (d.timeStamp.hour < 18):
          timeStamp = d.timeStamp
          d = d.value
          d = d.replace(',', ' ')
          d = d.split()
          data += ("%s;%s;%s\n" % (timeStamp, str(float(d[0])*2 + 10), str(float(d[1])*2 + 10)))

  else:
    data = -1

  return data

@login_required
def which_data(request):
  #print request.user
  retrString = '<ul>\n'
  u = str(request.user)
  if (u == 'max') or (u == 'Haksoo') or (u == 'ContributorA'):
    sen = Sensor.objects.all()
    for i in range(len(sen)):
      retrString += "<li><a href='/spotlight/sensordata/%s'>%s</a></li>\n" % (sen[i].id, '%s - %s' % (sen[i].owner, sen[i].name))
  elif u == 'PersonA':
    sen = Sensor.objects.get(id = 2)
    retrString += "<li><a href='/spotlight/sensordata/%s'>%s</a></li>\n" % (sen.id, '%s - %s' % (sen.owner, sen.name))
  else:
   retrString += str(request.user)
  retrString += '</ul>'
  return HttpResponse(retrString)

@login_required
def get_graph(request, sensor_id):
  if (str(request.user) == 'PersonA') and (sensor_id != '2'):
    return HttpResponse('You do not have any rights on this sensor...')
  
  # NEW - Plot Data w/ AmCharts
  return render_to_response("amline.html", {'sensorID': sensor_id})
  
  # OLD - Plot Data with matplotlib
  '''
  #Create graph of data
  fig = Figure()
  #plt.figure(1)
  if currSensor.sensorType.name == 'ECG':
    ax = fig.add_subplot(211)
    #ax.plot_date(data[0], data[1], '-')
    ax.plot_date(data[0][200:], data[1][200:], '-')
    ax.xaxis.set_major_formatter(DateFormatter('%H-%M-%S'))
    #ax.title = 'L Data'
    ax = fig.add_subplot(212)
    ax.plot_date(data[0][200:], data[2][200:], '-')
    #ax.plot_date(data[0], data[2], '-')
    ax.xaxis.set_major_formatter(DateFormatter('%H-%M-%S'))
    #ax.title = 'R Data'
  else:
    ax = fig.add_subplot(311)
    ax.plot_date(data[0][200:], data[1][200:], '-')
    ax.xaxis.set_major_formatter(DateFormatter('%H-%M-%S'))
    #ax.title = 'X Data'
    ax = fig.add_subplot(312)
    ax.plot_date(data[0][200:], data[2][200:], '-')
    ax.xaxis.set_major_formatter(DateFormatter('%H-%M-%S'))
    #ax.title = 'Y Data'
    ax = fig.add_subplot(313)
    #ax.plot_date(data[0], data[3], '-')
    ax.plot_date(data[0][200:], data[3][200:], '-')
    ax.xaxis.set_major_formatter(DateFormatter('%H-%M-%S'))
    #ax.title = 'Z Data'

  fig.suptitle(str(currSensor))
  
  fig.autofmt_xdate()
  canvas=FigureCanvas(fig)
  response=HttpResponse(content_type='image/png')
  canvas.print_png(response)
  '''


#@login_required
def amline_swfobject(request, url):
  #print url
  if url[len(url)-4:] == '.swf':
    with open("%s/template/amline/%s" % (ROOTAPPDIR, url)) as f:
      swfObject = f.read()
    response = HttpResponse(swfObject, content_type='application/x-shockwave-flash')
    return response
  
  return render_to_response("amline/%s" % url)

def amline_data(request, sensor_id):
  #Check request.user's permissions for sensor_id
  currSensor = Sensor.objects.get(id = int(sensor_id))
  data = get_data(currSensor, str(request.user))
  
  if data == -1:
    #print "Something went wrong..."
    return HttpResponse('Uh-oh')
    
  return HttpResponse(data, content_type = 'text/csv')

def amline_settings(request, sensor_id):
  newGraph = '''
  <graph gid="%d">                                           <!-- if you are using XML data file, graph "gid" must match graph "gid" in data file -->
                                                          
    <axis>%s</axis>                                       <!-- [left] (left/ right) indicates which y axis should be used -->
    <title>%s</title>                                  <!-- [] (graph title) -->
    <color>%s</color>                                  <!-- [] (hex color code) if not defined, uses colors from this array: #FF0000, #0000FF, #00FF00, #FF9900, #CC00CC, #00CCCC, #33FF00, #990000, #000066 -->
    <color_hover></color_hover>                             <!-- [#BBBB00] (hex color code) -->
    <line_alpha></line_alpha>                               <!-- [100] (0 - 100) -->
    <line_width></line_width>                               <!-- [0] (Number) 0 for hairline -->                                    
    <fill_alpha></fill_alpha>                               <!-- [0] (0 - 100) if you want the chart to be area chart, use bigger than 0 value -->
    <fill_color></fill_color>                               <!-- [grpah.color] (hex color code). Separate color codes with comas for gradient -->
    <balloon_color></balloon_color>                         <!-- [graph color] (hex color code) leave empty to use the same color as graph -->
    <balloon_alpha></balloon_alpha>                         <!-- [100] (0 - 100) -->      
    <balloon_text_color></balloon_text_color>               <!-- [#FFFFFF] (hex color code) -->
    <bullet></bullet>                                       <!-- [] (square, round, square_outlined, round_outlined, square_outline, round_outline, square_outline, round_outline, filename.swf) can be used predefined bullets or loaded custom bullets. Leave empty if you don't want to have bullets at all. Outlined bullets use plot area color for outline color -->
                                                            <!-- The chart will look for this file in "path" folder ("path" is set in HTML) -->
    <bullet_size></bullet_size>                             <!-- [8](Number) affects only predefined bullets, does not change size of custom loaded bullets -->
    <bullet_color></bullet_color>                           <!-- [graph color] (hex color code) affects only predefined (square and round) bullets, does not change color of custom loaded bullets. Leave empty to use the same color as graph  -->
    <bullet_alpha></bullet_alpha>                           <!-- [graph alpha] (hex color code) Leave empty to use the same alpha as graph -->      
    <hidden></hidden>                                       <!-- [false] (true / false) vill not be visible until you check corresponding checkbox in the legend -->
    <selected></selected>                                   <!-- [true] (true / false) if true, balloon indicating value will be visible then roll over plot area -->
    <balloon_text>
      <![CDATA[${value}]]>                                          <!-- [<b>{value}</b><br>{description}] ({title} {value} {series} {description} {percents}) You can format any balloon text: {title} will be replaced with real title, {value} - with value and so on. You can add your own text or html code too. -->
    </balloon_text>
    <data_labels>
      <![CDATA[]]>                                          <!-- [] ({title} {value} {series} {description} {percents}) Data labels can display value (and more) near your point on the plot area. -->
                                                            <!-- to avoid overlapping, data labels, the same as bullets are not visible if there are more then hide_bullets_count data points on plot area. -->                                                              
    </data_labels>  
    <data_labels_text_color></data_labels_text_color>       <!-- [text_color] (hex color code) --> 
    <data_labels_text_size></data_labels_text_size>         <!-- [text_size] (Number) -->
    <data_labels_position></data_labels_position>           <!-- [above] (below / above) -->            
    <vertical_lines></vertical_lines>                       <!-- [false] (true / false) whether to draw vertical lines or not. If you want to show vertical lines only (without the graph, set line_alpha to 0 -->
    <visible_in_legend></visible_in_legend>                 <!-- [true] (true / false) whether to show legend entry for this graph or not -->
  </graph>
  '''
  
  colors = ['#FF0000', '#0000FF', '#00FF00', '#FF9900', '#CC00CC', '#00CCCC', '#33FF00', '#990000', '#000066']

  #Check request.user's permissions for sensor_id
  currSensor = Sensor.objects.get(id = int(sensor_id))

  if (str(request.user) == 'PersonA') and (sensor_id != '2'):
    return HttpResponse('You do not have any rights on this sensor...')

  amSet = ''
  for i in range(currSensor.sensorType.numChannels):
    amSet += newGraph % (i, 'left', 'Channel %d' % i, colors[i])
 
  xmlFile = ''
  with open("%s/template/amline/amline_settings_NG.xml" % ROOTAPPDIR) as f:
    for line in f:
      xmlFile += line
      if line.find("<graphs>") != -1:
        xmlFile += amSet
      #if line.find("<data_type>") != -1:
      #  xmlFile += 'csv'
      if line.find("<!-- ENTER TITLE HERE -->") != -1:
        xmlFile += '<![CDATA[<b>%s - Owned By: %s</b>]]>' % (currSensor.name, currSensor.owner)
  
  return HttpResponse(xmlFile, content_type = 'text/xml')
