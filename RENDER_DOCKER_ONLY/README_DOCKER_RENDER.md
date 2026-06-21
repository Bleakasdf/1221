# Render Docker Deploy

Use this package to avoid Render Python/Ruby command problems.

1. Upload these files to the GitHub repository root:
   - app/
   - requirements.txt
   - Dockerfile
   - .dockerignore

2. In Render create NEW Web Service.

3. Select Runtime: Docker.

4. Do not set Build Command.

5. Do not set Start Command.

6. Add Environment Variables:
   BOT_TOKEN=old token
   DATABASE_URL=Neon connection string
   ALLOWED_TELEGRAM_IDS=
   EXPORT_DIR=exports
   TELEGRAM_PROXY=

7. Deploy.

Health URL:
/health

Expected response:
Training bot is running.
