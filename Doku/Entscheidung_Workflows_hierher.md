# Workflows gehören hierher, nicht in jedes Projekt

**Stand: Vorschlag.** Der Befund und die Empfehlung sind belegt; drei Fragen am Ende
muss der Nutzer beantworten, bevor gebaut wird. Nichts davon ist umgesetzt.

## Das Problem

Ein Projekt, das die Skills aus diesem Marketplace nutzt, muss den halben Ablauf selbst
richtig hinschreiben: den Auftragsworkflow, den Label-Wächter, die Label selbst. Steht
dort etwas anders als gedacht, arbeitet die Automatik nach anderen Regeln als die Skills
beschreiben — und niemand merkt es, weil beide Seiten für sich stimmig aussehen.

Das ist dieselbe Begründung, aus der die Skills überhaupt hier liegen und nicht in jedem
Projekt: *„Eine Quelle für alle Projekte; sonst altert dieselbe Regel in jedem Repository
getrennt."* Sie gilt für den Workflow genauso, nur ist sie dort bisher nicht angewandt.

## Was gemessen wurde

`Stoffverteilungsplan/.github/workflows/claude-aufgaben.yml`, rund 300 Zeilen, durchgesehen
auf projektspezifische Nennungen:

| Datei | projektspezifisch |
|---|---|
| `claude-aufgaben.yml` | **zwei Zeilen** — der Verweis auf `CLAUDE.md` und die cp1252-Regel für `Makros/*.bas` |
| `label-waechter.yml` | **nichts** (seit der Kontoname durch die Abfrage der Admin-Berechtigung ersetzt ist) |
| `zuordnung.py`, `modellwahl.py`, `fortschritt.py`, `abschluss.py` | **nichts** |
| `pruefung.yml` | der Aufruf der Projektprüfung und `openpyxl` — der Rest generisch |

Alles Übrige — Vorprüfung, Branchwahl, Modellwahl, Fortschrittskommentar, Rettungsschritt,
Skills-Nachweis, Abschlusskommentar, Sperrliste, Schlussmeldungsschema — gilt für jedes
Projekt gleich. Es liegt nur zufällig in einem.

## Die Entscheidung: ein Repository, kein zweites

Der Nutzer hat drei Wege genannt (Fork, zwei Repositories, eines) und zu einem tendiert.
Diese Empfehlung folgt ihm, aber aus einem eigenen Grund:

**Workflow und Skills sind zwei Hälften eines Vertrags.** Der Workflow reicht dem Modell
Werte an (`vorgang`, `branch`, die Id des Fortschrittskommentars) und verweist im Prompt
auf Abschnitte der Skills; die Skills setzen voraus, dass der Workflow das tut. Liegen sie
in getrennten Repositories, sind sie getrennt versioniert — und die Version, die
auseinanderläuft, ist genau die, an der es weh tut: Der Skill beschreibt einen Ablauf, den
der Workflow nicht mehr fährt.

Dagegen steht ein einziges Argument für zwei Repositories: Wer nur Skills will, bekommt
Workflows mit. Das kostet nichts — ein nicht aufgerufener Workflow tut nichts, und der
Marketplace lädt ohnehin nur, was unter `plugins:` steht.

**Kein Fork.** Ein Fork erbt die Historie und verliert den Bezug: Ab dem Tag gäbe es zwei
Repositories, die beide „die Arbeitsweise" heißen, und niemand könnte sagen, welches gilt.

## Was das Repository dann enthält

```
claude-skills/                          (Name siehe Frage 1)
├─ .claude-plugin/marketplace.json      Skills, wie bisher
├─ plugins/reiser-workflow/             überall geladen
├─ plugins/reiser-lokal/                nur lokal
├─ .github/workflows/
│  ├─ pruefung.yml                      prüft dieses Repository selbst
│  ├─ aufgaben.yml         NEU          on: workflow_call — der Auftragslauf
│  ├─ label-waechter.yml   NEU          on: workflow_call — nimmt fremde Label zurück
│  └─ label-abgleich.yml   NEU          on: workflow_call — legt die Label an
├─ .github/skripte/        NEU          zuordnung.py, modellwahl.py, fortschritt.py,
│                                       abschluss.py — mit ihren Selbsttests
└─ labels.yml              NEU          der Label-Katalog als Daten
```

**Aufrufbarer Workflow (`workflow_call`), keine Composite Action.** Eine Action kann
`permissions`, `concurrency` und `timeout-minutes` des Jobs nicht setzen; genau die tragen
hier Bedeutung (zwei Läufe dürfen nicht denselben Vorgang doppelt bearbeiten, und `actions:
read` ist die Bedingung dafür, dass der Lauf sein eigenes Ergebnis prüfen kann).

