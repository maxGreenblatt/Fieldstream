from django.http import *
from spotlightdb.fieldstream.models import *
from spotlightdb.fieldstream.forms import *
from django.core.exceptions import *
from django.contrib.auth.decorators import *
from django.contrib.auth.models import User as authUser
from django.contrib.auth import authenticate
import datetime
from matplotlib.dates import DateFormatter
from django.shortcuts import render_to_response
from django.template import RequestContext
import math
import time
import spotlightdb.fieldstream.jsonParse as jsonParse
import spotlightdb.fieldstream.privacy as privacy
import numpy
import paramiko
import json

ROOTAPPDIR = "/home/max/spotlight/spotlightdb"

def index(request):
  return render_to_response("%s/template/main.html" % ROOTAPPDIR, context_instance=RequestContext(request))

def register(request, url=None):
  if request.method == 'POST':
    form = UserRegistrationForm(request.POST)
    
    if form.is_valid():
      #Add User

      #Make sure passwords match
      if form.data['password'] != form.data['confirm_Password']:
        return HttpResponseRedirect('/register/PASSWORDSNOMATCH')
      
      # Mke sure username is available and email is not already in system
      newUser = 0
      newEmail = 0
      try:
        authUser.objects.get(username__exact=form.data['username'])
      except ObjectDoesNotExist:
        newUser = 1
      try:
        authUser.objects.get(email__exact=form.data['email'])
      except ObjectDoesNotExist:
        newEmail = 1
      
      if newUser == 0:
        return HttpResponseRedirect('/register/NAMEALREADYINUSE')
      
      if newEmail == 0:
        return HttpResponseRedirect('/register/EMAILALREADYINUSE')
      
      newSubject = authUser.objects.create_user(form.data['username'], form.data['email'], form.data['password'])
      
      newSubject.first_name = form.data['first_Name']
      newSubject.last_name = form.data['last_Name']
      newSubject.save()

      # User Profile
      # Generate SSH Keys
      keyName = '%s/ssh_keys/%s_rsa' % (ROOTAPPDIR, form.data['username'])
      sshKey = paramiko.RSAKey.generate(2048)
      
      sshKey.write_private_key_file(keyName)
      with open(keyName) as f:
        privKey = f.read()
      
      privKey = privKey.strip('\n\t')
      privKey = privKey.replace("\n", "")
      privKey = privKey.replace("\t", "")
      newProf = UserProfile(userID = newSubject, isGroup = False, privAPIKey = privKey, pubAPIKey = "ssh-rsa %s" % sshKey.get_base64())
      newProf.save()

      return HttpResponseRedirect('/register/thanks')
  else:
    if url != None:
      # TODO figure out how to do errors
      pass
    form = UserRegistrationForm()

  return render_to_response("%s/template/registration/registration.html" % ROOTAPPDIR, {'form': form, }, context_instance=RequestContext(request))

@login_required
def update_prof(request, url=None):
  if request.method == 'POST':
    form = UserRegistrationForm(request.POST)
    
    if form.is_valid():
      #Update User
      
      #Authenticate the user...
      user = authenticate(username = request.user, password = form.data['old_Password'])
      if user is None:
        return HttpResponseRedirect('/userprof/NOREAUTH')
      
      #Try to change passwords if desired
      if form.data['new_Password'] != '' and form.data['confirm_Password'] != '':
        if form.data['new_Password'] != form.data['old_Password'] and form.data['new_Password'] == form.data['confirm_Password']:
          request.user.set_password(form.data['new_Password'])
          request.user.save()
          return HttpResponseRedirect('/userprof/PASSWORDCHANGESUCCESS')
        else:
          return HttpResponseRedirect('/userprof/PASSWORDCHANGEFAIL')
      
      # Mke sure username is available and email is not already in system
      newEmail = 0
      try:
        authUser.objects.get(email__exact=form.data['email'])
      except ObjectDoesNotExist:
        newEmail = 1
      
      if newEmail == 0:
        return HttpResponseRedirect('/userprof/EMAILALREADYINUSE')
      else:
        request.user.email = form.data['email']
        request.user.save()
        return HttpResponseRedirect('/userprof/EMAILALUPDATE')

      newSubject.first_name = form.data['first_Name']
      newSubject.last_name = form.data['last_Name']
      newSubject.save()

      return HttpResponseRedirect('/userprof/NAMECHANGE')
  else:
    if url != None:
      # TODO figure out how to do errors
      pass
    data = {'first_Name': request.user.first_name, 'last_Name': request.user.last_name, 'email': request.user.email} 
    form = UserProfUpdateForm(initial=data)
    prof = UserProfile.objects.get(userID__exact=request.user.id)

  return render_to_response("%s/template/profile.html" % ROOTAPPDIR, {'form': form, 'username': request.user.username, 'APIKey': prof.privAPIKey, }, context_instance=RequestContext(request))


