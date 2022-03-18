import json
import re

import requests

r = requests.get('http://127.0.0.1:8000/article/tech/2').text
j = json.loads(r)
print(re.search('<table>(.*?)</table>', j['article']['content']))
