---
id: 56
title: BE-17 · Heisst ready wirklich ready?
status: done
priority: high
created: 2026-09-01T10:24:25.93867698+02:00
updated: 2026-09-01T12:54:30.532325268+02:00
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
