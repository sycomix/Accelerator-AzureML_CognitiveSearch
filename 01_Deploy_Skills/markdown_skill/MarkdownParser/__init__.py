# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import logging
import json
import azure.functions as func
from io import StringIO
import re

def unmark_element(element, stream=None):
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        body = json.dumps(req.get_json())
    except ValueError:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )
    
    if body:
        result = compose_response(body)
        return func.HttpResponse(result, mimetype="application/json")
    else:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )


def compose_response(json_data):
    values = json.loads(json_data)['values']
    
    # Prepare the Output before the loop
    results = {}
    results["values"] = []
    
    for value in values:
        output_record = transform_value(value)
        if output_record != None:
            results["values"].append(output_record)
    return json.dumps(results, ensure_ascii=False)

## Perform an operation on a record
def transform_value(value):
    try:
        recordId = value['recordId']
    except AssertionError  as error:
        return None

    # Validate the inputs
    try:         
        assert ('data' in value), "'data' field is required."
        data = value['data']        
        assert ('doc' in data), "'text1' field is required in 'data' object."
        
    except AssertionError  as error:
        return (
            {
            "recordId": recordId,
            "errors": [ { "message": "Error:" + error.args[0] }   ]       
            })

    try:   
        to_replace = ['#', '*','[',']','`','<','>','!','}','{', '\"']
        insideHeader=False
        insideCode=False
        clearedText=""  
        for line in value['data']['doc'].splitlines():
            if len(line) > 0:
                line=line.strip()
                if(len(line) >0):
                    if(line=="---"):
                        if(insideHeader==False):
                            insideHeader=True
                        else:
                            insideHeader=False
                    if(line.startswith('```')):
                        if(insideCode==False):
                            insideCode=True
                        else:
                            insideCode=False                                                    
                    if(insideHeader==False and insideCode==False and line[0].isalnum()):
                        line = re.sub(r'^[0-9]+.', '', line)
                        line = re.sub(r'\([^)]*\)', '', line)
                        line = re.sub(r'[^A-Za-z.0-9]', ' ', line)
                        clearedText += line       


    except:
        return (
            {
            "recordId": recordId,
            "errors": [ { "message": "Could not complete operation for record." }   ]       
            })

    return ({
            "recordId": recordId,
            "data": {
                "text": clearedText
                    }
            })