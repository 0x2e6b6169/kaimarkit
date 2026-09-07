# Engine und Texterkennung wählen

Welche Engine Deine Datei wandelt und ob sie Text aus Bildern liest, stellst Du über
dem gestrichelten Feld unter „Optionen" ein. Was Du dort änderst, gilt für den
nächsten Lauf; bereits umgewandelte Dateien bleiben, wie sie sind.

## Die Engine wählen

Deine Wahl triffst Du an einer Gruppe von Schaltern untereinander, „automatisch"
zuerst. Was ein Name bedeutet, sagt Dir der Halbsatz daneben, und das runde „i"
dahinter öffnet die längere Erklärung — mit der Maus beim Darüberfahren, mit der
Tastatur beim Anspringen. Escape schließt sie wieder. Benutzt Du einen
Screenreader, bekommst Du den Text beim Anspringen vorgelesen.

„automatisch" überlässt die Wahl dem Dienst. Er nimmt zur Dateiendung die erste
Engine seiner Liste, die gerade bereit ist; scheitert sie, nimmt er die nächste
und nennt den Grund in den Warnungen. Vorgewählt ist markitdown, die schnelle
Engine. Deine Wahl merkt sich der Browser; beim nächsten Aufruf der Seite steht
sie wieder da.

Nicht jede Engine ist immer wählbar:

- Eine Engine, die eine der Dateien in Deiner Warteschlange nicht liest, bleibt
  sichtbar und wird blass. Fährt der Mauszeiger darüber, nennt ein Hinweis den
  Grund: „liest diese Dateien nicht".
- Genauso ergeht es einer Engine, die auf diesem Dienst gar nicht installiert
  ist. Der Hinweis lautet dann „nicht installiert".
- Eine Engine, die gerade noch ihre Modelle lädt, heißt „(lädt noch)" und bleibt
  wählbar. Deine erste Anfrage wartet dann, bis sie so weit ist.

Fällt Deine Engine aus der Auswahl — etwa weil eine Datei dazukam, die sie nicht
liest —, springt die Wahl auf „automatisch" zurück.

## Text in Bildern erkennen

Steckt Dein Text in Bildern, schalte „Text in Bildern erkennen (OCR)" ein. Den
Schalter zeigt Dir die Oberfläche nur, wenn der Dienst die Texterkennung anbietet.
Rührst Du ihn nicht an, gilt die Voreinstellung des Dienstes; das steht dann auch
daneben.

Neben dem Schalter steht, wo er wirkt: **nur in PDF und Bilddateien**. Das runde
„i" dahinter zählt die Formate auf und nennt den Umweg. In einer .docx-, .pptx-,
.xlsx-, .html- oder .epub-Datei bleibt die Texterkennung aus, auch wenn Du den
Schalter anschaltest. Brauchst Du den Text aus einem Bild darin, speicher das
Dokument als PDF und lade es erneut hoch. Ausführlich steht das unter
[Grenzen](../admin/grenzen.md#ocr-greift-nur-in-pdf-und-bilddateien).

## Beides über die Schnittstelle

Dieselben zwei Einstellungen sind am Aufruf zwei Felder: `engine` und `ocr`. Setz
`$DIENST` auf die Adresse, unter der die Oberfläche antwortet.

```bash
curl -sf -F file=@tabelle.pdf -F engine=markitdown -F ocr=true \
     -H 'Accept: application/json' $DIENST/api/convert
```

```json
{
  "filename": "tabelle.pdf",
  "status": "ok",
  "markdown": "Kaimarkit Fixture\n\nFormat\n\npdf\n\nodt\n\n…",
  "engine": "markitdown",
  "warnings": [
    "MarkItDown übernimmt keine Bilder aus PDF. Enthielt tabelle.pdf Bilder, fehlt ihr Inhalt hier."
  ],
  "duration_ms": 19,
  "error": null
}
```

In `engine` steht, welche Engine es geworden ist. Lässt Du das Feld weg, bekommst
Du `auto`, dasselbe wie „automatisch" in der Oberfläche; `ocr` überschreibt die
Voreinstellung des Dienstes, so wie der Schalter es tut.

Nennst Du eine Engine ausdrücklich, ersetzt der Dienst sie nie durch eine andere.
Kann sie das Format nicht, antwortet er mit 400, statt still eine andere zu nehmen:

```json
{ "detail": "Engine pandoc kann .pdf nicht wandeln.", "code": "engine_unsuitable" }
```

Was gerade zur Wahl steht, nennt Dir `/api/capabilities`. Aus derselben Auskunft
baut die Oberfläche ihre Schaltergruppe:

```bash
curl -sf $DIENST/api/capabilities
```

```json
{
  "formats": {
    ".pdf":  ["docling", "markitdown"],
    ".docx": ["markitdown", "docling", "pandoc"]
  },
  "engines": {
    "markitdown": "ready",
    "docling":    "warming",
    "pandoc":     "ready"
  },
  "ocr_available": true,
  "default_engine": "auto"
}
```

Der Dienst nennt Dir alle Endungen, die er annimmt, dazu die geltenden Grenzen;
oben stehen zwei davon. Die drei Zustände in `engines` sind dieselben, die am
Schalter stehen: `ready` ist wählbar, `warming` heißt dort „(lädt noch)",
`unavailable` heißt „nicht installiert". Die Reihenfolge in `formats` ist die
Präferenz: Bei `engine=auto` kommt der erste Eintrag zum Zug. In `ocr_available`
steht, ob die Oberfläche Dir den Schalter zeigt.

Alle Felder dieser Auskunft stehen unter [API](../admin/api.md).
