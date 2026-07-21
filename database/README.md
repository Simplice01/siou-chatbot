# Base PostgreSQL SIOU

Ce dossier contient le modèle de base de données cible pour SIOU, aligné avec l'étude d'architecture.

## Objectif

La base doit permettre de stocker :

- les directions, agences, guichets et services compétents ;
- les documents officiels ou internes : décrets, arrêtés, accords, fiches, procédures ;
- les fiches de service structurées pour l'orientation des usagers ;
- les événements et actualités utiles au cas d'usage "quoi de neuf" ;
- les chunks RAG et leurs embeddings via `pgvector` ;
- les conversations, messages, sources citées, signalements et journaux d'audit ;
- la gouvernance documentaire : points focaux, validation, révision mensuelle.

## Fichiers

- `schema.sql` : script SQL complet PostgreSQL + pgvector.
- `seed_reference_data.sql` : données de référence minimales pour initialiser MTDI, ASIN, SBIN, Guichet Startup, etc.
- `render-postgres.md` : procédure pour créer la base sur Render et donner un lien de connexion.

## Tables principales

| Table | Rôle |
|---|---|
| `organizations` | Ministère, directions, agences, sociétés, cellules, guichets et services. |
| `users` | Secrétaires, points focaux, responsables ministère, administrateurs. |
| `source_files` | Fichiers sources déposés : PDF, Word, HTML, API, RSS. |
| `documents` | Documents normalisés, validés, publiés, avec dates et métadonnées. |
| `service_cards` | Fiches structurées d'orientation des usagers. |
| `events` | Événements numériques/IA, formations, journées portes ouvertes. |
| `document_chunks` | Fragments indexés pour le RAG avec `embedding vector(1536)`. |
| `conversations` | Sessions de chat. |
| `messages` | Questions/réponses du chatbot. |
| `message_sources` | Sources documentaires citées dans les réponses. |
| `feedback_reports` | Signalements de réponses fausses ou imprécises. |
| `review_tasks` | Tâches de révision documentaire. |
| `audit_logs` | Traçabilité des actions sensibles. |

## Relations clés

```text
organizations
  ├── users
  ├── source_files
  ├── documents
  ├── service_cards
  ├── events
  └── document_chunks

source_files ── documents ── document_chunks

conversations ── messages ── message_sources ── documents / document_chunks

messages ── feedback_reports

documents / service_cards ── review_tasks
```

## Dimension des embeddings

Le schéma utilise :

```sql
embedding vector(1536)
```

C'est adapté à `text-embedding-3-small` d'OpenAI en dimension par défaut.

Si l'équipe migre vers BGE-M3, il faudra créer une migration vers :

```sql
embedding vector(1024)
```

## Exécution locale

```bash
psql "$DATABASE_URL" -f database/schema.sql
```

Sur Windows PowerShell :

```powershell
psql $env:DATABASE_URL -f database/schema.sql
psql $env:DATABASE_URL -f database/seed_reference_data.sql
```
