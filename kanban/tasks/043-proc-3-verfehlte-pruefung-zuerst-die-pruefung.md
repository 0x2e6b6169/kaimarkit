---
id: 43
title: 'PROC-3 · Verfehlte Pruefung: zuerst die Pruefung verdaechtigen'
status: done
priority: low
created: 2026-08-31T14:05:10.07801012+02:00
updated: 2026-08-31T16:38:59.143407547+02:00
started: 2026-08-31T16:36:47.388039309+02:00
completed: 2026-08-31T16:38:58.330755595+02:00
assignee: katche
tags:
    - process
class: standard
---

## Ziel

Dreimal an einem Tag war die **Pruefung** eines Tickets unter genau der Annahme
geschrieben, die sie haette pruefen sollen. Dreimal war die Annahme der Fehler,
nicht die Umsetzung.

- **DOC-5** — `mkdocs build --strict` sollte das fehlende `def_list` fangen. Es
  ist fuer diese Fehlerklasse blind.
- **DOC-6** — die Pruefung fragte nach der richtigen Schreibweise der
  OCR-Sprachen und setzte damit voraus, dass ueberhaupt eine wirkt.
  `KAIMARKIT_OCR_LANGS` wirkte gar nicht (BE-12, #37).
- **IN-6** — die Pruefung erwartete ein kleineres Abbild und setzte voraus, dass
  die EasyOCR-Gewichte darin liegen. Sie lagen nicht drin; das Abbild konnte
  offline kein OCR und warf 500 (merge 87ed9d9).

Alle drei sind nur aufgefallen, weil der Subagent die Abweichung **gemeldet**
hat, statt sie zu schliessen. Die naheliegende Reaktion auf eine verfehlte
Vorgabe ist, die eigene Arbeit zu verdaechtigen und nachzubessern, bis die Zahl
stimmt. Genau dann verschwindet der Befund.

Beobachtet und zusammengestellt von akar.

## Die Frage

Soll die Arbeitsweise ausdruecklich festhalten, wie ein Subagent mit einer
verfehlten Pruefung umgeht? Der Vorschlag in zwei Saetzen:

> **Weicht eine Pruefung ab, ist zuerst die Pruefung verdaechtig, nicht die
> Arbeit.** Der Subagent meldet die Abweichung, statt sie zu schliessen.

Der erste Satz ist die Lehre, der zweite die Bedingung, unter der sie ueberhaupt
jemanden erreicht. Ohne den zweiten bessert ein Agent still nach.

Zu entscheiden ist, wie streng das gilt:

1. **Als Regel in CLAUDE.md**, im Abschnitt "Der Ticketschnitt" neben den vier
   Rumpfabschnitten. Gilt dann fuer jedes Ticket.
2. **Als Auflage im Auftrag**, die die Eltern-Sitzung beim Verteilen mitgibt.
   Beweglicher, aber jede Sitzung muss daran denken.
3. **So lassen.** Dreimal hat es ohne Regel funktioniert, weil die Subagenten
   von sich aus gemeldet haben.

## Reichweite

Beruehrt CLAUDE.md ("Der Ticketschnitt") und den Skill `/work-lane`, der die
Definition of done beschreibt. Faellt die Entscheidung fuer Form 1 oder 2, gehoert
sie ausserdem in den Skill `/agent-orchestration` in dot-claude — er gibt den
Ticketrumpf und die Rolle der Pruefung an neue Projekte weiter. Sonst gilt die
Lehre hier und nirgends sonst.

Die Aenderung liegt beim Nutzer, nicht bei einer Lane — wie bei PROC-1 (#35) und
PROC-2 (#41).

## Pruefung

Der Nutzer hat sich fuer eine Form entschieden, und die Stelle, die den
Ticketrumpf beschreibt, sagt danach ausdruecklich, was bei einer verfehlten
Pruefung zu tun ist.

[[2026-08-31]] Mon 14:07
Kein vierter Datenpunkt, sondern eine andere Frage — deshalb getrennt gehalten. akar meldet zwei Gewohnheiten, die er heute ad hoc in seinen Subagenten-Auftraegen eingefuehrt hat: (1) am Gegenstand pruefen statt am Werkzeug — im erzeugten HTML nach `<dl>` greppen statt `--strict` zu glauben, auf den Textinhalt pruefen statt auf HTTP 200; (2) jede Aussage ueber fremden Code nennt Anker aus Datei, Zeile und Commit. Beides ist Handwerk am Ticketrumpf, keine Verhaltensregel — und beides ist unstrittig, dreimal benutzt und einmal ausschlaggebend gewesen (DOC-6). Es steht deshalb bereits im Skill `/agent-orchestration` (dot-claude 28f5af4), im Abschnitt zur Pruefung und in der CLAUDE.md-Vorlage. **Offen bleibt allein die Frage dieses Tickets:** ob "melden statt schliessen" als Regel gilt. Die steht in der Vorlage bewusst nicht, weil sie hier zur Entscheidung liegt.

[[2026-08-31]] Mon 14:44
Vierter Fall, und der erste, der nicht einem Subagenten unterlief, sondern uns beiden. Bei der Suche nach Plattenplatz las akar `df -h /` und meldete 854 GB frei — die Zahl stimmte, sie gehoerte nur zum falschen Dateisystem. Docker Desktop legt seine Datenplatte auf `C:` ab, und `C:` war zu 97 Prozent voll. Die Pruefung war unter der Annahme geschrieben, Docker liege im Wurzeldateisystem; sie hat sauber gemessen und nichts belegt. Verschaerfend: akar hatte bemerkt, dass `/var/lib/docker` gar nicht existiert, und daraus keinen Verdacht gezogen. Dazu ein zweites Werkzeug, das dasselbe bestaetigte: `docker system df` meldet 8,6 GB — den **Inhalt**, nicht den belegten Platz. Die VHDX war 82,5 GB gross, rund 74 GB toter Raum. **Das Neue an diesem Fall:** Zwei Sitzungen haben denselben falschen Befund unabhaengig bestaetigt und sich damit gegenseitig plausibel gemacht. Eine zweite Messung mit demselben blinden Fleck ist keine Bestaetigung. Gemeldet von akar, aufgeloest ueber IN-7 (#44).

[[2026-08-31]] Mon 14:45
Die pruefbare Fassung des vierten Falls, von akar: **Ein fehlender Pfad ist kein Nebenbefund, sondern die Auskunft, dass man am falschen Ort misst.** Er hatte gesehen, dass `/var/lib/docker` nicht existiert, und daraus keinen Verdacht gezogen, sondern die uebrigen Zahlen genommen. Das ist der Punkt, an dem die Regel dieses Tickets gegriffen haette — und der einzige der vier Faelle, in dem ein einzelner Blick genuegt haette.

[[2026-08-31]] Mon 16:38
Entscheidung des Nutzers: **Form 1** — die Regel steht in CLAUDE.md und gilt fuer jedes Ticket.

Umgesetzt an vier Stellen in zwei Repos:

1. **kaimarkit `CLAUDE.md`**, Abschnitt "Der Ticketschnitt", hinter den vier Rumpfabschnitten und vor dem `handoff`-Block. Der Satz, der den Block einleitet, ist mitgeaendert: Eine verfehlte Pruefung und ein fehlendes Stueck aus einer anderen Lane benutzen dasselbe Werkzeug.
2. **kaimarkit `.claude/skills/work-lane/SKILL.md`**, "Definition of done", als zweiter Punkt hinter dem Pruefungs-Punkt.
3. **dot-claude `skills/agent-orchestration/SKILL.md`** — die bisherige Fassung galt nur fuer Pruefungen, die eine Zahl vorhersagen. Jetzt allgemein.
4. **dot-claude `assets/claude-md-abschnitte.md` und `assets/work-lane.SKILL.md`**, damit neue Projekte die Regel mitbekommen.

Der dritte Satz ist eine Abgrenzung und stand so nicht im Vorschlag: Gemeint ist die Annahme hinter der Pruefung; ein Fehler im eigenen Code bleibt ein Fehler im eigenen Code und wird behoben. Ohne ihn liest ein Subagent die Regel als Freibrief, bei jedem roten Test zu uebergeben.

Der **vierte Fall** (`df -h /`) faellt nicht unter diese Regel: Dort lag der Fehler im Messen, nicht im Melden. Seine beiden Lehren stehen bereits als Gewohnheiten im Pruefungs-Abschnitt von `/agent-orchestration`.
