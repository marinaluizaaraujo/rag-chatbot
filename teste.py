import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

resposta = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Explique o que é o useState do React em 3 frases simples."
)
print(resposta.text)