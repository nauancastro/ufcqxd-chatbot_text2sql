import os
from typing import List

from crewai import LLM, Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

from chatbot_pluviometrico.tools.consulta_banco import ConsultaBancoTool

load_dotenv()

LLM_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LLM_BASE_URL = os.getenv("ANTHROPIC_BASE_URL")
LLM_MODEL = os.getenv("ANTHROPIC_MODEL")

custom_llm = LLM(
    model=f"anthropic/{LLM_MODEL}",
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL,
)
print(f"LLM: anthropic/{LLM_MODEL} @ {LLM_BASE_URL}")


@CrewBase
class ChatbotPluviometrico():
    """Chatbot Pluviométrico crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def analista_climatico(self) -> Agent:
        return Agent(
            config=self.agents_config['analista_climatico'],
            tools=[ConsultaBancoTool()],
            llm=custom_llm,
            verbose=True,
        )

    @task
    def responder_pergunta(self) -> Task:
        return Task(
            config=self.tasks_config['responder_pergunta'],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.analista_climatico()],
            tasks=[self.responder_pergunta()],
            process=Process.sequential,
            memory=False,
            verbose=True,
        )


# Pré-instancia o crew uma única vez no startup do container.
# Evita pagar o custo de inicialização (ChromaDB, ONNX, YAML load)
# a cada mensagem recebida.
crew_instance = ChatbotPluviometrico().crew()
