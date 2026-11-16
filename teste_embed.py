import os
import numpy as np
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

frases = [
    "useState guarda valores que mudam dentro de um componente React",
    "useEffect executa código depois que o componente renderiza",
    "Receita de bolo de chocolate",
]

resultado = client.models.embed_content(
    model="gemini-embedding-001",
    contents=frases,
)
vetores = [np.array(e.values) for e in resultado.embeddings]

def similaridade(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print("useState x useEffect:", similaridade(vetores[0], vetores[1]))
print("useState x bolo:", similaridade(vetores[0], vetores[2]))