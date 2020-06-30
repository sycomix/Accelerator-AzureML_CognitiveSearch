# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from flask import Flask, redirect, url_for, request, make_response, current_app, jsonify
import json
import plac
from spacy.lang.en import English
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc, Span, Token
import spacy
import pandas as pd
import traceback
import os
import logging

logger = logging.getLogger(__name__)




def compose_response(json_data, nlp):
    values = json.loads(json_data)['values']
    
    # Prepare the Output before the loop
    results = {}
    results["values"] = []
    
    for value in values:
        output_record = transform_value(value, nlp)
        if output_record != None:
            results["values"].append(output_record)
    return results

## Perform an operation on a record
def transform_value(value, nlp):
    try:
        recordId = value['recordId']
    except AssertionError  as error:
        return None

    # Validate the inputs
    try:         
        assert ('data' in value), "'data' field is required."
        data = value['data']        
        assert ('doc' in data), "'doc' field is required in 'data' object."
        
    except AssertionError  as error:
        return (
            {
            "recordId": recordId,
            "errors": [ { "message": "Error:" + error.args[0] }   ]       
            })

    try:                
        # annotate the doc with the IOB tags based on the labls provided.
        annotated_doc = annotate_doc(value['data']['doc'], nlp)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        logger.debug(traceback.format_exc())
        return (
            {
            "recordId": recordId,
            "errors": [ { "message": "Could not complete operation for record. >"  + traceback.format_exc() }   ]       
            })

    return ({
            "recordId": recordId,
            "data": {
                "result": annotated_doc
                    }
            })

def annotate_doc(raw_doc, nlp):
    
    doc = nlp(raw_doc)
    param = [[token.text, token.tag_] for token in doc]
    df=pd.DataFrame(param)
    headers = ['text',  'tag']
    df.columns = headers  
    sentence_count = 0

    output = []
    for sent in doc.sents:
        line = { "sentence" : sent.text, "sentence_count": sentence_count}
        line["annotations"] = []

        for token in sent:
            line["annotations"].append({"token": token.text, "POS": token.tag_, "label": 'O' if token._.type == False else token._.type})
        output.append(line)
        sentence_count += 1
    return output

class CustomTagsComponent(object):
   

    name = "custom_tags"  # component name, will show up in the pipeline

    def __init__(self, nlp, label="PRODUCT"):
       
        labels = []
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))
        
        with open(os.path.join(APP_ROOT, 'labels.json')) as f:
        
            labels = json.loads(f.read())
        
        self.labels = { c["name"].lower(): c for c in labels}
        self.label = nlp.vocab.strings[label]  # get entity label ID
        
        
        patterns = [nlp(c) for c in self.labels.keys()]
        self.matcher = PhraseMatcher(nlp.vocab,attr='LOWER')
        self.matcher.add("PRODUCTS", None, *patterns)

        # Register attribute on the Token. We'll be overwriting this based on the matches
        
        Token.set_extension("is_product", default=False, force=True)
        Token.set_extension("type", default=False, force=True)


        # Register attributes on Doc and Span via a getter that checks if one of
        # the contained tokens is set to is_product== True.
        Doc.set_extension("has_product", getter=self.has_product, force=True)
        Span.set_extension("has_product", getter=self.has_product, force=True)

    def __call__(self, doc):
        """Apply the pipeline component on a Doc object and modify it if matches
        are found. Return the Doc, so it can be processed by the next component
        in the pipeline, if available.
        """
        matches = self.matcher(doc)
        
        prevMatch=None
        mainMatch=None
        processFlag=False
        matchNo=0
        updatedMatches = []
        for match in matches:
            if (matchNo>0):
                if(processFlag==False):
                    if(match[1]==prevMatch[1] and match[2]>prevMatch[2]):
                        mainMatch=match
                        processFlag=True
                    if(match[1]>prevMatch[1] and match[2]==prevMatch[2]):
                        mainMatch=prevMatch
                        processFlag=True
                    if(match[1]>=prevMatch[2] ):
                        updatedMatches.append(prevMatch)
                else:
                    if(match[1]>=mainMatch[2]):
                        updatedMatches.append(mainMatch)
                        processFlag=False

            if(matchNo == len(matches)-1):
                if(processFlag==True):
                    if(match[1]==prevMatch[1] and match[2]>prevMatch[2]):
                        updatedMatches.append(match)
                    else:
                        updatedMatches.append(mainMatch)
                else:
                     updatedMatches.append(match)
            prevMatch=match
            matchNo += 1        
        
        spans = []  # keep the spans for later so we can merge them afterwards
        for _, start, end in updatedMatches:
            # Generate Span representing the entity & set label
            entity = Span(doc, start, end, label=self.label)
            spans.append(entity)
            # Set custom attribute on each token of the entity
            
            first = True
            for token in entity:
                token._.set("is_product", True)
                if(first):
                    token._.set("type", "B-" + self.labels[entity.text.lower()]["type"])
                else:
                    token._.set("type", "I-" + self.labels[entity.text.lower()]["type"])
                first = False

            # Overwrite doc.ents and add entity  be careful not to replace!
            doc.ents = list(doc.ents) + [entity]
        
        return doc  # don't forget to return the Doc!

    def has_product(self, tokens):
        """Getter for Doc and Span attributes. Returns True if one of the tokens
        is a product. Since the getter is only called when we access the
        attribute, we can refer to the Token's 'is_product' attribute here,
        which is already set in the processing step."""
        return any([t._.get("is_product") for t in tokens])

def save_labels(body):
    with open('labels.json', 'r+', encoding='utf-8') as f:
        
        f.seek(0)
        json.dump(body, f, ensure_ascii=False, indent=4)
        f.truncate()


def create_app():
    app = Flask(__name__)
    app.logger.setLevel(logging.DEBUG)
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe(nlp.create_pipe('sentencizer'), first=True)
    custom_tags = CustomTagsComponent(nlp)  # initialise component
    nlp.add_pipe(custom_tags)  # add it to the pipeline
    # remove all other default compoennets to minimize work performed
    nlp.remove_pipe("ner")
    print("Pipeline", nlp.pipe_names)

    @app.route("/", methods = ['GET'])
    def index_get():
        content = "To invoke the skill POST the custom skill request payload to the /label endpoint. To set the custom entities, POST to the /annotations endopoint. For a sample, GET the /annotations."
        return make_response(content, 200)

    @app.route("/annotations", methods = ['GET'])
    def annotations_get():
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(APP_ROOT, 'labels.json')) as f:
    
            labels = json.loads(f.read())
            return jsonify(labels)
        return make_response("Error reading labels.json", 500)
            
                
    @app.route("/annotations", methods = ['POST'])
    def annotations():
        try:
            body = request.get_json()
        except ValueError:
            resp = make_response("Invalid body", 400)
            return resp
    
        if body:
            result = save_labels(body)
            nlp.remove_pipe("custom_tags")
            custom_tags = CustomTagsComponent(nlp)  # initialise component
            nlp.add_pipe(custom_tags)  # add it to the pipeline
            return jsonify(result), 201
        else:
            resp = make_response("Invalid body", 400)
            return resp


    @app.route("/label", methods = ['POST'])
    def index():
        try:
            body = json.dumps(request.get_json())
            #logger.warning(body)
        except ValueError:
            resp = make_response("Invalid body", 400)
            return resp
    
        if body:
            result = compose_response(body, nlp)
            return jsonify(result)
        else:
            resp = make_response("Invalid body", 400)
            return resp

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()    