import json
import os

FILE_NAME = "investmenttrainer/utils/caching.json"

def get_value(key):
    with open(os.path.join(os.getcwd(), FILE_NAME), "r") as c_file:
        file_content = c_file.read()
        if len(file_content.strip()) < 3:
            return None
        json_content = json.loads(file_content)
        if key not in json_content:
            return None
        c_file.close()
        return json_content[key]

def set_value(key, value):
    json_content = {}
    with open(os.path.join(os.getcwd(), FILE_NAME), "r") as c_file:
        file_contents = c_file.read()
        if len(file_contents) > 2:
            json_content = json.loads(file_contents)
        c_file.close()

    json_content[key] = value
    with open(os.path.join(os.getcwd(), FILE_NAME), "w") as c_file:
        c_file.write(json.dumps(json_content))
        c_file.close()


