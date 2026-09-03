# kaimarkit — die Aufrufe an einer Stelle.
#
# Alle Ziele laufen aus dem Wurzelverzeichnis. Compose leitet sein
# Projektverzeichnis aus der ersten -f-Datei ab und liest deshalb docker/.env.

.DEFAULT_GOAL := help
SHELL := /bin/bash

# Die Dateikette. Jede Ergaenzung haengt hinten an und ueberschreibt einzelne
# Werte der Basis. Authelia setzt Traefik voraus: Die ForwardAuth-Middleware
# haengt am Traefik-Router.
COMPOSE          := docker compose -f docker/docker-compose.yml
COMPOSE_TRAEFIK  := $(COMPOSE) -f docker/docker-compose.traefik.yml
COMPOSE_AUTHELIA := $(COMPOSE_TRAEFIK) -f docker/docker-compose.authelia.yml

ENV_FILE := docker/.env

# Der Stand des Arbeitsbaums, einmal hier ermittelt und an jedes Ziel
# weitergereicht, das baut. Compose setzt ihn als Bau-Argument ein, das Abbild
# behaelt ihn als ENV, und der Dienst meldet ihn unter /api/health. Im Container
# fragt deshalb niemand nach Git.
#
# Drei Faelle liefern nichts: ein Bau aus einem Tarball ohne .git, ein Klon ohne
# Tags und eine Maschine ohne git. Keiner davon darf den Bau abbrechen, deshalb
# faengt 2>/dev/null den Fehler ab. Bleibt der Wert leer, wird er auch nicht
# exportiert — sonst ueberschriebe die leere Zeichenkette einen Wert, den jemand
# fuer genau diesen Fall in docker/.env von Hand eingetragen hat.
KAIMARKIT_VERSION := $(shell git describe --tags --always --dirty 2>/dev/null)
ifneq ($(KAIMARKIT_VERSION),)
export KAIMARKIT_VERSION
endif

# Kein globales Python. Die Ziele rufen die Programme direkt aus der
# pyenv-Umgebung auf, damit kein aktiviertes Shell-Profil noetig ist.
PYENV_ROOT ?= $(HOME)/.pyenv
VENV       := $(PYENV_ROOT)/versions/claude-code
VENV_BIN   := $(VENV)/bin

.PHONY: help up up-traefik up-authelia down logs build dev test test-slow \
        test-slow-image lint docs-serve docs-release check-env check-docker \
        check-venv

help: ## Diese Uebersicht anzeigen
	@echo "kaimarkit — verfuegbare Ziele:"
	@echo
	@grep -hE '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN { FS = ":.*## " } { printf "  %-16s %s\n", $$1, $$2 }'
	@echo
	@echo "Beispiel: make docs-release VERSION=0.3"


# ── Betrieb ──────────────────────────────────────────────────────────────────

up: check-env check-docker ## Dienst bauen und starten
	$(COMPOSE) up -d --build

up-traefik: check-env check-docker ## Dienst hinter Traefik starten
	$(COMPOSE_TRAEFIK) up -d --build

up-authelia: check-env check-docker ## Dienst hinter Traefik und Authelia starten
	$(COMPOSE_AUTHELIA) up -d --build

down: check-env check-docker ## Dienst beenden und Container entfernen
	$(COMPOSE) down

logs: check-env check-docker ## Ausgabe des Dienstes mitlesen
	$(COMPOSE) logs -f

build: check-env check-docker ## Nur das Abbild bauen, nichts starten
	$(COMPOSE) build


# ── Entwicklung ──────────────────────────────────────────────────────────────

dev: check-venv ## Backend auf :8000 und Frontend auf :5173, beide mit Reload
	@echo "Backend auf :8000, Frontend auf :5173 — beenden mit Strg-C."
	@trap 'kill 0' EXIT INT TERM; \
	 ( cd backend && $(VENV_BIN)/uvicorn app.main:app --reload ) & \
	 ( cd frontend && npm run dev ) & \
	 wait

