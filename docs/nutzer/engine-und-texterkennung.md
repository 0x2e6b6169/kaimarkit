# Engine und Texterkennung wählen

Über dem gestrichelten Feld steht der Abschnitt „Optionen". Was dort eingestellt ist, gilt
für den nächsten Lauf. Bereits umgewandelte Dateien bleiben, wie sie sind.

## Die Engine wählen

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

## Text in Bildern erkennen

Der Schalter „Text in Bildern erkennen (OCR)" steht nur da, wenn der Dienst die
Texterkennung anbietet. Rührt ihn niemand an, gilt die Voreinstellung des
Dienstes; das steht dann auch daneben.

Neben dem Schalter steht, wo er wirkt: **nur in PDF und Bilddateien**. Das runde
„i" dahinter zählt die Formate auf und nennt den Umweg. In einer .docx-, .pptx-,
.xlsx-, .html- oder .epub-Datei bleibt die Texterkennung aus, auch wenn der
Schalter an ist. Wer den Text aus einem Bild darin braucht, speichert das Dokument
als PDF und lädt es erneut hoch. Ausführlich steht das unter
[Grenzen](../admin/grenzen.md#ocr-greift-nur-in-pdf-und-bilddateien).

## Beides über die Schnittstelle

Was die Optionen einstellen, sind zwei Felder am Aufruf: `engine` und `ocr`.
`$DIENST` steht für die Adresse, unter der die Oberfläche antwortet.

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

In `engine` steht, welche Engine es geworden ist. Wer das Feld beim Aufruf wegzulässt,
bekommt `auto`, dasselbe wie „automatisch" in der Oberfläche; `ocr` überschreibt die
Voreinstellung des Dienstes, so wie der Schalter es tut.

Eine ausdrücklich genannte Engine ersetzt der Dienst nie durch eine andere. Kann sie
das Format nicht, antwortet er mit 400, statt still eine andere zu nehmen:

```json
{ "detail": "Engine pandoc kann .pdf nicht wandeln.", "code": "engine_unsuitable" }
```

Was gerade zur Wahl steht, nennt `/api/capabilities`. Aus derselben Auskunft baut die
Oberfläche ihre Schaltergruppe:

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

Der Ausschnitt zeigt zwei Endungen; der Dienst nennt alle, die er annimmt, dazu die
geltenden Grenzen. Die drei Zustände in `engines` sind dieselben, die am Schalter
stehen: `ready` ist wählbar, `warming` heißt dort „(lädt noch)", `unavailable` heißt
„nicht installiert". Die Reihenfolge in `formats` ist die Präferenz — bei
`engine=auto` kommt der erste Eintrag zum Zug, der gerade bereit ist. In
`ocr_available` steht, ob die Oberfläche den Schalter zeigt.

Alle Felder dieser Auskunft stehen unter [API](../admin/api.md).
