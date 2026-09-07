# Eine Datei wandeln

Du legst Deine Datei ab, wartest kurz, siehst Dir das Markdown an und lädst es
herunter. Denselben Weg gehst Du als Aufruf der Schnittstelle — die Oberfläche
ruft dieselben Endpunkte auf, die auch ein Skript benutzt.

Ein Wort begegnet Dir dabei immer wieder: **Engine**. So heißt das Programm, das
die Umwandlung ausführt. Der Dienst bringt drei davon mit, und sie liefern zu
derselben Datei unterschiedliche Ergebnisse. Wählen kannst Du selbst; wie das
geht, steht unter [Engine und Texterkennung wählen](engine-und-texterkennung.md),
und was die drei unterscheidet, unter [Formate](../admin/formate.md).

Hast Du statt einer Datei eine Adresse, führt Dein Weg über
[Eine Webseite wandeln](webseiten-wandeln.md).

## Dateien hinzufügen

Zieh Deine Dateien aus dem Dateimanager auf das große gestrichelte Feld „Dateien
hierher ziehen oder auswählen" und lass sie dort los. Ein Klick darauf öffnet
stattdessen die Dateiauswahl. Mit der Tastatur führt Dich der Tabulator auf das
Feld, die Leertaste öffnet die Auswahl. Mehrere Dateien auf einmal sind erlaubt.

Welche Endungen der Dienst gerade annimmt, steht unter der Beschriftung — er
meldet sie selbst.

Legst Du mehr Einträge auf einmal ab, als der Dienst aufnimmt, erscheint unter der
Warteschlange ein Hinweis mit beiden Zahlen: wie viele hineinpassen und wie viele
draußen blieben. Diese und die übrigen Grenzen stehen unter
[Grenzen](../admin/grenzen.md#funf-werte-begrenzen-einen-aufruf).

## Den Fortschritt verfolgen

Jede Datei und jede Adresse bekommt eine eigene Zeile, in der Reihenfolge, in der
Du sie hinzugefügt hast. Die Zeile erscheint sofort, auch wenn ihre Umwandlung
noch nicht begonnen hat: Es laufen höchstens zwei auf einmal, die übrigen warten.

Wie weit eine Zeile ist, sagt sie als Zeichen und als Wort, damit auch ohne
Farbunterschied dasselbe dasteht:

- `◦ wartet` — noch nicht an der Reihe.
- `◐ läuft` — daneben zählt die Zeile mit, wie lange sie schon läuft:
  `läuft · 0:47`.
- `✓ fertig` — daneben stehen Engine und Dauer.
- `✗ fehlgeschlagen` — die Meldung des Dienstes steht darunter in einem roten
  Kasten, siehe [Warnungen und Fehler verstehen](warnungen-und-fehler.md).
- `⊘ abgebrochen` — siehe [Nicht mehr warten](#nicht-mehr-warten).

Eine gescheiterte Datei hält die übrigen nicht auf. Ihre Meldung bleibt in ihrer
eigenen Zeile, und die nächste Datei rückt nach. Über der Liste steht, wie
viele von wie vielen fertig sind, und daneben die Zahl der Fehlschläge.

Mit „Entfernen" nimmst Du eine Zeile aus der Liste. Läuft sie gerade, hört der
Browser zugleich auf, auf sie zu warten.

## Ansehen und herunterladen

„Vorschau" an einer fertigen Zeile klappt das Ergebnis auf; der Knopf heißt
danach „Vorschau schließen".

Aufgeklappt hast Du zwei Reiter zur Wahl: „Vorschau" zeigt das Markdown gesetzt,
mit Überschriften und Tabellen; „Rohtext" zeigt es Zeichen für Zeichen, so wie es
ein Sprachmodell bekommt. „Kopieren" legt den Rohtext in Deine Zwischenablage und
meldet, ob es geklappt hat.

Herunterladen kannst Du einzeln oder im Ganzen:

- „Herunterladen" an der Zeile legt eine Datei ab. Sie heißt wie die Vorlage, nur
  mit der Endung `.md`: aus `bericht.pdf` wird `bericht.md`.
- „Alles herunterladen" über der Liste packt alle fertigen Ergebnisse in ein
  Archiv namens `kaimarkit.zip`. Der Knopf bleibt gesperrt, solange noch etwas
  läuft; daneben steht dann, dass das Archiv danach bereitsteht. Ist eine Datei
  fehlgeschlagen, liegt im Archiv zusätzlich eine Liste `_errors.txt` mit einer
  Zeile je Fehlschlag.

## Nicht mehr warten

Dauert Dir eine laufende Zeile zu lange, beendest Du mit „Nicht mehr warten" das
Warten des Browsers — und nicht mehr als das. Der Dienst wandelt die Datei im
Hintergrund zu Ende und gibt seinen Platz erst dann oder an der
[Zeitgrenze](../admin/grenzen.md#die-zeitgrenze-beendet-den-wartevorgang-nicht-die-engine)
wieder frei.

Danach steht die Zeile auf „abgebrochen", und die nächste wartende Datei rückt
nach. Als Fehlschlag zählt der Abbruch nicht — entschieden hast Du ihn,
gescheitert ist nichts.

## Dieselbe Datei über die Schnittstelle

Setz `$DIENST` auf die Adresse, unter der die Oberfläche antwortet — dieselbe, die
bei Dir im Browser in der Adresszeile steht:

```bash
DIENST=http://localhost:8080
```

So schickst Du eine Datei hin und bekommst das Markdown als Datei zurück, das
Gegenstück zu „Herunterladen":

```bash
curl -sf -F file=@bericht.docx $DIENST/api/convert -o bericht.md
```

Der Rumpf der Antwort ist das Markdown, sonst nichts. Wie die Datei heißt, steht in
`content-disposition`, die Engine in `x-engine`:

```text
content-disposition: attachment; filename="bericht.md"; filename*=UTF-8''bericht.md
x-engine: markitdown
content-type: text/markdown; charset=utf-8
```

Gab es Warnungen, kommt `x-warnings` dazu. Kopfzeilen vertragen kein UTF-8, deshalb
steht der Text dort auf ASCII heruntergebrochen: Aus `lädt` wird `l?dt`. Brauchst Du
den Wortlaut einer Warnung, hol ihn aus der JSON-Antwort.

Willst Du statt der Datei alles, was auch die Zeile in der Warteschlange zeigt —
Engine, Dauer, Warnungen —, verlang JSON:

```bash
curl -sf -F file=@bericht.docx -H 'Accept: application/json' $DIENST/api/convert
```

```json
{
  "filename": "bericht.docx",
  "status": "ok",
  "markdown": "# Kaimarkit Fixture\n\nEin Absatz aus dem Fixturebestand.",
  "engine": "markitdown",
  "warnings": [],
  "duration_ms": 71,
  "error": null
}
```

Mehrere Dateien gibst Du `/api/convert/batch` in einem Aufruf mit. Es antwortet mit
einem Archiv, in dem je eine `.md` liegt, und legt `_errors.txt` dazu, sobald eine
Datei scheiterte — dasselbe, was „Alles herunterladen" packt:

```bash
curl -sf -F file=@bericht.docx -F file=@liste.csv \
     $DIENST/api/convert/batch -o ergebnis.zip
```

Auch hier nimmt eine gescheiterte Datei die übrigen nicht mit. Mit
`-H 'Accept: application/json'` bekommst Du statt des Archivs eine Liste der
Einträge, dazu die Zählung `total`, `succeeded` und `failed`.

Alle Endpunkte, Felder und Fehlercodes stehen unter [API](../admin/api.md).
