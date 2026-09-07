# Warnungen und Fehler verstehen

Die Oberfläche kennt drei Kästen: einen gelben und einen roten an der Zeile
einer Datei, und einen roten ganz oben auf der Seite. Der oberste meint nicht
eine Datei, sondern den Dienst. Jeder der drei Fälle hat sein Gegenstück in der
Antwort der Schnittstelle; die Aufrufe unten schreiben `$DIENST` für die Adresse,
unter der die Oberfläche antwortet.

## Ein gelber Kasten: etwas fehlt im Ergebnis

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

Denselben Wortlaut liefert die Schnittstelle im Feld `warnings`:

```bash
curl -sf -F file=@bericht.docx -H 'Accept: application/json' $DIENST/api/convert
```

```json
{
  "filename": "bericht.docx",
  "status": "ok",
  "markdown": "# Kaimarkit Fixture\n\nEin Absatz aus dem Fixturebestand.\n\n![]()",
  "engine": "markitdown",
  "warnings": [
    "In bericht.docx steckt ein Bild. Sein Inhalt fehlt im Markdown. MarkItDown liest keinen Text aus Bildern. Wer ihn braucht, speichert das Dokument als PDF und lädt es mit der Engine docling und eingeschalteter Texterkennung erneut hoch."
  ],
  "duration_ms": 70,
  "error": null
}
```

`warnings` ist immer da und leer, wenn nichts anzumerken war. `status` bleibt `ok`:
Das Ergebnis liegt vor, es fehlt nur etwas darin.

## Ein roter Kasten: es kam kein Ergebnis heraus

In dem Kasten steht die Meldung des Dienstes. Eine gescheiterte Datei hält die
übrigen nicht auf; die nächste rückt nach.

Über die Schnittstelle ist das keine 200-Antwort, sondern ein Fehlercode. Im Rumpf
steht dieselbe Meldung, dazu ein Kürzel, an dem ein Programm den Fall erkennt:

```bash
curl -s -F file=@notiz.xyz -H 'Accept: application/json' $DIENST/api/convert
```

```json
{ "detail": "Für .xyz gibt es keine Engine.", "code": "unsupported_format" }
```

`curl -sf` verschluckt diesen Rumpf; wer die Meldung sehen will, lässt das `-f` weg.
Im Stapel über `/api/convert/batch` scheitert die Anfrage deswegen nicht: Die Datei
wird ein Eintrag mit `status: "failed"` und dem Grund in `error`, die übrigen laufen
weiter.

```json
{
  "filename": "notiz.xyz",
  "status": "failed",
  "markdown": null,
  "engine": null,
  "warnings": [],
  "duration_ms": 1,
  "error": "Für .xyz gibt es keine Engine."
}
```

Welches Kürzel zu welchem Anlass gehört, steht vollständig unter
[API](../admin/api.md).

## Wenn der Dienst nicht antwortet

Ganz oben erscheint dann ein roter Kasten mit der Meldung und einem Knopf „Erneut
versuchen". Solange der Dienst schweigt, kennt die Seite weder die Engines noch
die erlaubten Endungen; die Auswahl bleibt leer. Der Knopf fragt noch einmal
nach. Hilft das nicht, ist der Dienst selbst nicht erreichbar — dann hilft nur,
wer ihn betreibt.

Am unteren Rand der Seite steht klein die Version des Dienstes. Wer dem Betreiber
einen Fehler meldet, nennt sie mit. Sie kommt aus `/api/health`, und derselbe
Aufruf beantwortet auch die Frage, ob der Dienst überhaupt noch da ist:

```bash
curl -sf $DIENST/api/health
```

```json
{ "status": "ok", "version": "0.2.0" }
```

Bleibt diese Antwort aus, liegt es nicht an der Datei.
