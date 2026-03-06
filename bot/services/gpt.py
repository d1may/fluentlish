import os

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("API"))


async def check_sentence(target, sentence):
    prompt = (
        f"If the word '{target}' or any of its forms (e.g., past, future, present) is present in the sentence, "
        f"then your task is to check the sentence for grammatical errors and write them out if there are any. "
        f"If the word '{target}' or any of its forms is NOT present, just report that.\n\n"
        f"Sentence: \"{sentence}\""
    )

    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content
