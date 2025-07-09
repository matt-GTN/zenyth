
---

## Prérequis

- Docker & Docker Compose
- Un nom de domaine pointant vers votre serveur
- Un compte Webshare avec un plan « Rotating Residential Proxy »
- Python 3.9+ (pour développement local)

---

## Installation

1. **Cloner le dépôt**
   ```bash
   git clone <url-du-repo>
   cd zenyth
   ```

2. **Configurer les variables d’environnement**
   - Copier le fichier `.env.example` en `.env` dans le dossier `backend`
   - Renseigner vos identifiants Webshare :
     ```
     WEBSHARE_PROXY_USERNAME=mon_username
     WEBSHARE_PROXY_PASSWORD=mon_password
     ```
   - (Optionnel) Ajouter d’autres variables selon vos besoins.

3. **Configurer Nginx**
   - Le fichier de conf Nginx pour chaque domaine se trouve dans `/etc/nginx/sites-available/`.
   - Exemple de virtual host :
     ```
     server {
         listen 80;
         server_name tryzenyth.app www.tryzenyth.app;
         return 301 https://$host$request_uri;
     }
     server {
         listen 443 ssl http2;
         server_name tryzenyth.app www.tryzenyth.app;
         # ... SSL config ...
         location / {
             proxy_pass http://localhost:3000;
         }
         location /api/ {
             proxy_pass http://localhost:8000/;
         }
     }
     ```
   - Activer la conf et recharger Nginx :
     ```bash
     ln -s /etc/nginx/sites-available/tryzenyth.app /etc/nginx/sites-enabled/
     systemctl reload nginx
     ```

4. **Lancer les services**
   ```bash
   docker compose up -d --build
   ```

---

## Utilisation

- Accédez à l’interface web via `https://votre-domaine/`
- Pour obtenir la transcription d’une vidéo, saisissez l’URL YouTube dans le champ prévu.
- L’API backend utilise automatiquement le proxy Webshare pour contourner les blocages IP.

---

## Dépannage

### Problèmes courants

- **Erreur 502 Bad Gateway**  
  → Vérifiez que le backend est bien démarré (`docker compose ps`).

- **Erreur "RequestBlocked" ou "IpBlocked"**  
  → Cela signifie que l’IP du proxy est blacklistée par YouTube.  
  → Essayez d’augmenter le nombre de retries, de changer de pool Webshare, ou contactez le support Webshare pour obtenir un pool « YouTube Unblocker ».

- **Erreur 407 Proxy Authentication Required**  
  → Vérifiez vos identifiants Webshare dans le `.env`.

- **Pas de trafic dans le dashboard Webshare**  
  → Vérifiez la configuration du proxy dans le code et dans le `.env`.

### Tester le proxy manuellement

Dans le conteneur backend :
```bash
docker compose exec -T backend python - << 'PY'
import os, requests
proxies = {
    "http":  f"http://{os.getenv('WEBSHARE_PROXY_USERNAME')}-rotate:{os.getenv('WEBSHARE_PROXY_PASSWORD')}@p.webshare.io:80",
    "https": f"http://{os.getenv('WEBSHARE_PROXY_USERNAME')}-rotate:{os.getenv('WEBSHARE_PROXY_PASSWORD')}@p.webshare.io:80",
}
r = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
print(r.text)
PY
```

---

## Crédits

- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
- [Webshare](https://www.webshare.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Nginx](https://nginx.org/)
- [Docker](https://www.docker.com/)

---

## Licence

Ce projet est sous licence MIT.

---

## Contact

Pour toute question ou contribution, ouvrez une issue ou contactez l’auteur.
