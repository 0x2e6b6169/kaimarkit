# syntax=docker/dockerfile:1

# kaimarkit — ein Abbild, das Backend, Frontend und Dokumentation ausliefert.
#
# Der Build-Kontext ist die Projektwurzel, nicht docker/. Alle COPY-Pfade lauten
# deshalb backend/, frontend/ und so weiter:
#
#     docker build -f docker/Dockerfile .
#
# Sechs Stufen: Frontend, Python-Abhaengigkeiten, Anwendung, Docling-Modelle,
# Dokumentation, Laufzeit. Nur die letzte landet im Abbild.


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
FROM python:3.12-slim AS deps

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/venv/bin:$PATH"

# Einzelne Abhaengigkeiten liefern nur ein sdist; ohne Compiler bricht der Bau ab.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv

# Erst die Abhaengigkeiten, dann der Quelltext — dasselbe Muster wie oben im
# Frontend. Kaeme "backend/" schon hier herein, verwuerfe jede Aenderung daran
# diese Schicht: gemessene 210 Sekunden fuer die Installation und, weil die
# Modellstufe darauf aufsetzt, weitere 200 fuer den Download.
#
# Welche Pakete es sind, steht in pyproject.toml und wird von dort gelesen, damit
# es nur eine Quelle dafuer gibt. Die Docs-Stufe liest ihre Gruppe ebenso.
COPY backend/pyproject.toml /src/backend/pyproject.toml

# Torch kommt aus dem CPU-Index. Die Standard-Wheels ziehen die CUDA-Bibliotheken
# nach und blaehen das Abbild um rund zwei Gigabyte auf. Der CPU-Index liefert
# dieselben Versionen mit dem lokalen Kennzeichen "+cpu", das pip vorzieht.
RUN python -c "import tomllib; print('\n'.join(tomllib.load(open('/src/backend/pyproject.toml','rb'))['project']['dependencies']))" > /tmp/requirements.txt \
    && pip install --extra-index-url https://download.pytorch.org/whl/cpu -r /tmp/requirements.txt


# ── 3. Anwendung ───────────────────────────────────────────────────────────────
FROM deps AS builder

COPY backend/ /src/backend/

# --no-deps, weil alles Noetige schon im venv liegt. Ohne den Schalter fragte pip
# den Index noch einmal ab und koennte dabei eine Abhaengigkeit austauschen, die
# die Stufe darueber eben erst festgelegt hat.
RUN pip install --no-deps /src/backend


# ── 4. Docling-Modelle ─────────────────────────────────────────────────────────
# Setzt auf "deps" auf und nicht auf "builder": Der Download braucht docling, nicht
# die Anwendung. So bleibt er erhalten, wenn sich allein der Quelltext aendert.
FROM deps AS models

# Vorgebacken, damit die Laufzeit ohne Netz auskommt. HF_HOME zeigt auf dasselbe
# Verzeichnis: Docling laedt einen Teil der Gewichte ueber den Hugging-Face-Cache,
# und der soll neben den uebrigen Modellen liegen, nicht in /root.
ENV HF_HOME=/opt/docling-models

