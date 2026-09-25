import os
from typing import Type

import psycopg2
from crewai.tools import BaseTool
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

# Log global de execuções SQL — acessível pela avaliação
execution_log: list = []


class ConsultaBancoInput(BaseModel):
    """Input que recebe uma consulta SQL gerada pelo LLM."""
    query: str = Field(..., description="Consulta SQL que será executada no banco de dados PostgreSQL")


class ConsultaBancoTool(BaseTool):
    name: str = "Consulta SQL no banco meteorológico"
    description: str = (
        "Use esta ferramenta para executar consultas SQL na tabela 'pluviometria'. "
        "Você deve gerar a SQL com base na pergunta do usuário e nas colunas conhecidas."
    )
    args_schema: Type[BaseModel] = ConsultaBancoInput

    def _run(self, query: str) -> str:
        forbidden = ['DELETE', 'DROP', 'UPDATE', 'INSERT', 'TRUNCATE', 'ALTER']
        if any(cmd in query.upper() for cmd in forbidden):
            execution_log.append({"query": query, "result": None, "error": "Comando proibido"})
            return "Erro: Apenas consultas SELECT são permitidas."

        try:
            conn = psycopg2.connect(os.getenv("SUPABASEDB_URI"))
            cur = conn.cursor()
            cur.execute(query)
            resultado = cur.fetchall()
            conn.close()
            execution_log.append({"query": query, "result": resultado, "error": None})
            return str(resultado) if resultado else "Sem resultados encontrados para essa consulta."
        except Exception as e:
            execution_log.append({"query": query, "result": None, "error": str(e)})
            return f"Erro ao executar a consulta: {str(e)}"
