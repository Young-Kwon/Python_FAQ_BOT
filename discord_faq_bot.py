""" Discord FAQ Bot Program

This program initializes and runs the faq_bot.py as a Discord bot, allowing
users to interact with the FAQ bot through Discord messages.

Author: Young Sang Kwon
Date: Nov 5th, 2023
Vertion: 2.0
"""

import discord
from faq_bot_plus import *

## Client Class Definition

class MyClient(discord.Client):
    """Represents a client connected to Discord.
    
    This class represents a bot user and handles the events
    related to its activities on Discord.
    """
    
    def __init__(self):
        """Initializes the bot user with default 'intents'.
        
        'intents' define which events the bot will receive updates for.
        """
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.questions, self.responses = load_FAQ_data()
        self.regex_list = load_fuzzy_regex_patterns()

    async def on_ready(self):
        """Event Handler: Called when the bot has successfully logged in.
        
        Prints a message to the console indicating the bot is online.
        """
        print('Logged on as', self.user)

    async def on_message(self, message):
        """Event Handler: Called when the bot receives a message.
        
        Args:
            message (discord.Message): Object containing message details.
            
        This handler processes the incoming message, determines the
        appropriate response, and sends it back to the channel. 
        """
        
        # Prevent the bot from responding to its own messages
        if message.author == self.user or message.author.bot:
            return
        
        # Process and sanitize incoming message
        utterance = message.content
        sanitized_utterance = sanitize_text(utterance)
        
        # Determine the response based on the sanitized message
        if sanitized_utterance == 'hello':  # Respond to 'hello'
            response = "Hello! How can I assist you?"
        elif sanitized_utterance == 'goodbye':  # Respond to 'goodbye' and exit
            response = "Goodbye! Have a wonderful day!"
            await message.channel.send(response)
            await self.close()
            return
        else:  # For other messages, understand the intent and generate a response
            intent = understand(utterance, self.regex_list)
            response = generate(intent, self.questions, self.responses, utterance)

        # Send the response back to the channel
        await message.channel.send(response)

def sanitize_text(text):
    """Sanitizes the input text.
    
    Args:
        text (str): The input string to be sanitized.
        
    Returns:
        str: The sanitized string.
        
    This function removes punctuation, reduces multiple whitespaces to single, 
    and converts text to lowercase.
    """
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    text = ' '.join(text.split())  # Remove extra whitespaces
    return text.lower()  # Convert to lowercase

## Bot Initialization and Login

client = MyClient()
with open("bot_token.txt") as file:  # Read bot token from file
    token = file.read()
client.run(token)  # Run the client with the read token
