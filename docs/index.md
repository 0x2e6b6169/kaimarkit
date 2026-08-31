# kaimarkit

kaimarkit wandelt PDF, ePub, docx und weitere Dokumente nach Markdown, damit man
den Kontext liest und prüft, den man einem Sprachmodell übergibt.

Wer ein PDF in ein Chatfenster zieht, sieht nicht, was dort ankommt. Tabellen
zerfallen in Wortreihen, Fußnoten landen mitten im Satz, und eine eingescannte Seite
liefert überhaupt keinen Text. Das Modell antwortet trotzdem. kaimarkit schiebt einen
Schritt dazwischen: Es zeigt das Markdown, bevor es jemand weiterreicht.

## Drei Engines, eine Auswahl je Endung

MarkItDown ist die schnelle Engine ohne Modelle und ohne Texterkennung. Docling liest
Layout und Tabellen und erkennt auf Wunsch gescannten Text, braucht dafür aber
Modelle im Speicher. Pandoc bedient die Formate, die sonst niemand liest — `.odt`,
`.rtf`, `.tex` —, kann PDF aber nicht lesen.

Welche Endung welche Engine bekommt und in welcher Reihenfolge, steht unter
[Formate](formate.md). Wer die Wahl selbst treffen will, nennt die Engine im Aufruf;
der Dienst ersetzt sie dann nie durch eine andere.

## Der Dienst legt nichts ab

Eine hochgeladene Datei liegt während der Umwandlung in einer temporären Datei und
ist danach gelöscht, auch wenn die Engine gescheitert ist. Es gibt keine Historie,
kein Konto und keine Anmeldung. Wer eine Anmeldung braucht, setzt
[Authelia](betrieb/authelia.md) davor.

## Wohin als Nächstes

- [Schnellstart](schnellstart.md) — vom Start des Containers bis zur ersten
  umgewandelten Datei.
- [Formate](formate.md) — die Matrix aus Endung und Engine, dazu OCR und Rückfall.
- [API](api.md) — die vier Endpunkte mit Aufrufen für curl.
- [Betrieb](betrieb/konfiguration.md) — alle Variablen, lokal, hinter Traefik, mit
  Anmeldung.
- [Entwicklung](entwicklung.md) — Aufbau des Projekts und eine vierte Engine
  ergänzen.
- [Grenzen](grenzen.md) — was das Werkzeug nicht kann.
