---
id: 30
title: INT-2 · Ende-zu-Ende-Pruefung im Container
status: todo
priority: medium
created: 2026-08-31T10:21:44.348462086+02:00
updated: 2026-08-31T15:02:49.630711073+02:00
assignee: akar
tags:
    - infra
depends_on:
    - 29
    - 26
    - 27
    - 34
    - 38
    - 44
class: standard
---

## Ziel

Belegen, dass das gebaute Image tut, was der Plan verspricht.

## Eigene Dateien

Keine - dieses Ticket prueft und meldet, es baut nicht.

## Vorgaben

Der Abschnitt "Pruefung am Ende" des Plans, vollstaendig durchlaufen:

- pytest mit und ohne `-m slow`
- die curl-Beispiele fuer Einzeldatei, Stapel-ZIP und die Fehlerpfade 413/415/400
- `make up`, dann `/api/health`, `/docs/`, `/docs/versions.json`, `/api/docs`
- `docker compose ... config` ueber alle drei Dateien: kein `${...}`, kein leerer
  Wert
- ein Build mit absolut gesetztem `KAIMARKIT_BUILD_CONTEXT`

Von Hand: ein gescanntes PDF mit und ohne OCR, ein PDF mit breiter Tabelle ueber
MarkItDown und Docling im Vergleich, ein ePub ueber Pandoc, ein Durchlauf im
Browser mit gemischten Dateien.

Nach einem zweiten `make docs-release`: zwischen den Versionen umschalten und
pruefen, dass die Links auf `/docs/<version>/` zeigen und nicht auf die Wurzel.

## Pruefung

Jeder Punkt oben abgehakt. Was nicht gelingt, wird als eigenes Ticket angelegt,
nicht stillschweigend uebergangen.


## Nachtrag aus DOC-2 (#21) und IN-4 (#25)

- `docs/schnellstart.md` enthaelt einen `!!! info`-Kasten, der sagt, dass die
  Oberfläche noch das Geruest ist. Sobald INT-1 (#29) `App.vue` verdrahtet hat,
  gehoert der Kasten weg.
- Die Anmeldung im Browser gegen ein echtes Authelia ist nie gelaufen. IN-4 hatte
  weder Image noch Netz dafuer und hat den Nachweis hierher uebergeben.

[[2026-08-31]] Mon 13:38
PO: depends_on um #34 und #38 ergaenzt. INT-2 prueft das Abbild, das IN-6 gerade veraendert, und die OCR-Sprachen, die DOC-6 gerade korrigiert. Die Reihenfolge steht damit im Board statt in einer Absprache. Entschieden auf akars Meldung hin.

[[2026-08-31]] Mon 14:43
Abgebrochen am 31.08.2026 gegen 14:45 auf Wunsch des Nutzers, nicht wegen eines Fehlers. akar-18 stand beim zweiten vollstaendigen Imagebau (Pruefpunkt "zweites make docs-release, zwischen den Versionen umschalten"), Worktree `.worktrees/task-30` auf Branch `task/30-e2e`, Ankercommit 87ed9d9. Der Build lief nachweislich — der Build-Cache wuchs in 25 Sekunden von 5,3 auf 8,4 GB —, er hing nicht. Grund des Abbruchs ist IN-7 (#44): Dockers Datenplatte liegt auf einem zu 97 Prozent vollen C:, und die Reorganisation haelt Docker an. Deshalb haengt INT-2 jetzt auch per depends_on an #44. **Beim Wiederaufsetzen laeuft INT-2 vollstaendig neu**, nicht ab der Abbruchstelle: Ein Ende-zu-Ende-Bericht ueber einen halb geprueften Zustand belegt nichts. Vorher `git worktree list` pruefen — steht `.worktrees/task-30` noch, laesst er sich weiterverwenden, sonst neu anlegen. Bis zum Abbruch waren gelaufen: pytest mit und ohne -m slow, die curl-Fehlerpfade, `make up`, drei `compose config`-Laeufe und ein Durchgang der Traefik/Authelia-Schicht (Container `kaimarkit` healthy, ohne veroeffentlichten Port — die beabsichtigte Wirkung von IN-3). Keiner dieser Punkte wurde als bestanden gemeldet; alle sind erneut zu belegen.


## Was der abgebrochene Lauf gemeldet hat (kein Nachweis)

akar-18 wurde auf Wunsch des Nutzers gestoppt, nicht wegen eines Fehlers. Seine
letzte Meldung, woertlich sinngemaess: Abbild gebaut, Stack lief durch (`make up`,
alle curl-Pfade, OCR mit und ohne, Browser-Durchlauf, **Authelia-Anmeldung im
Browser erfolgreich**); offen war allein der letzte Punkt, die Pruefung der zwei
`make docs-release`-Versionen im Container.

**Das ist ein Bericht, kein Beleg.** Die Einzelheiten stehen nirgends — keine
Ausgaben, keine Zeilen, kein Anker. Der naechste Lauf faengt vollstaendig neu an
und belegt alles selbst, auch die Authelia-Anmeldung. Der Vermerk steht hier nur,
damit bekannt ist, wie weit es getragen hatte und wo es zuletzt stand: Der Rest
der Kette hatte offenbar funktioniert, der Abbruch kam am letzten Pruefpunkt.

Ankercommit des Laufs: 87ed9d9. Worktree `.worktrees/task-30` bleibt stehen.

[[2026-08-31]] Mon 15:02
Verweis nachgezogen: Der "Abschnitt 'Pruefung am Ende' des Plans" aus den Vorgaben liegt jetzt im Repo, in `ENTWURF.md` (merge c2900a7). Vorher zeigte er auf `~/.claude/plans/…`, also auf eine Datei ausserhalb des Repos und ausserhalb jeder Sicherung. Der Abschnitt selbst ist unveraendert.
