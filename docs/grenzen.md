# Grenzen

Was kaimarkit nicht kann und woran eine Umwandlung scheitert.

## Vier Werte begrenzen einen Aufruf

Alle vier kommen aus der Umgebung. `docs/betrieb/konfiguration.md` beschreibt sie
im Einzelnen, `docker/.env.example` nennt die Standardwerte.

| Variable | Standard | Was sie begrenzt |
| --- | --- | --- |
| `KAIMARKIT_MAX_FILE_SIZE_MB` | 50 | Größe einer einzelnen Datei |
| `KAIMARKIT_MAX_FILES` | 20 | Dateien je Stapelaufruf |
| `KAIMARKIT_MAX_CONCURRENT` | 2 | gleichzeitige Umwandlungen |
| `KAIMARKIT_CONVERSION_TIMEOUT` | 600 | Sekunden je Datei |

Die Größe prüft der Dienst schon beim Empfang. Überschreitet die Datei das Limit,
bricht er ab und antwortet mit 413 und `file_too_large`. Den Rest des Uploads liest
er nicht mehr ein — eine Prüfung danach käme zu spät, dann läge die Datei bereits
vollständig im Speicher.

Solange eine Umwandlung läuft, liegt die Datei in einer temporären Datei. Danach
löscht der Dienst sie, auch wenn die Engine gescheitert ist. Gespeichert wird
nichts.

## Die Zeitgrenze beendet den Wartevorgang, nicht die Engine

Dauert eine Umwandlung länger als `KAIMARKIT_CONVERSION_TIMEOUT`, antwortet der
Dienst mit 504 und `conversion_timeout`. Die Engine arbeitet im Hintergrund weiter,
bis sie von selbst fertig ist, und verbraucht so lange Rechenzeit. Häufen sich die
Zeitüberschreitungen, sammeln sich diese Läufe an und der Dienst wird langsam;
dann hilft nur ein Neustart des Containers.

Eine Ausnahme ist Pandoc: Es läuft als eigener Prozess, und den beendet der
Dienst nach `KAIMARKIT_PANDOC_TIMEOUT` tatsächlich.

Wer regelmäßig an die Zeitgrenze stößt, setzt sie besser hoch, statt es mehrfach
zu versuchen: Jeder Versuch legt einen weiteren Lauf obendrauf.

## Gescannte Seiten ohne OCR bleiben leer

Ein PDF aus dem Scanner enthält Bilder und keinen Text. MarkItDown liest darin
nichts, weil es nichts zu lesen findet, und Pandoc kommt für PDF ohnehin nicht in
Frage. Das ist kein Fehler: Die Umwandlung gelingt, das Markdown bleibt leer, und
die Antwort nennt den Grund in `warnings`.

Text aus solchen Dateien holt allein Docling, und nur mit eingeschalteter
Texterkennung. `KAIMARKIT_OCR_ENABLED` setzt den Standard, das Feld `ocr` einer
einzelnen Anfrage überschreibt ihn:

```bash
curl -sf -F file=@scan.pdf -F engine=docling -F ocr=true \
     localhost:8000/api/convert -o scan.md
```

Zwei Dinge kosten das. Die Texterkennung ist um ein Vielfaches langsamer als das
Lesen einer Textebene, und ihre Sprachen müssen stimmen: `KAIMARKIT_OCR_LANGS` steht
auf `de,en`, ein französisches Dokument braucht dort seinen eigenen Eintrag, `fr`.

Läuft der Aufruf mit `engine=auto` und ist Docling noch nicht bereit, nimmt der
Dienst für das PDF die nächste Engine der Liste — und die findet dann eben keinen
Text. Wer sicher OCR will, nennt Docling ausdrücklich und wartet.

## Bilder werden nicht beschrieben

Ein Bild im Dokument erscheint im Markdown als Platzhalter oder als Alt-Text, nie
als Beschreibung seines Inhalts. Der Dienst schickt bewusst nichts an ein
Sprachmodell — er soll den Kontext zeigen, den man einem Modell gibt, und ihn nicht
selbst erzeugen. Ein Diagramm, dessen Aussage nur im Bild steht, geht dabei
verloren.

Bei einem PDF durch MarkItDown bleibt nicht einmal die Stelle übrig. Die Engine
liest dort nur die Textebene und lässt jedes Bild ersatzlos weg; im Markdown steht
danach weder Platzhalter noch Alt-Text. Der Dienst warnt deshalb bei jedem PDF, das
durch MarkItDown läuft. Docling setzt stattdessen `<!-- image -->` ein und zählt die
ersetzten Bilder.

## Jeder Worker hält eigene Docling-Modelle

Die Modelle liegen im Speicher des Prozesses, nicht daneben. Zwei Uvicorn-Worker
halten sie deshalb zweimal, mit jeweils rund 2 GB. `KAIMARKIT_WORKERS` erst
hochsetzen, wenn genug RAM da ist, und `KAIMARKIT_MEM_LIMIT` mit anheben — sonst
schießt der Kernel den Container beim ersten großen PDF ab. Dass es das war, zeigt
`docker inspect` als `OOMKilled`.

Gleichzeitige Anfragen sind der falsche Grund für mehr Worker. Wie viele
Umwandlungen nebeneinander laufen, regelt `KAIMARKIT_MAX_CONCURRENT` innerhalb eines
Prozesses; das kostet keinen zweiten Satz Modelle.

Wartezeit kostet auch der erste Aufruf. Docling beginnt seine Modelle zu laden,
sobald der Dienst hochfährt, und lädt sie im Hintergrund; jeder Neustart fängt damit
von vorn an. Bis das fertig ist, meldet die Auskunft `warming` und `engine=auto`
nimmt für ein PDF MarkItDown.

## Was der Dienst gar nicht tut

- **Nichts aufheben.** Es gibt keine Historie und keinen Zwischenspeicher. Wer ein
  Ergebnis behalten will, lädt es herunter.
- **Niemanden erkennen.** Die API kennt keine Anmeldung und keine Kennungen. Eine
  Anmeldung kommt von außen davor, siehe [Authelia](betrieb/authelia.md).
- **Nichts nachladen.** Alle Modelle stecken im Abbild. Aus dem Netz holt der
  Dienst zur Laufzeit nur, was ein Aufruf von `/api/convert/url` verlangt: die eine
  Seite, von einer öffentlichen Adresse, und nichts von sich aus.
- **Nichts zurückschreiben.** Der Weg führt nur in eine Richtung: nach Markdown.
  Aus Markdown wieder ein PDF zu machen, ist nicht Aufgabe dieses Dienstes.