def sensor_data_check(request, fieldsNeeded):
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

def epochToDjangoTime(t):
  gmt = time.gmtime(t)
  tFrac = str(t - math.floor(t))
  tFrac = tFrac[2:7]
  t = time.strftime("%Y-%m-%d %H:%M:%S", gmt)
  t = t + ".%s" % tFrac
  return t

def upload_data(request):
  if request.method != 'POST' or not request.is_secure():
    return HttpResponseBadRequest("Request must be a HTTPS post!")
  else:
    try:
      jsonObj = request.POST['Data']
    except KeyError:
      HttResponseBadRequest("Your POST object didn't contain an item with a key = 'Data'")
    try:
      jsonObj = jsonParse.cleanJSON(jsonObj)
    except KeyError:
      HttResponseBadRequest("Your POST object didn't contain an item with a key = 'APIKey'")
    # Test Key Authentication
    try:
      userProf = UserProfile.objects.get(privAPIKey__exact = jsonObj['APIKey'])
    except ObjectDoesNotExist:
      return HttpResponseBadRequest("Bad Key! Your key is = \n%s" % jsonObj['APIKey'])
    # Make sure this user owns this SensorNode
    try:
      currSN = SensorNode.objects.get(id__exact = jsonObj['SensorNode'])
      if userProf.userID != currSN.owner:
        return HttpResponseBadRequest("You do not own this sensor and therefore cannot add data to it")
    except ObjectDoesNotExist:
      return HttpResponseBadRequest("Wave Seg Series must be created in web UI before adding data to it!")
    # Try to get the WSS by name instead of ID as above
    except ValueError:
      try:
        currSN = SensorNode.objects.filter(owner__exact = userProf.userID).get(name__exact = jsonObj['SensorNode'])
        if userProf.userID != currSN.owner:
          return HttpResponseBadRequest("You do not own this sensor and therefore cannot add data to it")
      except ObjectDoesNotExist:
        return HttpResponseBadRequest("Wave Seg Series must be created in web UI before adding data to it!")
    for seg in jsonObj['WaveSeg']:
      ws = WaveSeg()
      ws.sensorNode_id = currSN.id
      try:
        ws.valuesFormat = '''%s''' % json.dumps(seg['ValueBlobFormat'])
        currNodeChan = SensorChannel.objects.filter(sensorNode__exact = currSN).values_list('name', flat=True)
        for chan in seg['ValueBlobFormat']:
          if chan not in currNodeChan:
            return HttpResponseBadRequest("%s is not a known channel for sensor %s" % (chan, currSN))
      except KeyError:
        return HttpResponseBadRequest("Could not find necessary ValueBlobFormat key")
      try:
        ws.values = '''%s''' % json.dumps(seg['ValueBlob'])
      except KeyError:
        return HttpResponseBadRequest("Could not find necessary ValueBlob key")
      try:
        if seg['SamplingInterval'] != None:
          ws.sampleInterval = float(seg['SamplingInterval'])
          isPeriodic = True
        else:
          isPeriodic = False
      except KeyError:
        isPeriodic = False
      try:
        wsST = float(seg['StartTime'])
        ws.startTime = epochToDjangoTime(wsST)
      except (KeyError, TypeError):
        try:
          timeVar = seg['ValueBlobFormat'].index('Time')
        except ValueError:
          timeVar = len(seg['ValuesBlobFormat'])
        wsST = float(seg['ValueBlob'][0][timeVar])
        ws.startTime = epochToDjangoTime(wsST)
      try:
        ws.endTime = epochToDjangoTime(float(seg['EndTime']))
      except (KeyError, TypeError):
        # Pull from the last value in Values or Calculate from start time and sample interval
        # Throw an error if you can't do one of the above two things
        if isPeriodic:
          ws.endTime =  epochToDjangoTime(wsST + float(ws.sampleInterval) * len(seg['ValueBlob']))
        else:
          try:
            timeVar = seg['ValueBlobFormat'].index('Time')
          except ValueError:
            timeVar = len(seg['ValueBlobFormat'])
          ws.endTime = epochToDjangoTime(float(seg['ValueBlob'][len(seg['ValueBlob']) - 1][timeVar]))
      try:
        if seg['StaticLocation'] != None:
          ws.staticLocationX = float(seg['StaticLocation']['X'])
      except KeyError:
        pass
      try:
        if seg['StaticLocation'] != None:
          ws.staticLocationY = float(seg['StaticLocation']['Y'])
      except KeyError:
        pass
      try:
        if seg['StaticLocation'] != None:
          ws.staticLocationH = float(seg['StaticLocation']['Z'])
      except KeyError:
        pass
      ws.save()

      # Add statistic calculations!
      # Check how many channels should be in each value set
      snChannels = SensorChannel.objects.order_by('id').filter(sensorNode__exact = currSN)
      
      #Set up list for statistics
      stats = []
      nonNumericChanName = []
      nonNumericChan = []
      for chan in range(len(snChannels)):
        stats.append([])
        if snChannels[chan].isNonNumeric:
          nonNumericChanName.append(snChannels[chan].name)
          nonNumericChan.append(snChannels[chan])

      # For each value set check how many channels there are
      # If any value == NULL drop it
      numValues = len(seg['ValueBlobFormat'])
      idx = 0
      for valSet in seg['ValueBlob']:
        if len(valSet) < numValues or len(valSet) > numValues + 4:
          return HttpResponseBadRequest("JSON Object not properly formatted")
        
        for chan in range(numValues):
          if valSet[chan] != 'NULL' and valSet[chan] != None:
            try:
              stats[chan].append(float(valSet[chan]))
            except ValueError:
              if seg['valueBlobFormat'][idx] not in nonNumericChanName:
                return HttpResponseBadRequest('All Values Must Be Numerical!!!')
              else:
                nameIDX = nonNumericChanName.index(seg['valueBlobFormat'][idx])
                currEnum = json.loads(nonNumericChan[nameIDX].nonNumericEnum)
                if valSet[chan] not in currEnum:
                  valSet[chan] = 'Null'
                else:
                  enumIDX = currEnum.index(valSet[chan])
                  valSet[chan] = enumIDX
                  stats[chan] = enumIDX
            except IndexError:
              return HttpResponseBadRequest('Too Many Channels for this Wave Segment Series')
        # There can be up to 4 extra channels that correspond to Time, X, Y, Z
        # If location changes there must at least be a NULL place holder for time
        if len(valSet) > numValues:
          for chan in range(numValues, len(valSet)):
            if valSet[chan] != 'NULL' and valSet[chan] != None:
              try:
                stats[chan].append(float(valSet[chan]))
              except ValueError:
                if seg['valueBlobFormat'][idx] not in nonNumericChanName:
                  return HttpResponseBadRequest('All Values Must Be Numerical!!!')
                else:
                  nameIDX = nonNumericChanName.index(seg['valueBlobFormat'][idx])
                  currEnum = json.loads(nonNumericChan[nameIDX].nonNumericEnum)
                  if valSet[chan] not in currEnum:
                    valSet[chan] = 'Null'
                  else:
                    enumIDX = currEnum.index(valSet[chan])
                    valSet[chan] = enumIDX
                    stats[chan] = enumIDX
              except IndexError:
                return HttpResponseBadRequest('Too Many Channels for this Wave Segment Series')
        idx += 1

      # This is for when the previous for-loop updates ValueBlob
      ws.values = '''%s''' % json.dumps(seg['ValueBlob'])
      ws.save()
      
      # Calc Stats for each channel
      for chan in range(len(stats)):
        currSN = snChannels[0].sensorNode
        if chan < numValues:
          chanID = SensorChannel.objects.order_by('id').filter(sensorNode__exact = currSN).get(name__exact = seg['ValueBlobFormat'][chan])
        else:
          over = chan - len(snChannels)
          if over == 0:
            chanID = SensorChannel.objects.order_by('id').filter(sensorNode__exact = currSN).get(name__exact = 'Time')
          elif over == 1:
            chanID = SensorChannel.objects.order_by('id').filter(sensorNode__exact = currSN).get(name__exact = 'X')
          elif over == 2:
            chanID = SensorChannel.objects.order_by('id').filter(sensorNode__exact = currSN).get(name__exact = 'Y')
          elif over == 3:
            chanID = SensorChannel.objects.order_by('id').filter(sensorNode__exact = currSN).get(name__exact = 'Z')
        
        newStat = Statistics()
        newStat.waveSegID = ws
        newStat.channelID = chanID
        
        if newStat.channelID.isNonNumeric:
          data = {}
          
          for i in range(len(stats[chan])):
            if stats[chan][i] in data:
              data[stats[chan][i]] += 1
            else:
              data[stats[chan][i]] = 1
          sortData = sorted(data.iteritems(), key=lambda (k,v): (v,k))
          
          newStatNN = StatisticsNonNumeric()
          newStatNN.waveSegID = ws
          newStatNN.channelID = chanID
          newStatNN.sortedData = sortData
          newStatNN.save()

        else:
          chanStats = numpy.array(stats[chan])
          if chanStats.size > 0:
            newStat.min = chanStats.min()
            newStat.max = chanStats.max()
            newStat.mean = chanStats.mean()
            newStat.median = numpy.median(chanStats)
            newStat.std = chanStats.std()
            newStat.save()
  
  return HttpResponse("Data Upload Succesful")
  
