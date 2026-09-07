---
id: 138
title: DOC-27 · Nutzer-Bereich spricht den Leser an, statt sich selbst zu beschreiben
status: todo
priority: high
created: 2026-09-07T12:58:55.787085414+02:00
updated: 2026-09-07T12:58:55.787085414+02:00
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
