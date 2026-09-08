---
name: fremde-gegenlese
description: >
  Lässt Tests und weitreichende Auslegungen von Anforderungen durch einen unabhängigen
  Agenten gegenprüfen, der weder den Code noch die eigenen Überlegungen kennt — er legt die
  Anforderung selbst aus und meldet nur, statt zu ändern. Deckt Interpretationsfehler und
  wiederholte falsche Annahmen auf, die kein eigener Test findet, weil Test und Code aus
  derselben Auslegung stammen. Nutze diesen Skill immer, wenn ein Test, ein Check oder eine
  Prüfebene neu entsteht oder umgebaut wird; bevor ein Pull Request herausgeht, der mehr als
  eine Funktion berührt; wenn eine Anforderung mehrdeutig war und du dich für eine Lesart
  entschieden hast; nach jedem gemeldeten Fehler, den die bestehenden Tests nicht gefunden
  haben; und wenn der Nutzer nach Gegenlese, Vier-Augen-Prinzip, externer Prüfung oder einem
  zweiten Agenten fragt. Gilt für jedes Softwareprojekt.
---

# Fremde Gegenlese

Die Anforderung des Nutzers, im Wortlaut:

> Sämtliche Tests und sämtliche weitreichenden Interpretationen von Anforderungen sollen
> durch einen externen Agenten nochmal gegengeprüft werden, um Interpretationsfehler und
> wiederholte falsche Annahmen aufzudecken.

## Wozu

Wer die Anforderung liest, den Code schreibt und den Test schreibt, legt dreimal gleich
aus. Der Test ist dann grün und der Code trotzdem falsch — der Test hat denselben blinden
Fleck. Eigene Tests prüfen, ob der Code zu **seiner eigenen Auslegung** passt. Die
Gegenlese prüft die Auslegung.

Belegt, nicht vermutet:

- Ein Check „keine leeren Zeilen am Ende" meldete **ok**, während 35 dastanden. Er suchte
  ab der letzten Zeile mit Inhalt nach oben — die Zeilen lagen darunter. Genau die
  Blickrichtung, aus der auch der Fehler entstanden war.
- Beim ersten Einsatz fanden zwei unabhängige Agenten **fünf bestätigte Fehler**, die
  durch sämtliche bestehenden Prüfungen gerutscht waren.
- Ein Agent, der prüfen sollte, ob alle personenbezogenen Daten aus einem Repository
  entfernt wurden, fand acht übersehene Stellen — nachdem die eigene Prüfung „sauber"
  gemeldet hatte.

## Wann

| Anlass | |
|---|---|
| Ein Test, Check oder eine Prüfebene entsteht oder wird umgebaut | **immer** — der Test ist dann selbst der Prüfgegenstand |
| Eine Anforderung war mehrdeutig und du hast dich für eine Lesart entschieden | **immer** |
| Ein Pull Request berührt mehr als eine Funktion | **immer**, vor dem Erstellen |
| Ein gemeldeter Fehler, den keine bestehende Prüfung gefunden hat | **immer**, mit der Zusatzfrage: *welche Prüfung hätte das finden müssen, und warum hat sie es nicht?* |
| Eine Zusage, deren Bruch nicht rückholbar ist (veröffentlichte Daten, gelöschte Historie, ausgelieferte Datei) | **immer**, und mit zwei Agenten |
| Einzeiler, Tippfehler, reine Textänderung | nein |

**Sie fällt nicht aus, weil die Zeit knapp ist.** Das ist der einzige Grund, aus dem sie
je ausgefallen ist, und jedes Mal stand hinterher ein Befund im Raum, den sie gefunden
hätte. Wenn du sie nicht durchführst, sag das ausdrücklich und nenne den Grund — nicht
stillschweigend weglassen.

## Die fünf Regeln des Auftrags

**1. Die Anforderung im Wortlaut mitgeben — nicht als eigene Zusammenfassung.**
Eine Zusammenfassung trägt die eigene Auslegung schon in sich. Genau die soll geprüft
werden. Also die Originaldatei, den Issue-Text, die Nachricht des Nutzers.

**2. Eigene Begründungen weglassen.** Kein „das ist so, weil …". Der fremde Agent soll das
Verhalten aus dem Code ableiten und selbst beurteilen, ob es zur Anforderung passt.

**3. Nur melden lassen, nichts ändern.** Ein Agent, der repariert, verschiebt den blinden
Fleck bloß um eine Instanz weiter. Das Ergebnis ist ein Befund, über den ein Mensch
entscheidet.

**4. Sicherheitsgrad verlangen.** Ohne ihn kommen zwanzig gleich laute Befunde zurück,
und das Sortieren kostet mehr als die Prüfung gespart hat.

