---
id: 81
title: BE-31 · Die Kodierungswarnung trifft auch echte Ersetzungszeichen
status: in-progress
priority: medium
created: 2026-09-01T16:24:41.480901999+02:00
updated: 2026-09-01T16:26:01.984785619+02:00
assignee: sophie
tags:
    - backend
    - bug
claimed_by: sophie-31
claimed_at: 2026-09-01T16:26:01.984785619+02:00
class: standard
---

## Befund (01.09.2026, aus der Abbruchbedingung von BE-29 nachgestellt)

`_encoding_warnings()` zählt U+FFFD im Ergebnis. Eine **strikt gültige** UTF-8-Datei,
die das Zeichen echt enthält — eine Dokumentation über Mojibake, oder das Ergebnis
einer früheren Wandlung —, löst damit eine Warnung aus, die nicht zutrifft.

Der Subagent hat den Fall nicht überlegt, sondern nachgestellt, wie es die
Abbruchbedingung verlangte. Er ist im Ausgelieferten.

## Entscheidung des PO: wird behoben, nicht hingenommen

Zwei Dinge dämpfen den Fall — er ist selten, und der Warntext sagt „vermutlich anders
kodiert" statt es zu behaupten. Trotzdem: Der Dienst sagt gelegentlich etwas Unwahres
über eine Datei, und bei einem Werkzeug, dessen einziger Zweck das ehrliche Bild vom
Kontext ist, wiegt das schwerer als anderswo. Eine Warnung, der man nicht trauen
kann, ist auf Dauer schlimmer als keine — sie lehrt das Wegsehen.

Ausschlaggebend ist, dass es billig zu unterscheiden ist. Es ist kein Erraten der
Kodierung.

## Eigene Dateien

- `backend/app/converters/registry.py` (Klasse `_Passthrough`)
- `backend/tests/test_converters.py`
- `docs/formate.md` (Abschnitt „Die Matrix")

`registry.py` ist die Engpassdatei; der Abschnitt „Die Matrix" gehört nach dem
Ticketschnitt zu derselben Hand. Solange dieses Ticket offen ist, fasst beides kein
zweites an.

## Vorgaben

Ein echtes U+FFFD steht in der Datei als die drei Bytes `EF BF BD`. Eines, das
`errors="replace"` erzeugt hat, steht dort nicht. Damit lassen sich beide exakt
trennen, ohne zu raten — naheliegend:

```python
raw = path.read_bytes()
echt = raw.count(b"\xef\xbf\xbd")
markdown = raw.decode("utf-8", errors="replace")
ersetzt = markdown.count("�") - echt
```

Ob das der beste Weg ist, entscheidet die Lane am Gegenstand — die Vorgabe ist, dass
nur **eingefügte** Ersetzungszeichen zählen. Gewarnt wird ab eins.

**Zweiter Teil, derselbe Merge:** `docs/formate.md`, Abschnitt „Die Matrix", sagt über
`.md` „gibt sie unverändert zurück". Bei fremder Kodierung stimmt das nicht — die
Bytes ändern sich, seit `errors="replace"` dort steht, und das galt schon vor BE-29.
Der Satz gehört berichtigt; er beschreibt dieselbe Sache wie die Warnung.

## Prüfung

- Eine strikt gültige UTF-8-Datei mit einem echten `�` liefert `warnings: []`.
- Eine ISO-8859-1-Datei mit sechs Umlauten liefert eine Warnung mit der Zahl 6.
- Der gemischte Fall: eine ISO-8859-1-Datei, die zusätzlich ein echtes `�` enthält,
  nennt nur die eingefügten.
- Gegenprobe: Ohne die Änderung schlägt der erste Test fehl.
- `docs/formate.md` sagt über `.md` nicht mehr „unverändert".
- `pytest -q -rs` grün, Sammelzahl in der Notiz.
