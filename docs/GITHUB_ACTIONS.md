# Automatisation GitHub Actions — Deribit

## Fonctionnement

- **Workflow** : `.github/workflows/deribit_daily.yml`
- **Horaire** : `15 0 * * *` → 00:15 UTC chaque jour
- **Déclenchement manuel** : Actions → Deribit BTC Options Daily → Run workflow
- **Sorties** :
  - Commit automatique dans `data/raw/` et `data/logs/last_run.json`
  - Insertion Neon (`btc_options`) via le secret `DATABASE_URL`
  - Artefact ZIP conservé 90 jours (JSON + `last_run.json`)

## Mise en place (une fois)

Le workflow est déjà sur `main`. Vérifiez que les **Actions** sont activées (*Settings → Actions → General → Allow all actions*).

Secret requis : **`DATABASE_URL`** (connection string Neon, `sslmode=require`).

Permissions : *Settings → Actions → Workflow permissions* → **Read and write**.

## Coûts

- Gratuit pour les dépôts publics (minutes Actions incluses).
- Dépôts privés : quota mensuel de minutes (suffisant pour ~1 run/jour < 5 min).

## Dépannage

| Problème | Solution |
|----------|----------|
| Workflow absent | Pousser `.github/workflows/deribit_daily.yml` sur `main` |
| Push refusé | Workflow permissions → **Read and write** |
| Pas de commit | Vérifier les logs ; l’API Deribit doit répondre |
| Postgres échoue | Vérifier `DATABASE_URL` dans les secrets ; voir `last_run.json` dans l’artefact |
| ETL OK mais job rouge | Ancienne version : le commit peut échouer (`continue-on-error`) ; vérifier l’étape **Run ETL pipeline** |
