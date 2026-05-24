import random
from openai import OpenAI


# Farklı başlangıç yapıları — her başvuruda değişsin
_INTRO_VARIANTS = [
    "Ich bewerbe mich",
    "Hiermit möchte ich mich bewerben",
    "Mit großem Interesse habe ich Ihre Stellenanzeige gelesen",
    "Ihre Ausschreibung hat mich sofort angesprochen",
    "Die ausgeschriebene Stelle hat mich sehr angesprochen",
]


def generate_anschreiben(
    job_title: str,
    company: str,
    job_description: str,
    api_key: str,
    user_background: str = "",
) -> str:
    if not api_key:
        return ""
    try:
        client = OpenAI(api_key=api_key)

        intro = random.choice(_INTRO_VARIANTS)

        # İlan açıklamasından anahtar detayları çıkar
        desc_excerpt = ""
        if job_description:
            # İlk 600 karakter yeterli — çok uzun verme
            desc_excerpt = job_description[:600].replace("\n", " ").strip()

        system_prompt = (
            "Du schreibst ein kurzes, persönliches Bewerbungsanschreiben auf Deutsch. "
            "Wichtige Regeln:\n"
            "- Maximal 4 Sätze, flüssig und natürlich klingend\n"
            "- Beziehe dich auf konkrete Details aus der Stellenbeschreibung\n"
            "- Klingt wie ein echter junger Mensch, nicht wie eine KI\n"
            "- Verwende deutsche Sonderzeichen korrekt: ä, ö, ü, Ä, Ö, Ü und ß\n"
            "- Schreibe z.B. 'für', 'möchte', 'Grüßen', nicht 'fuer', 'moechte', 'Gruessen'\n"
            "- Keine generischen Phrasen wie 'hohe Motivation' oder 'teamfähig'\n"
            "- Kein Betreff, keine Anrede, keine Grußformel, kein Name\n"
            "- Antworte NUR mit dem Anschreiben-Text, sonst nichts"
        )

        user_parts = [
            f"Stelle: {job_title}",
            f"Unternehmen: {company}",
        ]
        if desc_excerpt:
            user_parts.append(f"Stellenbeschreibung: {desc_excerpt}")
        if user_background:
            user_parts.append(f"Über mich: {user_background}")
        user_parts.append(f"Beginne mit: \"{intro}\"")
        user_parts.append("Schreibe jetzt das Anschreiben:")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "\n".join(user_parts)},
            ],
            max_tokens=250,
            temperature=0.85,
        )
        text = response.choices[0].message.content.strip()
        # Tırnak işareti varsa kaldır
        text = text.strip('"').strip("'")
        return text
    except Exception:
        return ""
