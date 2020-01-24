import json
import os
import random

from flask import Flask, request, make_response

import whatsons_noggin

# Flask app starts in a global layout
app = Flask(__name__)

symptoms_list = list()

ask_symptoms = ["Could you share another symptom?", "Do you observe any other symptoms?", "Could you let me know of any other symptom you are experiencing?", "Do you want to share another symptom?", "Do you notice any other symptoms?", "Do you wish to share any other symptoms?", "Are you experiencing any other symptoms?"]

tell_results = ["I think you might have :", "You could be down with :", "You might possibly be affected with :"]

welcome_results = ["Hello. I'm Dr. Gupta! I am your virtual doctor for the day. How are your feeling today?", "Hi! I'm Dr.Whatson! Your friendly Virtual Assistant. How are you feeling today?", "Hi! I'm Dr.Whatson! Your friendly Virtual Assistant. How are you doing today?"]


@app.route('/')
def homepage():
    return app.send_static_file('index.html')


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print("REQUEST:\n", json.dumps(req, indent=4))

    # Process the request
    req_dict = json.loads(request.data)

    intent = req_dict["result"]["metadata"]["intentName"]
    entity_key_val = req_dict["result"]["parameters"]
    query = req_dict["result"]["resolvedQuery"]

    res = process_intent(intent, entity_key_val, query)

    # Process response
    res = json.dumps(res, indent=4)
    print("RESPONSE:\n", res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def process_intent(intent, entity_dic, query):
    global symptoms_list
    print("PROCESSING INTENT ", intent, entity_dic)

    speech = resp = ""
    suggestions = []
    if intent.lower() == "welcome intent":
        symptoms_list = list()
        speech = random.choice(welcome_results)

    elif intent.lower() == "symptoms intent":
        if "symptom" in entity_dic:
            symp = krishna_parse(entity_dic["symptom"])
            symptoms_list.extend(symp)
            resp, suggestions = krishna_predict(symptoms_list)
            # speech += random.choice(tell_results) + "\n" + resp + "\n"
        speech += random.choice(ask_symptoms)

    elif intent.lower() == "results intent":  # or intent.lower() == "symptoms intent - no":
        resp, suggestions = krishna_predict(symptoms_list)
        speech = random.choice(tell_results) + "\n" + resp
        suggestions = []

    elif intent.lower() == "symptoms intent - yes":
        print("yoyoyo")
        print("-" * 20)
        resp, suggestions = krishna_predict(symptoms_list)
        # speech = random.choice(tell_results) + "\n" + resp + "\n"
        speech += random.choice(ask_symptoms)

    elif intent.lower() == "symptoms intent - fallback":
        print("qwiqwslqwn ---", query)
        print("+" * 20)
        symp = krishna_parse(query)
        symptoms_list.extend(symp)
        resp, suggestions = krishna_predict(symptoms_list)
        # speech = random.choice(tell_results) + "\n" + resp + "\n"
        speech += random.choice(ask_symptoms)

    if not speech:
        speech = """I could not understand that. I could do more as I evolve. Please try again"""
        suggestions = ["tell me my results"]

    res = makeWebhookResult(speech, suggestions)

    return res


def krishna_parse(symptom):
    return whatsons_noggin.parse(symptom)


def krishna_predict(symptoms_list):
    return whatsons_noggin.predict(symptoms_list)


def makeWebhookResult(speech, suggestions):
    print("Response:")
    print(speech)

    result = {}
    result["data"] = {}
    result["data"]["google"] = {}
    result["data"]["google"]["richResponse"] = {}
    result["data"]["google"]["richResponse"]["expectUserResponse"] = True
    result["data"]["google"]["richResponse"]["suggestions"] = []

    result["data"]["google"]["richResponse"]["items"] = []

    res = {
        "simpleResponse": {
            "textToSpeech": speech
        }
    }

    result["data"]["google"]["richResponse"]["items"].append(res)

    if suggestions:

        for s in suggestions:
            temp_d = {}
            temp_d["title"] = s[:25]
            result["data"]["google"]["richResponse"]["suggestions"].append(temp_d)

    return result


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0', threaded=True)
