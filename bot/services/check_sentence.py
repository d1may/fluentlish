import requests, spacy 


nlp = spacy.load("en_core_web_sm")

def sentence_contains_word(target, text):
    target = target.split()[0]
    try:
        doc = nlp(text)
        check_target = [token.lemma_.lower() for token in doc]
        if target.lower() in check_target:
            return grammar_check(text)
        else:
            return "There is no target word"
    except Exception:
        return "The sentence is not correct"

def grammar_check(text):
    url = "https://api.languagetoolplus.com/v2/check"
    data = {
        "text": text,
        "language": "en-US"
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        result = response.json()
        matches = result.get("matches", [])
        if not matches:
            return "✅ No grammar issues found."
        output = "❌ Issues:\n"
        for match in matches:
            issue = match["message"]
            context = match["context"]["text"]
            offset = match["context"]["offset"]
            length = match["context"]["length"]
            error_part = context[offset:offset+length]
            replacements = [r["value"] for r in match.get("replacements", [])]
            suggestion = ", ".join(replacements[:3]) if replacements else "—"
            output += f"\n• <b>{error_part}</b>: {issue}\n   ➤ Suggestion: {suggestion}"
        return output
    else:
        return f"🌐 Error: {response.status_code}"