@login_required
def get_sensors(name):
  #Compile a list of sensors that name has any access to
  
  #Find out what groups name is a part of

  #Search all DataContributor XML files for name and groups it is apart of
  pass

def get_data(request):
  if request.method != 'POST' or not request.is_secure():
    return HttpResponseBadRequest("Request must be a HTTPS post!")
  else:
    #if 'data' in request.POST:
    jsonObj = request.POST['Data']
    jsonObj = jsonParse.cleanJSON(jsonObj)
    # Test Key Authentication
    try:
      userProf = UserProfile.objects.get(privAPIKey__exact = jsonObj['APIKey'])
    except ObjectDoesNotExist:
      return HttpResponseBadRequest("Bad Key! Your key is = \n%s" % jsonObj['APIKey'])
    retData = privacy.process_privacy(userProf.userID, jsonObj)
  #Get all Data for sensorID
  #Modify data based on name's access privleges
    #Find sensorID.owner's XML file and find rule for name and sensorID
    #Modify data of SensorID

  data = -1
  return HttpResponse(retData)

def get_data2(request):
  #if request.method != 'POST' or not request.is_secure():
  #  return HttpResponseBadRequest("Request must be a HTTPS post!")
  #else:
    #if 'data' in request.POST:
  jsonObj = request.POST['Data']
  jsonObj = jsonParse.cleanJSON(jsonObj)
  # Test Key Authentication
  try:
    userProf = UserProfile.objects.get(privAPIKey__exact = jsonObj['APIKey'])
  except ObjectDoesNotExist:
    return HttpResponseBadRequest("Bad Key! Your key is = \n%s" % jsonObj['APIKey'])
  retData = privacy.process_privacy(userProf.userID, jsonObj)
  #Get all Data for sensorID
  #Modify data based on name's access privleges
    #Find sensorID.owner's XML file and find rule for name and sensorID
    #Modify data of SensorID

  data = -1
  return HttpResponse(retData)

