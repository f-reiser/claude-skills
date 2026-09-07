# Typen, Label, Priorität

## Issue-Typen

| Typ | wofür |
|---|---|
| **Bug** | Fehlverhalten |
| **Feature** | neue Anforderung |
| **Task** | alles andere, etwa Dokumentation |

Gesetzt von Claude wie von Menschen. Eigene Issues bekommen den Typ immer selbst; bei
fremden Issues ohne Typ setzt Claude ihn, wenn die Einordnung eindeutig ist, und meldet
nur die Zweifelsfälle.

## Label

Die Schreibweise ist bindend, `gh label list` zeigt die gültige Fassung.

**Label gelten für Issues und für Pull Requests gleichermaßen** — ein Pull Request mit
`Einarbeiten` wird behandelt wie ein Issue mit `Einarbeiten`.

| Label | Bedeutung | setzt | entfernt |
|---|---|---|---|
| `Dokumentation` | es geht um Dokumentation jeder Art | Claude, Nutzer | beide |
| `Duplicate` | dupliziert ein anderes Issue | Claude, Nutzer | beide |
| `Einarbeiten` | durchgesehen, kann umgesetzt werden | **nur Nutzer** | beide |
| `Entscheidung` | der Nutzer muss zwischen Alternativen wählen | **nur Claude** | beide |
| `Gegenlese` | Befund der fremden Gegenlese (Prüfebene 9) | **nur Claude** | beide |
| `Pruefluecke` | eine Prüfung kann strukturell nicht anschlagen | **nur Claude** | beide |
| `Rückfrage` | Nachschärfen nötig, keine echte Wahl | **nur Claude** | beide |
| `Untersuche` | Bug soll nachgestellt und analysiert werden | **nur Nutzer** | Claude nach der Analyse |
| `WontDone` | wird nicht umgesetzt, braucht Begründung als Kommentar | **nur Nutzer** | Nutzer |

Weitere Label können hinzukommen. Ein unbekanntes Label ist kein Grund, ein Issue zu
überspringen — aber ein Grund nachzufragen, wenn es die Behandlung ändern könnte.

### Rückfrage oder Entscheidung?

**Entscheidung**, wenn zwei oder mehr echte Alternativen zur Wahl stehen und der Nutzer
eine auswählen muss. **Rückfrage**, wenn die Richtung feststeht und nur nachgeschärft
werden muss.

### Duplicate richtig gesetzt

Ist `Duplicate` gesetzt, **muss** das abdeckende Issue in den Relationships stehen — dort
nur die Nummer. Ein Kommentar kommt dazu, wenn eine Erklärung nötig ist, warum es ein
Duplikat ist.

Fällt dir ein `Duplicate`-Issue ohne diesen Verweis auf: **warnen**. Ohne den Verweis ist
das Label wertlos, weil niemand findet, wohin die Sache verschoben wurde.

## Priorität

`Urgent` · `High` · `Medium` · `Low` — **ohne Angabe gilt Medium.**

Höhere Priorität wird bevorzugt, aber **Abhängigkeiten schlagen Priorität**: Ein
dringendes Issue, das auf einem anderen aufbaut, wartet trotzdem. Bei gleicher Priorität
entscheidet das Alter (älter zuerst).

`Low` wird im Vier-Stunden-Lauf nicht jedes Mal berücksichtigt, sondern **nur nachts
zwischen 0:00 und 4:00** und nur bei ausreichendem Limit.

Priorität ist kein Feld des Issues selbst, sondern ein Feld im zugehörigen Project. Das
Lesen braucht den Scope `read:project`; fehlt er oder gibt es kein Project, gilt Medium.
