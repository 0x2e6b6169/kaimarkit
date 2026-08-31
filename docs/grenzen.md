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
| `KAIMARKIT_CONVERSION_TIMEOUT` | 120 | Sekunden je Datei |

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
