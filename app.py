import os
import json
import time
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELOS_CHAT = [
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
]
MODELO_EMBED = "gemini-embedding-001"
CACHE = "embeddings_cache.json"


def carregar_pedacos(pasta="docs", tamanho=1500, sobreposicao=150):
    pedacos = []
    for nome in os.listdir(pasta):
        if nome.endswith(".txt"):
            with open(os.path.join(pasta, nome), "r", encoding="utf-8") as f:
                texto = f.read()
            for i in range(0, len(texto), tamanho - sobreposicao):
                pedacos.append({"fonte": nome, "texto": texto[i:i + tamanho]})
    return pedacos


def gerar_embeddings(textos):
    vetores = []
    for i in range(0, len(textos), 40):
        lote = textos[i:i + 40]
        for tentativa in range(5):
            try:
                resultado = client.models.embed_content(model=MODELO_EMBED, contents=lote)
                break
            except Exception as erro:
                if "429" in str(erro) and tentativa < 4:
                    print("Limite do plano gratuito atingido. Aguardando 30 segundos...")
                    time.sleep(30)
                else:
                    raise
        vetores.extend([np.array(e.values) for e in resultado.embeddings])
    return vetores


def carregar_ou_gerar_vetores(pedacos):
    textos = [p["texto"] for p in pedacos]
    if os.path.exists(CACHE):
        with open(CACHE, "r", encoding="utf-8") as f:
            dados = json.load(f)
        if dados["textos"] == textos:
            print("Embeddings carregados do cache.")
            return [np.array(v) for v in dados["vetores"]]
    vetores = gerar_embeddings(textos)
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump({"textos": textos, "vetores": [v.tolist() for v in vetores]}, f)
    return vetores


def buscar(pergunta, pedacos, vetores, k=3):
    v = gerar_embeddings([pergunta])[0]
    notas = [np.dot(v, x) / (np.linalg.norm(v) * np.linalg.norm(x)) for x in vetores]
    melhores = np.argsort(notas)[::-1][:k]
    return [pedacos[i] for i in melhores]


def responder(pergunta, trechos):
    contexto = "\n\n".join(f"[{t['fonte']}]\n{t['texto']}" for t in trechos)
    instrucao = (
        "Você é um tutor de React. Responda em português, de forma curta, "
        "usando SOMENTE os trechos fornecidos. Se a resposta não estiver "
        "nos trechos, diga que não encontrou na documentação."
    )
    config = types.GenerateContentConfig(system_instruction=instrucao, temperature=0.2)
    prompt = f"Trechos da documentação:\n{contexto}\n\nPergunta: {pergunta}"

    for rodada in range(3):
        for modelo in MODELOS_CHAT:
            try:
                r = client.models.generate_content(model=modelo, contents=prompt, config=config)
                return r.text
            except Exception as erro:
                if "503" in str(erro) or "429" in str(erro):
                    print(f"{modelo} ocupado, tentando outro modelo...")
                else:
                    return f"Erro ao responder ({erro.__class__.__name__}): {erro}"
        print("Todos os modelos ocupados. Aguardando 10 segundos...")
        time.sleep(10)
    return "Não consegui responder agora. Tente de novo em alguns minutos."



if __name__ == "__main__":
    pedacos = carregar_pedacos()
    print(f"{len(pedacos)} pedaços carregados. Preparando embeddings...")
    vetores = carregar_ou_gerar_vetores(pedacos)
    print("Pronto! Digite sua pergunta (ou 'sair').")

    while True:
        pergunta = input("\nVocê: ")
        if pergunta.lower() == "sair":
            break
        trechos = buscar(pergunta, pedacos, vetores)
        print("\nTutor:", responder(pergunta, trechos))
        print("Fontes:", ", ".join(sorted({t["fonte"] for t in trechos})))