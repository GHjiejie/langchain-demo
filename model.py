import os

import dotenv
from langchain.chat_models import init_chat_model


dotenv.load_dotenv()

chat_model_response = init_chat_model(
    model="gpt-5.3-codex",
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
    default_headers={
        "User-Agent": "codex_vscode/0.118.0-alpha.2 (Mac OS 26.2.0; arm64) unknown (VS Code; 26.325.31654)",
        "x-stainless-os": "Unknown",
        "x-stainless-lang": "python",
    },
    use_responses_api=True,
    reasoning_effort="xhigh",
    
    
)