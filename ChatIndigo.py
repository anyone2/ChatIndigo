import sys
import keyring
import openai   
from pprint import pprint
import alexa_remote_control
import json
import re
import requests


def set_web_page(url, username, password, the_timeout=5):
    
    # username is not needed nor used currently
    # define header for API call
    my_headers = {"Authorization":
                  f"Bearer {password}"}

    try:
        response = requests.get(url, headers=my_headers, timeout=5)

        # https://www.nylas.com/blog/use-python-requests-module-rest-apis/
        response.raise_for_status()

        # Code here will only run if the request is successful

        if 'could not find variable' not in str(response.content):
            return response.content
        else:  # could not find variable
            return None

    except requests.exceptions.HTTPError as errh:
        print("errh: {}".format(errh))
    except requests.exceptions.ConnectionError as errc:
        print("errc: {}".format(errc))
    except requests.exceptions.Timeout as errt:
        print("errt: {}".format(errt))
    except requests.exceptions.RequestException as err:
        print("err: {}".format(err))


def refined_intent():
    return (''' # noqa

Respond to requests sent to a smart home in JSON format which will be interpreted 
by an application code to execute the actions. 

These requests should be categorized into five groups:
 - "command": change the state of an accessory (required properties in the response JSON: action,
    location, target, value, comment)
 - "query": get state of an accessory (required properties in the response JSON: action, location, target, property)
 - "answer": when the request has nothing to do with the smart home. Answer these to the best of your knowledge.  
    (required properties in the response JSON: action, answer)
 - "clarify": when the action is not obvious and requires rephrasing the input from the user, 
    ask the user to be more specific. This will be categorised into a "question" action. 
    (required properties in the response JSON: action, question)
- "action group": change the state of a room effecting multiple accessories within the room (required properties in the response JSON: action,
    location, target, value, comment)

Details about the response JSON:
The "action" property should be one of the request categories: "command", "action group", "query", "answer", "clarify"
The "location" property should contain the name of the room in lowercase.
The "target" property is a numerical value assigned to each device when the action is 'command'
The "target" property is a numerical value assigned to each room when the action is 'action group'

When multiple devices are to be turn on or off, use action 'action group' and the target for the room in your JSON response.
In case of queries, the "property" property should be "state" in lowercase.
In case of commands, the "comment" property is an additional comment from you that concludes the command, 
something that reassures the user that their command handled.

Properties of the smart home:
 - has a kitchen, Family Room room, loft, dining room, master bedroom, carriage house, hallway, garage, 1st floor
 - you can control light switches and their dim level or on/off state, in each room and query their state.
 - you can turn on or off all devices in a room using the On/Off target values for the room.


if you want to turn on multiple lights in a room your action should be 'group' then use these values

Master Bedroom is a room. To turn OFF all lights use target value 1567227526 and to turn ON use 1546644531
LOFT is a room. To turn OFF all lights use target value  168677203 and to turn ON use 1546644531
Kitchen is a room. To turn OFF all lights in the kitchen use target value  1189558621 to turn on use 550050465
Carriage House is a room. To turn OFF all lights use target value  1625760457, to turn on use 1189558621

device Hopes Virtual Lamp is a Virtual On/Off Device locate in the Master Bedroom, JSON target is 504830581
device Bathroom Light is a SwitchLinc Dimmer  locate in the Master Bedroom, JSON target is 31976241
device Back Blind is a Window Blind Motor locate in the Master Bedroom, JSON target is 1133464319
device Left Blind is a Window Blind Motor locate in the Master Bedroom, JSON target is 205013253
device Right Blind is a Window Blind Motor locate in the Master Bedroom, JSON target is 1618886294
device Restroom Fan is a Dimmer Device locate in the Master Bedroom, JSON target is 99059449
device Master Ceiling Fan is a Dimmable Power Switch locate in the Master Bedroom, JSON target is 1215782701
device Master Closet is a On/Off Device locate in the Master Bedroom, JSON target is 587615442
device Master Restroom Fan is a On/Off Device locate in the Master Bedroom, JSON target is 1000024269
device Master Restroom Light is a SwitchLinc Relay locate in the Master Bedroom, JSON target is 560092650

device Carriage Door Light is a On/Off Device locate in the Carriage House, JSON target is 21995933
device Carriage Fan is a On/Off Device locate in the Carriage House, JSON target is 1860470472
device Carriage House - Left Lamp is a Dimmer Device  locate in the Carriage House, JSON target is 1104365571
device Carriage House - Right Lamp is a Dimmer Device  locate in the Carriage House, JSON target is 875108688
device Carriage House Desk Lamp is a Dimmer Device  locate in the Carriage House, JSON target is 1747896389
device Carriage Kitchenette Light is a SwitchLinc Dimmer  locate in the Carriage House, JSON target is 1081597744
device Carriage Light is a On/Off Device locate in the Carriage House, JSON target is 1502484654

device Dual Bulb Virtual Lamp is a Virtual On/Off Device locate in the Loft, JSON target is 126290059
device Globe Virtual Lamp is a Virtual On/Off Device locate in the Loft, JSON target is 1013365613
device Nicks Virtual Lamp is a Virtual On/Off Device locate in the Loft, JSON target is 812323192
device 3rd Floor BR30 - 2 is a SwitchLinc Dimmer  locate in the Loft, JSON target is 126547135
device Ceiling Fan - 2 is a SwitchLinc Relay locate in the Loft, JSON target is 1038184308
device 3rd Floor Hallway is a SwitchLinc Dimmer  locate in the Loft, JSON target is 95147255
device 3rd Floor LED Lamp is a On/Off Module locate in the Loft, JSON target is 1252158401
device 3rd Floor Window Fan is a On/Off device located in the loft, JSON target is 916783950

device Flood Lights - Two is a SwitchLinc Dimmer locate in the Kitchen, JSON target is 19273622
device Pendant Light - Two is a SwitchLinc Dimmer locate in the Kitchen, JSON target is 994692320
device Sink is a Micro Module Dimmer  locate in the Kitchen, JSON target is 503060833


        ''')


