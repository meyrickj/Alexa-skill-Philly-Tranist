import urllib2
import json
import re

API_BASE_URL = "https://www3.septa.org/hackathon"


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
        on_session_started(
            {"requestId": event["request"]["requestId"]}, event["session"])

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
    elif intent_name == "GetAdvisory":
        return get_advisory(intent)
    elif intent_name == "GetDetour":
        return get_detour(intent)
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
                    "With the skill you can ask me to check for any alerts on all SEPTA rail transit and Bus service, as well as elevator outages. " \
                    "For example, you can say are there any issues on route 47? or what elevators are out? Please ask me what you would like to know"

    reprompt_text = "Please ask me for the status of a bus route or train line, " \
                    "for example, Route 47 or the Broad Street line. " \
                    "You can also ask me for elevator status"
            
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_elevator_status():
    session_attributes = {}
    card_title = "Septa Elevator Status"
    reprompt_text = ""
    should_end_session = True

    response = urllib2.urlopen(API_BASE_URL + "/elevator")
    septa_elevator_status = json.load(response)

    if septa_elevator_status['meta']['elevators_out'] == 0:
        speech_output = 'All Elevators are currently operational'
    else:
        speech_output = "The Following elevators are out. "
        for elevators in septa_elevator_status['results']:
            speech_output += 'On ' + elevators['line'] + ' at station ' + elevators['station'] + \
                ' the ' + elevators['elevator'] + \
                ' elevator has ' + elevators['message'] + ' . '

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_status(intent):
    session_attributes = {}
    card_title = "Septa Status"
    speech_output = "I'm not sure which route you wanted the status for. " \
                    "Please try again. Try asking about the Market Frankford line or a bus route, such as Route 66."
    reprompt_text = ""

    if "route" in intent["slots"]:
        route_name = intent["slots"]["route"]["value"]
        route_code = get_route_code(route_name.lower())

        if (route_code != "unkn"):

            response = urllib2.urlopen(
            API_BASE_URL + "/Alerts/get_alert_data.php?req1=" + route_code)
            route_status = json.load(response)

            bus_route = "bus_route"
            regional_rail = "rr_route"
            trolley_route = "trolley_route"

            if bus_route in route_code:
                if len(route_status[0]["current_message"]) > 0:
                    speech_output = "The current status of route " + \
                        route_status[0]["route_name"] + "." + \
                        route_status[0]["current_message"]
                    should_end_session = True
                else:
                    speech_output = "There are currently no alerts for route " + \
                        route_status[0]["route_name"] + "." + \
                        " This route is running normally."
                    should_end_session = True

            elif regional_rail in route_code:
                if len(route_status[0]["current_message"]) > 0:
                    speech_output = "The current status of the " + \
                        route_status[0]["route_name"] + "line. " + \
                        route_status[0]["current_message"]
                    should_end_session = True    
                else:
                    speech_output = "There are currently no alerts for the " + \
                        route_status[0]["route_name"] + "line. " + \
                        " This line is running normally."
                    should_end_session = True

            elif trolley_route in route_code:
                if len(route_status[0]["current_message"]) > 0:
                    speech_output = "The current status of route " + \
                        route_status[0]["route_name"] + "." + \
                        route_status[0]["current_message"]
                    should_end_session = True
                else:
                    speech_output = "There are currently no alerts for route " + \
                        route_status[0]["route_name"] + "." + \
                        " This route is running normally."
                    should_end_session = True
        else:              
            reprompt_text = "I'm not sure which route you wanted the status for. " \
                    "Please try again. Try asking about the Market Frankford line or a bus route, such as Route 66."
            should_end_session = False
        
    

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# ------------- Function to get system advisory messages ----------------------------------
def get_advisory(intent):
    session_attributes = {}
    card_title = "Septa Advisory Message"
    speech_output = "I'm not sure which route you wanted the current advisory message for. " \
                    "Please try again. Try asking about the Market Frankford line or a bus route, such as Route 66."
    reprompt_text = ""

    if "route" in intent["slots"]:
        route_name = intent["slots"]["route"]["value"]
        route_code = get_route_code(route_name.lower())

        if (route_code != "unkn"):

            response = urllib2.urlopen(
            API_BASE_URL + "/Alerts/get_alert_data.php?req1=" + route_code)
            route_status = json.load(response)

            bus_route = "bus_route"
            regional_rail = "rr_route"
            trolley_route = "trolley_route"

            if bus_route in route_code:
                if len(route_status[0]["advisory_message"]) > 0:
                    # advisory message that contains html tags that need to be removed
                    advisory_msg_raw = route_status[0]["advisory_message"]
                    # Replace HTML tags with a space
                    advisory_msg_clean = re.sub("<.*?>", " ", advisory_msg_raw)
                    
                    speech_output = "The current advisory message for route " + \
                        route_status[0]["route_name"] + " is. " + \
                        advisory_msg_clean 
                    should_end_session = True
                else:
                    speech_output = "There are currently no advisories for route " + \
                        route_status[0]["route_name"] + "."  + \
                        " This route is running normally."
                    should_end_session = True

            elif regional_rail in route_code:
                if len(route_status[0]["advisory_message"]) > 0:
                    # advisory message that contains html tags that need to be removed
                    advisory_msg_raw = route_status[0]["advisory_message"]
                    # Replace HTML tags with a space
                    advisory_msg_clean = re.sub("<.*?>", " ", advisory_msg_raw)
                    
                    speech_output = "The current advisory message of the " + \
                        route_status[0]["route_name"] + "line. " + \
                        advisory_msg_clean 
                    should_end_session = True    
                else:
                    speech_output = "There are currently no advisories for the " + \
                        route_status[0]["route_name"] + "line. " + \
                        " This line is running normally."
                    should_end_session = True

            elif trolley_route in route_code:
                if len(route_status[0]["advisory_message"]) > 0:
                    # advisory message that contains html tags that need to be removed
                    advisory_msg_raw = route_status[0]["advisory_message"]
                    # Replace HTML tags with a space
                    advisory_msg_clean = re.sub("<.*?>", " ", advisory_msg_raw)
                    
                    speech_output = "The current advisory message for route " + \
                        route_status[0]["route_name"] + " is. " + \
                        advisory_msg_clean
                    should_end_session = True
                else:
                    speech_output = "There are currently no alerts for route " + \
                        route_status[0]["route_name"] + ". " + \
                        " This route is running normally."
                    should_end_session = True
        else:              
            reprompt_text = "I'm not sure which route you wanted the advisory message for. " \
                    "Please try again. Try asking about the Market Frankford line or a bus route, such as Route 66."
            should_end_session = False
        
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# ---------------- Function to get detour status -----------------------------------

