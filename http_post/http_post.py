import requests
import json
from argparse import ArgumentParser

def get_option():
    argparser = ArgumentParser()
    argparser.add_argument('-f', '--file', type=str,
                           default="xxx.json",
                           help='Specify json file')
    argparser.add_argument('-u', '--url', type=str,
                           default="http://example.com",
                           help='Specify POST URL')
    return argparser.parse_args()

# -- arg parser
args = get_option()
JSON_FNAME = args.file
URL = args.url
print('input .json file name: ' + str(JSON_FNAME))
print('input url: ' + str(URL))

# -- http post 
json_open = open(args.file, 'r')
json_load = json.load(json_open)
json_data = json.dumps(json_load)
response = requests.post(URL, data=json_data)
print(response.text)
