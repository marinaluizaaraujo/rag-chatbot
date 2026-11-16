# RAG Chatbot: Tutor de React

Chatbot de terminal que responde dúvidas sobre React **usando somente trechos da documentação oficial** como fonte. Foi feito em Python com a técnica de **RAG** (*Retrieval-Augmented Generation*) e a API do Gemini, para estudar como combinar busca semântica com modelos de linguagem e reduzir respostas inventadas.

## ⚙️ O que ele faz

- Lê arquivos de texto com a documentação de React (pasta `docs/`)
- Encontra os trechos mais relacionados com a pergunta do usuário
- Pede ao modelo que responda **apenas com base nesses trechos**, em português
- Mostra de quais arquivos vieram as informações usadas
- Se a resposta não estiver nos documentos, avisa que não encontrou, em vez de inventar

## Como funciona

1. **Divisão em trechos:** cada `.txt` é cortado em pedaços de 1500 caracteres, com 150 de sobreposição para não perder contexto nas bordas.
2. **Embeddings:** cada trecho vira um vetor numérico com o modelo `gemini-embedding-001`. Textos com significado parecido ficam com vetores parecidos.
3. **Cache:** os vetores são salvos em `embeddings_cache.json`, então só são gerados na primeira execução (ou quando os documentos mudam).
4. **Busca:** a pergunta também vira um vetor, e os 3 trechos mais parecidos são escolhidos por **similaridade de cosseno** (calculada com NumPy).
5. **Resposta:** os trechos e a pergunta são enviados ao Gemini com a instrução de responder só com base neles. O modelo usa temperatura baixa (0,2) para respostas mais estáveis.

## 🛠️ Tecnologias

- Python 3.13
- [google-genai](https://pypi.org/project/google-genai/) (API do Gemini: geração de texto e embeddings)
- NumPy (similaridade de cosseno)
- python-dotenv (leitura da chave de API)

## 🗂️ Estrutura do projeto

```
rag-chatbot/
├── docs/                  # textos da documentação usados como base de conhecimento
├── app.py                 # código do chatbot
├── .env                   # chave da API (não vai para o GitHub)
├── .gitignore
└── README.md
```

## ▶️ Como rodar

**1. Clone o repositório e entre na pasta**
```
git clone https://github.com/marinaluizaaraujo/rag-chatbot.git
cd rag-chatbot
```

**2. Crie e ative um ambiente virtual** (Windows)
```
python -m venv venv
venv\Scripts\activate
```

**3. Instale as dependências**
```
pip install -U google-genai python-dotenv numpy
```

**4. Configure a chave da API**

Gere uma chave gratuita no [Google AI Studio](https://aistudio.google.com/) e crie um arquivo `.env` na raiz do projeto:
```
GEMINI_API_KEY=sua_chave_aqui
```

**5. Execute**
```
python app.py
```

Na primeira execução, os embeddings são gerados (alguns segundos) e salvos em cache. Depois é só digitar perguntas, como:

- *Para que serve o useState?*
- *Quando devo usar o useEffect?*
- *Por que preciso usar `key` em listas?*

Digite `sair` para encerrar.

## 🧪 Avaliação

Testei o chatbot com perguntas sobre os documentos e uma pergunta fora do tema, para verificar se ele reconhece quando não tem a resposta.

| # | Pergunta | Esperado | Resultado |
|---|----------|----------|-----------|
| 1 | Para que serve o useState? | Explicar estado em componentes, citando `usestate.txt` | ✅ Resposta correta, com a fonte certa |
| 2 | Quando devo usar o useEffect? | Explicar sincronização com sistemas externos |⚠️ Parcial: acertou o uso com sistemas externos, mas não mencionou dependências |
| 3 | Por que preciso usar `key` em listas? | Explicar identificação dos itens pelo React | ✅ Resposta correta; a lista de fontes incluiu um arquivo sem relação (usestate.txt) |
| 4 | Como passo um valor padrão para uma prop? | Mostrar a sintaxe `size = 100` na desestruturação | ✅ Correto, com exemplo de código|
| 5 | Como faço um bolo de chocolate? | Dizer que não encontrou na documentação | ✅ Recusou corretamente; as fontes listadas são só os trechos mais próximos, não usados na resposta |

## ⚠️ Limitações

- Os documentos são cópias de **5 páginas** de react.dev, o que cobre só uma parte pequena do React. Perguntas fora desses temas não serão respondidas.
- O texto copiado do site manteve alguns restos da interface (botões, trechos de código cortados) e traduções imperfeitas, o que pode atrapalhar a busca.
- A busca compara a pergunta com todos os trechos em memória, sem banco vetorial. Funciona bem para poucos documentos, mas não escalaria para uma base grande.
- O plano gratuito da API limita as chamadas por minuto. Durante os testes houve erros `429` (limite de uso) e `503` (alta demanda no modelo); por isso o código espera e tenta de novo, e pode alternar entre modelos disponíveis.
- A qualidade da resposta depende dos trechos recuperados: se a busca trouxer trechos pouco relevantes, a resposta também será fraca.
- A interface é apenas o terminal.
- O campo “Fontes” mostra os trechos recuperados pela busca, e não necessariamente os que o modelo usou, então pode listar arquivos pouco relacionados com a pergunta.

## 🚀 Próximos passos

- Adicionar mais páginas da documentação
- Limpar melhor os textos antes de indexar
- Usar um banco vetorial (como Chroma) e comparar com a busca atual
- Criar uma interface web simples (Streamlit)
- Medir a qualidade das respostas com um conjunto maior de perguntas de teste

## 📚 Fontes dos documentos

Conteúdo da documentação oficial do React, usado aqui para fins educacionais. Os direitos pertencem aos autores originais.

- [useState](https://pt-br.react.dev/reference/react/useState)
- [useEffect](https://pt-br.react.dev/reference/react/useEffect)
- [Passando propriedades para um componente](https://pt-br.react.dev/learn/passing-props-to-a-component)
- [Renderizando listas](https://pt-br.react.dev/learn/rendering-lists)
- [Renderização condicional](https://pt-br.react.dev/learn/conditional-rendering)

## 🌸 Autora

Marina Luiza Paiva: projeto desenvolvido como estudo de IA generativa aplicada (RAG) com Python.