def get_detour(intent):
    session_attributes = {}
    card_title = "Septa Detour Message"
    speech_output = "I'm not sure which route you wanted the detour status for. " \
                    "Please try again. Try asking about the Market Frankford line or a bus route, such as Route 66."
    reprompt_text = ""

    if "route" in intent["slots"]:
        route_name = intent["slots"]["route"]["value"]
        route_code = get_route_code(route_name.lower())

        if (route_code != "unkn"):

            response = urllib2.urlopen(
            API_BASE_URL + "/Alerts/get_alert_data.php?req1=" + route_code)
            route_status = json.load(response)

            for route in route_status:
                if len(route_status[0]["detour_message"]) > 0:
                    speech_output += "There is currently a detour for route " + route_status[0]["route_name"] + ". " + " Due to " + /
                        route_status[0]["detour_reason"] + ". " + "The start location of the detour is "  + route_status[0]["detour_start_location"] + ". " + / 
                        "The detour will last between " + route_status[0]["detour_start_date_time"] + " and "  +  route_status[0]["detour_end_date_time"])
                    should_end_session = True
                else:
                    speech_output = "There are currently no detours for route " + route_status[0]["route_name"] + "." + " This route is running normally."        
                    should_end_session = True
        else:              
            reprompt_text = "I'm not sure which route you wanted the advisory message for. " \
                    "Please try again. Try asking about the Market Frankford line or a bus route, such as Route 66."
            should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))                

			