@login_required
def which_data(request):
  #print request.user
  retrString = '<ul>\n'
  #TODO STUFF
  retrString += '</ul>'
  return HttpResponse(retrString)

@login_required
def get_graph(request, sensor_id):
  '''
  if (str(request.user) == 'PersonA') and (sensor_id != '2'):
    return HttpResponse('You do not have any rights on this sensor...')
  '''
  # TODO Check user permissions!

  # Plot Data w/ AmCharts
  return render_to_response("amline.html", {'sensorID': sensor_id}, context_instance=RequestContext(request))

@login_required
def amline_swfobject(request, url):
  #print url
  if url[len(url)-4:] == '.swf':
    with open("%s/template/amline/%s" % (ROOTAPPDIR, url)) as f:
      swfObject = f.read()
    response = HttpResponse(swfObject, content_type='application/x-shockwave-flash')
    return response
  
  return render_to_response("amline/%s" % url, context_instance=RequestContext(request))

@login_required
def amline_data(request, sensor_id):
  #Check request.user's permissions for sensor_id
  
  currSensor = SensorNode.objects.get(id = int(sensor_id))
  data = get_data(currSensor, str(request.user))
  
  if data == -1:
    #print "Something went wrong..."
    return HttpResponse('Uh-oh')
    
  return HttpResponse(data, content_type = 'text/csv')

