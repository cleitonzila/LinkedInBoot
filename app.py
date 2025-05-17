import os
import uuid
import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

import PyPDF2
from google import genai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types

# ─── Configuration ─────────────────────────────────────────────────────────────

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_ID = "gemini-2.0-flash"

app = Flask(__name__)

# ADK session setup
APP_NAME   = "linkedin_course_extractor"
USER_ID    = "user_001"
SESSION_ID = "session_001"

session_service = InMemorySessionService()
session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)

# ─── Helper: run any Agent ─────────────────────────────────────────────────────

def call_agent(agent: Agent, message_text: str) -> str:
    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    content = types.Content(
        role="user",
        parts=[types.Part(text=message_text)]
    )
    response = ""
    for event in runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content
    ):
        if event.is_final_response():
            for part in event.content.parts:
                if part.text:
                    response += part.text
    return response.strip()

# ─── PDF text extractor ────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        return "".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as e:
        raise ValueError("Erro ao processar o PDF.") from e

# ─── Agent 1: extrator de nome de curso ────────────────────────────────────────

def agente_extrator(text_info: str) -> str:
    agent = Agent(
        name="agente_extrator",
        model=MODEL_ID,
        instruction=(
            "Você é um assistente especializado em extração de texto. "
            "Seu objetivo é identificar o **nome exato do curso** presente no texto fornecido. "
            "O nome do curso geralmente aparece como um título, em formato claro e direto. "
            "Responda apenas com o nome do curso, sem informações adicionais."
        )
    )
    return call_agent(agent, text_info)


# ─── Agent 2: buscador de notícias ─────────────────────────────────────────────

def agente_buscador(titulo: str) -> str:
    buscador = Agent(
        name="agente_buscador",
        model=MODEL_ID,
        description="Agente que busca informações no Google",
        instruction=(
            "Você é um assistente de pesquisa altamente eficiente. "
            "Sua tarefa é buscar informações sobre o curso especificado abaixo. "
            "Você deve utilizar a ferramenta de busca do Google (google_search) para encontrar: "
            "1. Conteúdo abordado no curso. "
            "2. Tecnologias utilizadas no curso. "
            "Retorne apenas as informações mais relevantes e bem organizadas."
        ),
        tools=[google_search]
    )
    payload = f"Nome do curso: {titulo}\n"
    return call_agent(buscador, payload)

# ─── Agent 3: escritor de post LinkedIn ───────────────────────────────────────

def agente_escritor(curso_title: str, curso_info: str) -> str:
    escritor = Agent(
        name="agente_escritor",
        model=MODEL_ID,
        instruction=(
            "Você é um especialista em redação de posts para LinkedIn. "
            "Você acabou de concluir um curso na Alura, uma escola de tecnologia. "
            "Escreva um post de LinkedIn comemorando a conclusão do curso. "
            "Use um tom inspirador e profissional. "
            "Inclua as seguintes seções: "
            "- Uma introdução que expresse sua satisfação por concluir o curso. "
            "- Uma breve descrição do que você aprendeu e como isso será útil. "
            "- Uma chamada para conectar com outros profissionais da área. "
            "- Quatro hashtags relevantes (como #tecnologia, #aprendizado, #Alura, #carreira)."
        )
    )
    prompt = f"Título do curso: {curso_title}\nConteúdo do curso: {curso_info}"
    return call_agent(escritor, prompt)

# ─── Flask route ──────────────────────────────────────────────────────────────

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'certificate' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400
        cert = request.files['certificate']
        if cert.filename == '':
            return jsonify({"error": "Nenhum arquivo selecionado"}), 400

        try:
            text = extract_text_from_pdf(cert)
            if not text:
                return jsonify({"error": "PDF vazio ou sem texto."}), 400

            # 1) extrai nome do curso
            curso_title = agente_extrator(text)
            if not curso_title:
                return jsonify({"error": "Não foi possível identificar o curso."}), 400

            # 2) busca últimas notícias sobre o curso
            curso_info = agente_buscador(curso_title)

            # 3) gera post para LinkedIn
            linkedin_post = agente_escritor(curso_title, curso_info)

            return jsonify({
                "post": linkedin_post
            })

        except Exception as e:
            app.logger.error(f"Erro no processamento: {e}")
            return jsonify({"error": str(e)}), 500

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
