from django.db import models
from django.forms import ModelForm
from django.core.exceptions import *
from django.contrib.auth.models import User

# Create your models here

# Subjects Tables
class Subject(models.Model):
  name = models.CharField(max_length=255)
  isGroup = models.BooleanField()
  userID = models.ForeignKey(User)

  def __unicode__(self):
    return self.name

class Relationship(models.Model):
  #Need an insertion check to enforce that metaGroup isGroup == TRUE
  metaGroup = models.ForeignKey('Subject', related_name='metaGroup')
  member = models.ForeignKey('Subject', related_name='member')
  isMemberProducer = models.BooleanField()

  def __unicode__(self):
    return 'MetaGroup = %s, Member = %s' % (self.metaGroup, self.member)

#Mapping Tables
class LocationMapping(models.Model):
  name = models.CharField(max_length=255)
  #Need an insertion check to enforce that group isGroup == TRUE
  group = models.ForeignKey('Subject')
  location = models.ForeignKey('Location')
  radius = models.DecimalField(max_digits=23, decimal_places=20)

  def __unicode__(self):
    return self.name

class TimeMapping(models.Model):
  name = models.CharField(max_length=255)
  #Need an insertion check to enforce that group isGroup == TRUE
  group = models.ForeignKey('Subject')
  rangeStart = models.TimeField()
  rangeEnd = models.TimeField()

  def __unicode__(self):
    return self.name

class Placement(models.Model):
  name = models.CharField(max_length=255)
  #Need an insertion check to enforce that group isGroup == TRUE
  group = models.ForeignKey('Subject')

  def __unicode__(self):
    return self.name


#Sensor Tables - NEW!!!
class SensorNode(models.Model):
  name = models.CharField(max_length=255)
  owner = models.ForeignKey('Subject')
  
  def __unicode__(self):
    return '%s - %s' % (self.owner, self.name)

class SensorChannel(models.Model):
  name = models.CharField(max_length=255)
  sensorNode = models.ForeignKey('SensorNode')
  placement = models.ForeignKey('Placement')

  def __unicode__(self):
    return self.name

#Data Tables - NEW!!!!
class WaveSegSeries(models.Model):
  channels = models.CharField(max_length=255)
  sensorNode = models.ForeignKey('SensorNode')

  def __unicode__(self):
    return '%s - %s' % (self.sensorNode.name, self.channels)

class WaveSeg(models.Model):
  waveSegSeries = models.ForeignKey('WaveSegSeries')
  startTime = models.DateTimeField(auto_now_add = False, null = True, blank = True)
  sampleInterval = models.FloatField(null = True, blank = True)
  staticLocation = models.TextField(null = True, blank = True)
  values = models.TextField()
  statitics = models.TextField(null = True, blank = True)
  
  def __unicode__(self):
    return '%s - %s' % (self.waveSegSeries, self.startTime)

#Sensor Tables - OLD!!!!!
class Sensor(models.Model):
  sensorType = models.ForeignKey('SensorType')
  name = models.CharField(max_length=255)
  owner = models.ForeignKey('Subject')

  def __unicode__(self):
    return '%s - %s' % (self.owner, self.name)

class SensorType(models.Model):
  name = models.CharField(max_length=255)
  #Need an insertion check to enforce that group isGroup == TRUE
  group = models.ForeignKey('Subject')
  numChannels = models.IntegerField(blank = True, null = True)
  sampleInterval = models.IntegerField(blank = True, null = True)

  def __unicode__(self):
    return self.name

#Data Tables - OLD!!!!
class Location(models.Model):
  gpsX = models.DecimalField(max_digits=23, decimal_places=20)
  gpsY = models.DecimalField(max_digits=23, decimal_places=20)
  gpsH = models.DecimalField(max_digits=23, decimal_places=20)
  gpsP = models.DecimalField(max_digits=23, decimal_places=20)
  isMapping = models.BooleanField()
  
  def __unicode__(self):
    return str(self.gpsX) + ", " + str(self.gpsY) + ", " + str(self.gpsH) + ", " + str(self.gpsP)

class Data(models.Model):
  location = models.ForeignKey('Location')
  timeStamp = models.DateTimeField(auto_now_add = False)
  value = models.TextField()
  sensor = models.ForeignKey('Sensor')
  min = models.DecimalField(max_digits = 30, decimal_places = 15)
  max = models.DecimalField(max_digits = 30, decimal_places = 15)
  avg = models.DecimalField(max_digits = 30, decimal_places = 15)
  numSamples = models.IntegerField(null = True, blank = True)
  
  def __unicode__(self):
    return "Sensor ID: " + str(self.sensor) + ", Timestamp = " + str(self.timeStamp)
