import sys
import keyring
import openai   
from pprint import pprint
import alexa_remote_control
import json
import re
from intents import anyones_intent


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


def main():

    openai.api_key = keyring.get_password("openai", "key1")

    if len(sys.argv) > 1:

        the_prompt = anyones_intent() + " " + sys.argv[1]
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


if __name__ == '__main__':
    main()
