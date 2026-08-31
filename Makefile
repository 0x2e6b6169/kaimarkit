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

# Kein globales Python. Die Ziele rufen die Programme direkt aus der
# pyenv-Umgebung auf, damit kein aktiviertes Shell-Profil noetig ist.
PYENV_ROOT ?= $(HOME)/.pyenv
VENV       := $(PYENV_ROOT)/versions/claude-code
VENV_BIN   := $(VENV)/bin

.PHONY: help up up-traefik up-authelia down logs build dev test test-slow lint \
        docs-serve docs-release check-env check-venv

help: ## Diese Uebersicht anzeigen
	@echo "kaimarkit — verfuegbare Ziele:"
	@echo
	@grep -hE '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN { FS = ":.*## " } { printf "  %-14s %s\n", $$1, $$2 }'
	@echo
	@echo "Beispiel: make docs-release VERSION=0.3"


# ── Betrieb ──────────────────────────────────────────────────────────────────

up: check-env ## Dienst bauen und starten
	$(COMPOSE) up -d --build

up-traefik: check-env ## Dienst hinter Traefik starten
	$(COMPOSE_TRAEFIK) up -d --build

up-authelia: check-env ## Dienst hinter Traefik und Authelia starten
	$(COMPOSE_AUTHELIA) up -d --build

down: check-env ## Dienst beenden und Container entfernen
	$(COMPOSE) down

logs: check-env ## Ausgabe des Dienstes mitlesen
	$(COMPOSE) logs -f

build: check-env ## Nur das Abbild bauen, nichts starten
	$(COMPOSE) build


# ── Entwicklung ──────────────────────────────────────────────────────────────

dev: check-venv ## Backend auf :8000 und Frontend auf :5173, beide mit Reload
	@echo "Backend auf :8000, Frontend auf :5173 — beenden mit Strg-C."
	@trap 'kill 0' EXIT INT TERM; \
	 ( cd backend && $(VENV_BIN)/uvicorn app.main:app --reload ) & \
	 ( cd frontend && npm run dev ) & \
	 wait

test: check-venv ## Tests ohne die Docling-Modelle
	cd backend && $(VENV_BIN)/pytest -q

test-slow: check-venv ## Tests mit Docling, dauert
	cd backend && $(VENV_BIN)/pytest -q -m slow

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

check-venv:
	@test -x $(VENV_BIN)/python || { \
	  echo "Die pyenv-Umgebung \"claude-code\" fehlt unter $(VENV)."; \
	  echo "Anlegen mit: pyenv virtualenv 3.12 claude-code"; exit 1; }
