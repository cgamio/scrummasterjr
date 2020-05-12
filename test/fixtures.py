import json

def okRequestResponse(json_data):
    return {'status_code': 200, 'text': json.dumps(json_data)}

def badRequestResponse(text):
    return {'status_code': 500, 'text': text}
