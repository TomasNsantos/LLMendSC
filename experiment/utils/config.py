from dotenv import load_dotenv
import os

# Carrega variáveis do .env (uma vez só no projeto)
load_dotenv()

# API da OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