# Docling zieht ueber rapidocr das OpenCV-Rad herein, und dessen Bibliothek
# erwartet drei Systembibliotheken, die python:3.12-slim nicht mitbringt. Ohne sie
# scheitert schon das Herunterladen der Modelle an "import cv2".
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0t64 libxcb1 \
    && rm -rf /var/lib/apt/lists/*

# Der vorgegebene Satz bringt EasyOCR nicht mit; seit docling 2.56 ist es ein
# Extra. Der Adapter waehlt es aber ausdruecklich, deshalb der zweite Aufruf: ohne
# ihn fehlt craft_mlt_25k.pth, und jede Wandlung mit Texterkennung scheitert im
# Betrieb an HF_HUB_OFFLINE=1. Die Sprachen sind die Voreinstellung von
# KAIMARKIT_OCR_LANGS.
RUN docling-tools models download --output-dir /opt/docling-models \
    && docling-tools models download --output-dir /opt/docling-models easyocr \
        --easyocr-lang de --easyocr-lang en


# ── 5. Dokumentation ───────────────────────────────────────────────────────────
FROM python:3.12-slim AS docs

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

# Die Eingaben kommen einzeln herein, in der Reihenfolge, in der sie sich aendern:
# die Abhaengigkeiten selten, die Seiten oefter, ".git" bei jedem Commit. Ein
# "COPY . ." zog den ganzen Kontext herein und verwarf damit die Stufe nach jedem
# Commit — gemessene 20 bis 43 Sekunden fuer eine Aenderung, die kein Wort der
# Dokumentation anfasst; wie viel davon, haengt an der Leitung, denn
# PIP_NO_CACHE_DIR laedt mkdocs-material jedes Mal neu. Was die Stufe nicht liest,
# gehoert deshalb auch nicht in sie: weder backend/app noch frontend/ noch docker/.
#
# Die Abhaengigkeiten stehen in backend/pyproject.toml unter der Gruppe "docs".
# Sie werden von dort gelesen, damit es nur eine Quelle dafuer gibt.
COPY backend/pyproject.toml /src/backend/pyproject.toml
RUN python -c "import tomllib; print('\n'.join(tomllib.load(open('backend/pyproject.toml','rb'))['project']['optional-dependencies']['docs']))" > /tmp/docs-requirements.txt \
    && pip install -r /tmp/docs-requirements.txt

# Die aktuelle Fassung entsteht immer. Sie ist das, was ein Repo vor dem ersten
# Release ausliefert, und zugleich der Rueckfall fuer jeden Kontext ohne
# brauchbares .git.
COPY mkdocs.yml /src/mkdocs.yml
COPY docs/ /src/docs/
RUN mkdocs build --site-dir /docs-site

# Und zuletzt die veroeffentlichte Fassung, wenn es sie gibt: Unter gh-pages liegt
# die von mike gebaute Dokumentation mit allen Versionen; die eben gebaute kennt
# nur die eine. Wo der Zweig existiert, ersetzt er sie.
#
# Zwei Faelle daneben. In einem frischen Klon vor dem ersten Release gibt es den
# Zweig nicht. Und kommt der Kontext aus einem Git-Worktree, ist ".git" dort kein
# Verzeichnis, sondern eine Datei mit einem Zeiger auf den Haupt-Checkout; im
# Container laeuft dieser Zeiger ins Leere. Git nimmt das nicht hin und beendet
# jeden Aufruf im Baum mit 128 — auch "git config --global", das aus dem Repo
# nichts liest. Deshalb steht die Frage nach dem Verzeichnis vor dem ersten
# Git-Aufruf und nicht erst vor dem zweiten.
#
# Der Bind-Mount zeigt auf die Wurzel des Bau-Kontextes, nicht auf ".git" selbst.
# Daran haengt, ob der Bau ueberhaupt beginnt: BuildKit loest die Quelle eines
# Mounts schon auf, wenn es den Cache-Schluessel bildet, also bevor die erste
# Zeile des Skripts laeuft. Zeigt sie auf ".git" und fehlt das Verzeichnis, endet
# der Bau mit '"/.git": not found', und die Wache darunter kommt nie an die Reihe.
# Die Wurzel des Kontextes gibt es dagegen immer; ob ".git" darin liegt,
# entscheidet erst das Skript. So baut auch, wer den Quelltext als Tarball oder
# als flachen Klon ohne Verlauf bezogen hat.
#
# ".git" wird nur gelesen und nicht kopiert: Eine Schicht von zwoelf Megabyte mit
# dem Verlauf darin braucht niemand. Am Zwischenspeicher aendert die groessere
# Quelle wenig. Ein Bind-Mount geht mit seinem Inhalt in den Cache-Schluessel ein;
# bisher verwarf jeder Commit diese Schicht, jetzt tut es jede Aenderung am
# Kontext. Beides kostet Sekundenbruchteile, weil pip install und mkdocs build
# oberhalb des Mounts stehen und erhalten bleiben.
RUN --mount=type=bind,source=.,target=/ctx \
    set -e; \
    [ -d /ctx/.git ] || exit 0; \
    git config --global --add safe.directory /ctx; \
    GH_PAGES=""; \
    for ref in gh-pages origin/gh-pages; do \
        if git -C /ctx rev-parse --verify "$ref" >/dev/null 2>&1; then GH_PAGES="$ref"; break; fi; \
    done; \
    [ -n "$GH_PAGES" ] || exit 0; \
    rm -rf /docs-site; \
    mkdir -p /docs-site; \
    git -C /ctx archive "$GH_PAGES" | tar -x -C /docs-site


# ── 6. Laufzeit ────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Muss zu PANDOC_VERSION in docker/.env.example passen.
ARG PANDOC_VERSION=3.6.4

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/opt/venv/bin:$PATH" \
    DOCLING_ARTIFACTS_PATH=/opt/docling-models \
    HF_HOME=/opt/docling-models \
    HF_HUB_OFFLINE=1

# Pandoc als .deb aus dem Release. libgl1, libglib2.0-0t64 und libxcb1 braucht das
# OpenCV-Rad, das mit docling hereinkommt. curl wird nur zum Holen des .deb
# gebraucht und danach wieder entfernt. Die Texterkennung braucht kein
# Systempaket: EasyOCR liegt als Gewichte in /opt/docling-models.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        libgl1 \
        libglib2.0-0t64 \
        libxcb1 \
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

# Der Stand, aus dem gebaut wurde. Das Makefile ermittelt ihn mit "git describe"
# und reicht ihn als Bau-Argument herein; im Abbild steht er als ENV, und der
# Dienst meldet ihn unter /api/health. Nichts davon ruft git auf: Die Docs-Stufe
# haengt ".git" als Bind-Mount ein, die Laufzeit sieht es nie.
#
# Leer ist ein zulaessiger Wert — Bau aus einem Tarball, Klon ohne Tags, keine
# Installation von git. Der Bau laeuft dann durch, und das Backend faellt auf
# __version__ aus app/__init__.py zurueck.
#
# Steht so weit unten, weil sich der Wert bei jedem Commit aendert: Alles nach
# der ENV-Zeile faellt dann aus dem Zwischenspeicher. Oben im ENV-Block haette
# das die Pandoc-Installation und die COPY-Schichten mitgerissen.
ARG KAIMARKIT_VERSION=""
ENV KAIMARKIT_VERSION=${KAIMARKIT_VERSION}

EXPOSE 8000

# Docling laedt seine Modelle beim Start. Die start_period deckt das ab.
HEALTHCHECK --interval=30s --timeout=10s --start-period=180s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=5)"

# --proxy-headers, weil vor dem Dienst ein Reverse Proxy stehen kann. Die
# Workerzahl kommt aus der Umgebung; jeder Worker haelt eigene Docling-Modelle im
# Speicher, deshalb ist der Standard 1.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*' --workers ${KAIMARKIT_WORKERS:-1}"]
