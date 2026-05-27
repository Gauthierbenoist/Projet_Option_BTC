# Automatisation GitHub Actions — Deribit

## Fonctionnement

- **Workflow** : `.github/workflows/deribit_daily.yml`
- **Horaire** : `15 0 * * *` → 00:15 UTC chaque jour
- **Déclenchement manuel** : Actions → Deribit BTC Options Daily → Run workflow
- **Sorties** :
  - Commit automatique dans `data/raw/` et `data/cleaned/`
  - Artefact ZIP conservé 90 jours (onglet Actions → run → Artifacts)

## Mise en place (une fois)

Le workflow est déjà sur `main`. Vérifiez que les **Actions** sont activées (*Settings → Actions → General → Allow all actions*).

## Coûts

- Gratuit pour les dépôts publics (minutes Actions incluses).
- Dépôts privés : quota mensuel de minutes (suffisant pour ~1 run/jour < 5 min).

## Dépannage

| Problème | Solution |
|----------|----------|
| Workflow absent | Pousser `.github/workflows/deribit_daily.yml` sur `main` |
| Push refusé | *Settings → Actions → Workflow permissions* → **Read and write** |
| Pas de commit | Vérifier les logs ; l’API Deribit doit répondre |
| Postgres échoue | Vérifier les 5 secrets ou retirer `POSTGRES_PASSWORD` pour mode CSV seul |
