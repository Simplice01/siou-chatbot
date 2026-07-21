# Mettre la base PostgreSQL SIOU sur Render

## 1. Créer la base

Dans Render :

1. `New +`
2. `Postgres`
3. Nom recommandé :

```text
siou-postgres
```

4. Database :

```text
siou
```

5. User :

```text
siou_user
```

6. Région : choisir la même région que le backend Render si possible.
7. Plan recommandé pour un test sérieux :

```text
basic-256mb
```

Render Blueprint utilise aujourd'hui des plans PostgreSQL du type `basic-256mb`, `basic-1gb`, etc.

Render documente la création d'une base via `New + > Postgres` et fournit ensuite les URLs de connexion depuis l'onglet `Info`.

## 2. Récupérer l'URL de connexion

Dans la page de la base Render :

- utiliser `Internal Database URL` pour un backend hébergé sur Render ;
- utiliser `External Database URL` pour pgAdmin, DBeaver, DataGrip, un ordinateur local ou un autre système externe.

L'équipe externe à qui tu envoies la connexion aura généralement besoin de l'`External Database URL`.

## 3. Activer le schéma

Depuis ton PC, deux options.

Option A - avec le script Python du projet :

```powershell
cd backend
$env:DATABASE_URL="postgresql://USER:PASSWORD@HOST:PORT/DBNAME"
python scripts/init_database.py
```

Option B - avec `psql` :

```powershell
$env:DATABASE_URL="postgresql://USER:PASSWORD@HOST:PORT/DBNAME"
psql $env:DATABASE_URL -f database/schema.sql
psql $env:DATABASE_URL -f database/seed_reference_data.sql
```

Ou avec le `PSQL Command` fourni par Render :

```bash
psql "postgresql://USER:PASSWORD@HOST:PORT/DBNAME" -f database/schema.sql
psql "postgresql://USER:PASSWORD@HOST:PORT/DBNAME" -f database/seed_reference_data.sql
```

Le script active :

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Render indique que ses bases PostgreSQL supportent des extensions populaires, dont `pgvector`, selon la version PostgreSQL.

## 4. Variables à ajouter au backend Render

Quand le backend utilisera PostgreSQL, ajouter :

```env
DATABASE_URL=<Internal Database URL Render>
```

Ne pas utiliser l'External Database URL entre deux services Render si l'Internal Database URL est disponible.

Le fichier `render.yaml` du projet contient déjà une base `siou-postgres` et expose automatiquement `DATABASE_URL` au backend via `fromDatabase`.

## 5. Ce qu'il faut envoyer à l'équipe externe

Pour qu'ils puissent connecter leur système :

```text
Host:
Port:
Database:
User:
Password:
SSL mode: require
External Database URL:
```

À éviter dans un email public : envoyer le mot de passe en clair dans le même message que le lien. Idéalement, envoyer l'URL à une personne autorisée et le mot de passe via un second canal.

## Sources Render

- Render - Create and Connect to Render Postgres : https://render.com/docs/postgresql-creating-connecting
- Render - Supported Extensions for Render Postgres : https://render.com/docs/postgresql-extensions
