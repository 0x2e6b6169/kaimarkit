---
id: 55
title: IN-10 · Jede Backend-Aenderung baut Torch und Docling neu
status: done
priority: medium
created: 2026-09-01T09:57:11.385309146+02:00
updated: 2026-09-01T13:48:14.358653719+02:00
started: 2026-09-01T12:39:31.063630981+02:00
completed: 2026-09-01T13:48:13.736647596+02:00
assignee: akar
tags:
    - infra
    - performance
depends_on:
    - 45
    - 59
class: standard
---

## Befund (01.09.2026, beim Neubau fuer IN-9 gemessen)

Der Neubau nach BE-13 und BE-14 lief ueber elf Minuten und steckte in Stufe #20,
`pip install` von Torch, Docling, transformers und easyocr. Erwartet waren fuenf
Minuten mit warmem Cache. Der Cache hat nicht gegriffen, und der Grund steht im
Dockerfile.

## Ursache

`docker/Dockerfile`, Stufe `builder`:

```
COPY backend/ /src/backend/
RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu /src/backend
```

Der `COPY` bringt den gesamten Quelltext in die Schicht **vor** dem `pip install`.
Jede Aenderung an irgendeiner Datei unter `backend/` — auch an einem Test — macht
die Installationsschicht ungueltig. Dann wird alles neu geholt und gebaut, obwohl
sich keine einzige Abhaengigkeit geaendert hat.

Verschaerfend: `models` leitet sich mit `FROM builder` ab. Faellt der Cache in
`builder`, faellt er auch fuer den Modell-Download — das sind noch einmal rund zehn
Minuten. Beide Male gemessen, heute morgen und eben.

Die Frontend-Stufe macht es bereits richtig: erst `package.json` und
`package-lock.json`, dann `npm ci`, danach der Quelltext. Die Backend-Stufe folgt
diesem Muster nicht.

## Wirkung

Bei der Arbeitsweise dieses Projekts trifft es jedes Backend-Ticket, das im
Container geprueft werden soll. Zwanzig Minuten je Durchgang, bei denen sich nichts
Neues installiert.

## Eigene Dateien

- `docker/Dockerfile` (Stufe `builder`)
- `docs/entwicklung.md`, falls die Bauzeiten dort genannt sind

Haengt an #45 (IN-8), das den Dockerfile bereits besitzt.

## Vorgaben

Abhaengigkeiten und Anwendung in getrennte Schichten. Naheliegend ist, zuerst nur
`backend/pyproject.toml` zu kopieren und daraus die Abhaengigkeiten zu installieren,
danach den Quelltext zu kopieren und das Paket ohne Abhaengigkeiten nachzuziehen.
Welcher Weg genau, entscheidet die umsetzende Lane — die Wirkung ist die Vorgabe,
nicht das Mittel.

## Pruefung

- Eine Aenderung an einer Datei unter `backend/` und danach `make up`: Die Stufen
  fuer `pip install` und den Modell-Download melden `CACHED`.
- Gegenprobe: Eine Aenderung an `backend/pyproject.toml` laesst beide Stufen zu
  Recht neu laufen.
- Die gemessene Bauzeit nach einer reinen Quelltextaenderung steht in der
  Ticketnotiz, gemessen und nicht geschaetzt.

## Zurueckgestellt

Vom Nutzer zurueckgestellt, bis die Abnahmefassung steht (01.09.2026).

[[2026-09-01]] Tue 10:14
Die Zahl, gemessen statt geschaetzt (von akar): Von `make down` um 09:44:25 bis `healthy` um 10:13:30 vergingen **29 Minuten**. Ausgeloest hat das eine Aenderung unter `backend/` — die Merges von BE-13 und BE-14 —, ohne dass sich eine einzige Abhaengigkeit geaendert haette.

Zum Vergleich die Erwartung, unter der zuvor geplant wurde: fuenf Minuten, gerechnet aus einem warmen Cache. Der Unterschied zwischen fuenf und neunundzwanzig ist der Betrag, um den dieses Ticket jeden Durchgang verkuerzt.

Das ist zugleich der Ausgangswert fuer die Pruefung: Nach der Aenderung muss eine reine Quelltextaenderung deutlich darunter liegen, und die gemessene Zeit gehoert in die Ticketnotiz.