Im Projekt bleibt dann dies stehen:

```yaml
on:
  schedule:  [{ cron: "0 */4 * * *" }]
  workflow_dispatch:

jobs:
  aufgaben:
    uses: f-reiser/claude-skills/.github/workflows/aufgaben.yml@reiser-workflow--v1.3.0
    secrets: inherit
    with:
      projektregeln: |
        Die Projektregeln in CLAUDE.md haben Vorrang - insbesondere die
        cp1252-Regel fuer Makros/*.bas.
      pruefbefehl: python Makros/pruefe_alles.py
```

Der Zeitplan bleibt beim Projekt: `on: schedule` wirkt nur in der Datei, die im
Standardbranch des Projekts liegt, und wie oft ein Projekt bearbeitet werden will, ist
seine Sache.

## Die drei Probleme, die der Nutzer benannt hat

### Die Label

Sie werden heute von Hand im Projekt gepflegt — 19 Stück, mit Beschreibung und Farbe. Wer
ein neues Projekt anlegt, legt sie nach oder wundert sich, warum die Automatik nichts tut.
`claude-aufgaben.yml` fängt ein fehlendes Label bereits ab (`|| true`), das heißt: Ein
vergessenes Label ist ein *stiller* Ausfall.

**Vorschlag: `labels.yml` als Datei hier, dazu ein aufrufbarer Workflow, der abgleicht.**
Name, Beschreibung und Farbe stehen einmal; `gh label create --force` legt an oder
aktualisiert. Angestoßen von Hand (`workflow_dispatch`) und bei jedem Push auf `main` im
Projekt. **Nur anlegen und ändern, nie löschen** — ein fremdes Label ist kein Fehler,
sondern ein Label, das dieses Projekt zusätzlich braucht.

Dieselbe Datei speist den Wächter: Welche Label geschützt sind, steht dann nicht mehr in
zwei Listen.

### `label-waechter.yml`

Ist bereits generisch: Seit die Prüfung nicht mehr einen Kontonamen vergleicht, sondern
`repos/:repo/collaborators/:login/permission` abfragt, steht kein Projektbezug mehr darin.
Er muss nur noch hierher verschoben und mit `on: workflow_call` versehen werden. Die Liste
der geschützten Label kommt aus `labels.yml`.

### `pruefung.yml`

Zerfällt sauber in zwei Teile:

- **projektspezifisch** — welche Prüfung läuft (`Makros/pruefe_alles.py`), welche
  Abhängigkeiten sie braucht (`openpyxl`), welche Ebenen nicht automatisierbar sind. Das
  bleibt im Projekt.
- **generisch** — die Selbsttests der Skripte hier, und der Schritt, der das Ergebnis im
  Fortschrittskommentar des Vorgangs vermerkt. Das kommt hierher.

Das Projekt ruft den generischen Teil als zweiten Job auf. Es bleibt bei einem
Prüf-Workflow im Projekt, weil ein Projekt seine Prüfung selbst kennt — nur der Teil, den
alle teilen, wird nicht mehr abgeschrieben.

## Eine Folge, die man nicht übersehen darf

Ab diesem Umbau holt sich ein fremder Workflow **ausführbaren Code** aus diesem
Repository, über einen Tag. Damit gilt hier, was `semver-und-releases` beschreibt: *„Holt
sich irgendwo ein fremder Workflow etwas aus dem Projekt über einen Tag, hängt er an genau
dieser Nummer."*

Konkret ändert sich dreierlei:

1. Der Satz in `README.md`, dieses Repository enthalte *„bewusst keinen ausführbaren Code,
   den ein Projekt-Workflow über einen Tag holen müsste"*, wird **falsch** und muss weg.
2. Ein Release wird sicherheitsrelevant: Wer den Tag verschieben könnte, führte Code in
   fremden Projekten aus. Tags werden ohnehin nie verschoben — ab jetzt ist das keine
   Ordnungsfrage mehr.
3. Die aufrufenden Projekte müssen beim Update ihre Referenz nachziehen. Das gehört auf
   die Release-Checkliste, sonst fahren sie stillschweigend die alte Fassung weiter.

Ein `@main` statt eines Tags würde das umgehen und ist trotzdem falsch: Dann ändert ein
Merge hier sofort das Verhalten aller Projekte, ohne Release und ohne dass es jemand
bemerkt.

## Was offen ist

Siehe die Fragen am Ende des Chat-Laufs, in dem dieses Dokument entstanden ist:
Umbenennung des Repositories, Versionsverriegelung der Plugins, Umgang mit dem
Release-Namen.
