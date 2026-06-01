# Projet_Option_BTC

Pipeline journalier des options BTC actives sur **Deribit** : archive JSON (`data/raw/`) + chargement **PostgreSQL (Neon)**.

- Documentation : [data/README.md](data/README.md)
- Neon : [docs/NEON_SETUP.md](docs/NEON_SETUP.md)
- GitHub Actions : [docs/GITHUB_ACTIONS.md](docs/GITHUB_ACTIONS.md)

```bash
pip install -r requirements.txt
cp .env.example .env   # DATABASE_URL
python data/scripts/run_daily_pipeline.py
```
