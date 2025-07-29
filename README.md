# Random English Words Bot

## Description:
Telegram bot for learning English words. The bot sends users random words, selects them according to their level of knowledge, helps them learn words in practice, and gets word definitions. There are two versions of the bot: regular and premium (/payment). The premium version has an improved sentence checking system using the openAI API chatgpt4.1, and the user can create several dictionaries and fully manage them.

Features:

1. Sending a new word from the dictionary.

2. Automatic selection of words according to the user's level.

3. Definitions and examples of word usage (according to the Cambridge dictionary).

4. Ability to evaluate the difficulty of the word (“Too easy”, ‘Ok’, “Too hard”).

5. List of learned words.

6. Asynchronous work with the database.

7. Custom keyboards for easy interaction.

8. Word checking with the free LanguageTool API or Chatgpt in the premium version
____
## 🚀 Installation
git clone <URL>
cd fluentlishbot
____
## Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
____
## Install requirements
pip install -r requirements.txt
python -m spacy download en_core_web_sm
____
## Run the bot
python start_bot.py
____
## Usage
/start - start the bot.
/new_word - get a new word.
/definition - get the definition of a word.
/studied - view the list of studied words.
/profile - check you profile
/payment - buy premium 
____