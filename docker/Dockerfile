# syntax=docker/dockerfile:1

# kaimarkit — ein Abbild, das Backend, Frontend und Dokumentation ausliefert.
#
# Der Build-Kontext ist die Projektwurzel, nicht docker/. Alle COPY-Pfade lauten
# deshalb backend/, frontend/ und so weiter:
#
#     docker build -f docker/Dockerfile .
#
# Fuenf Stufen: Frontend, Python-Abhaengigkeiten, Docling-Modelle, Dokumentation,
# Laufzeit. Nur die letzte landet im Abbild.


# ── 1. Frontend ────────────────────────────────────────────────────────────────
FROM node:22-alpine AS frontend

WORKDIR /build

# Erst die Sperrdatei, dann der Quelltext: So bleibt die Schicht mit npm ci
# erhalten, solange sich nur Komponenten aendern.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


# ── 2. Python-Abhaengigkeiten ──────────────────────────────────────────────────
FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/venv/bin:$PATH"

# Einzelne Abhaengigkeiten liefern nur ein sdist; ohne Compiler bricht der Bau ab.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv

COPY backend/ /src/backend/

# Torch kommt aus dem CPU-Index. Die Standard-Wheels ziehen die CUDA-Bibliotheken
# nach und blaehen das Abbild um rund zwei Gigabyte auf. Der CPU-Index liefert
# dieselben Versionen mit dem lokalen Kennzeichen "+cpu", das pip vorzieht.
RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu /src/backend


# ── 3. Docling-Modelle ─────────────────────────────────────────────────────────
FROM builder AS models

# Vorgebacken, damit die Laufzeit ohne Netz auskommt. HF_HOME zeigt auf dasselbe
# Verzeichnis: Docling laedt einen Teil der Gewichte ueber den Hugging-Face-Cache,
# und der soll neben den uebrigen Modellen liegen, nicht in /root.
ENV HF_HOME=/opt/docling-models

RUN docling-tools models download --output-dir /opt/docling-models


# ── 4. Dokumentation ───────────────────────────────────────────────────────────
FROM python:3.12-slim AS docs

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY . .

# Zwei Wege zur ausgelieferten Dokumentation, und der zweite ist der Grund, dass
# der allererste Bau ueberhaupt durchlaeuft: Im veroeffentlichten Repo liegt unter
# gh-pages die von mike gebaute Fassung mit allen Versionen. In einem frischen
# Klon vor dem ersten Release gibt es diesen Zweig nicht — dann baut die Stufe die
# aktuelle Fassung selbst.
#
# Die Abhaengigkeiten stehen in backend/pyproject.toml unter der Gruppe "docs".
# Sie werden von dort gelesen, damit es nur eine Quelle dafuer gibt.
RUN git config --global --add safe.directory /src \
    && mkdir -p /docs-site \
    && GH_PAGES="" \
    && for ref in gh-pages origin/gh-pages; do \
           if git rev-parse --verify "$ref" >/dev/null 2>&1; then GH_PAGES="$ref"; break; fi; \
       done \
    && if [ -n "$GH_PAGES" ]; then \
           git archive "$GH_PAGES" | tar -x -C /docs-site; \
       else \
           python -c "import tomllib; print('\n'.join(tomllib.load(open('backend/pyproject.toml','rb'))['project']['optional-dependencies']['docs']))" > /tmp/docs-requirements.txt \
           && pip install -r /tmp/docs-requirements.txt \
           && mkdocs build --site-dir /docs-site; \
       fi


# ── 5. Laufzeit ────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Muss zu PANDOC_VERSION in docker/.env.example passen.
ARG PANDOC_VERSION=3.6.4

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/opt/venv/bin:$PATH" \
    DOCLING_ARTIFACTS_PATH=/opt/docling-models \
    HF_HOME=/opt/docling-models \
    HF_HUB_OFFLINE=1

# Tesseract fuer die Texterkennung, Pandoc als .deb aus dem Release. curl wird nur
# zum Holen gebraucht und danach wieder entfernt.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        tesseract-ocr \
        tesseract-ocr-deu \
        tesseract-ocr-eng \
    && curl -fsSL -o /tmp/pandoc.deb \
        "https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-1-amd64.deb" \
    && dpkg -i /tmp/pandoc.deb \
    && rm /tmp/pandoc.deb \
    && apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system kaimarkit \
    && useradd --system --gid kaimarkit --home-dir /opt/kaimarkit --shell /usr/sbin/nologin kaimarkit

# Die Anwendung steckt im venv: pip hat sie zusammen mit ihren Abhaengigkeiten
# installiert. Ein zweites Abbild des Quelltextes im Container wuerde nur die
# Frage aufwerfen, welches der beiden laeuft.
COPY --from=builder /opt/venv /opt/venv
COPY --from=models --chown=kaimarkit:kaimarkit /opt/docling-models /opt/docling-models
COPY --from=frontend --chown=kaimarkit:kaimarkit /build/dist /opt/kaimarkit/static
COPY --from=docs --chown=kaimarkit:kaimarkit /docs-site /opt/kaimarkit/docs

WORKDIR /opt/kaimarkit
USER kaimarkit

EXPOSE 8000

# Docling laedt seine Modelle beim Start. Die start_period deckt das ab.
HEALTHCHECK --interval=30s --timeout=10s --start-period=180s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=5)"

# --proxy-headers, weil vor dem Dienst ein Reverse Proxy stehen kann. Die
# Workerzahl kommt aus der Umgebung; jeder Worker haelt eigene Docling-Modelle im
# Speicher, deshalb ist der Standard 1.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*' --workers ${KAIMARKIT_WORKERS:-1}"]
