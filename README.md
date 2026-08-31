# kaimarkit

kaimarkit wandelt PDF, ePub, docx und weitere Dokumente nach Markdown. Wer eine
Datei an ein Sprachmodell übergibt, sieht sonst nicht, was dort ankommt: zerfallene
Tabellen, verrutschte Fußnoten, eine gescannte Seite ganz ohne Text. kaimarkit zeigt
das Markdown, bevor es weitergeht.

Dahinter arbeiten drei Engines. MarkItDown wandelt schnell und ohne Modelle, Docling
liest Layout und Tabellen und erkennt gescannten Text, Pandoc bedient `.odt`, `.rtf`
und `.tex`. Der Dienst wählt nach Dateiendung, und keine hochgeladene Datei überlebt
ihre Umwandlung.

## Starten

```bash
cp docker/.env.example docker/.env
make up
curl -sf -F file=@bericht.pdf localhost:8080/api/convert -o bericht.md
```

`make up` baut das Abbild und startet den Container. Der erste Bau backt die
Docling-Modelle ein und braucht dafür mehrere Gigabyte Platz. Danach antwortet der
Dienst unter <http://127.0.0.1:8080>; `make help` nennt alle Ziele.

Die Oberfläche wird noch zusammengesetzt: Dropzone, Warteschlange, Optionen und
Vorschau liegen als einzelne Bausteine bereit, die Startseite zeigt bisher nur das
Gerüst. Der Weg über curl funktioniert vollständig.

## Das Handbuch

Die Dokumentation ist die einzige Quelle für Bedienung und Betrieb. Sie liegt unter
[`docs/`](docs/index.md), im laufenden Container unter `/docs`, als Vorschau über
`make docs-serve` auf <http://127.0.0.1:8001>.

- [Schnellstart](docs/schnellstart.md) — vom Start des Containers bis zur ersten
  umgewandelten Datei
- [Formate](docs/formate.md) — welche Endung welche Engine bekommt
- [API](docs/api.md) — die Endpunkte mit Aufrufen für curl
- [Betrieb](docs/betrieb/konfiguration.md) — alle Variablen, lokal, hinter Traefik,
  mit Anmeldung
- [Entwicklung](docs/entwicklung.md) — der Aufbau des Projekts und eine vierte
  Engine ergänzen
- [Grenzen](docs/grenzen.md) — was das Werkzeug nicht kann

Den verbindlichen Wortlaut der Schnittstelle hält [`contracts/api.md`](contracts/api.md)
fest.
