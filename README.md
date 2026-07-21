# SIOU Document AI

Lecteur documentaire intelligent local. L'utilisateur ouvre un PDF, lit le document et dialogue avec une IA qui répond uniquement à partir du PDF ouvert.

## Architecture

- `backend/` : FastAPI, PostgreSQL, parsing PDF, chunking, embeddings, FAISS, retrieval, prompt strict, LLM OpenAI ou Ollama.
- `frontend/` : Next.js, TypeScript, TailwindCSS, bibliothèque de PDF, lecteur, zoom, pagination, recherche, panneau IA et sources cliquables.
- `backend/documents/` : dossier local où déposer les PDF.
- `backend/vector_store/` : index FAISS et métadonnées générés automatiquement.
- `database/` : schéma PostgreSQL cible, données de référence et guide Render.

## Configuration Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
```

Variables principales dans `backend/.env` :

```env
DATABASE_URL=postgresql://...
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
LLM_PROVIDER=openai
OPENAI_CHAT_MODEL=gpt-4o-mini
```

Pour Ollama :

```env
EMBEDDING_PROVIDER=ollama
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_CHAT_MODEL=llama3.1
```

Le provider `hash` est disponible pour les tests locaux sans clé API. Pour une vraie utilisation, choisis `openai` ou `ollama`.

## Indexation

Dépose les PDF dans :

```text
backend/documents/
```

Puis lance :

```bash
cd backend
python scripts/index_documents.py
```

Le script détecte les nouveaux PDF, évite les doublons via empreinte SHA-256 et réindexe seulement les fichiers modifiés.

## Lancement Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Endpoints principaux :

- `GET /api/health`
- `GET /api/documents`
- `GET /api/db/documents`
- `GET /api/source-files`
- `GET /api/organizations`
- `GET /api/service-cards`
- `GET /api/users`
- `GET /api/conversations`
- `GET /api/documents/{document_id}/file`
- `POST /api/index`
- `POST /api/documents/reindex`
- `POST /api/chat`
- `POST /api/feedback`
- `GET /api/admin/stats`

Payload chat :

```json
{
  "question": "Quel est le montant du contrat ?",
  "document": "document-id"
}
```

Réponse :

```json
{
  "answer": "...",
  "confidence": 0.82,
  "sources": [],
  "pages": [3],
  "citation": "..."
}
```

## Configuration Frontend

```bash
cd frontend
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

L'application sera disponible sur `http://localhost:3000`.

## Tests

```bash
cd backend
pytest
```

Les tests couvrent :

- chunking
- embeddings locaux déterministes
- indexation FAISS
- retrieval
- service RAG
- API FastAPI

## Structure

```text
backend/
  app/
    api/
    core/
    services/
    ai/
    models/
    schemas/
    utils/
  documents/
  vector_store/
  scripts/
  tests/
frontend/
  app/
  components/
  layouts/
  hooks/
  lib/
  services/
  types/
  public/
```

## Comportement IA

Le prompt système impose une règle stricte : aucune connaissance externe. Si les extraits récupérés ne contiennent pas la réponse, l'API renvoie clairement que l'information est absente du document.

## PostgreSQL et RAG

L'application utilise une architecture hybride :

- PostgreSQL structure les documents, fichiers sources, organisations, fiches services, conversations, messages et sources utilisées.
- FAISS garde l'index vectoriel rapide pour retrouver les passages pertinents sans relire toute la base à chaque question.
- `POST /api/chat` interroge l'index documentaire, demande au LLM de répondre uniquement à partir des extraits, puis enregistre la conversation et les sources dans PostgreSQL quand `DATABASE_URL` est configuré.
