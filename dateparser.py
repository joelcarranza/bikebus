import datetime
import re

def parse_time(text,date=None):
  if date is None:
    date = datetime.datetime.today()
  # remove seconds
  date = date.replace(second=0,microsecond=0)
  # normalize remove anything but numbers and letters
  text = re.sub(r'[^\d\w]','',text).lower()

  # shortcuts for labels for specific times
  if text == 'noon':
    text = '12p'
  elif text == 'midnight':
    text = '12a'

  # match to int+modifier
  m = re.match(r'(\d+)([a-z]+)?',text)
  if m:
    timestr,mod = m.groups()
    time = int(timestr)
    # N hr - relative
    if mod in ['h','hr','hour','hours']:
      return date + datetime.timedelta(hours=time)
    # N min - relative
    elif mod in ['m','min','minute','minutes']:
      return date + datetime.timedelta(minutes=time)
    # TODO: what about o'clock?
    # specify am/pm
    elif mod in ['a','am','p','pm']:
      if time < 24: # just hours
        hour = time
        minute = 0
      elif time > 100:
        hour = int(time/100)
        minute = time % 100
      else:
        raise ValueError, ("Don't understand date '"+text+"'")
      if hour == 12: # stupid 12 - bleh
        hour = 0
      if mod[0] == 'p':
        hour += 12
      newdate = date.replace(hour=hour,minute=minute)
      while newdate < date:
        newdate = newdate + datetime.timedelta(hours=24)
      return newdate
    # raw number
    elif mod is None:
      if time < 24: # just hours
        hour = time
        minute = 0
      elif time > 100:
        hour = int(time/100)
        minute = time % 100
      else:
        raise ValueError, ("Don't understand date '"+text+"'")
      if hour == 12:
        hour = 0
      newdate = date.replace(hour=hour,minute=minute)
      while newdate < date:
        newdate = newdate + datetime.timedelta(hours=12)
      return newdate
  raise ValueError, ("Don't understand date '"+text+"'")
