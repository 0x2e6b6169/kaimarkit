---
id: 56
title: BE-17 · Heisst ready wirklich ready?
status: done
priority: high
created: 2026-09-01T10:24:25.93867698+02:00
updated: 2026-09-01T17:28:34.458586678+02:00
started: 2026-09-01T12:40:23.978293179+02:00
completed: 2026-09-01T12:53:49.630901447+02:00
assignee: sophie
tags:
    - backend
    - bug
class: standard
---

## Befund (01.09.2026, aus IN-9 im laufenden Container)

Der Container galt **nach 9 Sekunden** als `healthy`, und `/api/capabilities` meldete
von Anfang an alle drei Engines auf `ready`. Der erste Docling-Aufruf danach brauchte
trotzdem 32 Sekunden.

Die Dokumentation beschreibt etwas anderes: `docs/betrieb/lokal.md` nennt das Warten
als dritten Schritt und sagt, `/api/capabilities` melde Docling so lange als
`warming`. Dieser Zustand war nie zu sehen.

## Die Frage

Ist Docling nach 9 Sekunden wirklich geladen, oder heisst der Zustand nur so? Zwei
Faelle mit verschiedenen Folgen:

- **Der Zustand stimmt**, und die 32 Sekunden gehen auf den ersten Aufruf selbst.
  Dann ist die Doku zu aendern, nicht der Code.
- **Der Zustand stimmt nicht** — `ready` wird gemeldet, bevor der Konverter steht.
  Dann verspricht `/api/capabilities` etwas, das es nicht halten kann, und ein
  Frontend, das sich darauf verlaesst, schickt zu frueh.

Was von beidem zutrifft, entscheidet die Messung, nicht die Vermutung.

## Eigene Dateien

- `backend/app/` — die Stelle, die `warming` und `ready` setzt
- `backend/tests/` — der zugehoerige Test
- `docs/betrieb/lokal.md` (Abschnitte "Drei Schritte" und "Was vorher da sein muss")

