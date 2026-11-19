# Serveur Snap N Cash pour un Space Hugging Face (SDK Docker). Construit par scripts/deploy_space.sh.
FROM python:3.12-slim

# Un Space Docker tourne sous l'utilisateur 1000
RUN useradd -m -u 1000 user
ENV PATH="/home/user/.local/bin:$PATH" PYTHONUNBUFFERED=1
WORKDIR /home/user/app

COPY --chown=user requirements.txt .
USER user
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user backend ./backend
COPY --chown=user agents ./agents

# Port attendu par le Space (app_port dans README.md). --proxy-headers : l'adresse du client vient du proxy du Space.
EXPOSE 7860
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860", "--proxy-headers", "--forwarded-allow-ips", "*"]