[[2026-09-01]] Tue 12:06
Die Ursache reicht weiter als der Titel sagt (Nebenbefund von akar aus dem Lauf zu #45, 01.09.2026): Der Bau **aus dem Worktree** hat `pip install` (300 s) und den Modell-Download (379 s) komplett neu gefahren, **obwohl unter `backend/` nichts geaendert war**. Geaendert war allein die Docs-Stufe im Dockerfile.

Damit ist die Praemisse dieses Tickets zu eng gefasst. "Jede Backend-Aenderung baut Torch neu" stimmt, ist aber nicht der ganze Fall — der Cache faellt auch ohne Backend-Aenderung.

Eine naheliegende Erklaerung scheidet aus, geprueft statt vermutet: `COPY . .` steht in Zeile 86 und gehoert zur **Docs-Stufe**, die mit einem eigenen `FROM` bei Zeile 76 beginnt. Die Builder-Stufe (Zeilen 29-47) kopiert nur `backend/`. Das Rauschen aus `.git`, das bei jedem Commit anfaellt, kann die Installationsschicht also nicht ungueltig machen.

**Was die Schichten wirklich verwirft, ist damit offen.** Wer dieses Ticket umsetzt, faengt bei dieser Frage an und nicht bei der Umstellung: zweimal hintereinander bauen, ohne etwas zu aendern, und sehen, ob `CACHED` erscheint. Erst wenn feststeht, was den Cache verwirft, ist zu entscheiden, ob die Trennung von Abhaengigkeiten und Quelltext ueberhaupt hilft.

## Umgesetzt (akar-24, 01.09.2026) — Merge bbf7180, Commit 12d3d17

### Die Diagnose zuerst, wie der zweite Nachtrag es verlangt

Zweimal hintereinander gebaut, ohne etwas zu aendern: Der zweite Lauf brauchte
**3 Sekunden**, jede Stufe meldete `CACHED`. Der Cache greift also — er wird
verworfen, und die Frage war wodurch.

### Die Ursache liegt in .dockerignore, nicht im Dockerfile

Ein Muster ohne Schraegstrich vergleicht in `.dockerignore` nur die **oberste
Ebene** des Kontextes. `__pycache__/`, `.pytest_cache/`, `.ruff_cache/` und
`node_modules/` liessen deshalb `backend/app/__pycache__`,
`backend/.pytest_cache` und `backend/.ruff_cache` durch. Jeder Lauf von `pytest`
oder `ruff` schrieb sie neu, der naechste Bau verwarf damit `COPY backend/`
(alte Fassung, Zeile 42) und installierte Torch und Docling ein weiteres Mal.
Ueber `FROM builder` (Zeile 51) fiel der Modell-Download gleich mit.

Belegt, nicht vermutet: Ein Probeabbild mit `COPY backend/ /x/` meldete `CACHED`,
solange nichts geschah; eine einzige geaenderte `.pyc`-Datei unter
`backend/app/__pycache__` liess es neu laufen; der Lauf danach war wieder
`CACHED`.

Damit ist auch der Nebenbefund aus dem Lauf zu #45 erklaert: Dort war unter
`backend/` nichts geaendert — aber vorher waren die Tests gelaufen.

Die Praemisse des Rumpfes stimmt trotzdem, sie war nur nicht der ganze Fall: Auch
in einem sauberen Kontext verwirft jede Aenderung unter `backend/` dieselbe
Schicht.

### Was geaendert wurde

- `.dockerignore`: Die Artefaktmuster haben jetzt das Praefix `**/`. Geprueft mit
  einem Probeabbild — angelegte `backend/app/__pycache__`, `backend/.pytest_cache`,
  `frontend/node_modules` und ein `__pycache__` in der Wurzel kamen alle nicht mehr
  im Kontext an.
- `docker/Dockerfile`: sechs Stufen statt fuenf. `deps` installiert die
  Abhaengigkeiten, die es aus `backend/pyproject.toml` liest; `builder`
  (`FROM deps`) legt die Anwendung mit `--no-deps` darauf; `models` setzt jetzt
  auf `deps` auf statt auf `builder`, weil der Download docling braucht und nicht
  die Anwendung.
- `docs/entwicklung.md`: neuer Abschnitt „Das Abbild bauen".

### Die Pruefung

**Aenderung unter `backend/`, danach bauen** — bestanden. `deps 5/5`
(`pip install`) und `models 2/2` (Modell-Download) melden `CACHED`.

**Gegenprobe mit geaenderter `backend/pyproject.toml`** — bestanden. Beide Stufen
laufen zu Recht neu, 210 s und 173 s.

**Die Zahlen.** Dieselbe Quelltextaenderung (ein Kommentar in
`backend/app/__init__.py`), derselbe warme Cache:

| | Bauzeit |
|---|---|
| vorher, alter Dockerfile | **485 s** (`pip install` 210 s, Modell-Download 173 s) |
| nachher | **86 s** (beide `CACHED`; es lief nur `pip install --no-deps`, 6 s) |

Eine zweite Bestaetigung von aussen: `make up` aus dem Haupt-Checkout brauchte
**195 s**, beide Stufen `CACHED` — obwohl `backend/__pycache__`,
`backend/.pytest_cache` und `backend/.ruff_cache` dort weiterhin auf der Platte
liegen. Genau das war vorher der Fall, der alles verwarf.

**Vorbehalt zur Messlage.** Alle Zahlen entstanden vor dem VPN des Nutzers, in
einem Zug und unter gleichen Netzbedingungen; die beiden Laeufe mit echtem
Download liegen mit 485 s und 482 s eng beieinander. Nach der Warnung wurde kein
weiterer Lauf mit Zeitnahme gemacht, der herunterlaedt. Die 86 s holen nichts aus
dem Netz und haengen deshalb nicht daran.

**Funktionspruefung des neuen Abbilds.** `/api/health` meldet `ok`, alle drei
Engines stehen auf `ready`, `tabelle.pdf` laeuft ueber docling und ueber
markitdown, `text.odt` ueber pandoc — Antwort fuer Antwort dieselbe wie beim
laufenden alten Abbild. Der Dienst aus dem Haupt-Checkout ist `healthy`.

### Nebenbefund, nicht geaendert

Die Docs-Stufe kopiert mit `COPY . .` (Zeile 86 der alten, 100 der neuen Fassung)
den ganzen Kontext einschliesslich `.git`. Sie laeuft deshalb nach jedem Commit
neu. Gemessen kostet das 20 bis 23 Sekunden — klein genug, um es hier stehen zu
lassen, gross genug, um es zu nennen.
