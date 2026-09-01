---
id: 55
title: IN-10 · Jede Backend-Aenderung baut Torch und Docling neu
status: backlog
priority: medium
created: 2026-09-01T09:57:11.385309146+02:00
updated: 2026-09-01T10:14:25.760901274+02:00
assignee: akar
tags:
    - infra
    - performance
depends_on:
    - 45
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
