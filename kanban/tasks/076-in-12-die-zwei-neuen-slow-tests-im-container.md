---
id: 76
title: IN-12 · Die zwei neuen slow-Tests im Container fahren
status: todo
priority: medium
created: 2026-09-01T13:16:13.857772486+02:00
updated: 2026-09-01T14:00:16.316801786+02:00
started: 2026-09-01T14:00:15.714875061+02:00
assignee: akar
tags:
    - infra
    - tests
class: standard
---

## Ziel

Die offene Kette aus BE-18 (#58) schließen: Fixture → docling → Warnung.

## Ausgangslage

#58 hat `backend/tests/fixtures/breit.pdf` gebaut — **byte-identisch** mit dem
Wegwerf-PDF, an dem akar-21 den Platzhalter beobachtet hat (md5
9d46a776c4337f48efe87038d01bb5a8). Dazu zwei Tests hinter `-m slow`:

- `test_a_wide_table_becomes_a_placeholder_with_a_warning`
- `test_a_plain_table_produces_no_warning`

Beide haben lokal nur übersprungen — docling steht nicht in der geteilten Umgebung.
Die Kette ist damit **wiederhergestellt, nicht belegt**: Sie ruht auf einer
Beobachtung an derselben Datei, nicht auf einem Lauf gegen den heutigen Stand.

Das ist genau die Lücke, wegen der #58 überhaupt entstanden ist — ein Fixture, von
dem niemand weiß, ob es den Fall auslöst, sichert nichts.

## Eigene Dateien

Keine. Dieses Ticket ändert nichts; es misst und schreibt das Ergebnis in die Notiz
von #58 und in seine eigene.

Ändert sich beim Lauf etwas am Repo, ist das ein Befund und gehört gemeldet.

## Vorgaben

Im gebauten Abbild:

    pytest -q -m slow -rs -k "placeholder or plain_table"

Beide Tests müssen laufen, nicht überspringen — steht dort „docling ist nicht
installiert", ist der Lauf am falschen Ort.

Das Ergebnis gehört wörtlich in die Notiz von #58, mit dem Commit, aus dem das Abbild
gebaut ist. Fällt der breite Fall anders aus als erwartet, ist die Modellfassung der
Unterschied und nicht das Fixture — dann ist es ein Befund für sophies Lane, keiner,
der hier behoben wird.

## Prüfung

- Beide Tests laufen im Container und überspringen nicht.
- Ihr Ausgang steht in den Notizen von #58 und diesem Ticket, mit dem Abbildstand.
- Am Repo hat sich nichts geändert: `git status` ist sauber.

## Warum Backlog

Es braucht ein gebautes Abbild. #55 (IN-10) baut ohnehin gerade mehrfach — wenn dabei
ein Abbild auf aktuellem Stand entsteht, kostet dieses Ticket Minuten. Vorher wäre es
ein eigener 29-Minuten-Bau für zwei Tests.

[[2026-09-01]] Tue 13:25
**Zweite Beobachtung für denselben Lauf** (aus #48, gemeldet von sophie): `ConversionError.__init__` schreibt seit BE-15 bei jeder Erzeugung eine `log.warning`-Zeile mit dem ungekürzten Wortlaut. Die Begründung ist sachlich richtig — der Stapel fängt seine Fehler selbst ab und erreicht den Ausnahmebehandler nie, nur im Konstruktor ist der volle Wortlaut sicher zu haben.

Protokollieren als Nebenwirkung des Erzeugens ist trotzdem ungewöhnlich: **Jede** erzeugte `ConversionError` schreibt, auch eine, die gleich darauf abgefangen und ordentlich behandelt wird. Ob das im Betrieb Rauschen erzeugt, sagt erst ein Lauf mit vielen Fehlern.

Beim Container-Lauf deshalb mit ansehen: einen Stapel mit mehreren fehlschlagenden Dateien schicken und zählen, wie viele Zeilen dabei entstehen. Das Ergebnis gehört als Notiz an #48. Ist es Rauschen, wird es ein eigenes Ticket — hier wird nichts geändert.

[[2026-09-01]] Tue 14:00
Nach `todo` gezogen (01.09.2026). Voraussetzung erfüllt: Das Abbild ist aus `bbf7180` gebaut und aktuell, der Container läuft.

**Auflage: Der laufende Dienst des Nutzers bleibt stehen.** Er testet gerade auf `127.0.0.1:8080`. Dieses Ticket fährt Tests **im** Abbild und baut nichts — es darf den Container weder ersetzen noch abräumen. Seit #49 gibt es dafür `make test-slow-image`: Es startet einen eigenen Container aus dem Abbild, hängt `backend/` lesend hinein und wirft ihn danach weg. Das ist der Weg.

#77 (IN-13) bleibt derweil im Backlog — es baut und würde den Dienst ersetzen.
