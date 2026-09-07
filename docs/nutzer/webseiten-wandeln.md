# Eine Webseite wandeln

Eine Webseite musst Du nicht erst auf Deinen Rechner laden. Trag ihre Adresse in
das mehrzeilige Feld unter „Webseiten, eine Adresse je Zeile" ein und schick sie
mit „Webseiten wandeln" ab; der Dienst holt die Seiten selbst.

Eine Zeile, die weder mit `http://` noch mit `https://` beginnt, schickt die
Oberfläche gar nicht erst ab. Sie bleibt im Feld stehen und wird darunter
genannt. Alles Weitere prüft der Dienst — ob der Name auflöst, ob er ins offene
Netz zeigt, ob dort ein Dokument liegt —, und seine Meldung steht dann in der
Zeile der Warteschlange.

Jede geholte Seite reiht sich in dieselbe Warteschlange ein wie eine hochgeladene
Datei. Ihren Namen bekommt sie aus dem Titel der Seite: Aus `https://example.com/`
wird `example-domain.html`. Fanden nicht alle Adressen Platz, stehen die übrigen
wieder im Feld — von dort schickst Du sie gleich noch einmal ab.

Welche Seiten der Dienst nicht brauchbar wandelt, steht unter
[Grenzen](../admin/grenzen.md#webseiten-nur-offentlich-kein-javascript).

## Dieselbe Adresse über die Schnittstelle

`/api/convert/url` nimmt eine Adresse je Aufruf, als JSON. Setz `$DIENST` auf die
Adresse, unter der die Oberfläche antwortet:

```bash
curl -sf -H 'Content-Type: application/json' \
     -d '{"url": "https://example.com/"}' $DIENST/api/convert/url
```

```json
{
  "filename": "example-domain.html",
  "status": "ok",
  "markdown": "# Example Domain\n\nThis domain is for use in documentation examples without needing permission. Avoid use in operations.\n\n[Learn more](https://iana.org/domains/example)",
  "engine": "markitdown",
  "warnings": [],
  "duration_ms": 10,
  "error": null
}
```

In `filename` steht derselbe Name, den auch die Warteschlange anzeigt. Einen
Markdown-Zweig über `Accept`, wie ihn `/api/convert` kennt, gibt es hier nicht: Die
Antwort ist immer JSON. Neben `url` nimmt der Rumpf `engine` und `ocr`, dieselben
zwei Optionen wie beim Upload.

Eine Zeile ohne `http://` oder `https://` schickt die Oberfläche gar nicht erst ab.
Über die Schnittstelle antwortet der Dienst darauf selbst, mit 400 und dem Code
`invalid_url`:

```json
{ "detail": "example.com: nur http- und https-Adressen werden geholt.", "code": "invalid_url" }
```

Denselben Code bekommst Du für eine Adresse, die nicht ins offene Netz zeigt —
auch dann, wenn erst eine Weiterleitung dorthin führt:

```json
{
  "detail": "127.0.0.1 zeigt auf 127.0.0.1, und das ist keine öffentliche Adresse.",
  "code": "invalid_url"
}
```

Die übrigen Fehlercodes stehen unter [API](../admin/api.md).
