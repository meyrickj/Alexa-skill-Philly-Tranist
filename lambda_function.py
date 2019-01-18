import urllib2
import json

API_BASE_URL="https://www3.septa.org/hackathon"

from __future__ import print_function


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            'type': 'PlainText',
            'text': output 
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                'type': "PlainText",
                'text': reprompt_text 
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }

# --------------- Functions for the Alexa skill ----------------------


def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.xxx-xxxx-xxxx-xxxx-xxxxx-xxxx"):
        raise ValueError("Invalid Application ID")
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

  
    if intent_name == "GetElevators":
        return get_elevator_status()
    elif intent_name == "GetStatus":
        return get_status(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "Philly Transit - Thank You"
    speech_output = "Thank you for using the Philly Transit Septa skill. "
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "Philly Transit"
    speech_output = "Welcome to the Alexa Philly Transit Septa skill. " \
                    "ask me for system status or elevator status ."
    reprompt_text = "Please ask me for trains times from a station, " \
                    "for example Fremont."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def get_status(intent):
    session_attributes = {}
    card_title = "Septa Status"
    speech_output = "I'm not sure which route you wanted the status for. " \
                    "Please try again. Try asking about the Market Frankford line or a bus route, such as Route 66."
    reprompt_text = "I'm not sure which route you wanted the status for. " \
                    "Try asking about the Market Frankford line or a bus route, such as Route 66."
    should_end_session = False

    if "Route" in intent["slots"]:
        route_name = intent["slots"]["Route"]["value"]
        route_code = get_route_code(route_name.lower())

        if (route_code != "unkn"):
            
            response = urllib2.urlopen(API_BASE_URL + "/Alerts/get_alert_data.php?req1=" + route_code)
            route_status = json.load(response)  

            if len(route_status[0]["current_message"]) > 0:
                speech_output = "The current status of" + route_status[0]["route_name"] + route_status[0]["current_message"] 
            else:
                speech_output = "The " + route_status[0]["route_name"] + " is running normally."   
            
            reprompt_text = ""
            
    return build_response(session_attributes, build_speechlet_response(
       card_title, speech_output, reprompt_text, should_end_session))
            
            
            
            

def get_elevator_status():
    session_attributes = {}
    card_title = "Septa Elevator Status"
    reprompt_text = ""
    should_end_session = False

    response = urllib2.urlopen(API_BASE_URL + "/elevator")
    septa_elevator_status = json.load(response)
    
    if septa_elevator_status['meta']['elevators_out'] == 0: 
        speech_output = 'All Elevators are currently operational' 
    else: 
        for elevators in septa_elevator_status['results']:
            speech_output += 'On' + elevators['line'] + ' at station ' + elevators['station'] + ' the ' + elevators['elevator'] + ' elevator has ' + elevators['message'] + ' . ' 

        
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        

def get_route_code(route_name):
    return {
        "Route 1":	"bus_route_1",
        "Route 2":	"bus_route_2",
        "Route 3":	"bus_route_3",
        "Route 4":	"bus_route_4",
        "Route 5":	"bus_route_5",
        "Route 6":	"bus_route_6",
        "Route 7":	"bus_route_7",
        "Route 8":	"bus_route_8",
        "Route 9":	"bus_route_9",
        "Route 12":	"bus_route_12",
        "Route 14":	"bus_route_14",
        "Route 16":	"bus_route_16",
        "Route 17":	"bus_route_17",
        "Route 18":	"bus_route_18",
        "Route 19":	"bus_route_19",
        "Route 20":	"bus_route_20",
        "Route 21":	"bus_route_21",
        "Route 22":	"bus_route_22",
        "Route 23":	"bus_route_23",
        "Route 24":	"bus_route_24",
        "Route 25":	"bus_route_25",
        "Route 26":	"bus_route_26",
        "Route 27":	"bus_route_27",
        "Route 28":	"bus_route_28",
        "Route 29":	"bus_route_29",
        "Route 30":	"bus_route_30",
        "Route 31":	"bus_route_31",
        "Route 32":	"bus_route_32",
        "Route 33":	"bus_route_33",
        "Route 35":	"bus_route_35",
        "Route 37":	"bus_route_37",
        "Route 38":	"bus_route_38",
        "Route 39":	"bus_route_39",
        "Route 40":	"bus_route_40",
        "Route 42":	"bus_route_42",
        "Route 43":	"bus_route_43",
        "Route 44":	"bus_route_44",
        "Route 45":	"bus_route_45",
        "Route 46":	"bus_route_46",
        "Route 47":	"bus_route_47",
        "Route 47m": "bus_route_47m",
        "Route 48":	"bus_route_48",
        "Route 50":	"bus_route_50",
        "Route 52":	"bus_route_52",
        "Route 53":	"bus_route_53",
        "Route 54":	"bus_route_54",
        "Route 55":	"bus_route_55",
        "Route 56":	"bus_route_56",
        "Route 57":	"bus_route_57",
        "Route 58":	"bus_route_58",
        "Route 59":	"bus_route_59",
        "Route 60":	"bus_route_60",
        "Route 61":	"bus_route_61",
        "Route 62":	"bus_route_62",
        "Route 64":	"bus_route_64",
        "Route 65":	"bus_route_65",
        "Route 66":	"bus_route_66",
        "Route 67":	"bus_route_67",
        "Route 68":	"bus_route_68",
        "Route 70":	"bus_route_70",
        "Route 73":	"bus_route_73",
        "Route 75":	"bus_route_75",
        "Route 77":	"bus_route_77",
        "Route 78":	"bus_route_78",
        "Route 79":	"bus_route_79",
        "Route 80":	"bus_route_80",
        "Route 84":	"bus_route_84",
        "Route 88":	"bus_route_88",
        "Route 89":	"bus_route_89",
        "Route 90":	"bus_route_90",
        "Route 91":	"bus_route_91",
        "Route 92":	"bus_route_92",
        "Route 93":	"bus_route_93",
        "Route 94":	"bus_route_94",
        "Route 95":	"bus_route_95",
        "Route 96":	"bus_route_96",
        "Route 97":	"bus_route_97",
        "Route 98":	"bus_route_98",
        "Route 99":	"bus_route_99",
        "Route 103": "bus_route_103",
        "Route 104": "bus_route_104",
        "Route 105": "bus_route_105",
        "Route 106": "bus_route_106",
        "Route 107": "bus_route_107",
        "Route 108": "bus_route_108",
        "Route 109": "bus_route_109",
        "Route 110": "bus_route_110",
        "Route 111": "bus_route_111",
        "Route 112": "bus_route_112",
        "Route 113": "bus_route_113",
        "Route 114": "bus_route_114",
        "Route 115": "bus_route_115",
        "Route 117": "bus_route_117",
        "Route 118": "bus_route_118",
        "Route 119": "bus_route_119",
        "Route 120": "bus_route_120",
        "Route 123": "bus_route_123",
        "Route 124": "bus_route_124",
        "Route 125": "bus_route_125",
        "Route 126": "bus_route_126",
        "Route 127": "bus_route_127",
        "Route 128": "bus_route_128",
        "Route 129": "bus_route_129",
        "Route 130": "bus_route_130",
        "Route 131": "bus_route_131",
        "Route 132": "bus_route_132",
        "Route 133": "bus_route_133",
        "Route 139": "bus_route_139",
        "Route 150": "bus_route_150",
        "Route 201": "bus_route_201",
        "Route 204": "bus_route_204",
        "Route 205": "bus_route_205",
        "Route 206": "bus_route_206",
        "Route 310": "bus_route_310",
        "Route BSO": "bus_route_BSO",
        "Route MFO": "bus_route_MFO",
        "Route G": "bus_route_G",
        "Route H": "bus_route_H",
        "Route XH": "bus_route_XH",
        "Route J": "bus_route_J",
        "Route K": "bus_route_K",
        "Route L": "bus_route_L",
        "Route R": "bus_route_R",
        "Route LUCY": "bus_route_LUCY",
        "LUCY": "bus_route_LUCY",
        "Broad Street Owl": "rr_route_bso",
        "Market Frankford Owl": "rr_route_mfo",
        "Broad Street Line": "rr_route_bsl",
        "Market Frankford Line": "rr_route_mfl",
        "Norristown High Speed Line": "rr_route_nhsl",
        "Airport": "rr_route_apt",
        "Chestnut Hill East": "rr_route_chw",
        "Chestnut Hill West": "rr_route_che",
        "Cynwyd": "rr_route_cyn",
        "Fox Chase": "rr_route_fxc",
        "Lansdale/Doylestown": "rr_route_landdoy",
        "Manayunk/Norristown": "rr_route_nor",
        "Media/Elwyn": "rr_route_med",
        "Paoli/Thorndale": "rr_route_pao",
        "Trenton": "rr_route_trent",
        "Warminster": "rr_route_warm",
        "Wilmington/Newark": "rr_route_wilm",
        "West Trenton": "rr_route_wtren",
        "Glenside Combined": "rr_route_gc",
        "Route 10": "trolley_route_10",
        "Route 11": "trolley_route_11",
        "Route 13": "trolley_route_13",
        "Route 15": "trolley_route_15",
        "Route 34": "trolley_route_34",
        "Route 36": "trolley_route_36",
        "Route 101": "trolley_route_101",
        "Route 102": "trolley_route_102"
    }.get(route_name, "unkn")               

