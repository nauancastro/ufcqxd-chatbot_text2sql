# 🌧️ Chatbot Pluviométrico

Chatbot de WhatsApp que responde, em linguagem natural, perguntas sobre dados
históricos de chuva (pluviometria) do município de **Quixadá – CE**. O
público-alvo são **agricultores locais**: eles perguntam no grupo do WhatsApp
em português coloquial ("quanto choveu em março de 2020?", "teve seca esse
ano?") e o bot traduz a pergunta em SQL, consulta uma base histórica de mais
de 50 anos de registros e responde de forma conversacional — sem que o usuário
precise saber o que é SQL ou sequer o que é um banco de dados.

Este repositório contém o **código-fonte da aplicação**. Ele é a implementação
prática de um estudo maior sobre a viabilidade de **Modelos de Linguagem
(LLMs)** como camada de tradução Text-to-SQL para democratizar o acesso a
dados climáticos por comunidades rurais.

📄 **A pesquisa completa** — metodologia, framework de avaliação, comparação
entre modelos de linguagem e discussão dos resultados — foi publicada como
Trabalho de Conclusão de Curso na Universidade Federal do Ceará (UFC) e está
disponível no repositório institucional:

> **["Avaliação de Modelos de Linguagem na tarefa Text-to-SQL para consulta de dados pluviométricos"](http://repositorio.ufc.br/handle/riufc/87838)**

---

## Por que esse projeto existe

Comunidades agrícolas do interior do Ceará dependem fortemente de dados de
chuva para decisões de plantio e manejo, mas esses dados normalmente vivem em
planilhas, boletins técnicos ou sistemas que exigem alguma alfabetização
digital para consultar. A proposta aqui foi simples de enunciar e difícil de
validar com rigor: **um agricultor pode obter essa informação apenas
perguntando no WhatsApp, em português, do jeito que ele já fala?**

Para responder isso sem "achismo", a pesquisa foi além de construir o bot —
ela avaliou formalmente, com métricas usadas na literatura de Text-to-SQL
(Spider, BIRD), se diferentes LLMs conseguem gerar SQL correto o suficiente
para esse domínio, e quais falham e por quê. Um dos achados: um modelo aberto
de 31B parâmetros superou o modelo proprietário usado em produção, sugerindo
que tamanho de modelo não é o único fator relevante para essa tarefa. Os
detalhes completos, dataset de avaliação e discussão estão na monografia
linkada acima.

---

## Como funciona

```
Mensagem no WhatsApp
   → Evolution API (gateway)
     → Webhook Flask  (filtra grupo + menção ao bot)
       → Agente CrewAI "analista_climatico"
           → gera SQL via tool calling
           → ConsultaBancoTool (executor read-only) → Supabase/PostgreSQL
       → agente formula a resposta em linguagem natural
   → resposta enviada de volta ao WhatsApp
```

- **Dados:** série pluviométrica de Quixadá (1974–2025), origem FUNCEME,
  hospedada no Supabase (PostgreSQL).
- **LLM:** configurável via variáveis de ambiente — compatível com qualquer
  modelo/provedor que fale o formato da API Anthropic.
- **Orquestração de agente:** [CrewAI](https://www.crewai.com/).
- **Gateway WhatsApp:** [Evolution API](https://github.com/EvolutionAPI/evolution-api).
- **Segurança da camada SQL:** a `ConsultaBancoTool` bloqueia por padrão
  qualquer instrução destrutiva (`DELETE`, `DROP`, `UPDATE`, `INSERT`,
  `TRUNCATE`, `ALTER`) antes de executar a query gerada pelo agente — o bot só
  tem acesso de leitura à base.

---

## Estrutura do repositório

```
app/
├── webhook.py                      # Entry point Flask (porta 5000)
├── knowledge/                      # Persona hints do CrewAI
└── src/chatbot_pluviometrico/
    ├── crew.py                     # Agente "analista_climatico" + task + crew
    ├── main.py                     # Execução local e envio via Evolution API
    ├── config/
    │   ├── agents.yaml              # Persona e instruções do agente
    │   └── tasks.yaml               # Template da task (placeholders {hoje} e {Q})
    ├── tools/
    │   └── consulta_banco.py        # ConsultaBancoTool — executor SQL read-only
    └── dadosfunceme/
        └── chuvas/
            ├── importar_pluviometria.py   # Importador dos dados brutos da FUNCEME
            └── posto121_quixada.txt       # Série histórica bruta (posto 121, Quixadá)
```

---

## Executando a aplicação

Pré-requisitos: Python ≥3.10 <3.13 e [`uv`](https://docs.astral.sh/uv/).

```bash
# Instalar dependências
uv sync

# Configurar credenciais
cp .env.example .env        # e preencher os valores (ver seção abaixo)

# Rodar o webhook (Flask na porta 5000)
uv run python app/webhook.py

# Teste rápido via CLI, sem precisar do WhatsApp
uv run python -m chatbot_pluviometrico.main
```

> **Windows:** ative a venv (`.venv\Scripts\activate`) antes de rodar comandos
> `crewai`, para evitar erros de encoding com os emojis usados internamente
> pelo CrewAI no terminal do Windows.

### Variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

| Variável | Descrição |
|----------|-----------|
| `TARGET_GROUP_ID` | JID do grupo de WhatsApp que o bot escuta |
| `TARGET_MENTIONED_JID` | JID do próprio bot, usado para detectar menções |
| `ANTHROPIC_API_KEY` / `ANTHROPIC_BASE_URL` / `ANTHROPIC_MODEL` | Configuração do LLM (qualquer provedor compatível com a API Anthropic) |
| `SUPABASEDB_URI` | String de conexão PostgreSQL com os dados pluviométricos |
| `EVOLUTION_API_URL` / `EVOLUTION_API_KEY` / `EVOLUTION_INSTANCE` | Configuração do gateway Evolution API |

---

## Stack

Python · CrewAI · Flask · psycopg2 · Supabase (PostgreSQL) · Evolution API ·
[`uv`](https://docs.astral.sh/uv/) · Ruff

---

## Sobre a pesquisa

Este código foi desenvolvido como parte de um Trabalho de Conclusão de Curso
em Sistemas de Informação pela Universidade Federal do Ceará, apresentado em
julho de 2026. Para o framework de avaliação Text-to-SQL, o dataset de teste,
os relatórios comparativos entre modelos de linguagem e o texto completo da
monografia, consulte:

📄 **[Repositório institucional da UFC — riufc/87838](http://repositorio.ufc.br/handle/riufc/87838)**

## Autor

**Nauan Castro** — [nauanhs1@gmail.com](mailto:nauanhs1@gmail.com)
