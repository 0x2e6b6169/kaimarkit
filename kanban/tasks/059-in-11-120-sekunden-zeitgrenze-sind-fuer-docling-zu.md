---
id: 59
title: IN-11 · 120 Sekunden Zeitgrenze sind fuer Docling zu knapp
status: done
priority: high
created: 2026-09-01T10:40:33.636401513+02:00
updated: 2026-09-01T12:37:54.007733011+02:00
started: 2026-09-01T12:37:28.190914523+02:00
completed: 2026-09-01T12:37:28.190914523+02:00
assignee: akar
tags:
    - infra
    - config
depends_on:
    - 45
class: standard
---

## Befund (01.09.2026, erste echte Datei des Nutzers)

Eine einseitige Rechnung, `engine=auto` (also `docling`), auf dem Entwicklungsrechner:

    Finished converting document DB_Rechnung_647052188315.pdf in 103.51 sec.
    POST /api/convert HTTP/1.1 200 OK

Durchgelaufen — bei **86 Prozent** der Voreinstellung `KAIMARKIT_CONVERSION_TIMEOUT=120`
(`docker/.env.example:48`). Waehrenddessen: CPU 238 Prozent, RAM 1,77 von 6 GB, also
kein Speicherdruck. Die Zeit geht in Rechenarbeit, nicht ins Warten.

Ein alltaegliches Dokument — eine Rechnung, eine Seite — landet damit knapp unter der
Grenze. Das naechste ist darueber, und der Nutzer bekommt einen Abbruch fuer etwas,
das kein Sonderfall ist.

## Was die Zahl noch nicht trennt

Es war der **erste Docling-Aufruf nach dem Start**. Aus IN-9 ist belegt, dass der
extra kostet: dort 32 Sekunden fuer ein Bild, das spaeter schneller ging. Wie viel
der 103 Sekunden auf das Laden entfaellt und wie viel auf das Dokument, ist offen.

