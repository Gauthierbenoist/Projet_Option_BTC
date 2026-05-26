# Snapshots Deribit (GitHub Actions)

Ce dossier est rempli **automatiquement** par le workflow [`.github/workflows/deribit_daily.yml`](../../.github/workflows/deribit_daily.yml) chaque jour à **00:15 UTC**.

| Sous-dossier | Contenu |
|--------------|---------|
| `raw/YYYY-MM-DD/` | JSON brut API Deribit |
| `cleaned/` | CSV nettoyé du jour |
| `logs/` | `last_run.json` (statut dernière exécution) |

Les données locales (`data/raw/`, `data/cleaned/`) restent sur votre machine et ne sont pas poussées sur Git.