def get_route_code(septa_route_name):
    return {
        "route 1":	"bus_route_1",
        "route 2":	"bus_route_2",
        "route 3":	"bus_route_3",
        "route 4":	"bus_route_4",
        "route 5":	"bus_route_5",
        "route 6":	"bus_route_6",
        "route 7":	"bus_route_7",
        "route 8":	"bus_route_8",
        "route 9":	"bus_route_9",
        "route 12":	"bus_route_12",
        "route 14":	"bus_route_14",
        "route 16":	"bus_route_16",
        "route 17":	"bus_route_17",
        "route 18":	"bus_route_18",
        "route 19":	"bus_route_19",
        "route 20":	"bus_route_20",
        "route 21":	"bus_route_21",
        "route 22":	"bus_route_22",
        "route 23":	"bus_route_23",
        "route 24":	"bus_route_24",
        "route 25":	"bus_route_25",
        "route 26":	"bus_route_26",
        "route 27":	"bus_route_27",
        "route 28":	"bus_route_28",
        "route 29":	"bus_route_29",
        "route 30":	"bus_route_30",
        "route 31":	"bus_route_31",
        "route 32":	"bus_route_32",
        "route 33":	"bus_route_33",
        "route 35":	"bus_route_35",
        "route 37":	"bus_route_37",
        "route 38":	"bus_route_38",
        "route 39":	"bus_route_39",
        "route 40":	"bus_route_40",
        "route 42":	"bus_route_42",
        "route 43":	"bus_route_43",
        "route 44":	"bus_route_44",
        "route 45":	"bus_route_45",
        "route 46":	"bus_route_46",
        "route 47":	"bus_route_47",
        "route 47m": "bus_route_47m",
        "route 48":	"bus_route_48",
        "route 50":	"bus_route_50",
        "route 52":	"bus_route_52",
        "route 53":	"bus_route_53",
        "route 54":	"bus_route_54",
        "route 55":	"bus_route_55",
        "route 56":	"bus_route_56",
        "route 57":	"bus_route_57",
        "route 58":	"bus_route_58",
        "route 59":	"bus_route_59",
        "route 60":	"bus_route_60",
        "route 61":	"bus_route_61",
        "route 62":	"bus_route_62",
        "route 64":	"bus_route_64",
        "route 65":	"bus_route_65",
        "route 66":	"bus_route_66",
        "route 67":	"bus_route_67",
        "route 68":	"bus_route_68",
        "route 70":	"bus_route_70",
        "route 73":	"bus_route_73",
        "route 75":	"bus_route_75",
        "route 77":	"bus_route_77",
        "route 78":	"bus_route_78",
        "route 79":	"bus_route_79",
        "route 80":	"bus_route_80",
        "route 84":	"bus_route_84",
        "route 88":	"bus_route_88",
        "route 89":	"bus_route_89",
        "route 90":	"bus_route_90",
        "route 91":	"bus_route_91",
        "route 92":	"bus_route_92",
        "route 93":	"bus_route_93",
        "route 94":	"bus_route_94",
        "route 95":	"bus_route_95",
        "route 96":	"bus_route_96",
        "route 97":	"bus_route_97",
        "route 98":	"bus_route_98",
        "route 99":	"bus_route_99",
        "route 103": "bus_route_103",
        "route 104": "bus_route_104",
        "route 105": "bus_route_105",
        "route 106": "bus_route_106",
        "route 107": "bus_route_107",
        "route 108": "bus_route_108",
        "route 109": "bus_route_109",
        "route 110": "bus_route_110",
        "route 111": "bus_route_111",
        "route 112": "bus_route_112",
        "route 113": "bus_route_113",
        "route 114": "bus_route_114",
        "route 115": "bus_route_115",
        "route 117": "bus_route_117",
        "route 118": "bus_route_118",
        "route 119": "bus_route_119",
        "route 120": "bus_route_120",
        "route 123": "bus_route_123",
        "route 124": "bus_route_124",
        "route 125": "bus_route_125",
        "route 126": "bus_route_126",
        "route 127": "bus_route_127",
        "route 128": "bus_route_128",
        "route 129": "bus_route_129",
        "route 130": "bus_route_130",
        "route 131": "bus_route_131",
        "route 132": "bus_route_132",
        "route 133": "bus_route_133",
        "route 139": "bus_route_139",
        "route 150": "bus_route_150",
        "route 201": "bus_route_201",
        "route 204": "bus_route_204",
        "route 205": "bus_route_205",
        "route 206": "bus_route_206",
        "route 310": "bus_route_310",
        "route BSO": "bus_route_BSO",
        "route MFO": "bus_route_MFO",
        "route G": "bus_route_G",
        "route H": "bus_route_H",
        "route XH": "bus_route_XH",
        "route J": "bus_route_J",
        "route K": "bus_route_K",
        "route L": "bus_route_L",
        "route r": "bus_route_r",
        "route lucy": "bus_route_lucy",
        "lucy": "bus_route_lucy",
        "boulevard Direct": "bus_route_BLVDDIR",
        "broad street owl": "rr_route_bso",
        "market frankford owl": "rr_route_mfo",
        "broad street line": "rr_route_bsl",
        "market frankford line": "rr_route_mfl",
        "norristown high speed line": "rr_route_nhsl",
        "airport": "rr_route_apt",
        "chestnut hill east": "rr_route_chw",
        "chestnut hill west": "rr_route_che",
        "cynwyd": "rr_route_cyn",
        "fox chase": "rr_route_fxc",
        "lansdale/doylestown": "rr_route_landdoy",
        "lansdale doylestown": "rr_route_landdoy",
        "manayunk/norristown": "rr_route_nor",
        "manayunk norristown": "rr_route_nor",
        "media/elwyn": "rr_route_med",
        "media elwyn": "rr_route_med",
        "paoli/thorndale": "rr_route_pao",
        "paoli thorndale": "rr_route_pao",
        "trenton": "rr_route_trent",
        "warminster": "rr_route_warm",
        "wilmington/newark": "rr_route_wilm",
        "wilmington newark": "rr_route_wilm",
        "west trenton": "rr_route_wtren",
        "glenside combined": "rr_route_gc",
        "glenside": "rr_route_gc",
        "route 10": "trolley_route_10",
        "route 11": "trolley_route_11",
        "route 13": "trolley_route_13",
        "route 15": "trolley_route_15",
        "route 34": "trolley_route_34",
        "route 36": "trolley_route_36",
        "route 101": "trolley_route_101",
        "route 102": "trolley_route_102"
    }.get(septa_route_name, "unkn")
