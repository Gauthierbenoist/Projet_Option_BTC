# Migration PostgreSQL → Neon

## Ce dont j’ai besoin (depuis le dashboard Neon)

Dans ton projet **btc_options** → **Connection details** :

### Option A (recommandée) — une seule variable

Copie la **connection string** (mode **Direct**, pas pooler pour les inserts massifs) :

```
postgresql://USER:PASSWORD@ep-xxxx.region.aws.neon.tech/neondb?sslmode=require
```

À mettre dans :
- `.env` local : `DATABASE_URL=...`
- GitHub Secrets : secret `DATABASE_URL` (même valeur)

### Option B — variables séparées

| Variable | Où la trouver sur Neon |
|----------|-------------------------|
| `POSTGRES_HOST` | Host (`ep-....neon.tech`) |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_DB` | nom de la base (ex. `neondb`) |
| `POSTGRES_USER` | utilisateur |
| `POSTGRES_PASSWORD` | mot de passe |
| `POSTGRES_SSLMODE` | `require` |

## Configuration locale

1. Édite `.env` à la racine (ne jamais committer) :

```env
DATABASE_URL=postgresql://USER:PASSWORD@ep-xxx.neon.tech/neondb?sslmode=require
PIPELINE_SKIP_DB=0
```

2. Initialise le schéma + migre l’historique :

```bash
python data/scripts/backfill_db.py
```

3. Vérifie dans Neon SQL Editor :

```sql
SELECT snapshot_date, COUNT(*) FROM btc_options GROUP BY snapshot_date ORDER BY snapshot_date;
```

## GitHub Actions (automatisation SQL)

Ajoute le secret **`DATABASE_URL`** dans  
`Settings → Secrets and variables → Actions`.

Le workflow poussera alors chaque jour :
- JSON/CSV dans le repo
- lignes dans Neon (`btc_options`)

## Sécurité

- Ne partage pas le mot de passe dans le chat.
- Utilise uniquement `.env` (local) et GitHub Secrets (cloud).
