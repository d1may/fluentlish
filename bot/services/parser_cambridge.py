import aiohttp
from bs4 import BeautifulSoup

async def get_cambridge_data(word):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://dictionary.cambridge.org/dictionary/english-russian/{word}", headers=headers) as response:

            if response.status != 200:
                return None

            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            results = []

            entries = soup.select(".entry-body__el")

            for entry in entries:
                # Part of Speech
                pos_tag = entry.select_one(".pos.dpos")
                part_of_speech = pos_tag.text.strip() if pos_tag else "—"

                # Транскрипції
                ipa_uk_tag = entry.select_one(".uk .pron.dpron")
                ipa_us_tag = entry.select_one(".us .pron.dpron")
                ipa_uk = ipa_uk_tag.text.strip() if ipa_uk_tag else "—"
                ipa_us = ipa_us_tag.text.strip() if ipa_us_tag else "—"

                # CEFR Level
                cefr_tag = entry.select_one(".def-info .epp-xref")
                level = cefr_tag.text.strip() if cefr_tag else "—"

                # Значення і приклади
                sense_blocks = entry.select(".sense-body")
                for sense in sense_blocks:
                    definition_tag = sense.select_one(".def.ddef_d.db")
                    trans_tag = sense.select_one(".trans.dtrans")
                    example_tags = sense.select(".examp.dexamp")

                    if definition_tag:
                        definition = definition_tag.text.strip()
                        examples = [ex.text.strip() for ex in example_tags]
                        # Витягуємо текст з першого перекладу, якщо є
                        translation = trans_tag.text.strip()
                        results.append({
                            "definition": definition,
                            "examples": examples,
                            "level": level,
                            "ipa_uk": ipa_uk,
                            "ipa_us": ipa_us,
                            "part_of_speech": part_of_speech,
                            "translation": translation
                        })
                        
                if results:
                    return {
                        "word": word,
                        "definition": results[0]["definition"],
                        "examples": results[0]["examples"],
                        "level": results[0]["level"],
                        "ipa_uk": results[0]["ipa_uk"],
                        "ipa_us": results[0]["ipa_us"],
                        "part_of_speech": results[0]["part_of_speech"],
                        "translation": results[0]["translation"],
                    }
                else:
                    return None
    return None