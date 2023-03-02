#!/usr/bin/env python3

from urllib.request import Request, urlopen
import json
import keyring
from pprint import pprint


def make_request(req_dict, reflector, Lookup):

    apikey = keyring.get_password("IndigoAPI", "Key1")

    try:
        if Lookup:
            req = Request(
                f"https://{reflector}.indigodomo.net/v2/api/indigo.devices")
            req.add_header('Authorization', f"Bearer {apikey}")
            with urlopen(req) as request:
                device_list = json.load(request)
        message = json.dumps(req_dict).encode("utf8")         
        req = Request(f"https://{reflector}.indigodomo.net/v2/api/command", 
                      data=message)
        req.add_header('Authorization', f"Bearer {apikey}")
        with urlopen(req) as request:
            reply = json.load(request)
            if Lookup:
                for d in device_list:
                    if d['id'] == req_dict['objectId']:
                        return (reply, d['name'])
            else:
                return (reply, None)
    except ValueError as e:
        print(f"{e}")
    except IOError as e:
        print(f"{e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")


def allowControl(
        reflector, device_id, device_action, value=None, 
        delay=None, duration=None, Lookup=None):
    
    action = {
        'dim': 'dim',
        'on': 'turnOn',
        'lock': 'lock',
        'off': 'turnOff',
        'unlock': 'unlock',
        'enable': 'enable',
        'toggle': 'toggle',
        'brighten': 'brighten',
        'status': 'statusRequest',
        'setbrightness': 'setBrightness',           
    }.get(device_action, None)

    if not action:
        return f"Your request, '{device_action}', is unknown."

    req_dict = {'objectId': device_id}

    if action in ['brighten', 'dim', 'setBrightness']:

        device_type = 'dimmer'
        if value is None:
            return f"A value is required for '{device_type}' requests"        
        req_dict.setdefault('parameters', {})['by'] = value

    else:  # not a dimmable device
        device_type = 'device'

    # define the device and action
    req_dict["message"] = f"indigo.{device_type}.{action}"

    if delay:
        req_dict.setdefault('parameters', {})['delay'] = delay

    if duration:
        req_dict.setdefault('parameters', {})['duration'] = duration

    results = make_request(req_dict, reflector, Lookup)
    req_dict['action'] = device_action
    return results, req_dict


def main():

    # indigo.devices[1823514063] # "3rd Floor Hallway"
    # indigo.devices[1252158401] # "3rd Floor LED Lamp"
    # indigo.devices[1747896389] # "Carriage House Desk Lamp"
    # indigo.devices[31976241] # "Master Bathroom Light"

    reflector = 'macmini'
    results, device_name = allowControl(reflector=reflector, 
                                        device_id=31976241,
                                        device_action='toggle',
                                        delay=None,
                                        duration=None,
                                        Lookup=False)  # 

    if results[0]:
        if results[1] is not None:
            # print('message sent')
            print(f"sent '{device_name['action']}' message "
                  f"to '{results[1]}' ")
        else:
            print(f"sent '{device_name['action']}' ""message "
                  f"to {device_name['objectId']}' ")


if __name__ == "__main__":
    main()
