# Eine Webseite wandeln

Eine Webseite braucht keinen Umweg über den eigenen Rechner. Unter „Webseiten,
eine Adresse je Zeile" steht ein mehrzeiliges Feld; „Webseiten wandeln" schickt
jede Zeile ab, und der Dienst holt die Seiten selbst.

Eine Zeile, die weder mit `http://` noch mit `https://` beginnt, schickt die
Oberfläche gar nicht erst ab. Sie bleibt im Feld stehen und wird darunter
genannt. Alles Weitere prüft der Dienst — ob der Name auflöst, ob er ins offene
Netz zeigt, ob dort ein Dokument liegt —, und seine Meldung steht dann in der
Zeile der Warteschlange.

Jede geholte Seite reiht sich in dieselbe Warteschlange ein wie eine hochgeladene
Datei. Ihren Namen bekommt sie aus dem Titel der Seite: Aus `https://example.com/`
wird `example-domain.html`. Fanden nicht alle Adressen Platz, stehen die übrigen
wieder im Feld — von dort lassen sie sich gleich noch einmal abschicken.

Welche Seiten der Dienst nicht brauchbar wandelt, steht unter
[Grenzen](../admin/grenzen.md#webseiten-nur-offentlich-kein-javascript).
