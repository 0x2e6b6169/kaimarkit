---
id: 138
title: DOC-27 · Nutzer-Bereich spricht den Leser an, statt sich selbst zu beschreiben
status: done
priority: high
created: 2026-09-07T12:58:55.787085414+02:00
updated: 2026-09-07T13:11:38.104083049+02:00
started: 2026-09-07T13:11:37.361556983+02:00
completed: 2026-09-07T13:11:37.361556983+02:00
assignee: akar
tags:
    - docs
class: standard
---

## Ziel

Direkte Nutzerkorrektur am Stil des Nutzer-Bereichs. Zwei Dinge stören, und sie hängen
zusammen: Die Seiten beschreiben sich selbst, statt den Leser anzusprechen, und sie
setzen beim Aufbau der Oberfläche an, statt beim Anliegen dessen, der sie öffnet.

Der Nutzer nennt als Beispiel den Einstieg von `dateien-wandeln.md`:

> Diese Seite beschreibt den Weg von der Datei zum Markdown: hinzufügen, warten,
> ansehen, herunterladen. Sie zeigt ihn zweimal — in der Oberfläche und als Aufruf
> der Schnittstelle. Die Oberfläche ruft dieselben Endpunkte auf, die auch ein
> Skript benutzt.

Drei Sätze, die von der Seite handeln statt von der Sache. Wer sie liest, weiß danach,
wie die Seite gebaut ist — und keinen Schritt mehr über sein eigenes Anliegen.

Dieselbe Anlage steht auf den anderen drei Seiten:

- `engine-und-texterkennung.md`: "Über dem gestrichelten Feld steht der Abschnitt
  ‚Optionen'." — beginnt beim Bildschirmaufbau, nicht beim Vorhaben.
- `warnungen-und-fehler.md`: "Die Oberfläche kennt drei Kästen …" — eine
  Bestandsaufnahme der Oberfläche, keine Antwort auf "ich habe da eine Warnung, was
  nun?".
- `dateien-wandeln.md`: "Wer selbst wählen will, findet den Weg unter …" — die
  unpersönliche "Wer …"-Wendung steht überall dort, wo eine Anrede hingehört.

## Eigene Dateien

- `docs/nutzer/dateien-wandeln.md`
- `docs/nutzer/webseiten-wandeln.md`
- `docs/nutzer/engine-und-texterkennung.md`
- `docs/nutzer/warnungen-und-fehler.md`
- `mkdocs.yml` (Abschnitt `nav`), nur falls sich Seitentitel ändern

Nicht hier: `docs/admin/` und `docs/index.md`. Der Admin-Bereich behält seinen
unpersönlichen Ton; dass die beiden Bereiche danach verschieden klingen, ist gewollt
und kein Fehler.

## Vorgaben

**Anrede: `Du`, und zwar großgeschrieben.** `Du`, `Dir`, `Dein`, `Dich` — auch
mitten im Satz. Das ist die ausdrückliche Wahl des Nutzers, keine Nachlässigkeit; wer
das später liest, "berichtigt" es nicht. Durchgehend auf allen vier Seiten, ohne
Rückfall in "man" oder "der Nutzer".

**Kein Satz, der die Seite selbst zum Gegenstand hat.** "Diese Seite beschreibt …",
"Sie zeigt ihn zweimal …", "Der folgende Abschnitt nennt …" — alle weg. Die erste
Zeile ist die wertvollste Stelle des Textes; dort steht die Sache, nicht das
Inhaltsverzeichnis.

**Jeder Abschnitt folgt derselben Ordnung: erst das Anliegen, dann der Weg.** Was
willst Du erreichen — und dann, wie Du dorthin kommst. Nicht umgekehrt, und nicht
stattdessen eine Beschreibung dessen, was auf dem Bildschirm zu sehen ist. Der
Bildschirmaufbau kommt vor, wo er dem Weg dient, nicht als Bestandsaufnahme.

**Überschriften nennen ein Vorhaben, keine Bauteile.** "Die Engine wählen" taugt
schon; "Die Warteschlange" beschreibt ein Bauteil und gehört umformuliert, wenn sich
ein Vorhaben dahinter benennen lässt.

