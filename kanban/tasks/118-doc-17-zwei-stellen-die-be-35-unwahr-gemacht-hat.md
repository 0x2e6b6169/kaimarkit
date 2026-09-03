---
id: 118
title: DOC-17 · Zwei Stellen, die BE-35 unwahr gemacht hat
status: done
priority: medium
created: 2026-09-03T14:55:03.218310731+02:00
updated: 2026-09-03T14:59:58.029877165+02:00
started: 2026-09-03T14:59:57.300436008+02:00
completed: 2026-09-03T14:59:57.300436008+02:00
assignee: akar
tags:
    - docs
class: standard
---

## Ziel

Zwei Befunde von akar beim Abschluss von DOC-15 (#109), beide durch BE-35 entstanden und
beide bewusst nicht mitgeändert, weil sie fremden Abschnitten gehören.

1. `docs/schnellstart.md:12` sagt, der Dienst hole zur Laufzeit nichts mehr aus dem Netz.
   Seit `POST /api/convert/url` stimmt das so absolut nicht mehr. Der Abschnitt „Was der
   Dienst gar nicht tut" in `docs/grenzen.md` ist schon berichtigt; diese Stelle nicht.
2. In der Tabelle „Vier Werte begrenzen einen Aufruf" fehlt `KAIMARKIT_URL_TIMEOUT`. Mit
   der neuen Variable sind es fünf — und die Überschrift zählt mit.

## Eigene Dateien

- `docs/schnellstart.md` (Zeile 12 und ihr Absatz)
- die Seite mit der Tabelle „Vier Werte begrenzen einen Aufruf" samt Überschrift

Die zweite Datei steht hier bewusst nicht mit Namen: Erst nachsehen, wo die Tabelle
steht — `docs/betrieb/konfiguration.md` ist die Vermutung, nicht der Befund. Steht sie an
zwei Stellen, gehören beide dazu; Konvention 6 zieht `docker/.env.example` mit, falls
dort eine Zahl oder ein Kommentar dieselbe Aussage macht.

Nicht hier: `docs/grenzen.md`, `docs/api.md`, `docs/index.md`, `docs/formate.md` — alle
vier hat DOC-15 zuletzt angefasst und sie stimmen.

## Vorgaben

- Die Aussage in `schnellstart.md` wird genau, nicht gestrichen. Der Dienst holt eine
  Seite, wenn man ihn ausdrücklich darum bittet, und sonst nichts — kein Nachladen von
  Modellen, keine Telemetrie, keine eingebetteten Ressourcen einer geholten Seite.
- Die Überschrift nennt die Zahl, die die Tabelle führt. Wer eine Zeile ergänzt, ändert
  die Zahl mit; sonst entsteht genau der Fehler wieder, der dieses Ticket ist.

## Prüfung

- Rot vor grün, ohne Test: Vor der Arbeit einmal belegen, dass beide Stellen den
  bemängelten Wortlaut führen (Zeilennummer und Zitat in die Notiz), und danach, dass
  sie ihn nicht mehr führen.
- `grep -rn "Vier Werte" docs/` findet nach der Arbeit nichts mehr.
- `mkdocs build --strict` ohne Warnung.


## Ergebnis (akar-39)

Erledigt, Merge b6ac8cb (Branch task/118-two-stale-statements, Commit aef660c).

**Befund zum Ticketschnitt.** Die Tabelle „Vier Werte begrenzen einen Aufruf" steht in
`docs/grenzen.md:5` — also in einer der vier Dateien, die der Rumpf unter „Nicht hier"
als stimmend ausschließt. Der Ausschluss war eine Behauptung über den Quelltext und
traf für diesen Abschnitt nicht zu. Ziel 2 und die Prüfung (`grep -rn "Vier Werte"
docs/` findet nichts) sind ohne eine Änderung an `grenzen.md` unerfüllbar, deshalb habe
ich sie vorgenommen — aber nur im Abschnitt „Fünf Werte begrenzen einen Aufruf". Den
Abschnitt „Was der Dienst gar nicht tut", den DOC-15 berichtigt hat, habe ich nicht
angefasst. Kollisionsprüfung: BE-38 (#117) ist das einzige andere offene Ticket, das
`grenzen.md` nennt, und schließt die Datei ausdrücklich aus. Keine Kollision.

**Rot vor grün, vor der Arbeit:**

- `docs/schnellstart.md:11-12` — „… dafür holt der Dienst zur Laufzeit nichts mehr aus
  dem Netz."
- `docs/grenzen.md:5` — „## Vier Werte begrenzen einen Aufruf"
- `docs/grenzen.md:7` — „Alle vier kommen aus der Umgebung."

Danach: `grep -rn "Vier Werte" docs/` gibt Rückgabewert 1 und findet nichts,
`grep -rn "nichts mehr aus dem Netz" docs/` ebenso.

**Zählung.** Die Tabelle führt nach der Ergänzung genau fünf Zeilen
(`MAX_FILE_SIZE_MB`, `MAX_FILES`, `MAX_CONCURRENT`, `CONVERSION_TIMEOUT`,
`URL_TIMEOUT`), maschinell gezählt. Überschrift und Folgesatz nennen beide „fünf".
`KAIMARKIT_PANDOC_TIMEOUT` bleibt bewusst draußen: Es begrenzt nicht den Aufruf,
sondern den Pandoc-Prozess, und steht im Abschnitt darunter.

**Quelltextprüfung für die Aussage in `schnellstart.md`.** `backend/app/fetching.py` ist
die einzige Datei unter `backend/app/`, die `httpx` importiert; `requests`,
`urllib.request` und `urlopen` kommen nirgends vor. `_store()` schreibt allein den
Antwortkörper — eingebettete Ressourcen wie Bilder oder Stylesheets holt der Dienst
nachweislich nicht. Der Absatz sagt jetzt: Modelle lädt der Dienst zur Laufzeit nicht
mehr nach, ins Netz greift er nur auf Verlangen eines Aufrufs von `/api/convert/url`,
dann genau die eine Seite, und von sich aus schickt er nichts hinaus, auch keine
Nutzungsdaten.

**Konvention 6.** `docker/.env.example:79` führt `KAIMARKIT_URL_TIMEOUT=30` mit
Kommentar bereits, `docs/betrieb/konfiguration.md:76` ebenfalls. Beide stimmen mit
`config.py` (`url_timeout: int = 30`) überein — keine Änderung nötig.

**Prüfung.** `mkdocs build --strict` in der pyenv-Umgebung `claude-code`: Rückgabewert
0, null Zeilen `WARNING` oder `ERROR`. Auf die alte Überschrift zeigte kein Anker
(Suche nach `vier-werte` und `grenzen.md#` in `docs/`, `mkdocs.yml`, `README.md`: leer).