@login_required
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

  # TODO Check request.user's permissions for sensor_id
  currSensor = Sensor.objects.get(id = int(sensor_id))

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

@login_required
def sensor_node_form(request, is_update = -1, url = None):
  if request.method == 'POST':
    form = SensorNodeForm(request.POST)
    if form.is_valid():
      # Make sure sensor node name is not a duplicate for this user
      try:
        currSN = SensorNode.objects.filter(owner__exact = request.user).get(name__exact = form.cleaned_data['sensor_Name'])
        return HttpResponseRedirect('/snupdate/NameExists')
      except ObjectDoesNotExist:
        pass

      if is_update != -1 or form.cleaned_data['hidden_id'] != '':
        try:
          currSN = SensorNode.objects.get(id__exact=form.cleaned_data['hidden_id'])
        except ObjectDoesNotExist:
          return HttpResponseRedirect('/snupdate/ObjDNE')
        if request.user == currSN.owner:
          currSN.name = form.cleaned_data['sensor_Name']
          currSN.save()
        else:
          return HttpResponseRedirect('/snupdate/BadRights')
      else:
        currSN = SensorNode()
        currSN.name = form.cleaned_data['sensor_Name']
        currSN.owner = request.user
        currSN.save()

        # Each new sensor needs 4 default channels Time, X, Y, Z
        defaultChan = ['Time', 'X', 'Y', 'Z']
        for chan in defaultChan:
          currSC = SensorChannel()
          currSC.name = chan
          currSC.sensorNode = currSN
          currSC.isNonNumeric = False
          currSC.save()
      
      return HttpResponseRedirect('/snview/')
  else:
    snThisUser = SensorNode.objects.order_by('name').filter(owner__exact = request.user)
    displayData = []
    for sn in snThisUser:
      scData = {'nodeData': {}, 'channelData': []}
      scData['nodeData'] = {'id': sn.id, 'name': sn.name}
      scThisSN = SensorChannel.objects.order_by('sensorNode', 'id').filter(sensorNode__exact = sn)
      for sc in scThisSN:
        data = (sc.id, sc.name)
        scData['channelData'].append(data)
      displayData.append(scData)

    if url != None:
      # TODO This should handle errors
      form = SensorNodeForm()
    elif is_update != -1:
      try:
        currSN = SensorNode.objects.get(id__exact=is_update)
      except ObjectDoesNotExist:
        return HttpResponseRedirect('/snupdate/ObjDNE')
      if currSN.owner == request.user:
        form = SensorNodeForm(initial={'sensor_Name': currSN.name, 'hidden_id': currSN.id})
      else:
        return HttpResponseRedirect('/snupdate/BadRights')
    else:
      form = SensorNodeForm()
  return render_to_response('snForm.html', {'form': form, 'userData': displayData}, context_instance=RequestContext(request))

