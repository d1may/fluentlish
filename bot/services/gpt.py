# /// script
# requires-python = ">=3.12"
# dependencies = [
#         "openai",
# ]
# ///
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
API = os.getenv("API")

client = OpenAI(api_key=API)

def check_sentence(target, sentence):

    prompt = (
        f"If the word '{target}' or any of its forms (e.g., past, future, present) is present in the sentence, "
        f"then your task is to check the sentence for grammatical errors and write them out if there are any. "
        f"If the word '{target}' or any of its forms is NOT present, just report that.\n\n"
        f"Sentence: \"{sentence}\""
    )

    response2 = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return (response2.choices[0].message.content)