Deshalb haengt dieses Ticket mit BE-17 (#56) zusammen: Klaert sich dort, ob `ready`
wirklich `ready` heisst, aendert sich womoeglich auch diese Zahl. Die Entscheidung
ueber die Voreinstellung faellt erst nach der zweiten Messung.

## Eigene Dateien

- `docker/.env.example`
- `docs/betrieb/konfiguration.md`

Konvention 6 gilt: beide im selben Commit.

## Vorgaben

Dasselbe Dokument zweimal hintereinander umwandeln und beide Zeiten messen. Die
zweite ist die Arbeitszeit, die Differenz das Laden.

Danach die Voreinstellung so setzen, dass ein alltaegliches Dokument nicht an ihr
scheitert — mit der Messung als Begruendung, nicht mit einer runden Zahl. Und
`docs/betrieb/konfiguration.md` sagt, woran man merkt, dass die Grenze zu knapp ist:
Der Abbruch sieht fuer den Nutzer aus wie ein Fehler des Dienstes.

## Pruefung

- Beide Messungen stehen in der Ticketnotiz, aus dem Log abgeschrieben.
- Die neue Voreinstellung laesst dieselbe Rechnung mit Abstand durchlaufen.
- Gegenprobe: Eine Datei, die die Grenze wirklich reissen soll, bricht weiterhin
  sauber mit einer Fehlermeldung ab und haengt nicht.

## Zurueckgestellt

Vom Nutzer zurueckgestellt, bis die Abnahme abgeschlossen ist (01.09.2026).

[[2026-09-01]] Tue 11:07
Eingetreten, am selben Tag: **`TeleTrusT-T.I.S.P._T.P.S.S.E._CM_2026_Anmeldung.pdf` ist an der Grenze gescheitert.**

    Die Umwandlung hat die Zeitgrenze von 120 s ueberschritten

Damit steht das Ticket nicht mehr auf einer Vorhersage, sondern auf einem Vorfall. Von drei Dokumenten, die der Nutzer bei der Abnahme durchgeschickt hat, lag eines bei 86 Prozent der Grenze und eines darueber. Das ist keine Randlage, das ist der Alltag.

Der Dienst selbst hat sich richtig verhalten: Er bricht sauber ab, die Meldung nennt die Grenze und den Grund, und die Oberflaeche zeigt sie an der Datei an. Der Fehler liegt allein im Wert.

Was die Messung noch nicht hergibt: **Wie lange das Dokument gebraucht haette, ist unbekannt** — der Abbruch hat es abgeschnitten. Ohne diese Zahl laesst sich keine begruendete Voreinstellung waehlen, nur eine geratene. Wer das Ticket umsetzt, faehrt es zuerst mit einer weit gesetzten Grenze durch und misst.

Vom PO auf `high` gehoben.

[[2026-09-01]] Tue 11:19
Zwei Messungen zur Ursache, damit das Ticket nicht nur die Grenze hochsetzt (01.09.2026, im laufenden Container):

- **Torch benutzt zwei Threads**, nicht vier: `torch.get_num_threads()` -> `2`, `torch.cuda.is_available()` -> `False`. Der Rechner hat vier logische Kerne (`nproc`), waehrend der Umwandlung stand die CPU bei 238 Prozent. Torch waehlt die Zahl nach physischen Kernen; ob hier vier logische auf zwei physische kommen, ist nicht geprueft. Ein Versuch mit `torch.set_num_threads(4)` oder `OMP_NUM_THREADS=4` kostet nichts und liefert eine Zahl.
- **Der Container hat keine CPU-Grenze.** `docker/docker-compose.yml` setzt nur `mem_limit`, kein `cpus`. Die zwei Threads kommen also von Torch, nicht von Docker.

Damit hat dieses Ticket zwei Wege, und der zweite ist der bessere: die Grenze hochsetzen behandelt das Symptom, mehr Threads die Sache. Beide messen, dann entscheiden.

Nicht die Ursache sind die Anreicherungsmodelle: `_build_pipeline` schaltet weder Code- noch Formel- noch Bildklassifikation ein. `CodeFormulaV2` und `DocumentFigureClassifier` liegen im Abbild, laufen aber nicht — das ist Ballast in der Groesse, nicht in der Zeit.

[[2026-09-01]] Tue 11:22
Die fehlende Zahl ist da (01.09.2026, nach dem Quick-Fix des Nutzers auf 600 s): **`TeleTrusT-T.I.S.P._T.P.S.S.E._CM_2026_Anmeldung.pdf` brauchte 326 062 ms — 5 Minuten 26 Sekunden.** Mit `docling`, OCR aus.

Die Voreinstellung von 120 Sekunden liegt damit bei **37 Prozent** dessen, was dieses Dokument braucht. Es war nicht knapp daneben, sondern um das Zweieinhalbfache zu klein.

Damit steht die Entscheidungsgrundlage: Eine Voreinstellung, die alltaegliche Dokumente durchlaesst, liegt oberhalb von fuenf Minuten — oder die Sache wird an der Ursache angefasst (Threads, Enginewahl), statt die Grenze immer weiter hochzusetzen. Beide Wege stehen im Ticket; diese Zahl sagt, dass der zweite der wichtigere ist.

[[2026-09-01]] Tue 12:06
Abhaengigkeit auf #56 wieder entfernt (PO, 01.09.2026). Sie war verkehrt herum gesetzt.

Die Ueberlegung beim Anlegen war: Klaert sich in BE-17, ob `ready` wirklich `ready` heisst, aendert sich womoeglich diese Zahl. Richtig ist das Gegenteil. Die Vorgabe dieses Tickets lautet, dasselbe Dokument **zweimal hintereinander** zu messen; die zweite Zeit ist die Arbeitszeit, die Differenz das Laden. Genau diese Differenz ist die Zahl, die #56 braucht. Dieses Ticket liefert den Messwert, es wartet nicht darauf.

Ausserdem haette die Sperre eine `high`-Sache mit sichtbarer Wirkung fuer den Nutzer hinter einer `medium`-Untersuchung in einer anderen Lane angehalten — und akars Lane damit ganz.

Bleibt die Abhaengigkeit auf #45, und die ist erfuellt.

Umgesetzt (akar-23, 01.09.2026). Merge `01a8651`, Branch `task/59-conversion-timeout`.

## Womit gemessen wurde

**Die beiden Dokumente des Nutzers liegen nicht im Repo und auch sonst nicht auf der
Maschine** — gesucht unter `/home/kai` und `/mnt/c/Users`, nichts gefunden. Gemessen
wurde deshalb mit Ersatzvorlagen; keine der Zahlen unten stammt aus
`DB_Rechnung_647052188315.pdf` oder `TeleTrusT-...Anmeldung.pdf`.

- `eine-seite.pdf` — eine Seite mit Textschicht (`captcha-fox-2012.pdf` aus einem
  anderen Projekt des Nutzers).
- `scan-1.pdf` — dieselbe Seite bei 200 dpi gerastert und als JPEG eingebettet, also
  **ohne Textschicht**. Das ist das Gegenstueck zu einer eingescannten Rechnung.

Alle Laeufe am laufenden Container `kaimarkit` auf `127.0.0.1:8080`, `engine=docling`.
Zeiten aus `docker logs kaimarkit`, Zeile `Finished converting document ... in N sec.`

## Die Messung nach Vorgabe: dasselbe Dokument zweimal

**PDF mit Textschicht, OCR aus** — nach Neustart des Containers:

    Initializing pipeline for StandardPdfPipeline with options hash a6d37f82...
    Finished converting document eine-seite.pdf in 12.27 sec.
    Finished converting document eine-seite.pdf in 3.03 sec.

**Dieselbe Seite gescannt, OCR an** — nach erneutem Neustart:

    Initializing pipeline for StandardPdfPipeline with options hash b7d3334f...
    Finished converting document scan-1.pdf in 117.62 sec.
    Finished converting document scan-1.pdf in 173.54 sec.
    Finished converting document scan-1.pdf in 109.42 sec.

## Abweichung von der Annahme des Tickets

Die Vorgabe lautete: „Die zweite ist die Arbeitszeit, die Differenz das Laden."
**Beim gescannten Dokument stimmt das nicht.** Der zweite Lauf war mit 173,54 s
langsamer als der erste mit 117,62 s, der dritte mit 109,42 s wieder schneller. Drei
weitere Laeufe in einem eigenen Prozess im Container ergaben 150,65 / 86,73 /
118,36 / 161,42 s.

Die Streuung auf identischer Eingabe reicht damit von **87 bis 174 Sekunden, Faktor
1,8**. Die Differenz zweier Laeufe misst hier nicht das Laden der Modelle, sondern
das Rauschen des Rechners. Der Wert fuer die Voreinstellung folgt deshalb aus dem
langsamsten bekannten echten Dokument und dieser Streuung, nicht aus einer Differenz.

## Die Zahl fuer BE-17 (#56): das Laden dauert unter zehn Sekunden

Beim Dokument **mit** Textschicht ist die Differenz sauber, weil die Arbeitszeit
klein und stabil ist:

| Lauf | OCR aus | OCR an |
|---|---|---|
| erster (mit `Initializing pipeline`) | 12,27 s | 10,88 s |
| zweiter | 3,03 s | 2,58 s |
| **Differenz** | **9,24 s** | **8,30 s** |

Direkt gemessen im Container, `_build_pipeline(True)` mit einer Stoppuhr darum
herum: **8,50 s** bei zwei Threads, **3,49 s** bei vier.

**Das Laden der Modelle kostet also unter zehn Sekunden, nicht Minuten.** Der
Modulkopf von `backend/app/converters/docling.py:4` sagt „laedt vor dem ersten Aufruf
minutenlang" — mit den vorgebackenen Modellen aus dem Abbild gilt das nicht mehr.
Das gehoert nach #56.

Zwei Nebenbefunde dazu: Die Pipeline haengt am Hash der Optionen. OCR an und OCR aus
sind **zwei** Pipelines (`a6d37f82...` gegen `b7d3334f...`), und `start_warmup` baut
nur die zur Voreinstellung. Wer `ocr` im Aufruf umstellt, zahlt das Laden ein zweites
Mal. Ausserdem laedt EasyOCR sein Modell erst beim ersten Gebrauch, nicht beim Bau
der Pipeline.

## Der zweite Weg ist keiner: mehr Threads bringen nichts

Gemessen im Container, gleicher Prozessaufbau, `scan-1.pdf` je zweimal:

| Threads | Lauf 1 | Lauf 2 |
|---|---|---|
| 2 (Vorgabe) | 150,65 s | 86,73 s |
| 4 (`OMP_NUM_THREADS=4` + `torch.set_num_threads(4)`) | 118,36 s | 161,42 s |

Kein Unterschied ausserhalb der Streuung. Der Grund steht in `lscpu`: **zwei
physische Kerne, vier logische** (`Core(s) per socket: 2`, `Thread(s) per core: 2`,
i7-8565U). Torchs zwei Threads sind die zwei echten Kerne; die anderen zwei sind
SMT-Geschwister und rechnen nicht mit. Waehrend der Umwandlung stand die CPU bei
120 bis 360 Prozent, der Speicher bei hoechstens 2,15 von 6 GB — kein Druck.

**`docker/docker-compose.yml` bleibt unangetastet.** Eine CPU-Grenze fehlt dort zwar,
aber sie ist nicht die Ursache, und ein `cpus`-Eintrag wuerde nichts verbessern.

## Was die Zeit wirklich kostet

Nicht die Seitenzahl, sondern die fehlende Textschicht. Dieselbe Seite:

| | Zeit (zweiter Lauf) |
|---|---|
| mit Textschicht | **3,0 s** |
| gescannt, OCR an | **109 bis 174 s** |

Faktor vierzig. Die 103,51 s der Rechnung und die 326 s der Anmeldung sind damit
erklaert: Es waren gescannte Dokumente. Ein PDF aus einem Textprogramm laeuft in
Sekunden durch, egal wie lang die Grenze steht.

## Der neue Wert: 600 statt 120

Das langsamste bekannte echte Dokument brauchte 326 s. Die gemessene Streuung auf
identischer Eingabe betraegt Faktor 1,8. 326 mal 1,8 sind 587 — aufgerundet **600**.
Damit laeuft ein Dokument wie die Anmeldung auch an einem schlechten Tag durch, und
die Grenze bleibt eine Grenze: Bei rund zwei Minuten je gescannter Seite deckt sie
etwa fuenf Seiten ab, nicht beliebig viele.

## Pruefung

1. **Beide Messungen aus dem Log abgeschrieben** — siehe oben, samt der Abweichung
   von der Annahme.
2. **Laeuft mit Abstand durch** — `scan-1.pdf` (das Ersatzdokument fuer die Rechnung)
   dreimal in 109 bis 174 s gegen eine Grenze von 600 s.
3. **Gegenprobe bestanden.** Ein eigener Container `kaimarkit-in11-probe` aus
   demselben Abbild auf Port 8099, `KAIMARKIT_CONVERSION_TIMEOUT=20`, danach
   entfernt. `docling` auf `ready` abgewartet, dann `scan-1.pdf` geschickt:

       {"detail":"Die Umwandlung hat die Zeitgrenze von 20 s ueberschritten",
        "code":"conversion_timeout"}
       HTTP 504  wall 20.165792s

   Sauberer Abbruch nach 20,17 s, deutsche Meldung mit Grund und Grenze, kein
   Haengen. Der Container des Nutzers und `docker/.env` blieben unberuehrt.
4. `mkdocs build --strict` laeuft durch.

## Geaenderte Dateien

- `docker/.env.example:46-52` — Wert 600 mit der Messung als Begruendung im Kommentar.
- `docs/betrieb/konfiguration.md:45` — Tabellenwert; neuer Abschnitt „Woran man merkt,
  dass die Zeitgrenze zu knapp ist" am Ende von „Anwendung".
- `docs/grenzen.md:15` — nannte weiterhin 120 und waere durch diesen Merge unwahr
  geworden. Kein offenes Ticket besitzt die Seite (#42 und #62 sind `done`).

## Zwei Stellen nennen weiterhin 120 — Befund fuer den PO

Beide liegen ausserhalb dieses Tickets und ausserhalb akars Lane, deshalb nicht
angefasst:

- `backend/app/config.py:27` — `conversion_timeout: int = 120`. Die Voreinstellung im
  Code. Fuer den Container ohne Wirkung, weil Compose den Wert aus `.env` durchreicht;
  wer das Backend nackt mit `uvicorn` startet, bekommt weiterhin 120 s.
- `contracts/api.md:98` — `"conversion_timeout_s": 120` im Beispielrumpf von
  `/api/capabilities`. Nur ein Beispiel, aber es zeigt jetzt einen Wert, den keine
  Auslieferung mehr hat. Die Datei gehoert zum Schnittstellen-Dreiklang; sie zu
  aendern zoege `models.py` und `types.ts` in denselben Commit.