@login_required
def sensor_channel_form(request, is_update = -1, url = None):
  snChoices = []
  snOpts = SensorNode.objects.order_by('id').filter(owner__exact = request.user)
  for opt in snOpts:
    snChoices.append((opt.id, opt.name))

  placeChoices = []
  placeOpts = Placement.objects.order_by('id').filter(group__exact = request.user)
  for opt in placeOpts:
    placeChoices.append((opt.id, opt.name))

  if request.method == 'POST':
    form = SensorChannelForm(request.POST)
    form.fields['sensor_Node'].choices = snChoices
    form.fields['channel_Placement'].choices = placeChoices
    
    if form.is_valid():
      # Make sure sensor node name is not a duplicate for this user
      try:
        testSC = SensorChannel.objects.filter(sensorNode__exact = form.cleaned_data['sensor_Node']).get(name__exact = form.cleaned_data['channel_Name'])
        if testSC.id != int(form.cleaned_data['hidden_id']) and testSC.id != int(is_update):
          return HttpResponseRedirect('/scupdate/NameExists_%s' % testSC.id)
      except ObjectDoesNotExist:
        pass

      if is_update != -1 or form.cleaned_data['hidden_id'] != '':
        try:
          currSC = SensorChannel.objects.get(id__exact=form.cleaned_data['hidden_id'])
          currSN = SensorNode.objects.get(id__exact=form.cleaned_data['sensor_Node'])
          if form.cleaned_data['channel_Placement'] != '':
            currPlace = Placement.objects.get(id__exact=form.cleaned_data['channel_Placement'])
        except ObjectDoesNotExist:
          return HttpResponseRedirect('/scupdate/ObjDNE')
        
        # Make sure channel is not Time, X, Y, Z (mandatory channels)
        if currSC.name in ['Time', 'X', 'Y', 'Z']:
          return HttpResponseRedirect('/scupdate/BadRights')

        if request.user == currSN.owner:
          currSC.name = form.cleaned_data['channel_Name']
          currSC.sensorNode = currSN
          currSC.isNonNumeric = form.cleaned_data['non_Numeric']
          
          # TODO This is assuming it's properly formatted...better way?
          if currSC.isNonNumeric:
            currSC.nonNumericEnum = form.cleaned_data['non_Numeric_Options'].split(', ')
            if len(currSC.nonNumericEnum) > 1:
              currSC.nonNumericEnum = ', '.join(currSC.nonNumericEnum)
            else:
              return HttpResponseRedirect('/scupdate/BadEnum')
          else:
            currSC.nonNumericEnum = ''

          if form.cleaned_data['channel_Placement'] != '' and request.user == currPlace.group:
            currSC.placement = currPlace
          currSC.save()
        else:
          return HttpResponseRedirect('/scupdate/BadRights')
      else:
        try:
          currSN = SensorNode.objects.get(id__exact=form.cleaned_data['sensor_Node'])
          if form.cleaned_data['channel_Placement'] != '':
            currPlace = Placement.objects.get(id__exact=form.cleaned_data['channel_Placement'])
        except ObjectDoesNotExist:
          return HttpResponseRedirect('/scview/ObjDNE')
        if request.user == currSN.owner:
          currSC = SensorChannel()
          currSC.name = form.cleaned_data['channel_Name']
          currSC.sensorNode = currSN
          currSC.isNonNumeric = form.cleaned_data['non_Numeric']

          # TODO This is assuming it's properly formatted...better way?
          if currSC.isNonNumeric:
            currSC.nonNumericEnum = form.cleaned_data['non_Numeric_Options'].split(', ')
            if len(currSC.nonNumericEnum) > 1:
              currSC.nonNumericEnum = ', '.join(currSC.nonNumericEnum)
            else:
              return HttpResponseRedirect('/scupdate/BadEnum')
          else:
            currSC.nonNumericEnum = ''
          
          if form.cleaned_data['channel_Placement'] != '' and request.user == currPlace.group:
            currSC.placement = currPlace
          currSC.save()
        else:
          return HttpResponseRedirect('/scview/BadRights')
      return HttpResponseRedirect('/scview/')
  else:
    if url != None:
      # TODO This should handle errors
      form = SensorChannelForm()
    elif is_update != -1:
      try:
        currSC = SensorChannel.objects.get(id__exact = is_update)
      except ObjectDoesNotExist:
        return HttpResponseRedirect('/scupdate/ObjDNE')
      if currSC.sensorNode.owner == request.user:
        initData = {'channel_Name': currSC.name, 'sensor_Node': currSC.sensorNode.id, 'channel_Placement': currSC.placement, 'hidden_id': currSC.id, 'non_Numeric': currSC.isNonNumeric, 'non_Numeric_Options': currSC.nonNumericEnum}
        form = SensorChannelForm(initial = initData)
      else:
        return HttpResponseRedirect('/scupdate/BadRights')
    else:
      form = SensorChannelForm()
  
  snThisUser = SensorNode.objects.order_by('name').filter(owner__exact = request.user)
  displayData = []
  for sn in snThisUser:
    scData = {'nodeData': {}, 'channelData': []}
    scData['nodeData'] = {'id': sn.id, 'name': sn.name}
    scThisSN = SensorChannel.objects.order_by('sensorNode', 'id').filter(sensorNode__exact = sn)
    for sc in scThisSN:
      data = (sc.id, sc.name)
      scData['channelData'].append(data)
    displayData.append(scData)

  form.fields['sensor_Node'].choices = snChoices
  form.fields['channel_Placement'].choices = placeChoices
  return render_to_response('scForm.html', {'form': form, 'userData': displayData}, context_instance=RequestContext(request))

