FROM python:3.11-slim

LABEL org.opencontainers.image.title="Edge Quantum Guard"
LABEL org.opencontainers.image.version="0.1.0"
LABEL org.opencontainers.image.description="EQG autonomous quantum execution control layer"

WORKDIR /app

COPY requirements.txt pyproject.toml README.md LICENSE VERSION ./
COPY src ./src
COPY main.py ./
COPY configs ./configs

RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -e .

ENV EQG_MODE=sim
ENV PYTHONUNBUFFERED=1

RUN mkdir -p /app/outputs

ENTRYPOINT ["python", "main.py"]
CMD ["--mode", "sim", "--smoke", "--output-dir", "/app/outputs"]