# -rs gehoert an jeden Lauf: Es nennt jeden uebersprungenen Test mit Grund.
# Ohne den Schalter faellt eine fehlende Abhaengigkeit nur als kleinere
# Sammelzahl auf, und die liest niemand.
test: check-venv ## Tests ohne die Docling-Modelle, Uebersprungenes mit Grund
	cd backend && $(VENV_BIN)/pytest -q -rs

# Docling steht nur im Abbild. Dieses Ziel meldet deshalb auf dem
# Entwicklungsrechner "3 skipped" und Rueckgabewert 0 — es belegt nichts.
test-slow: check-venv ## Die slow-Tests lokal; ohne Docling ueberspringen sie sich
	cd backend && $(VENV_BIN)/pytest -q -rs -m slow

# Hier laufen sie wirklich. Das Abbild bringt Docling und die Modelle mit;
# pytest und httpx fehlen ihm und kommen fuer den Lauf dazu. Das Backend haengt
# nur lesend darin, der Container verschwindet danach. Setzt "make build"
# voraus und laesst einen laufenden Dienst unberuehrt.
test-slow-image: check-env check-docker ## Die slow-Tests im Abbild, wo Docling steht — dauert
	@set -a; . ./$(ENV_FILE); set +a; \
	 docker run --rm -u root -v "$(CURDIR)/backend:/src:ro" -w /src \
	   "$$KAIMARKIT_IMAGE:$$KAIMARKIT_TAG" \
	   sh -c "pip install -q pytest httpx \
	          && python -m pytest -q -rs -m slow -p no:cacheprovider"

lint: check-venv ## ruff ueber das Backend laufen lassen
	cd backend && $(VENV_BIN)/ruff check .


# ── Dokumentation ────────────────────────────────────────────────────────────

docs-serve: check-venv ## Dokumentation als Vorschau auf :8001
	$(VENV_BIN)/mkdocs serve --dev-addr 127.0.0.1:8001

# mike schreibt in den Zweig gh-pages und verschiebt den Alias latest mit.
docs-release: check-venv ## Version veroeffentlichen: make docs-release VERSION=0.3
	@test -n "$(VERSION)" || { \
	  echo "VERSION fehlt. Aufruf: make docs-release VERSION=0.3"; exit 1; }
	$(VENV_BIN)/mike deploy --update-aliases $(VERSION) latest
	$(VENV_BIN)/mike set-default latest


# ── Voraussetzungen ──────────────────────────────────────────────────────────

check-env:
	@test -f $(ENV_FILE) || { \
	  echo "$(ENV_FILE) fehlt. Compose setzt sonst still leere Werte ein."; \
	  echo "Anlegen mit: cp docker/.env.example $(ENV_FILE)"; exit 1; }

# Fragt den Daemon, nicht das Plugin: "docker compose version" antwortet auch
# ohne Zugriff auf den Socket. "docker version" braucht einen Aufruf ueber den
# Socket und ist damit die Pruefung, die das Recht wirklich belegt. Eine einzelne
# API-Anfrage genuegt dafuer; "docker info" sammelt den ganzen Daemon-Zustand ein
# und braucht ein Vielfaches der Zeit.
check-docker:
	@docker version --format '{{.Server.Version}}' >/dev/null 2>&1 || { \
	  echo "Der Docker-Daemon antwortet nicht:"; \
	  docker version 2>&1 | tail -n 1; \
	  echo 'Fehlt die Gruppe: sudo usermod -aG docker $$USER, danach neu anmelden.'; \
	  echo "Was die Gruppe einschließt, steht in docs/betrieb/lokal.md."; exit 1; }

check-venv:
	@test -x $(VENV_BIN)/python || { \
	  echo "Die pyenv-Umgebung \"claude-code\" fehlt unter $(VENV)."; \
	  echo "Anlegen mit: pyenv virtualenv 3.12 claude-code"; exit 1; }
