# Open WebUI

Open WebUI kann das Auslesen hochgeladener Dateien an einen fremden Dienst abgeben.
Übernimmt kaimarkit diese Aufgabe, landet im Chat genau das Markdown, das die
Vorschau in kaimarkit zeigt. Ohne die Anbindung wandelt Open WebUI dieselbe Datei
mit einem eigenen Loader und bekommt womöglich etwas anderes heraus. Docling
erreicht Open WebUI sonst nur über einen eigenen Docling-Server; kaimarkit bringt
Docling samt Modellen schon mit.

Die Angaben hier sind gegen `ghcr.io/open-webui/open-webui:v0.11.3` geprüft
(22.09.2026). Eine andere Version kann andere Variablen oder ein anderes Verhalten
haben.

## Die drei Variablen auf der Seite von Open WebUI

```bash
CONTENT_EXTRACTION_ENGINE=external
EXTERNAL_DOCUMENT_LOADER_URL=http://kaimarkit:8000/api
EXTERNAL_DOCUMENT_LOADER_API_KEY=beliebig
```

Open WebUI hängt `/process` an die Adresse und ruft `PUT /api/process` auf. Die
Adresse endet deshalb auf `/api`, ohne Schrägstrich. `kaimarkit:8000` gilt, wenn beide
Container im selben Docker-Netz liegen; der Name ist der Dienstname aus der
Compose-Datei, der Port der innere. Nach außen veröffentlicht wird 8080, im Netz
zwischen den Containern hört der Dienst auf 8000.

Dieselben Einstellungen gibt es in Open WebUI auch unter *Admin-Einstellungen →
Dokumente*. Was dort gespeichert ist, gilt vor den Umgebungsvariablen.

## Der Schlüssel darf nicht leer sein

`EXTERNAL_DOCUMENT_LOADER_API_KEY` muss gesetzt sein, auch wenn kaimarkit ihn nicht
prüft. Open WebUI nimmt den externen Weg nur, wenn Adresse **und** Schlüssel gesetzt
sind. Fehlt einer, nutzt es wieder die eingebaute Extraktion, ohne Fehler und ohne
Meldung. Der Wert ist beliebig.

kaimarkit kennt keine Anmeldung und ignoriert den Kopf `Authorization`. Wer den
Endpunkt schützen will, erreicht ihn aus Open WebUI über das interne Docker-Netz und
veröffentlicht ihn nicht nach außen, oder setzt [Authelia](authelia.md) vor den
öffentlichen Weg. Der interne Weg führt an Traefik und Authelia vorbei.

## Jede Datei geht an kaimarkit, auch Quelltext

Mit `external` schickt Open WebUI jede hochgeladene Datei an kaimarkit, auch `.txt`,
`.py`, `.csv` und `.json`. Die eingebaute Extraktion reicht Textdateien an sich
vorbei, der externe Weg nicht. Weist kaimarkit eine Datei ab, scheitert der Upload in
Open WebUI.

Deshalb gilt an diesem Endpunkt ein Textrückfall: Kennt keine Engine die Endung, geht
der Inhalt als Text zurück, sofern er sauberes UTF-8 ohne Nullbytes ist. Im Ergebnis
steht dann `engine: passthrough` und eine Warnung. `KAIMARKIT_PROCESS_TEXT_FALLBACK=false`
schaltet das ab; dann scheitert in Open WebUI der Upload jeder Datei, für die kaimarkit
keine Engine hat. Binärdateien ohne Engine scheitern in beiden Fällen.

## Engine und Texterkennung kommen aus der Umgebung

Je Upload lässt sich weder die Engine noch die Texterkennung wählen. Open WebUI setzt
`/process` hinter die eingetragene Adresse; ein Anhängsel wie `?engine=docling`
stünde davor und machte die Adresse unbrauchbar. Es gelten `KAIMARKIT_DEFAULT_ENGINE`
und `KAIMARKIT_OCR_ENABLED` aus der [Konfiguration](konfiguration.md). Wer für Open
WebUI andere Voreinstellungen braucht als für die Oberfläche, betreibt einen zweiten
kaimarkit-Container mit eigener Umgebung.

## Was Open WebUI zurückbekommt

Das Markdown steht in `page_content`, dazu kommen `metadata` mit `filename`, `engine`,
`duration_ms` und, wenn es welche gab, `warnings`. Open WebUI übernimmt die Metadaten
in seine Vektordatenbank. Einen Fehler zeigt Open WebUI als
`Error loading document: <status> <text>`; im Text steht die Meldung von kaimarkit.
Den genauen Aufbau beschreibt die [API](api.md).

## Prüfen, ob die Anbindung greift

Nach dem Hochladen einer Datei im Chat muss im Protokoll von kaimarkit der Aufruf
stehen:

```bash
docker logs kaimarkit 2>&1 | grep 'PUT /api/process'
```

Fehlt er, hat Open WebUI die eingebaute Extraktion genommen. Die häufigste Ursache
ist ein leerer `EXTERNAL_DOCUMENT_LOADER_API_KEY`, die zweithäufigste ein Eintrag
unter *Admin-Einstellungen → Dokumente*, der die Umgebungsvariablen überdeckt.
