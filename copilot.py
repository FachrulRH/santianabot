import os
import json
from dotenv import load_dotenv
from openai import OpenAI


class Copilot:
    def clear_text(self, text):
        a = text.replace("\n", " ")
        b = a.split()
        c = " ".join(b)

        return c

    def get_answer(self, question):
        prompt = (
            "Jawablah pertanyaan yang diberikan secara singkat terkait gaya hidup sehat dalam bahasa Indonesia. Jika konteks bukan terkait gaya hidup sehat jawab dengan : Maaf saya tidak mengerti maksud anda saya di program hanya menjawab terkait konteks gaya hidup sehat."
            f"{question}"
        )

        load_dotenv()

        client = OpenAI(
            api_key=os.getenv("CHAT_GPT3_API_KEY")
        )
        response = client.chat.completions.create(
            max_tokens=510,
            temperature=0.5,
            messages=[{"role": "system", "content": prompt}],
            model="gpt-4-turbo",
        )

        text = response.choices[0].message.content.strip()

        return text