**Was bleibt:** alle Tatsachen, gemessenen Beispiele, Warnungswortlaute,
Zustandsbezeichnungen und Beschriftungen aus DOC-26 (#136). Dieses Ticket ändert die
Anlage und die Anrede, nicht den Inhalt. Und es gilt weiter "vollständiger, nicht
länger": Ein Satz, der beim Streichtest nichts hinterlässt, kommt nicht dazu.

`~/.claude/rules/SPRACHE.md` gilt unverändert.

## Prüfung

- Rot vor grün, zweifach belegbar: Die Suche nach den Selbstbeschreibungen ("Diese
  Seite", "Sie zeigt", "Der Abschnitt beschreibt" und Verwandte) findet vorher
  Treffer und nachher null. Die Suche nach der großgeschriebenen Anrede findet vorher
  null und nachher auf jeder der vier Seiten Treffer. Beides über den geflachten Text,
  nicht zeilenweise.
- Keine "Wer … will"-Wendung mehr an einer Stelle, an der eine Anrede möglich ist;
  wo eine stehen bleibt, steht in der Notiz, warum.
- Die 29 Wortlaute, Zustände und Beschriftungen aus DOC-26 sind vorher und nachher
  gezählt und vollständig wiedergefunden.
- Ändern sich Überschriften, ändern sich die Anker: jeden Verweis darauf prüfen. Das
  Skript aus DOC-24 (#134) kann Ziele und Anker bereits.
- `mkdocs build --strict` läuft durch. Keine Änderung unterhalb `docs/admin/`.

[[2026-09-07]] Mon 13:11
## Ergebnis (akar-46)

Zweig `task/138-doc-27`, Merge `6d3d4d3` (--no-ff). Nur die vier Seiten unter
`docs/nutzer/`; `mkdocs.yml` unverändert, weil keine H1 und damit kein
nav-Titel sich geändert hat. Nichts unterhalb `docs/admin/` und nichts an
`docs/index.md`.

**Rot vor grün, beide Richtungen.** Alle Zahlen über den geflachten Text
(`tr '\\n' ' '`), je Seite.

Selbstbeschreibungen (Muster: `Diese Seite|Sie zeigt ihn|Der folgende
Abschnitt|Der Abschnitt beschreibt|Die Beispiele schreiben|Zwei Beispiele, wie
sie|Der Ausschnitt zeigt|hier steht keine|beschreibt den Weg` u. a.) —
vorher 5 / 1 / 1 / 0, Summe **7**; nachher **0** auf allen vier Seiten. Die
sieben im Einzelnen: dateien-wandeln `Diese Seite`, `beschreibt den Weg`,
`Sie zeigt ihn`, `hier steht keine`, `Die Beispiele schreiben`;
engine-und-texterkennung `Der Ausschnitt zeigt`; warnungen-und-fehler
`Zwei Beispiele, wie sie`.

Anrede (`\\b(Du|Dir|Dich|Dein…)\\b`, groß) — vorher **0 / 0 / 0 / 0**;
nachher **25 / 19 / 15 / 4** (dateien-wandeln, engine-und-texterkennung,
warnungen-und-fehler, webseiten-wandeln). Kein `man`, kein `der Nutzer` mehr;
`entschieden hat ihn der Nutzer` ist `entschieden hast Du ihn` geworden.

**Die 29 Wortlaute.** Liste als Datei geführt und zeichengenau (`grep -F`)
gegen den geflachten Text aller vier Seiten geprüft: vorher 29/29, nachher
29/29, keiner fehlt. Zusammensetzung: 6 Zustandszeilen der Warteschlange
(`◦ wartet`, `◐ läuft`, `läuft · 0:47`, `✓ fertig`, `✗ fehlgeschlagen`,
`⊘ abgebrochen`), 20 Beschriftungen in Anführungszeichen und 3 Warnungstexte.
Zeilenweise hätte dieselbe Suche nur 17 der 20 Beschriftungen gefunden — drei
brechen um (`Dateien hierher ziehen oder auswählen`, `Erneut versuchen`,
`Webseiten, eine Adresse je Zeile`). Kein Aufruf und kein Antwortausschnitt ist
angefasst worden.

**Überschriften.** Drei umbenannt: `Die Warteschlange` → `Den Fortschritt
verfolgen` (Bauteil → Vorhaben), `Ein gelber Kasten: etwas fehlt im Ergebnis`
→ `Etwas fehlt im Ergebnis`, `Ein roter Kasten: es kam kein Ergebnis heraus`
→ `Es kam kein Ergebnis heraus` (beide setzten beim Bauteil an, jetzt beim
Anliegen). `Nicht mehr warten` bleibt absichtlich stehen: Es ist zugleich der
Knopfname und das Ziel des Ankers `#nicht-mehr-warten`.

**Anker-Lauf über den ganzen Baum.** Eigenes Skript (Slug wie python-markdown,
Codeblöcke ausgenommen) über `docs/**/*.md` plus `README.md`: **61 interne
Ziele, 0 kaputt** — Dateiziele und Anker. Gegenprobe, dass es greift: ein
verbogener Anker wird gemeldet (`TOTER ANKER … #gibt-es-nicht`). Auf keine der
drei alten Überschriften zeigte ein Verweis; `grep` über das ganze Repo nach
den alten und neuen Slugs findet außerhalb der Dateien selbst nichts. Es war
also kein Verweis aus `docs/index.md` oder `docs/admin/` betroffen und nichts
außerhalb der eigenen Dateien zu ändern.

**`mkdocs build --strict`** RC 0. Diese Prüfung war schon vorher grün und
belegt für dieses Ticket wenig: Sie prüft keine Anker (in DOC-24 festgestellt),
weshalb der Anker-Lauf die eigentliche Prüfung ist. Der rote Material-Hinweis
auf MkDocs 2.0 ist ein Herstellerhinweis.

**Stehengebliebene unpersönliche Wendungen: drei, alle mit Grund.** `Wer ihn
braucht, …` steht dreimal in `warnungen-und-fehler.md` — zweimal im Zitat des
gelben Kastens, einmal im Feld `warnings` der JSON-Antwort. Das ist der
Wortlaut, den das Backend ausgibt; er ist in DOC-26 gemessen und nicht
abgeschrieben worden. Wer ihn hier änderte, ließe die Doku etwas anderes sagen
als der Dienst. Ändern müsste ihn ein Backend-Ticket, nicht dieses. Alle
übrigen 12 `Wer …`-Wendungen aus dem Fließtext sind weg.

**Streichtest.** Vier Stellen sind wieder herausgeflogen, keine ganzen Absätze:
der Meta-Halbsatz `hier steht keine feste Liste`; ein von mir zuerst
geschriebenes `Bevor Du das Markdown weitergibst, sieh es Dir an` (nannte
keine Tatsache); die Wiederholung `— eine je Zeile —` neben der Beschriftung
`Webseiten, eine Adresse je Zeile`; und ein Dutzend reiner Höflichkeits-Dative
(`zeigt Dir`, `nennt Dir`, `hält Dir die übrigen nicht auf`), die nach der
Füllwortprobe aus SPRACHE.md nichts hinterließen. Die Anrede steht dort, wo Du
handelst oder etwas Dir gehört.

**Umfang.** 856→860, 604→634, 599→615, 347→354 Wörter (+2,4 % zusammen). Der
Zuwachs kommt aus der Anrede selbst — `Legst Du mehr Einträge ab` braucht mehr
Wörter als `Ist sie erreicht` —, nicht aus neuen Sätzen.

**Nichts außerhalb der eigenen Dateien gefunden, das falsch wäre.** Der Befund
aus DOC-26 zu `api/meta.py:52` (`ocr_available` aus `settings.ocr_enabled`)
besteht unverändert und betrifft weiter den Satz `Rührst Du ihn nicht an, gilt
die Voreinstellung des Dienstes`.
