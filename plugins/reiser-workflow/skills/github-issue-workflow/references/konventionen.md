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
| `Entscheidung` | zwei oder mehr echte Alternativen, der Nutzer muss eine wählen | **nur Claude** | beide |
| `Gegenlese` | für diesen Vorgang ist nach der Arbeit eine fremde Gegenlese zu fahren | **nur Nutzer** | **nur Claude**, wenn sie gelaufen ist |
| `GegenleseBefund` | die Gegenlese hat einen bestätigten Befund ergeben | **nur Claude** | beide |
| `Pruefluecke` | eine Prüfung kann strukturell nicht anschlagen | **nur Claude** | beide |
| `Rückfrage` | die Richtung steht fest, es fehlt nur die Schärfe | **nur Claude** | beide |
| `Untersuche` | Bug nachstellen; Verfahren in `SKILL.md`, „Bugs untersuchen" | **nur Nutzer** | Claude nach der Analyse |
| `WontDone` | wird nicht umgesetzt, braucht Begründung als Kommentar | **nur Nutzer** | Nutzer |

Weitere Label können hinzukommen. Ein unbekanntes Label ist kein Grund, ein Issue zu
überspringen — aber ein Grund nachzufragen, wenn es die Behandlung ändern könnte.

### Steuerlabel: Modell, Version, Aufwand

Sie sagen nichts über den Vorgang, sondern über den **Lauf**, der ihn abarbeitet — was
er kosten darf. Alle drei Gruppen: **nur Nutzer**, entfernen dürfen beide.

| Gruppe | Label |
|---|---|
| Modell | `Opus` · `Sonnet` |
| Version | `4` · `5` |
| Aufwand | `niedrig` · `mittel` · `hoch` · `extra hoch` · `maximal` |

**Über die Gruppen hinweg kombinierbar, innerhalb einer Gruppe nicht.** `Opus` + `4` +
`niedrig` ist eine gültige Vorgabe; `Opus` + `Sonnet` ist ein Widerspruch.

Ohne Label läuft der Durchgang mit einem günstigen Standard. Ohne Versionslabel gilt die
neueste Fassung des gewählten Modells, ohne Aufwandslabel `hoch`.

**Du wertest diese Label nicht aus.** Wenn du liest, ist die Wahl längst getroffen — sie
muss feststehen, bevor du startest, denn ein laufender Lauf kann sein Modell nicht mehr
wechseln. Der Workflow tut das (im Stoffverteilungsplan `.github/modellwahl.py`). Diese
Tabelle steht hier, damit du weißt, was der Nutzer damit steuert und was du ihm sagen
kannst, wenn er fragt — nicht als Handlungsanweisung.

### Duplicate richtig gesetzt

Ist `Duplicate` gesetzt, **muss** das abdeckende Issue in den Relationships stehen — dort
nur die Nummer. Ein Kommentar kommt dazu, wenn eine Erklärung nötig ist, warum es ein
Duplikat ist.

Fällt dir ein `Duplicate`-Issue ohne diesen Verweis auf: **warnen**. Ohne den Verweis ist
das Label wertlos, weil niemand findet, wohin die Sache verschoben wurde.

## Priorität

`Urgent` · `High` · `Medium` · `Low` — **ohne Angabe gilt Medium.**

Priorität ist kein Feld des Issues selbst, sondern ein Feld im zugehörigen Project. Das
Lesen braucht den Scope `read:project`; fehlt er oder gibt es kein Project, gilt Medium.

Wie Priorität, Abhängigkeit und Alter die Reihenfolge bestimmen, steht in `SKILL.md`,
Abschnitt „Welches Issue zuerst".

