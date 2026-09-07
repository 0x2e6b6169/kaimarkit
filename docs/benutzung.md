# Die Oberfläche

Diese Seite beschreibt, was auf dem Bildschirm passiert. Sie setzt nichts voraus
außer einem Browser und der Adresse, unter der der Dienst antwortet. Wer den
Dienst selbst starten will, findet den Weg unter [Schnellstart](schnellstart.md);
wer ihn aus einem Programm heraus rufen will, unter [API](api.md).

Ein Wort kommt immer wieder vor: **Engine**. So heißt das Programm, das die
Umwandlung ausführt. Der Dienst bringt drei davon mit, und sie
liefern zu derselben Datei unterschiedliche Ergebnisse. Welche das sind und was
sie unterscheidet, steht unter [Formate](formate.md).

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
stehen unter [Grenzen](grenzen.md#funf-werte-begrenzen-einen-aufruf).

## Webseiten wandeln

Eine Webseite braucht keinen Umweg über den eigenen Rechner. Unter „Webseiten,
eine Adresse je Zeile" steht ein mehrzeiliges Feld; „Webseiten wandeln" schickt
jede Zeile ab, und der Dienst holt die Seiten selbst.

Eine Zeile, die weder mit `http://` noch mit `https://` beginnt, schickt die
Oberfläche gar nicht erst ab. Sie bleibt im Feld stehen und wird darunter
genannt. Alles Weitere prüft der Dienst — ob der Name auflöst, ob er ins offene
Netz zeigt, ob dort ein Dokument liegt —, und seine Meldung steht dann in der
Zeile der Warteschlange.

Jede geholte Seite reiht sich in dieselbe Warteschlange ein wie eine hochgeladene
Datei. Ihren Namen bekommt sie aus dem Titel der Seite: Aus `https://example.com/`
wird `example-domain.html`. Fanden nicht alle Adressen Platz, stehen die übrigen
wieder im Feld — von dort lassen sie sich gleich noch einmal abschicken.

Welche Seiten der Dienst nicht brauchbar wandelt, steht unter
[Grenzen](grenzen.md#webseiten-nur-offentlich-kein-javascript).

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
  Kasten.
- `⊘ abgebrochen` — siehe [Nicht mehr warten](#nicht-mehr-warten).

Eine gescheiterte Datei hält die übrigen nicht auf. Ihre Meldung bleibt in ihrer
eigenen Zeile, und die nächste Datei rückt nach. Über der Liste steht, wie viele
von wie vielen fertig sind, und daneben die Zahl der Fehlschläge.

„Entfernen" nimmt eine Zeile aus der Liste. Läuft sie gerade, hört der Browser
zugleich auf, auf sie zu warten.

## Die Optionen

Über dem gestrichelten Feld steht der Abschnitt „Optionen". Was dort eingestellt ist, gilt
für den nächsten Lauf. Bereits umgewandelte Dateien bleiben, wie sie sind.

### Die Engine wählen

Die Engines stehen als Gruppe von Schaltern untereinander, „automatisch" zuerst.
Neben jedem Namen steht ein Halbsatz, und das runde „i" dahinter öffnet die
längere Erklärung — mit der Maus beim Darüberfahren, mit der Tastatur beim
Anspringen. Escape schließt sie wieder. Wer einen Screenreader benutzt, bekommt
den Text beim Anspringen vorgelesen.

„automatisch" überlässt die Wahl dem Dienst. Er nimmt zur Dateiendung die erste
Engine seiner Liste, die gerade bereit ist; scheitert sie, nimmt er die nächste
und nennt den Grund in den Warnungen. Vorgewählt ist markitdown, die schnelle
Engine. Die Wahl bleibt im Browser gemerkt und steht beim nächsten Aufruf der
Seite wieder da.

Nicht jede Engine ist immer wählbar:

- Eine Engine, die eine der Dateien in der Warteschlange nicht liest, bleibt
  sichtbar und wird blass. Fährt der Mauszeiger darüber, nennt ein Hinweis den
  Grund: „liest diese Dateien nicht".
- Genauso ergeht es einer Engine, die auf diesem Dienst gar nicht installiert
  ist. Der Hinweis lautet dann „nicht installiert".
- Eine Engine, die gerade noch ihre Modelle lädt, heißt „(lädt noch)" und bleibt
  wählbar. Die erste Anfrage wartet dann, bis sie so weit ist.

Fällt die gewählte Engine aus der Auswahl — etwa weil eine Datei dazukam, die sie
nicht liest —, springt die Wahl auf „automatisch" zurück.

### Text in Bildern erkennen

Der Schalter „Text in Bildern erkennen (OCR)" steht nur da, wenn der Dienst die
Texterkennung anbietet. Rührt ihn niemand an, gilt die Voreinstellung des
Dienstes; das steht dann auch daneben.

Neben dem Schalter steht, wo er wirkt: **nur in PDF und Bilddateien**. Das runde
„i" dahinter zählt die Formate auf und nennt den Umweg. In einer .docx-, .pptx-,
.xlsx-, .html- oder .epub-Datei bleibt die Texterkennung aus, auch wenn der
Schalter an ist. Wer den Text aus einem Bild darin braucht, speichert das Dokument
als PDF und lädt es erneut hoch. Ausführlich steht das unter
[Grenzen](grenzen.md#ocr-greift-nur-in-pdf-und-bilddateien).

## Warnungen lesen

Ein gelber Kasten an einer Zeile ist keine Fehlermeldung. Die Datei ist
umgewandelt, das Ergebnis liegt vor — aber etwas aus der Vorlage steht nicht
darin. Genau dafür ist dieser Dienst da: Er zeigt, was ankommt.

Eine Warnung bleibt nicht bei der Feststellung. Sie nennt den Grund und den
Umweg. Zwei Beispiele, wie sie tatsächlich dastehen:

> In bericht.docx steckt ein Bild. Sein Inhalt fehlt im Markdown. MarkItDown
> liest keinen Text aus Bildern. Wer ihn braucht, speichert das Dokument als PDF
> und lädt es mit der Engine docling und eingeschalteter Texterkennung erneut
> hoch.

> Docling hat in bericht.pdf 14 Bilder durch Platzhalter ersetzt. Ihr Inhalt fehlt
> im Markdown. Ohne eingeschaltete Texterkennung liest Docling den Text aus einem
> Bild nicht. Wer ihn braucht, schaltet die Texterkennung ein und lädt die Datei
> erneut hoch.

Der letzte Satz ist der wichtigste: Er sagt, was zu tun ist. Manchmal ist es die
andere Engine, manchmal der Schalter darüber, manchmal ein Blick ins Original.

Ein roter Kasten dagegen heißt, dass gar kein Ergebnis herauskam. Dann steht dort
die Meldung des Dienstes.

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
[Zeitgrenze](grenzen.md#die-zeitgrenze-beendet-den-wartevorgang-nicht-die-engine)
wieder frei.

Danach steht die Zeile auf „abgebrochen", und die nächste wartende Datei rückt
nach. Als Fehlschlag zählt der Abbruch nicht — entschieden hat ihn der Nutzer,
gescheitert ist nichts.

## Wenn der Dienst nicht antwortet

Ganz oben erscheint dann ein roter Kasten mit der Meldung und einem Knopf „Erneut
versuchen". Solange der Dienst schweigt, kennt die Seite weder die Engines noch
die erlaubten Endungen; die Auswahl bleibt leer. Der Knopf fragt noch einmal
nach. Hilft das nicht, ist der Dienst selbst nicht erreichbar — dann hilft nur,
wer ihn betreibt.

Am unteren Rand der Seite steht klein die Version des Dienstes. Wer dem Betreiber
einen Fehler meldet, nennt sie mit.