def main():

    openai.api_key = keyring.get_password("openai", "key1")

    if len(sys.argv) > 1:

        the_prompt = refined_intent() + " " + sys.argv[1]
        if len(sys.argv) > 2:
            # 0 - file
            # 1 - firt argument
            # 2 - second argument
            the_device = sys.argv[2]

        my_query = {'model': "text-davinci-003", 
                    'prompt': the_prompt, 
                    'temperature': 0.7, 
                    'max_tokens': 2048}

        response = openai.Completion.create(
                                        model=my_query['model'], 
                                        prompt=my_query['prompt'], 
                                        temperature=my_query['temperature'], 
                                        max_tokens=my_query['max_tokens']
                                            )

        # if response.get("choices", False) and len(sys.argv) > 2:
        #     say_this = response["choices"][0]["text"]

        #     alexa_remote_control.alexa_speak(say_this, the_device)
        # else:
        #     say_this = response["choices"][0]["text"]
        #     # pprint(say_this)
        #     the_dict = cleanup(say_this)
        #     pprint(the_dict)
        #     print(type(the_dict))

        if response.get("choices", False):

            say_this = response["choices"][0]["text"]
            the_dict = cleanup(say_this)

            if len(sys.argv) > 2:

                alexa_remote_control.alexa_speak(
                                        the_dict.get('comment', 
                                                     'Something went wrong'), 
                                        the_device)

            else:

                pprint(the_dict)
        else:
            print('No response received')


def cleanup(string):
    
    string = string.replace('\n', '')
    # Extract text between "{" and "}"
    match = re.search(r'\{.*\}', string)
    if match:
        json_str = match.group(0)
        # Remove line feeds from JSON string
        json_str = json_str.replace('\n', '')
        # Convert JSON string to Python dict
        data = json.loads(json_str)
        return(data)
    else:
        print("No match found")
        return None


if __name__ == '__main__':
    main()
