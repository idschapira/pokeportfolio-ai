# CLAUDE.md — PokéPortfolio AI (capstone)

Repositório **público** da submissão do capstone do curso Kaggle "5-Day AI Agents".
Este repo deve conter **só o produto** (código + README + license). Notas de
mentoria ficam em `_mentoria/` (gitignorada — nunca vai para o GitHub).

> **Ao trabalhar no capstone, mantenha aberta também a pasta do curso**
> (`Kaggle-AI-Agents-MBA`), pois lá fica o original do `Diário_Aprendizado.md`.
> Uma cópia de referência dele está em `_mentoria/` para consulta offline.

## Documentos de apoio (em `_mentoria/`, só local)
- `Diário_Capstone.md` — decisões, escopo, progresso e dúvidas do projeto final. **Ler antes de qualquer tarefa.**
- `Regras_Capstone.md` — regras oficiais do hackathon. **Ler antes de decisões sobre a submissão.**
- `Diário_Aprendizado.md` — cópia de referência das lições do curso.
- `AUTENTICACAO.md` — passo a passo manual de login (`agents-cli`, ADC/`gcloud`) e split WSL/Windows.

## Segurança — regra inegociável (a mais importante)
Nunca peça ao usuário para colar, digitar ou exibir uma chave de API, token ou
segredo — em nenhuma superfície (chat ou runner `!`). Toda interação é
potencialmente logada. 🚨 **NENHUMA chave/senha no código ou na submissão.**

Segredos (`GEMINI_API_KEY`, `GOOGLE_API_KEY`) ficam em variáveis de ambiente
(`~/.bashrc`); referencie pelo nome (`"$GEMINI_API_KEY"`), nunca pelo valor. A
chave da API de cartas (pokewallet.io/pokemontcg.io) entra como variável de
ambiente e em `.env` (gitignorado) — `.env.example` guarda só os **nomes**.

**Nunca execute você mesmo login/autenticação** (`agents-cli login`,
`gcloud auth login`). Isso é manual, feito pelo usuário fora da sessão. No máximo
rode comandos de **status**. Se não estiver autenticado, pare e aponte o usuário
para `_mentoria/AUTENTICACAO.md`. Se uma chave vazar, alerte e instrua a revogar
em https://aistudio.google.com/apikey.

## Ao encontrar um bug — buscar nos diários ANTES de debugar
Procure primeiro em `_mentoria/Diário_Aprendizado.md` (lições técnicas do curso:
API drift, Windows/WSL, auth, deploy) e em `_mentoria/Diário_Capstone.md` (bugs do
projeto) se já enfrentamos algo parecido, e reaplique a solução. Só investigue do
zero se não houver registro. Bug novo → registre causa e solução no diário
correspondente.

## Visão do produto (resumo)
Agente **Concierge** que cadastra cartas Pokémon por **texto livre** (ex.: "2
Charizard ex 151 NM, 1 Mewtwo GX PSA 9"): interpreta → extrai entidades → resolve
ambiguidades (via MCP) → pede confirmação → salva e atualiza o portfólio com valor
total. MVP: single-user, só texto, persistência Firestore, submissão em inglês.
Conceitos do curso demonstrados: **ADK, MCP, Security, Deployability, Agents CLI**.
Detalhes e decisões completas em `_mentoria/Diário_Capstone.md`.

## Higiene do repositório público
- O repo é **público**: jamais commitar `_mentoria/`, `.env`, chaves ou credenciais.
- `README.md` em **inglês**: problema, solução, arquitetura, setup (vale 20 pts).
- Licença: **CC-BY 4.0**.

## Ambiente
WSL2 Ubuntu — usar `uv`/`agents-cli`, não pip/venv manual. Projeto GCP:
`kaggle-dia5-agent-runtime`. Para deploy via `agents-cli` (binário Windows) é
preciso exportar `GOOGLE_APPLICATION_CREDENTIALS` (ADC no WSL) e
`GOOGLE_CLOUD_PROJECT` — ver `_mentoria/AUTENTICACAO.md`.