@login_required
def rules_form(request, is_update = -1, url = None):
  if request.method == 'POST':
    # TODO A dynamically created form...
    form = RulesForm(request.POST)
    
    if int(form.data['form_Type']) == 1:
      if form.is_valid():
        # Convert Form Data to a JSON-Style Object/Dictionary
        jsonObj = {"PrivacyContract": {"Rule": [{"Condition": '', "Action": ''}]}}

        if is_update != -1 or form.cleaned_data['hidden_id'] != '':
          try:
            jsonObj['PrivacyContract']['Rule'][0]['RuleID'] = int(form.cleaned_data['hidden_id'])
          except KeyError:
            return HttpResponseRedirect('/rules/badUpdate')
        jsonObj['PrivacyContract']['Rule'][0]['Condition'] = json.loads(form.cleaned_data['condition'])
        if form.cleaned_data['action'] == 'Allow' or form.cleaned_data['action'] == 'Deny':
          jsonObj['PrivacyContract']['Rule'][0]['Action'] = form.cleaned_data['action']
        else:
          jsonObj['PrivacyContract']['Rule'][0]['Action'] = {form.cleaned_data['action']: json.loads(form.cleaned_data['calculation'])}
        

        # Add Rule to Database
        retVal = privacy_rules(jsonObj, request.user, True)

        if retVal != 0:
          return retVal

        return HttpResponseRedirect('/rules/')
    
    elif int(form.data['form_Type']) == 0:
      string = ""
      for k in form.data.keys():
         string += "%s <br>" % k
      return HttpResponse(request.content)
  else:
    if url != None:
      # TODO This should handle errors
      form = RulesForm()
    elif is_update != -1:
      try:
        currPR = privacyRules.objects.get(id__exact = is_update)
        currDC = ruleToUserMap.objects.filter(rule__exact = currPR)
        currSN = ruleToSensorNodeMap.objects.filter(rule__exact = currPR)
        currSC = ruleToChannelMap.objects.filter(rule__exact = currPR)
      except ObjectDoesNotExist:
        return HttpResponseRedirect('/rules/ObjDNE')
      if currPR.owner == request.user:
        jsonRule = json.loads(currPR.rule)
        try:
          initData = {'hidden_id': currPR.id, 'form_Type': '1', 'condition': json.dumps(jsonRule['Condition']), 'action': jsonRule['Action'].keys()[0], 'calculation': json.dumps(jsonRule['Action'][jsonRule['Action'].keys()[0]])}
        except:
          initData = {'hidden_id': currPR.id, 'form_Type': '1', 'condition': json.dumps(jsonRule['Condition']), 'action': jsonRule['Action'], 'calculation': ''}
        form = RulesForm(initial = initData)
      else:
        return HttpResponseRedirect('/rules/BadRights')
    else:
      form = RulesForm()
  
  prThisUser = privacyRules.objects.order_by('id').filter(owner__exact = request.user)
  displayData = []
  for pr in prThisUser:
    # Print each rule, something maybe a little more palettable than just the JSON, but for now...
    jsonRule = json.loads(pr.rule)
    try:
      currRule = {'id': pr.id, 'condition': json.dumps(jsonRule['Condition']), 'action': jsonRule['Action'].keys()[0], 'calculation': json.dumps(jsonRule['Action'][jsonRule['Action'].keys()[0]])}
    except:
      currRule = {'id': pr.id, 'condition': json.dumps(jsonRule['Condition']), 'action': jsonRule['Action'], 'calculation': ''}
    displayData.append(currRule)

  return render_to_response('rulesForm.html', {'form': form, 'userData': displayData}, context_instance=RequestContext(request))

