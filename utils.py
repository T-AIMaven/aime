import ast
import re
import json

# List of months to remove
months = ["(jan)", "(feb)", "(mar)", "(apr)", "(may)", "(jun)", "(jul)", "(aug)", "(sep)", "(oct)", "(nov)", "(dec)"]
Q = ["(q1)", "(q2)", "(q3)", "(q4)"]

def preprocess_string_list(string_list):
    # Remove the surrounding brackets
    string_list = string_list.strip()[1:-1]
    # Add quotes around each element, preserving spaces and handling single words
    processed_string = re.sub(r'([^,\s]+(?:\s+[^,\s]+)*)', r'"\1"', string_list)  # Handle phrases with spaces
    processed_string = re.sub(r'(?<=, )(\w+)', r'"\1"', processed_string)  # Add quotes around single words after commas
    # Re-add brackets to the processed string
    return f'[{processed_string}]'

def preprocess_string_json(string_json):
    response_json = json.loads(string_json)
    return response_json

def event_filter_M_Q(econe_events):
    for month in months:
        econe_events['event'] = econe_events['event'].str.replace(month, '', regex=False)
    for q in Q:
        econe_events['event'] = econe_events['event'].str.replace(q, '', regex=False)
    # Strip any leading/trailing whitespace
    econe_events['event'] = econe_events['event'].str.strip()
    return econe_events