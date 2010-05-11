from django.db import models
from django.forms import ModelForm
from django.core.exceptions import *
from django.contrib.auth.models import User
#just adding a comment
# Create your models here
# TODO All tables other than UserProfile should have keys to the UserProfile Table instead of the User Table from auth

# Subjects Tables
class UserProfile(models.Model):
  userID = models.ForeignKey(User, related_name='userID', unique=True)
  isGroup = models.BooleanField()
  groupOwner = models.ForeignKey(User, related_name='groupOwner', null=True, blank=True)
  privAPIKey = models.TextField()
  pubAPIKey = models.TextField()

  def __unicode__(self):
    return "%s's Profile" % self.userID.username

class Relationship(models.Model):
  metaGroup = models.ForeignKey(User, related_name='metaGroup')
  member = models.ForeignKey(User, related_name='member')
  isMemberProducer = models.BooleanField()

  def __unicode__(self):
    return 'MetaGroup = %s, Member = %s' % (self.metaGroup, self.member)

#Mapping Tables
class LocationMapping(models.Model):
  name = models.CharField(max_length=255)
  group = models.ForeignKey(User, limit_choices_to = {'isGroup__exact': True})
  locationX = models.FloatField()
  locationY = models.FloatField()
  locationH = models.FloatField()
  radius = models.FloatField()

  def __unicode__(self):
    return self.name

class TimeMapping(models.Model):
  name = models.CharField(max_length=255)
  group = models.ForeignKey(User, limit_choices_to = {'isGroup__exact': True})
  rangeStart = models.TimeField()
  rangeEnd = models.TimeField()

  def __unicode__(self):
    return self.name

class Placement(models.Model):
  name = models.CharField(max_length=255)
  group = models.ForeignKey(User)

  def __unicode__(self):
    return self.name

class SensorNode(models.Model):
  name = models.CharField(max_length=255)
  owner = models.ForeignKey(User)
  
  def __unicode__(self):
    return '%s - %s' % (self.owner, self.name)

class SensorChannel(models.Model):
  name = models.CharField(max_length=255)
  sensorNode = models.ForeignKey('SensorNode')
  placement = models.ForeignKey('Placement', null=True, blank=True)
  isNonNumeric = models.BooleanField(default=False)
  nonNumericEnum = models.TextField(null=True, blank=True)

  def __unicode__(self):
    return '%s: %s' % (self.sensorNode, self.name)

class WaveSeg(models.Model):
  sensorNode = models.ForeignKey('SensorNode')
  startTime = models.DateTimeField(auto_now_add = False)
  endTime = models.DateTimeField(auto_now_add = False)
  sampleInterval = models.FloatField(null = True, blank = True)
  staticLocationX = models.FloatField(null = True, blank = True)
  staticLocationY = models.FloatField(null = True, blank = True)
  staticLocationH = models.FloatField(null = True, blank = True)
  valuesFormat = models.TextField()
  values = models.TextField()
  
  def __unicode__(self):
    return '%s - %s' % (self.sensorNode, self.startTime)

class Statistics(models.Model):
  waveSegID = models.ForeignKey('WaveSeg')
  channelID = models.ForeignKey('SensorChannel')
  min = models.FloatField()
  max = models.FloatField()
  mean = models.FloatField()
  median = models.FloatField()
  std = models.FloatField()

  def __unicode__(self):
    return '%s:%s - %s' % (self.channelID.sensorNode.owner, self.channelID.name, self.waveSegID.startTime)

class StatisticsNonNumeric(models.Model):
  waveSegID = models.ForeignKey('WaveSeg')
  channelID = models.ForeignKey('SensorChannel')
  sortedData = models.TextField()

  def __unicode__(self):
    return '%s:%s - %s' % (self.channelID.sensorNode.owner, self.channelID.name, self.waveSegID.startTime)

class privacyRules(models.Model):
   owner = models.ForeignKey(User)
   rule = models.TextField()

class ruleToUserMap(models.Model):
   rule = models.ForeignKey('privacyRules')
   consumer = models.ForeignKey(User)

class ruleToSensorNodeMap(models.Model):
   rule = models.ForeignKey('privacyRules')
   sensorNode = models.ForeignKey('sensorNode')

class ruleToChannelMap(models.Model):
   rule = models.ForeignKey('privacyRules')
   sensorChannel = models.ForeignKey('sensorChannel')

