# Deploiement de test SIOU

## 1. Backend Render

1. Ouvrir Render.
2. Cliquer sur `New +`.
3. Choisir `Blueprint`.
4. Selectionner le repo GitHub `Simplice01/siou-chatbot`.
5. Render lit le fichier `render.yaml`.
6. Renseigner la variable secrete `OPENAI_API_KEY`.
7. Lancer le deploy.

Le backend sera disponible sous une URL du type :

```text
https://siou-backend.onrender.com
```

Verifier :

```text
https://siou-backend.onrender.com/api/health
```

La reponse attendue est :

```json
{"status":"ok"}
```

## 2. Frontend Vercel

1. Ouvrir Vercel.
2. `Add New` puis `Project`.
3. Importer le repo `Simplice01/siou-chatbot`.
4. Definir `Root Directory` sur :

```text
frontend
```

5. Garder le preset `Next.js`.
6. Ajouter la variable d'environnement :

```env
NEXT_PUBLIC_API_BASE_URL=https://siou-backend.onrender.com/api
```

Remplacer l'URL par l'URL reelle Render.

7. Lancer le deploy.

Le lien a envoyer pour test sera l'URL Vercel :

```text
https://votre-projet.vercel.app
```

## Note

Sur le plan gratuit Render, le backend peut dormir apres inactivite. Le premier message peut donc etre lent, puis les reponses deviennent plus rapides.

