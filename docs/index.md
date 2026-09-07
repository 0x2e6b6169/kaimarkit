# kaimarkit

kaimarkit wandelt PDF, ePub, docx und weitere Dokumente nach Markdown, damit man
den Kontext liest und prüft, den man einem Sprachmodell übergibt.

Wer ein PDF in ein Chatfenster zieht, sieht nicht, was dort ankommt. Tabellen
zerfallen in Wortreihen, Fußnoten landen mitten im Satz, und eine eingescannte Seite
liefert überhaupt keinen Text. Das Modell antwortet trotzdem. kaimarkit schiebt einen
Schritt dazwischen: Es zeigt das Markdown, bevor es jemand weiterreicht.

## Diese Dokumentation hat zwei Teile

**[Für Nutzer](nutzer/dateien-wandeln.md)** — die Arbeit im Browser. Eine Datei
oder eine Webseite wandeln, Engine und Texterkennung wählen, eine Warnung lesen.
Diese Seiten setzen nichts voraus außer einem Browser und der Adresse, unter der
der Dienst antwortet.

**[Für Admins](admin/schnellstart.md)** — den Dienst bereitstellen. Installieren,
konfigurieren, hinter Traefik stellen, eine Anmeldung davorsetzen, Grenzen setzen,
die Schnittstelle ansprechen. Diese Seiten setzen Terminal, Docker und curl voraus.

Wer am Quelltext mitarbeitet, findet den Aufbau des Projekts unter
[Entwicklung](entwicklung.md).

## Drei Engines, eine Auswahl je Endung

MarkItDown ist die schnelle Engine ohne Modelle und ohne Texterkennung. Docling liest
Layout und Tabellen und erkennt auf Wunsch gescannten Text, braucht dafür aber
Modelle im Speicher. Pandoc bedient die Formate, die sonst niemand liest — `.odt`,
`.rtf`, `.tex` —, kann PDF aber nicht lesen.

Welche Endung welche Engine bekommt und in welcher Reihenfolge, steht unter
[Formate](admin/formate.md). Wer die Wahl selbst treffen will, nennt die Engine im
Aufruf; der Dienst ersetzt sie dann nie durch eine andere.

## Der Dienst legt nichts ab

Eine hochgeladene Datei liegt während der Umwandlung in einer temporären Datei und
ist danach gelöscht, auch wenn die Engine gescheitert ist. Es gibt keine Historie,
kein Konto und keine Anmeldung. Wer eine Anmeldung braucht, setzt
[Authelia](admin/authelia.md) davor.