Nicht der Abschnitt "Pruefen, ob der Dienst antwortet" — der gehoert DOC-11 (#57).

## Pruefung

- Gemessen ist, wann der Konverter tatsaechlich bereit ist, und wann
  `/api/capabilities` es sagt. Beide Zahlen stehen in der Ticketnotiz.
- Gehen sie auseinander, meldet `/api/capabilities` `warming`, bis der Konverter
  steht — mit einem Test, der ohne die Korrektur fehlschlaegt.
- Stimmen sie ueberein, ist `docs/betrieb/lokal.md` berichtigt und sagt nicht mehr
  Warten voraus, wo keines noetig ist.

## Zurueckgestellt

Vom Nutzer zurueckgestellt, bis die Abnahmefassung steht (01.09.2026).

[[2026-09-01]] Tue 12:06
Die Messung fuer dieses Ticket entsteht in #59 (IN-11): Dort wird dasselbe Dokument zweimal hintereinander umgewandelt. Die Differenz zwischen erstem und zweitem Lauf **ist** die Ladezeit des Konverters — also die Zahl, um die es hier geht. Wer #56 aufnimmt, sieht zuerst in der Notiz von #59 nach, statt selbst zu messen.

[[2026-09-01]] Tue 12:40
Die Messung aus #59 (IN-11) liegt vor und **kippt die Prämisse dieses Tickets** (akar, 01.09.2026).

Das Laden dauert **unter zehn Sekunden**, nicht Minuten: 9,24 s und 8,30 s als Differenz zwischen erstem und zweitem Lauf, 8,50 s direkt an `_build_pipeline` gemessen. Die ursprüngliche Frage — ob `ready` nach neun Sekunden zu früh gemeldet wird — beantwortet sich damit weitgehend von selbst: Neun Sekunden sind ungefähr die Ladezeit.

Der eigentliche Befund ist ein anderer und macht das Ticket erst wertvoll:

**`start_warmup` baut nur eine von zwei Pipelines.** OCR an und OCR aus sind in Docling zwei verschiedene Pipelines mit verschiedenem Options-Hash. Wer die eine vorlädt und dann die andere anfordert, zahlt die Ladezeit ein zweites Mal — und `/api/capabilities` meldet währenddessen `ready`.

Zweiter Befund: `backend/app/converters/docling.py:4` behauptet im Modulkopf, der Aufruf dauere „minutenlang", weil dort die Modelle geladen werden. Gemessen sind es 8,5 Sekunden. Der Satz ist unwahr und gehört in dieses Ticket, weil es dieselbe Sache betrifft.

**Neuer Zuschnitt daraus**, ersetzt die Frage oben: Nicht mehr „heißt `ready` wirklich `ready`", sondern: Beide Pipelines vorladen oder `ready` erst melden, wenn die angeforderte steht — und den Modulkopf berichtigen.

Nicht mehr Teil dieses Tickets: Die Zeitgrenze ist in #59 erledigt, und der Thread-Weg ist gemessen und tot — der Rechner hat zwei physische Kerne, Torchs zwei Threads sind richtig.

Vom PO auf `high` gehoben: Ein `ready`, das nicht hält, ist eine falsche Auskunft an das Frontend.


[[2026-09-01]] Tue 13:05
**Entscheidung des PO (katche), eingetragen von der sophie-Sitzung, weil sophie-20 den
Claim haelt: Beide Pipelines vorladen. `ready` bleibt, wie es ist.**

Der Grund liegt nicht bei den rund 17 Sekunden, sondern beim anderen Weg: `ready` erst
zu melden, wenn die *angeforderte* Pipeline steht, verlangt, dass `/api/capabilities`
je Variante Auskunft gibt. Das ist eine Erweiterung der Schnittstelle und zieht
`contracts/api.md`, `models.py` und `types.ts` in denselben Commit — fuer eine Auskunft,
die der Aufrufer im Regelfall gar nicht auswertet. Zu teuer fuer den Gewinn.

Die doppelte Startzeit ist unkritisch: `KAIMARKIT_HEALTH_START_PERIOD` steht auf 180 s,
der Healthcheck hat Luft, und sie faellt einmal beim Start an statt bei jeder
Umwandlung.

**Zwei Zahlen gehoeren gemessen und hierher, weil die Entscheidung auf ihnen ruht:** die
tatsaechliche Zeit bis `healthy` und der Speicherzuwachs durch die zweite Pipeline.
Bisher gemessen waren 1,77 GB von 6 GB — es ist Platz, aber Platz ist keine Messung.

**Faellt eine der Zahlen deutlich schlechter aus als erwartet, wird uebergeben**, nicht
auf den anderen Weg gewechselt. Der ist eine Schnittstellenaenderung und gehoert dann
neu geschnitten.


[[2026-09-01]] Tue — umgesetzt (sophie-20), Branch task/56-beide-pipelines, Commit 5dfe6fe

**Weg: beide Pipelines vorladen, `ready` bleibt, wie es ist** — der Entscheidung des PO
folgend. `_warmup` baut jetzt beide OCR-Einstellungen nacheinander, die eingestellte
Voreinstellung zuerst: Sie wird am ehesten verlangt, und wer die andere waehlt, wartet
hoechstens an der Sperre in `_pipeline` statt auf einen zweiten Ladevorgang. Scheitert
die erste, endet der Warmlauf — fehlt die Bibliothek, ist auch die zweite nicht zu bauen,
und `state()` meldet weiterhin `unavailable`.

**Was bleibt und bewusst bleibt:** Zwischen der ersten und der zweiten Pipeline meldet
`/api/capabilities` `ready`, waehrend eine der beiden Einstellungen noch fehlt — rund
achteinhalb Sekunden. Das Fenster steht im Modulkopf von `docling.py` und in
`docs/betrieb/lokal.md`, statt verschwiegen zu werden. Wer dort die fehlende Einstellung
verlangt, wartet an der Sperre und bekommt ein richtiges Ergebnis, nur spaeter.

Modulkopf berichtigt: keine Minuten mehr, sondern die gemessenen achteinhalb Sekunden je
Pipeline. Dieselbe Unwahrheit stand im Docstring von `tests/test_lifespan.py` und ist dort
mitberichtigt. `docs/betrieb/lokal.md` (Abschnitt „Drei Schritte") sagt jetzt, was
geschieht: `healthy` heisst, dass der Dienst laeuft, nicht dass Docling geladen hat; der
Warmlauf baut zwei Pipelines zu je rund achteinhalb Sekunden; wer in dieser Zeit ein PDF
schickt, bekommt es ueber `engine=auto` von MarkItDown gewandelt.

**Tests.** Neu: `test_warmup_builds_both_ocr_pipelines` (nach dem Warmlauf stehen beide,
und keine Umwandlung baut danach noch etwas) und
`test_warmup_builds_the_configured_setting_first`. Rot vor gruen, gegen den unveraenderten
Code ausgefuehrt: `3 failed, 13 passed`, dreimal `assert [True] == [False, True]` — in
beiden neuen Tests und in `test_get_converter_starts_the_warmup`. Danach `116 passed,
4 deselected` (`pytest -q`), `4 skipped` bei `-m slow` (docling ist lokal nicht
installiert und darf es in der geteilten Umgebung nicht werden), `ruff check .` sauber.

**Zwei Zahlen bleiben offen — im Container zu pruefen:**

- **Zeit bis `healthy`.** Vom Warmlauf unberuehrt: Der Healthcheck ruft `/api/health`,
  und diese Antwort haengt nicht an den Modellen. Gemessen ist das hier nicht; die
  Aussage ist aus dem Quelltext gelesen (`docker/docker-compose.yml`, `app/api/meta.py`).
- **Speicherzuwachs durch die zweite Pipeline.** Nicht gemessen. Vorher standen 1,77 GB
  von 6 GB. Der Zuwachs sind die Modelle einer zweiten Pipeline samt EasyOCR; er faellt
  nacheinander an, es gibt also keine doppelte Spitze. Faellt er deutlich hoeher aus als
  erwartet, gehoert der Weg neu geschnitten.

Beides ist ohne docling und ohne Containerbau nicht zu belegen und gehoert der
Infrastruktur-Lane.

**Befund, nicht geaendert (war vorher schon falsch):** `backend/app/main.py:47` sagt im
Lifespan-Docstring, ohne das Vorladen wartete der erste Nutzer „minutenlang";
`docs/betrieb/konfiguration.md:144` legt nahe, der Healthcheck warte auf die Modelle.
Beide Stellen gehoeren anderen Tickets.

[[2026-09-01]] Tue 14:09
**Die zwei offenen Zahlen bleiben offen — Zwischenstand des PO (01.09.2026).**

Ich hatte zugesagt, Zeit bis `healthy` und Speicherzuwachs beim nächsten Container-Lauf zu holen. Am laufenden Dienst geht beides **nicht** sauber:

- **Zeit bis `healthy`:** `docker inspect` hält nur die letzten Healthcheck-Einträge; bei einem Container, der seit über einer Stunde läuft, ist der erste längst herausgerollt. Der Startzeitpunkt allein sagt nichts darüber, wann der erste Check gelang.
- **Speicher:** Gemessen sind jetzt 476 MiB im Ruhezustand. Die 1,77 GB von heute Vormittag entstanden **während einer Umwandlung**. Die beiden Zahlen nebeneinanderzustellen wäre derselbe Fehler wie bei den zwei Durchsatzwerten — verschiedene Bedingungen, kein Vergleich.

Beide Zahlen brauchen einen kontrollierten Neustart: Container hoch, Zeit bis `healthy` nehmen, Speicher im Ruhezustand ablesen — einmal mit und einmal ohne das Vorladen der zweiten Pipeline. Das ersetzt den laufenden Dienst und geht deshalb erst, wenn der Nutzer durch ist.

Bis dahin ruht die Entscheidung aus diesem Ticket auf einer Schätzung (2 × 8,5 s bei 180 s Startfenster) und nicht auf einer Messung. Das ist vertretbar, aber es ist nicht dasselbe, und es soll hier stehen statt vergessen zu werden.

## Messwerte vom Neustart aus IN-13 (#77), gemessen von akar-27 am 01.09.2026

Abbildstand: `kaimarkit:local`, gebaut aus dem Haupt-Checkout auf **6b4c3b4**
(`merge: IN-13 Docs-Stufe kopiert nur, was sie braucht`). Ein Abbild, ein
Container, zwei frische Starts unmittelbar hintereinander. `docker/.env`
unveraendert, also `KAIMARKIT_WORKERS=1` und `KAIMARKIT_MEM_LIMIT=6GB`.

**Gemessen, nicht gefolgert.** Die Entscheidung liegt bei sophies Lane.

### 1. Zeit bis `healthy`

| Marke | Zeit nach Containerstart |
|---|---|
| `/api/health` antwortet zum ersten Mal | **2,8 s** |
| erster Healthcheck laeuft an / besteht | +5,2 s / +5,8 s |
| `docker inspect` meldet `healthy` | **6,3 s** |

Beide Starts lagen auf die Zehntelsekunde gleich (2,83 s / 6,25 s und
2,78 s / 6,33 s). Gegen `KAIMARKIT_HEALTH_START_PERIOD=180 s` ist das der
Faktor 29 — nicht knapp.

Die 6,3 s sind durch das Healthcheck-Intervall von 30 s nach oben begrenzt
abgelesen; die genaue Zahl steht im Protokoll (`Start=+5,2 s`, `ExitCode=0` bei
`End=+5,8 s`).

### 2. Speicher im Ruhezustand

**294 MiB von 6 GiB, also 4,8 %** — abgelesen, nachdem die CPU unter 5 % gefallen
war, vor jeder Umwandlung.

Dabei ein Befund, der die Zahl selbst betrifft: Im ersten Lauf hatte ich sie bei
t+6 s genommen und 197 MiB erhalten — mitten im Vorladen, die CPU stand da noch
bei 96 %. Der Warmlauf ist erst bei **t+11 s** fertig; erst danach steht der
Speicher bei 294 MiB. Wer diese Messung wiederholt, muss auf die CPU warten,
sonst misst er einen halb gefuellten Prozess.

### 3. Speicher waehrend einer Umwandlung

`POST /api/convert` mit `backend/tests/fixtures/tabelle.pdf` und `engine=docling`,
am selben Container unmittelbar danach:

| | Lauf 1 | Lauf 2 |
|---|---|---|
| Hoechststand | 1012 MiB (16,5 %) | 972 MiB (15,8 %) |
| unmittelbar danach | 1007 MiB | 972 MiB |
| Dauer der Umwandlung | 28,2 s | 12,0 s |

**Rund 1 GiB von 6 GiB.** Auch das ist nicht knapp.

Zwei Beobachtungen dazu, ohne Folgerung:

- Der Speicher faellt nach der Umwandlung nicht zurueck. Er bleibt bei knapp
  1 GiB stehen. Fuer die Grenze von 6 GiB bei einem Worker bleibt trotzdem reichlich
  Luft; bei mehreren Workern waere es die Zahl, mit der man rechnet.
- Die **erste** Umwandlung dauerte mit 28,2 s mehr als doppelt so lange wie die
  zweite mit 12,0 s, obwohl beide nach abgeschlossenem Warmlauf liefen. Das
  Vorladen deckt also nicht alles ab, was beim ersten Durchlauf einmalig anfaellt.

### Ein Befund fuer BE-17 selbst

`/api/health` antwortet nach 2,8 s, der Container gilt nach 6,3 s als `healthy` —
das Vorladen ist zu diesem Zeitpunkt noch nicht durch, es endet erst bei t+11 s.
Die `start_period` von 180 s ist damit begruendet, dass Docling seine Modelle
beim Start laedt; die Gesundheitsauskunft wartet darauf aber nicht. Ein Container
gilt als gesund, bevor er seine erste Umwandlung schnell beantworten kann. Ob das
so gewollt ist, entscheidet diese Lane.

**Ausdruecklich nicht gemessen:** kein Vergleich mit und ohne Vorladen, kein
zweites Abbild — so war es aufgetragen.

[[2026-09-01]] Tue 17:28
**Die drei Messwerte sind da (aus #77, Abbildstand `6b4c3b4`), und meine Entscheidung ruht damit auf Messungen statt auf einer Schätzung:**

    6,3 s bis `healthy`      gegen 180 s `start_period`
    294 MiB im Ruhezustand   von 6 GiB Limit
    rund 1 GiB unter Last    am selben Container, unmittelbar danach

Nichts fällt knapp aus, in keiner Richtung. Das Vorladen beider Pipelines bleibt.

**Zum Nebenbefund, dass `healthy` nach 6,3 s kommt, das Vorladen aber erst bei t+11 s durch ist: kein Folgeticket.** Das Fenster ist rund fünf Sekunden lang, und wer es trifft, zahlt eine langsamere erste Umwandlung — keinen Fehlschlag. `healthy` auf das Vorladen warten zu lassen, verzögerte die Verfügbarkeit des Containers für nichts: Die API antwortet nach 2,8 s und ist dann auch benutzbar.

Der zweite Nebenbefund ist der eigentliche Rest dieser Frage und liegt als #84 (BE-32): Die **erste** Umwandlung dauerte 28,2 s gegen 12,0 s bei der zweiten, obwohl beide nach dem Vorladen liefen. Da ist etwas, das dieses Ticket nicht abdeckt.
