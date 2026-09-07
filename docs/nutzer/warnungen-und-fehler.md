# Warnungen und Fehler verstehen

Die Oberfläche kennt drei Kästen: einen gelben und einen roten an der Zeile
einer Datei, und einen roten ganz oben auf der Seite. Der oberste meint nicht
eine Datei, sondern den Dienst.

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

## Ein roter Kasten: es kam kein Ergebnis heraus

In dem Kasten steht die Meldung des Dienstes. Eine gescheiterte Datei hält die
übrigen nicht auf; die nächste rückt nach.

## Wenn der Dienst nicht antwortet

Ganz oben erscheint dann ein roter Kasten mit der Meldung und einem Knopf „Erneut
versuchen". Solange der Dienst schweigt, kennt die Seite weder die Engines noch
die erlaubten Endungen; die Auswahl bleibt leer. Der Knopf fragt noch einmal
nach. Hilft das nicht, ist der Dienst selbst nicht erreichbar — dann hilft nur,
wer ihn betreibt.

Am unteren Rand der Seite steht klein die Version des Dienstes. Wer dem Betreiber
einen Fehler meldet, nennt sie mit.
