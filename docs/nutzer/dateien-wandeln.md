# Eine Datei wandeln

Diese Seite beschreibt den Weg von der Datei zum Markdown: hinzufügen, warten,
ansehen, herunterladen. Sie setzt nichts voraus außer einem Browser und der
Adresse, unter der der Dienst antwortet. Wer den Dienst selbst starten will,
findet den Weg unter [Schnellstart](../admin/schnellstart.md); wer ihn aus einem
Programm heraus rufen will, unter [API](../admin/api.md).

Ein Wort kommt immer wieder vor: **Engine**. So heißt das Programm, das die
Umwandlung ausführt. Der Dienst bringt drei davon mit, und sie liefern zu
derselben Datei unterschiedliche Ergebnisse. Wer selbst wählen will, findet den
Weg unter [Engine und Texterkennung wählen](engine-und-texterkennung.md); was die
drei unterscheidet, steht unter [Formate](../admin/formate.md).

Eine Adresse statt einer Datei geht auch — das steht unter
[Eine Webseite wandeln](webseiten-wandeln.md).

## Dateien hinzufügen

Auf der Seite liegt ein großes gestricheltes Feld: „Dateien hierher ziehen oder
auswählen". Beides geht. Wer Dateien aus dem Dateimanager darauf zieht, lässt sie
dort los; wer klickt, bekommt die Dateiauswahl. Mit der Tastatur führt der
Tabulator auf das Feld, die Leertaste öffnet die Auswahl. Mehrere Dateien auf
einmal sind erlaubt.

Unter der Beschriftung stehen die Endungen, die der Dienst gerade annimmt. Er
meldet sie selbst; hier steht keine feste Liste.

Der Dienst nimmt nur eine begrenzte Zahl von Einträgen auf einmal. Ist sie
erreicht, erscheint unter der Warteschlange ein Hinweis mit beiden Zahlen: wie
viele hineinpassen und wie viele draußen blieben. Diese und die übrigen Grenzen
stehen unter [Grenzen](../admin/grenzen.md#funf-werte-begrenzen-einen-aufruf).

## Die Warteschlange

Jede Datei und jede Adresse bekommt eine eigene Zeile, in der Reihenfolge des
Hinzufügens. Die Zeile erscheint sofort, auch wenn ihre Umwandlung noch nicht
begonnen hat: Es laufen höchstens zwei auf einmal, die übrigen warten.

Eine Zeile nennt ihren Zustand als Zeichen und als Wort, damit auch ohne
Farbunterschied dasselbe dasteht:

- `◦ wartet` — noch nicht an der Reihe.
- `◐ läuft` — daneben zählt die Zeile mit, wie lange sie schon läuft:
  `läuft · 0:47`.
- `✓ fertig` — daneben stehen Engine und Dauer.
- `✗ fehlgeschlagen` — die Meldung des Dienstes steht darunter in einem roten
  Kasten, siehe [Warnungen und Fehler verstehen](warnungen-und-fehler.md).
- `⊘ abgebrochen` — siehe [Nicht mehr warten](#nicht-mehr-warten).

Eine gescheiterte Datei hält die übrigen nicht auf. Ihre Meldung bleibt in ihrer
eigenen Zeile, und die nächste Datei rückt nach. Über der Liste steht, wie viele
von wie vielen fertig sind, und daneben die Zahl der Fehlschläge.

„Entfernen" nimmt eine Zeile aus der Liste. Läuft sie gerade, hört der Browser
zugleich auf, auf sie zu warten.

## Ansehen und herunterladen

An einer fertigen Zeile steht „Vorschau". Der Knopf klappt das Ergebnis auf und
heißt danach „Vorschau schließen".

Aufgeklappt stehen zwei Reiter zur Wahl: „Vorschau" zeigt das Markdown gesetzt,
mit Überschriften und Tabellen; „Rohtext" zeigt es Zeichen für Zeichen, so wie es
ein Sprachmodell bekommt. „Kopieren" legt den Rohtext in die Zwischenablage und
meldet, ob es geklappt hat.

Herunterladen geht einzeln oder im Ganzen:

- „Herunterladen" an der Zeile legt eine Datei ab. Sie heißt wie die Vorlage, nur
  mit der Endung `.md`: aus `bericht.pdf` wird `bericht.md`.
- „Alles herunterladen" über der Liste packt alle fertigen Ergebnisse in ein
  Archiv namens `kaimarkit.zip`. Der Knopf bleibt gesperrt, solange noch etwas
  läuft; daneben steht dann, dass das Archiv danach bereitsteht. Ist eine Datei
  fehlgeschlagen, liegt im Archiv zusätzlich eine Liste `_errors.txt` mit einer
  Zeile je Fehlschlag.

## Nicht mehr warten

An einer laufenden Zeile steht „Nicht mehr warten". Der Knopf hält, was sein Name
sagt, und nicht mehr: Er beendet das Warten des Browsers. Der Dienst wandelt die
Datei im Hintergrund zu Ende und gibt seinen Platz erst dann oder an der
[Zeitgrenze](../admin/grenzen.md#die-zeitgrenze-beendet-den-wartevorgang-nicht-die-engine)
wieder frei.

Danach steht die Zeile auf „abgebrochen", und die nächste wartende Datei rückt
nach. Als Fehlschlag zählt der Abbruch nicht — entschieden hat ihn der Nutzer,
gescheitert ist nichts.