# TODO Add a method of UPDATING and DELETING rules
def upload_rules(request):
  if request.method != 'POST' or not request.is_secure():
    return HttpResponseBadRequest("Request must be a HTTPS post!")
  else:
    try:
      jsonObj = request.POST['Data']
    except KeyError:
      return HttpResponseBadRequest("Your POST object didn't contain an item with a key = 'Data'")
    try:
      jsonObj = jsonParse.cleanJSON(jsonObj)
    except KeyError:
      return HttpResponseBadRequest("Your POST object didn't contain an item with a key = 'APIKey'")
    # Test Key Authentication
    try:
      userProf = UserProfile.objects.get(privAPIKey__exact = jsonObj['APIKey'])
    except ObjectDoesNotExist:
      return HttpResponseBadRequest("Bad Key! Your key is = \n%s" % jsonObj['APIKey'])
    # Add/Update these rules in database
    retVal = privacy_rules(jsonObj, userProf.userID)
  if retVal == 0:
    return HttpResponse("Rule Upload Succesful")
  else:
    return retVal
    
def privacy_rules(jsonObj, user, fromWeb = False):
  try:
    rules = jsonObj['PrivacyContract']['Rule']
  except KeyError:
    return HttpResponseBadRequest("Can't Find Rules in JSON")
  for rule in rules:
    # TODO Possibly add a flag in each rule, like an ID to denote an update
    currID = -1
    try:
      currID = int(rule['RuleID'])
      if privacyRules.objects.get(id = currID).owner != user:
        if fromWeb:
          return HttpResponseRedirect('/rules/badRights')
        else:
          return HttpResponseBadRequest("You don't have rights to update this sensor")
    except KeyError:
      pass
    except ObjectDoesNotExist:
      if fromWeb:
        return HttpResponseRedirect('/rules/badID')
      else:
        return HttpResponseBadRequest("The rule you requested to update could not be found in our system")

    # Create New or Update Rule and Save
    if currID != -1:
      r = privacyRules.objects.get(id = currID)
      r.rule = json.dumps(rule)
    else:
      r = privacyRules(owner = user, rule = '''%s''' % json.dumps(rule))
    r.save()

    # TODO Make it possible to use IDs instead of User Names 
    try:
      dc = rule['Condition']['DataConsumer']
      if currID != -1:
        ruleToUserMap.objects.filter(rule = r).delete()
      for c in dc:
        try:
          consumer = authUser.objects.get(username__exact = c)
          rtum = ruleToUserMap(rule = r, consumer = consumer)
          rtum.save()
        except ObjectDoesNotExist:
          return HttpResponseBadRequest("Can't Find User with username = %s" % c)
    except KeyError:
      pass
    
    try:
      sn = rule['Condition']['SensorNode']
      if currID != -1:
        ruleToSensorNodeMap.objects.filter(rule = r).delete()
      for n in sn:
        try:
          sensorNode = SensorNode.objects.get(name__exact = n)
          rtsnm = ruleToSensorNodeMap(rule = r, sensorNode = sensorNode)
          rtsnm.save()
        except ObjectDoesNotExist:
          return HttpResponseBadRequest("Can't Find Sensor Node with name = %s" % n)
    except KeyError:
      pass
    
    try:
      sc = rule['Condition']['SensorChannel']
      if currID != -1:
        ruleToChannelMap.objects.filter(rule = r).delete()
      for c in sc:
        c = c.split('.')
        try:
          sn = SensorNode.objects.get(name__exact = c[0])
          chan = SensorChannel.objects.filter(sensorNode__exact = sn).get(name__exact = c[1])
          rtcm = ruleToChannelMap(rule = r, channel = chan)
          rtcm.save()
        except ObjectDoesNotExist:
          return HttpResponseBadRequest("Can't Find Channel with name = %s.%s" % (c[0], c[1]))
    except KeyError:
      pass
  return 0