**5. Jeden Befund selbst nachprüfen, bevor du ihn weitergibst.** Beim ersten Einsatz waren
fünf von neun echt. Ungeprüft weitergereichte Befunde sind Rauschen — und sie beschädigen
das Vertrauen in die nächste Gegenlese.

Zwei Agenten sind besser als einer; sie überschneiden sich weniger, als man erwartet.

## Der Auftragstext

Wörtlich verwendbar, `<…>` ersetzen:

```
Du prüfst fremden Code gegen eine fremde Anforderung. Du kennst weder den Autor
noch seine Überlegungen, und das ist Absicht.

ANFORDERUNG
    <die Anforderung im Original — Datei, Issue-Text, Nachricht>
    Lege sie selbst aus. Frage nicht nach, was gemeint ist; wenn eine Stelle
    mehrdeutig ist, ist genau das ein Befund.

CODE
    <die betroffenen Dateien und die zugehörigen Tests>

AUFTRAG
    Prüfe, ob der Code und seine Tests die Anforderung erfüllen. Achte besonders auf:
    - Tests, die eine Größe mit derselben Funktion nachprüfen, mit der der Code sie
      bestimmt — solche Tests bestätigen nur, dass der Code zu sich selbst passt.
    - Prüfungen, die aus struktureller Ursache gar nicht anschlagen können.
    - Zusagen der Anforderung, für die es keine Prüfung gibt.

    ÄNDERE NICHTS. Melde.

FORM JEDES BEFUNDS
    Titel:            eine Zeile
    Stelle:           Datei und Funktion
    Was ich sehe:     das beobachtete Verhalten, ohne Deutung
    Warum das ein Problem ist: Bezug auf die Anforderung, mit Zitat
    Sicherheitsgrad:  sicher | vermutlich | unklar
                      sicher     = im Code nachweisbar
                      vermutlich = plausibel, aber vom Laufzeitverhalten abhängig
                      unklar     = die Anforderung gibt es nicht eindeutig her
```

Bei einer Suchaufgabe („ist wirklich alles entfernt?") tritt an die Stelle der drei
Aufzählungspunkte, wonach zu suchen ist — und die Aufforderung, **selbst zu bestimmen, wo
gesucht werden muss**. Der teuerste Fehler dieser Art war eine Prüfung, die alle Textteile
einer Datei durchsuchte, aber nicht den kompilierten Anteil; dort standen die Daten dann.

## Wohin mit dem Ergebnis

Jeder **bestätigte** Befund wird ein Issue mit dem Label `GegenleseBefund`
(`github-issue-workflow`), kein stiller Fix im laufenden Branch — sonst weiß hinterher
niemand, dass die Gegenlese etwas gefunden hat. Ein Befund über eine Prüfung, die
strukturell nicht anschlagen kann, trägt zusätzlich `Pruefluecke`.

Jeder **nicht bestätigte** Befund wird mit einer Zeile Begründung verworfen, aber sichtbar:
als Notiz im Pull Request oder im Issue. Still verworfene Befunde kommen bei der nächsten
Gegenlese wieder, und dann prüfst du sie ein zweites Mal.

## Wenn der Vorgang das Label `Gegenlese` trägt

Damit fordert der Nutzer eine Gegenlese für **genau diesen** Vorgang an, zusätzlich zu
allem, was ohnehin fällig wäre. Sie läuft, wenn die Arbeit fertig ist — nicht vorher.

Der Endzustand ist die eigentliche Zusage, und er ist vollständig festgelegt:

| | |
|---|---|
| `Gegenlese` | **immer** entfernt |
| `GegenleseBefund` | gesetzt, wenn es bestätigte Befunde gab — sonst ausdrücklich nicht |
| Kommentar im Issue | **immer** |

**Gab es Befunde:** jeder bestätigte als Kommentar **im Issue**, mit Stelle und
Sicherheitsgrad. Hier nicht als neues Issue — der Nutzer will sie dort sehen, wo er sie
angefordert hat.

**Gab es keine:** ein Kommentar mit einer **stichpunktartigen Liste dessen, was geprüft
wurde**. Ohne sie weiß später niemand, ob die Prüfung schon gelaufen ist, und sie läuft
ein zweites Mal — teuer und ohne Ertrag. „Keine Befunde" allein leistet das nicht; die
Liste ist der eigentliche Wert des Durchgangs.

Bleibt `Gegenlese` stehen, gilt die Arbeit als **nicht fertig**.

## Nicht dasselbe wie ein Code-Review

Ein Review fragt: *Ist der Code gut geschrieben?* Die Gegenlese fragt: *Ist er die
richtige Auslegung der Anforderung?* Daher Regel 2.
