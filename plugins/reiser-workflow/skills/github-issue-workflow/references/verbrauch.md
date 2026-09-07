# Das Kassenbuch der unbeaufsichtigten Läufe

Wie das Budget technisch zustande kommt. Die **Schwellen** stehen in `scripts/verbrauch.py`
und werden über `verbrauch.py entscheidung` abgefragt; hier steht nur, woher die Zahlen
kommen, die dort hineingehen.

## Warum überhaupt ein eigenes Kassenbuch

Das verbleibende Limit eines Claude-Abonnements ist **nicht abfragbar**. Es gibt dafür
keinen Endpunkt: die Usage-and-Cost- und Spend-Limits-APIs gelten für Organisationen mit
API-Schlüssel, nicht für ein Pro-/Max-Abonnement, und `claude-code-action` gibt keinen
Verbrauch als Output heraus. Ein Feature-Request dafür ist offen
([claude-code#44328](https://github.com/anthropics/claude-code/issues/44328)).

Was **doch** geht: den eigenen Verbrauch mitschreiben. Damit ist der Zähler bekannt, auch
wenn der Nenner es nicht ist — also setzt der Nutzer den Nenner selbst. Das ist nicht der
Notbehelf, für den es aussieht, sondern die bessere Größe: Er entscheidet damit, welchen
Teil seines Limits die Automatik überhaupt anfassen darf, statt sie bis zur Wand fahren
zu lassen.

## Woher die Zahl kommt

`claude-code-action` gibt `execution_file` aus — den Ereignis-Log des Laufs. Der letzte
Eintrag mit `type == "result"` trägt den Verbrauch:

```json
{"type": "result", "num_turns": 12, "duration_ms": 184000, "total_cost_usd": 0.42,
 "usage": {"input_tokens": 900, "output_tokens": 15400,
           "cache_creation_input_tokens": 62000, "cache_read_input_tokens": 1840000}}
```

Der Log ist je nach Fassung ein JSON-Array oder eine Zeile-pro-Ereignis-Datei — das steht
in keiner Dokumentation, es ist beobachtet. `verbrauch.py` bedient beides.

## Rollende Fenster statt echter Zurücksetzungen

Wann Anthropic die Fenster zurücksetzt, ist nicht dokumentiert und aus den Daten nicht
ableitbar — lokal beobachtete Rücksprünge lagen 3,6 Tage auseinander, obwohl die App von
einer Woche spricht.

Deshalb wird **gar nicht erst versucht**, den Termin nachzubilden. Das Kassenbuch summiert
über ein rollendes Fenster: alles aus den letzten 5 Stunden, alles aus den letzten 7 Tagen.
Ein rollendes Fenster ist immer mindestens so streng wie das echte und braucht kein Wissen
über dessen Grenzen. Es kostet gelegentlich einen ausgelassenen Durchgang; das ist der
Preis, und er ist niedriger als der umgekehrte Fehler.

## Womit gemessen wird

Vorrangig `total_cost_usd`, weil das die Gewichtung der Token-Arten schon enthält — ein
gelesener Cache-Token kostet einen Bruchteil eines Ausgabe-Tokens, und eine ungewichtete
Token-Summe würde die Läufe deshalb um Größenordnungen falsch bewerten.

Ist das Feld `0` (kommt vor, wenn über ein Abonnement statt über einen API-Schlüssel
abgerechnet wird), gilt ersatzweise `output_tokens + input_tokens +
cache_creation_input_tokens`. Welche Größe ein Eintrag trägt, steht im Eintrag — sonst
summiert man später Äpfel und Birnen.

**Die ersten Wochen sind Kalibrierung.** Das Budget ist eine gesetzte Zahl, kein
gemessener Anteil am echten Limit. Der Nutzer vergleicht, was das Kassenbuch für eine
Woche ausweist, mit dem, was ihm die App anzeigt, und zieht das Budget nach. Bis dahin
lieber zu klein ansetzen.

## Wo es liegt

Als Workflow-Artefakt, nicht als Datei im Repository: ein Kassenbuch, das bei jedem Lauf
einen Commit erzeugt, macht die Historie unbrauchbar. Jeder Lauf lädt das jüngste
Artefakt, hängt seinen Eintrag an, wirft Einträge älter als 8 Tage weg und lädt es wieder
hoch — ein Download, ein Upload, unabhängig davon, wie viele Läufe im Fenster liegen.

`actions/download-artifact` holt nur Artefakte **desselben** Laufs; gebraucht wird das des
vorherigen. Deshalb über `gh`:

```yaml
      - uses: actions/checkout@v6
        with:
          repository: f-reiser/claude-skills
          ref: reiser-workflow--v0.3.0
          path: .skills

      # Der erste Lauf findet nichts, das ist kein Fehler.
      - name: Kassenbuch holen
        continue-on-error: true
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          id=$(gh run list --workflow einarbeiten.yml --status completed \
                 --limit 1 --json databaseId --jq '.[0].databaseId')
          [ -n "$id" ] && gh run download "$id" --name verbrauch --dir .

      - name: Budget melden
        run: $SKRIPT bericht | tee -a "$GITHUB_STEP_SUMMARY"
        env:
          SKRIPT: python .skills/plugins/reiser-workflow/skills/github-issue-workflow/scripts/verbrauch.py

      # nach dem Claude-Schritt, immer - auch wenn er scheiterte
      - name: Kassenbuch fortschreiben
        if: always()
        run: >
          python .skills/plugins/reiser-workflow/skills/github-issue-workflow/scripts/verbrauch.py
          fortschreiben "${{ steps.claude.outputs.execution_file }}"
      - uses: actions/upload-artifact@v5
        if: always()
        with:
          name: verbrauch
          path: verbrauch.json
          retention-days: 8
```

`gh run download` braucht `actions: read`, das der Workflow ohnehin hat. Schlägt der
Schritt fehl, beginnt das Kassenbuch neu, und es gilt die Regel für „kein Kassenbuch"
aus `SKILL.md`.

**Ein beweglicher Branch stünde hier falsch:** Der Workflow führt das Skript aus, und was
ausgeführt wird, gehört festgenagelt — sonst ändert ein fremder Push, was auf dem Runner
läuft. Der Preis dafür ist, dass der Tag bei jedem Release nachgezogen werden muss; er
steht deshalb auf der Release-Liste im README.

## Format

```json
{"eintraege": [
  {"t": 1757217120, "usd": 0.42, "token": 78300,
   "gemessen": true, "vorgaenge": 2, "lauf": "1234567890"}
]}
```

`t` sind Sekunden seit 1970 — für einen Vergleich reicht das, und es spart das
Zeitzonenproblem, das ein ISO-String mitbrächte.

`vorgaenge` ist die Zahl der in diesem Lauf abgearbeiteten Issues oder Pull Requests —
daraus entsteht der Schnitt pro Vorgang, mit dem im nächsten Lauf geschätzt wird, ob noch
einer hineinpasst. Claude schreibt sie am Ende des Laufs in `vorgaenge.txt`; fehlt die
Datei, gilt 1.

`gemessen: false` heißt: der Lauf ist eingetragen, aber sein Verbrauch stand nicht im Log
— abgestürzt, abgebrochen, Datei leer.

## Selbsttest

```bash
python scripts/verbrauch.py --selbsttest
python scripts/verbrauch_mutation.py
```

Beide melden Anzahl und Ergebnis selbst. Wozu der Mutationstest da ist:
`test-driven-development`.
