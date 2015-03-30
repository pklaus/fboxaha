import json
import os.path
import requests
from xml.dom.minidom import parseString
import hashlib
from pprint import pprint

class FritzAHA(object):

    GET_SESSION_ID_URL = "http://{host}/login_sid.lua"
    AHA_URL = "https://{host}/webservices/homeautoswitch.lua?ain={ain}&switchcmd={switchcmd}&sid={sid}"
    BASE_URL = "http://{host}/{address}"

    def __init__(self, host, username, password):
        self._sid = None
        self._cookies = None
        self.host = host
        self.username = username
        self.password = password
        self.get_session_id()

    @property
    def session_id_url(self):
        return FritzAHA.GET_SESSION_ID_URL.format(host=self.host)

    def create_response(challenge, password):
        text = "%s-%s" % (challenge, password)
        text = text.encode("utf-16le")
        res = "%s-%s" % (challenge, hashlib.md5(text).hexdigest())
        return res

    def get(self, *args, **kwargs):
        if self._sid and 'params' in kwargs:
            kwargs['params'].update({'sid': self._sid})
        #if self._cookies:
        #    kwargs.update({'cookies': self._cookies})
        req = requests.get(*args, **kwargs)
        #self._cookies = req.cookies
        #import pdb; pdb.set_trace()
        return req

    def get_session_id(self, sid = None):
      params = dict()
      if sid is not None:
          params['sid'] = sid
      req = self.get(self.session_id_url, params=params)
      data = req.text

      xml = parseString(data)
      sid = xml.getElementsByTagName("SID").item(0).firstChild.data

      if sid != "0000000000000000":
          self._sid = sid
      else:
          challenge = xml.getElementsByTagName("Challenge").item(0).firstChild.data
          params = {'response' : FritzAHA.create_response(challenge, self.password)}
          if self.username: params.update({'username' : self.username})
          req = self.get(self.session_id_url, params=params)
          data = req.text
          xml = parseString(data)
          sid = xml.getElementsByTagName("SID").item(0).firstChild.data
          if sid == "0000000000000000": raise FritzAHAError("login to fritzbox failed")
          self._sid = sid

    @property
    def power_devices(self):
        ''' returns a list of tuples (device_id, connectstate, switchstate) '''
        url = self._url("/net/home_auto_query.lua")
        params = {'command' : 'AllOutletStates', 'xhr' : 0 }
        req = self.get(url, params=params)
        data = req.text
        data = json.loads(data)
        count = int(data["Outlet_count"])
        res = []
        for i in range(1,count+1):
            device = (int(data["DeviceID_%d" % i]), int(data["DeviceConnectState_%d" % i]), int(data["DeviceSwitchState_%d" % i]))
            res.append(device)
        return res

    def get_temperature(self, device_id):
        ''' get the temperature of this device in celsius '''
        url = self._url("/net/home_auto_query.lua")
        params = {'command' : 'AllOutletStates', 'xhr' : 0 }
        req = self.get(url, params=params)
        data = req.text
        data = json.loads(data)
        for i in xrange(len(data)): # we cannot have more devices then entries in this list
            try:
                if data["DeviceID_%d" % i] == str(device_id):
                    return float(data["DeviceTemp_%d" % i])/10.0
            except KeyError: pass
        return 0

    def get_consumption(self, device_id, timerange = "10"):
        ''' get the average power consumption of this device for the given time range. range may be 10, 24h, month or year'''
        tranges = ("10","24h","month","year")
        if timerange not in tranges: raise FritzAHAError("unknown timerange, possible values are: %s" % str(tranges))
        url = self._url("/net/home_auto_query.lua")
        params = {'command' : 'EnergyStats_%s' % timerange, 'id' : device_id, 'xhr' : 0 }
        req = self.get(url, params=params)
        data = req.text
        data = json.loads(data)
        average = float(data["EnStats_average_value"])/100.0
        return average

    def get_last_consumption(self, device_id):
        ''' get the last known (latest) power consumption of this device '''
        url = self._url("/net/home_auto_query.lua")
        params = {'command' : 'EnergyStats_10', 'id' : device_id, 'xhr' : 0 }
        req = self.get(url, params=params)
        data = req.text
        data = json.loads(data)
        latest = float(data["EnStats_watt_value_1"])/100.0
        return latest

    def get_power_state(self, device_id):
        ''' returns either 0 (power off) or 1 (power on) '''
        url = self._url("/net/home_auto_query.lua")
        params = {'command' : 'OutletStates', 'id' : device_id, 'xhr' : 1 }
        req = self.get(url, params=params)
        data = req.text
        data = json.loads(data)
        switchState = int(data["DeviceSwitchState"])
        return switchState

    def _url(self, address):
        return FritzAHA.BASE_URL.format(host=self.host, address=address)

    def set_power_state(self, device_id, value):
        url = self._url("/net/home_auto_query.lua")
        params = {'command' : 'SwitchOnOff', 'id' : device_id, 'value_to_set' : value, 'xhr' : 1 }
        req = self.get(url, params=params)
        data = req.text
        data = json.loads(data)
        res = int(data["RequestResult"])
        return res

    def power_on(self, device_id):
        ''' power on the device '''
        self.set_power_state(device_id, 1)

    def power_off(self, device_id):
        ''' power off the device '''
        self.set_power_state(device_id, 0)

class FritzAHAError(NameError):
    pass

if __name__ == "__main__":
    pass
