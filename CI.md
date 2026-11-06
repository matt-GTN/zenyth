# CI et images Docker

Chaque pull request construit les images de production (installation des dépendances et build frontend). Aucun secret applicatif ni accès VPS n’est requis. Il n’existe pas encore de suite de tests applicatifs automatisée dans cette CI.

Un push sur `main` ou un lancement manuel depuis `main` publie les images sur GHCR avec le SHA complet du commit et `latest`. Déployer le tag SHA ou le digest, puis conserver cette référence pour le rollback. Les PR ne publient pas d’image. Le déploiement du VPS reste une opération distincte.

Images :
- `ghcr.io/matt-gtn/zenyth-backend:<commit-sha>`
- `ghcr.io/matt-gtn/zenyth-frontend:<commit-sha>`
