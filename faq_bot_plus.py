"""
FAQ Bot

Description: A chatbot that provides answers to user questions using fuzzy pattern matching.
Function: analyze_utterance
          load_FAQ_data
          load_fuzzy_regex_patterns
          understand
          sanitize_text
          generate
          main
Author: Young Sang Kwon
Date: Nov 5th, 2023
Version: 3.0
"""

import string
import regex as re
import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

# Define patterns for speech act classification
patterns = [
    {"label": "CHARACTER", "pattern": [{"LOWER": {"IN": ["adam", "eve", "cain", "abel", "noah", "abram", "sarai", "abraham", "sarah", "isaac", "rebekah", "esau", "jacob", "joseph"]}}]},
    {"label": "PLACE", "pattern": [{"LOWER": {"IN": ["eden", "babel", "mount ararat", "egypt"]}}]},
    {"label": "EVENT", "pattern": [{"LOWER": {"IN": ["flood", "tower of babel", "sodom and gomorrah"]}}]}
]

# This class manages responses for a chatbot, ensuring that the chatbot can alternate between different responses for each type of entity recognized.
class ResponseManager:
    def __init__(self):
        self.last_response = {}

    def get_response(self, entity_label, entity_text):
        responses = {
            "CHARACTER": [
                f"What would you like to know about {entity_text}?",
                f"I'm not quite sure about {entity_text}. Can you ask about another character or a different topic?"
            ],
            "PLACE": [
                f"What would you like to know about the place called {entity_text}?",
                f"The place called {entity_text} is beyond my current knowledge. What else can I assist with?"
            ],
            "EVENT": [
                f"What details are you interested in about the event known as {entity_text}?",
                f"I have limited information on the event called {entity_text}. Perhaps inquire about a different event?"
            ],
            "OTHER": [
                f"Sorry, I don’t have information on {entity_text}.",
                f"My knowledge about {entity_text} is limited. Feel free to ask another question."
            ]
        }

        # Get the current response index for the entity label, defaulting to 0
        response_index = self.last_response.get(entity_label, 0)
        # Get the response
        response = responses.get(entity_label, responses["OTHER"])[response_index]
        # Update the response index for the next time (alternate between 0 and 1)
        self.last_response[entity_label] = (response_index + 1) % 2
        return response


# Instantiate the ResponseManager outside of the function to maintain state across function calls
response_manager = ResponseManager()

for pattern in patterns:
    matcher.add(pattern["label"], [pattern["pattern"]])    

def load_FAQ_data():
    """
    Load questions and answers from text files.

    Args:
        None

    Returns:
        tuple: Lists containing questions and corresponding answers.
    """    
    questions = []
    answers = []
    
    # Load questions from file.
    with open('questions.txt', 'r') as q_file:
        questions = [line.strip() for line in q_file.readlines()]
    
    # Load answers from file.
    with open('answers.txt', 'r') as a_file:
        answers = [line.strip() for line in a_file.readlines()]
   
    return questions, answers

def load_fuzzy_regex_patterns():
    """
    Load regex patterns from a file for fuzzy matching.

    Args:
        None

    Returns:
        list: List of regex patterns.
    """
    with open('regex.txt', 'r') as r_file:
        patterns = [pattern.strip() for pattern in r_file.readlines()]
    return patterns

def understand(utterance, regex_list):
    """
    Match the user's utterance with the best fitting regex pattern.

    Args:
        utterance (str): User input.
        regex_list (list): List of regex patterns.

    Returns:
        int: Index of the best matching pattern or -1 if no match.
    """
    best_match_idx = -1
    best_match_errors = float('inf')  # Initialize with a high value
    
    # Iterate over regex patterns to find the best match.
    for idx, regex in enumerate(regex_list):
        match = re.search(regex, utterance, flags=re.IGNORECASE)
        if match:
            total_errors = sum(match.fuzzy_counts)  # Sum of substitutions, insertions, and deletions
            if total_errors < best_match_errors:
                best_match_errors = total_errors
                best_match_idx = idx
    
    return best_match_idx

def sanitize_text(text):
    """
    Sanitize user input.

    Args:
        text (str): User input.

    Returns:
        str: Sanitized text.
    """    
    # Remove punctuation from the text.
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove excessive spaces.
    text = ' '.join(text.split())
    return text.lower()

def generate(intent, questions, answers, utterance):
    """
    Generate a response based on the intent matched.

    Args:
        intent (int): Index of matched intent.
        questions (list): List of questions.
        answers (list): List of answers.

    Returns:
        str: Generated response.
    """
     # Check if there's no match.
    if intent == -1:
        # return "Sorry, I don't know the answer to that!"
        return analyze_utterance(utterance)
    return answers[intent]

def analyze_utterance(utterance):
    """
    Analyze an utterance using NLP and pattern matching.

    Args:
        utterance (str): The user's message or question that needs analysis.

    Returns:
        str: A response based on the analysis or a default response if no information is extracted.
    """
    doc = nlp(utterance)

    # Check for biblical entities using matcher
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        label = nlp.vocab.strings[match_id]
        return response_manager.get_response(label, span.text)

    # Check for other named entities
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "GPE", "LOC", "ORG"]:            
            return response_manager.get_response("OTHER", ent.text)

    # default response
    return "Can you please rephrase your question or ask about something else?"

def main():
    print("Hello! I have knowledge about chat bots. Type 'goodbye' when you wish to end the conversation.")
    print()
    
    questions, responses = load_FAQ_data()
    regex_list = load_fuzzy_regex_patterns()  # Updated function call
    
    # Interaction loop.
    while True:
        utterance = input(">>> ")
        sanitized_utterance = sanitize_text(utterance)
        
        # Basic greetings handling.
        if sanitized_utterance == "hello":
            print("Hello! How can I assist you?")
            print()
            continue
        elif sanitized_utterance == "goodbye":
            print("Goodbye! Have a wonderful day!")
            break
        
        # Process user input and generate response
        intent = understand(utterance, regex_list)
        response = generate(intent, questions, responses, utterance)
        print(response)
        print()
    
    print("It was pleasant interacting with you!")

if __name__ == "__main__":
    main()