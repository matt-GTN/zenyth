FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --uid 10001 --create-home appuser && chown -R appuser:appuser /app
USER appuser
# Fail the image build when API imports or route registration break.
RUN OPENROUTER_API_KEYS=ci-placeholder python -c "from api import app; assert '/summarize' in app.openapi()['paths']"
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "600"]