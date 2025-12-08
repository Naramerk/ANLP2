# Load from .env, initialize LLM client
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "http://a6k2.dgx:34000/v1")
API_KEY = os.getenv("LITELLM_API_KEY", "sk-pNtjvNgR-9llKvVyq3fbPw")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen3-32b")

llm = ChatOpenAI(
    model=MODEL_NAME,
    base_url=LITELLM_BASE_URL,
    api_key=API_KEY,
    temperature=0.7,
)

