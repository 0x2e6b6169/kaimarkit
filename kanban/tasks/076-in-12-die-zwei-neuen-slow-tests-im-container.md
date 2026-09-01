---
id: 76
title: IN-12 · Die zwei neuen slow-Tests im Container fahren
status: backlog
priority: medium
created: 2026-09-01T13:16:13.857772486+02:00
updated: 2026-09-01T13:16:13.857772486+02:00
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
