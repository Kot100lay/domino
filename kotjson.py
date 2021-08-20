import os
import json
from types import SimpleNamespace

def json_check(key, jsonfile = 'pepedata.json'):
    with open(jsonfile, 'r') as f:
        file = json.load(f)
    return file[key]

def json_modify( key, data, jsonfile="pepedata.json"):
    
    # modyfing the one keyword
    '''in_file = open(jsonfile, 'r')
    data_file = in_file.read()
    x = json.loads(data_file)'''
    with open(jsonfile, 'r') as f:
        x = json.load(f)
        x[key] = data
    # overriding the original with the modified filess
    with open(jsonfile, 'w') as f:
        f.write(json.dumps(x))

def responses(jsonfile = "responses.json"): # returns a json to use in the actual code
    with open(jsonfile, 'r', encoding="UTF-8") as f:
        file = json.load(f)
    
    return file
        
responses = SimpleNamespace(**(responses())['normal'])