# Fluentlish

Telegram bot for learning English words. The bot sends users random words, selects them according to their level of knowledge, helps them learn words in practice, and gets word definitions. There are two versions of the bot: regular and premium (`/payment`). The premium version has an improved sentence checking system using the OpenAI API (GPT-4), and the user can create several dictionaries and fully manage them.

## Features

1. Sending a new word from the dictionary.
2. Automatic selection of words according to the user's level.
3. Definitions and examples of word usage (according to the Cambridge dictionary).
4. Ability to evaluate the difficulty of the word ("Too easy", "Ok", "Too hard").
5. List of learned words.
6. Asynchronous work with the database.
7. Custom keyboards for easy interaction.
8. Word checking with the free LanguageTool API or ChatGPT in the premium version.

## Installation

```bash
git clone <URL>
cd fluentlish
```

### Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### Install dependencies

```bash
pip install .
python -m spacy download en_core_web_sm
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
uv run python -m spacy download en_core_web_sm
```

### Environment variables

Create a `.env` file in the project root:

```
TOKEN=your_telegram_bot_token
API=your_openai_api_key
PORT=10000
```

### Run the bot

```bash
python start_bot.py
```

## Commands

- `/start` — start the bot
- `/new_word` — get a new word
- `/definition` — get the definition of a word
- `/studied` — view the list of studied words
- `/my_words` — view all words in your dictionary
- `/add_word <word>` — add a word to your dictionary
- `/del_word <word>` — delete a word from your dictionary
- `/profile` — check your profile
- `/payment` — buy premium
