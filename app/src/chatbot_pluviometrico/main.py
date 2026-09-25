import os
from datetime import datetime

import requests

from chatbot_pluviometrico.crew import crew_instance

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:20259")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE")


def _current_time() -> str:
    return datetime.now().strftime("%d-%m-%Y")


def rodarzap(msg: str, numero: str) -> None:
    inputs = {
        "hoje": _current_time(),
        "Q": msg,
    }

    try:
        result = crew_instance.kickoff(inputs=inputs)
        print(f"\n✅ Resultado da execução:\n{result}")

        url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE}"
        headers = {
            "apikey": EVOLUTION_API_KEY,
            "Content-Type": "application/json",
        }
        data = {
            "number": numero,
            "text": str(result),
        }

        response = requests.post(url, json=data, headers=headers)
        print(f"Evolution API → {response.status_code}")

    except Exception as e:
        raise Exception(f"Erro ao executar o crew: {e}")


def run() -> None:
    """Executa o crew via CLI para testes."""
    inputs = {
        "hoje": _current_time(),
        "Q": "O total de chuva de 2018 foi quanto, e me diga também qual foi o dia que choveu mais, e quanto choveu nesse dia",
    }
    try:
        result = crew_instance.kickoff(inputs=inputs)
        print(f"\n✅ Resultado:\n{result}")
    except Exception as e:
        raise Exception(f"Erro ao executar o crew: {e}")
