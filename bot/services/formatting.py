def format_definition(result: dict) -> str:
    return (
        f"📘 <b>Word:</b> <code>{result['word'].upper()}</code>\n"
        f"🧩 <b>Part of Speech:</b> {result['part_of_speech']}\n"
        f"🔊 <b>UK:</b> {result['ipa_uk']} | <b>US:</b> {result['ipa_us']}\n"
        f"🎯 <b>Level:</b> {result['level']}\n\n"
        f"🧠 <b>Definition:</b> <code>{result['definition']}</code>\n"
        f"🧾 <b>Example 1:</b> {result['examples'][0] if result['examples'] else '—'}\n"
        f"🧾 <b>Example 2:</b> {result['examples'][1] if len(result['examples']) > 1 else '—'}\n"
        f"✏️ <b>Translation:</b> <tg-spoiler>{result['translation']}</tg-spoiler>\n"
    )
