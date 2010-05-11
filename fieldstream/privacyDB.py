from spotlightdb.fieldstream.models import *
from django.contrib.auth.models import User
from time import gmtime, strftime
import math
import json

# Returns of list of PrivacyRules
def get_privacy_rules(requestorID, sensorOwnerName, searchSensorNodes, searchSensorChannels):
  # Get sensor owner from name
  try:
    sensorOwner = User.objects.get(username__exact = sensorOwnerName)
  except ObjectDoesNotExist:
    return []

  # Get All rules that pertain to the sensorOwner
  allOwnerRules = privacyRules.objects.filter(owner__exact = sensorOwner).order_by('id')
  
  # Determine which rules are owned by sensorOwner and apply to requestor
  rtum = ruleToUserMap.objects.filter(rule__in = allOwnerRules).filter(consumer__exact = requestorID).order_by('id')
  returnRules = []
  for r in rtum:
    returnRules.append(r.rule)
  
  # Determine which rules are owned by sensorOwner and apply to NO specific data consumer
  rtum = ruleToUserMap.objects.filter(rule__in = allOwnerRules).order_by('id')
  prID = []
  for r in rtum:
    prID.append(r.rule.id)
  noConsumerRules = privacyRules.objects.filter(owner__exact = sensorOwner).exclude(id__in = prID).order_by('id')
  returnRules.extend(noConsumerRules)

  # Determine which rules are ownder by sensorOwner and apply to NO specific data consumer and apply to a given list of sensor nodes
  rtsnm = []
  if len(searchSensorNodes) > 0:
    rtsnm = ruleToSensorNodeMap.objects.filter(rule__in = noConsumerRules).filter(sensorNode__in = searchSensorNodes).order_by('id')
  for r in rtsnm:
    returnRules.append(r.rule)
  
  # Determine which rules are owned by sensorOwner and apply to NO specific data consumer and apply to a given list of sensorChannels on given sensorNodes
  scIDList = []
  rtscm = []
  for sc in searchSensorChannels:
    try:
      currSN = SensorNode.objects.filter(owner__exact = sensorOwner).get(name__exact = sc[0])
      scIDList.append(SensorChannel.objects.filter(sensorNode__exact = currSN).get(name__exact = sc[1]).id)
    except ObjectDoesNotExist:
      continue
  rtscm = ruleToChannelMap.objects.filter(rule__in = noConsumerRules).filter(sensorChannel__in = scIDList)
  for r in rtscm:
    returnRules.append(r.rule)

  return returnRules

# Returns a querySet of WaveSegs
def get_wavesegs(searchSensorOwner, searchSensorNodes, searchSensorChannels, searchTimes, searchLocations):
  # Get sensor owner
  sensorOwner = User.objects.get(username__exact = searchSensorOwner)

  # Figure out what sensor nodes we need all channels
  sensorNodeFull = SensorNode.objects.filter(owner = sensorOwner).filter(name__in = searchSensorNodes)
  returnWS = WaveSeg.objects.filter(sensorNode__in = sensorNodeFull)

  # Assuming searchSensorChannels = [(sensorNode, sensorChannel), ...]
  channelDict = {}
  sSC = searchSensorChannels 
  for i in range(len(sSC)):
    # Remove any sensor channels where wave segs for the nodes are being gotten
    if sSC[i][0] in searchSensorNodes:
      continue
    # Create a dictionary of node: [channel,...]
    else:
      # Shouldn't ever see this, but just in case
      if sSC[i][1] in ['Time', 'X', 'Y', 'Z']:
        continue
      if sSC[i][0] in channelDict:
        channelDict[sSC[i][0]].append(sSC[i][1])
      else:
        channelDict[sSC[i][0]] = [sSC[i][1]]

  # Get more wave segs 
  listOfID = []
  for node in channelDict:
    try:
      currNode = SensorNode.objects.filter(owner = sensorOwner).get(name = node)
    except ObjectDoesNotExist:
      continue
    currNodeWS = WaveSeg.objects.filter(sensorNode = currNode)
    
    currNodeChan = SensorChannel.objects.filter(sensorNode = currNode)
    
    chanNames = []
    for chan in currNodeChan:
      chanNames.append(chan.name)
    
    for ws in currNodeWS:
      tmpFormat = json.loads(ws.valuesFormat)
      if len(tmpFormat) >= len(chanNames):
        x = chanNames
        y = tmpFormat
      else:
        y = chanNames
        x = tmpFormat
      for name in x:
        if name in y:
          listOfID.append(ws.id)
          break
  returnWS = returnWS | WaveSeg.objects.filter(id__in = listOfID)

  # Limit WaveSegs based on start and end times
  timeQuery = WaveSeg.objects.none()
  for time in searchTimes:
    t0 = gmtime(time[0])
    t0Frac = str(time[0] - math.floor(time[0]))
    t0Frac = t0Frac[2:7]
    t0 = strftime("%Y-%m-%d %H:%M:%S", t0)
    t0 = t0 + ".%s" % t0Frac
    
    t2 = gmtime(time[2])
    t2Frac = str(time[2] - math.floor(time[2]))
    t2Frac = t2Frac[2:7]
    t2 = strftime("%Y-%m-%d %H:%M:%S", t2)
    t2 = t2 + ".%s" % t2Frac
    
    if t0 == None:
      if time[3] == True:
        timeQuery = timeQuery | WaveSeg.objects.filter(endTime__lte = t2)
      else:
        timeQuery = timeQuery | WaveSeg.objects.filter(endTime__lt = t2)
    elif t2 == None:
      if time[1] == True:
        timeQuery = timeQuery | WaveSeg.objects.filter(startTime__gte = t0)
      else:
        timeQuery = timeQuery | WaveSeg.objects.filter(startTime__gt = t0)
    else:
      if time[1] == True and time[3] == True:
        timeQuery = timeQuery | WaveSeg.objects.filter(startTime__gte = t0).filter(endTime__lte = t2)
      elif time[1] == True and time[3] == False:
        timeQuery = timeQuery | WaveSeg.objects.filter(startTime__gte = t0).filter(endTime__lt = t2)
      if time[1] == False and time[3] == True:
        timeQuery = timeQuery | WaveSeg.objects.filter(startTime__gt = t0).filter(endTime__lte = t2)
      if time[1] == False and time[3] == False:
        timeQuery = timeQuery | WaveSeg.objects.filter(startTime__gt = t0).filter(endTime__lt = t2)
  
  if len(searchTimes) > 0:
    returnWS = returnWS & timeQuery

  # TODO Handle locations....
  return returnWS
