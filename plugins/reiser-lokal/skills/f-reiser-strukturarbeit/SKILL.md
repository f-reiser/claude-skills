---
name: f-reiser-strukturarbeit
description: >
  NUR relevant für Softwareprojekte der GitHub-Organisation f-reiser (aktuell:
  Stoffverteilungsplan, claude-skills) und NUR in einer Sitzung am eigenen Rechner — bei
  jedem Projekt ohne Bezug zu dieser Organisation ignorieren. Für f-reiser-Projekte:
  Kontext für Strukturaufgaben, die direkt im Chat statt über den Issue-Workflow erledigt
  werden — Skillset erweitern oder korrigieren, projektübergreifende Workflows anpassen,
  Projektstruktur ändern. Ergänzt die Skills aus reiser-workflow um das, was dort nicht
  hingehört, weil es nur lokal gilt: wie sich eine Chat-Sitzung von einer Sitzung in
  GitHub Actions unterscheidet, welches der angemeldeten GitHub-Konten wofür zuständig
  ist, und welche Befehle ein Release auslösen. Nutze diesen Skill, sobald in einem
  f-reiser-Projekt eine Strukturaufgabe ansteht statt einer Fachaufgabe an einem
  einzelnen Repository, wenn zu klären ist, welches Konto oder Repository gemeint ist,
  und bei jedem Release-Befehl des Nutzers.
---

# Strukturarbeit — nur Organisation f-reiser, nur lokal

## Zwei Schranken, bevor irgendetwas hier gilt

**1. Nur in einer lokalen Sitzung.** Dieser Skill steckt im Plugin `reiser-lokal`. Ein
unbeaufsichtigter Lauf lädt nur `reiser-workflow` und sieht ihn deshalb gar nicht —
diese Schranke hält der Workflow, nicht dein Urteil. Findest du ihn trotzdem in einer
Sitzung vor, in der `$GITHUB_ACTIONS` gesetzt ist, ist das ein Fehler in der
Workflow-Datei: melden, und nichts aus diesem Skill anwenden.

Warum das zwei Plugins sind und keine zwei Repositories: `README.md` im Wurzelverzeichnis.

**2. Nur Organisation f-reiser.** Bei jedem anderen Projekt — auch bei anderen eigenen
Repositories außerhalb dieser Organisation — sagt dieser Skill nichts Sinnvolles. Vor der
Anwendung kurz prüfen: Läuft die Arbeit in einem der unten genannten Repositories, oder an
etwas, das erkennbar dafür entstehen soll?

## Wofür dieser Skill sonst da ist

Für Aufgaben, die keine Fachaufgabe an EINEM Projekt sind, sondern die Struktur betreffen,
die mehrere f-reiser-Projekte teilen: das Skillset erweitern oder korrigieren, Workflows
projektübergreifend anpassen, eine Projektstruktur ändern. Solche Aufgaben laufen bewusst
**direkt über den Chat**, nicht über den Issue-Workflow mit Label „Einarbeiten"
(`github-issue-workflow`) — das geht schneller, und es ist nicht die Art Aufgabe, die an
ein einzelnes Repository gebunden ist.

**Der grundsätzliche Workflow ändert sich dadurch nicht.** Sobald ein Branch existiert,
gilt exakt das, was `reiser-workflow:git-branch-strategie` und die übrigen Skills aus
`reiser-workflow` beschreiben — Feature-Branch, Rebase, aufgeräumte Historie, Pull
Request, Merge nur durch den Nutzer. **Nur der Einstiegspunkt ist anders:** keine
Issue-Erstellung, keine Label-Steuerung — die Anforderung steht im Chat, nicht im
Issue-Text. Ein Branchname ohne Issue-Nummer ist hier deshalb normal (z. B.
`entferne-kontonamen-git-branch-strategie` statt `issue-<nr>-<slug>`).

Dieser Skill dupliziert `reiser-workflow` nicht. Für Rebase-Regeln, PR-Konventionen,
Gegenlese und den Release-*Ablauf* gelten unverändert die dortigen Skills; bei Bedarf dort
nachladen, nicht hier wiederholen.

## Zwei Einstiegspunkte, eine Organisation

| | Chat-Sitzung (Claude Code/App, wie diese hier) | Sitzung über claude-api/GitHub Actions |
|---|---|---|
| ausgelöst durch | Chat mit dem Nutzer | Vorgang mit Auftragslabel |
| GitHub-Zugriff über | `gh` CLI mit den angemeldeten Konten | eigenes Token der Aktion |
| Zugriff auf Bot- oder Admin-Konto | ja | **nein** |
| lädt dieses Plugin | ja | **nein** |

Das Umschaltverfahren aus `git-branch-strategie`
(`GH_TOKEN=$(gh auth token --user …)`) setzt voraus, dass beide Konten bei `gh` angemeldet
sind. Das ist nur auf der Maschine der Fall, auf der du selbst arbeitest.

## Welches Konto wofür — ermitteln, nicht nachschlagen

Die Kontennamen stehen **absichtlich nirgends im Repository**: es ist öffentlich, und eine
abgeschriebene Liste altert. Beides erledigt eine Abfrage:

```bash
gh auth status                                  # welche Konten sind angemeldet?
gh api "repos/$(gh repo view --json nameWithOwner --jq .nameWithOwner)/collaborators/<login>/permission" --jq .permission
```

| Antwort | Rolle | zuständig für |
|---|---|---|
| `admin` | Admin-Konto | Repository anlegen, Branch-Schutzregeln, Collaborators, Label, Issue-Typen — **vorher ansprechen** |
| `write` | Bot-Konto | laufende Arbeit: Commits, Branches, Pull Requests, Issues, Releases |

Das ist die konkrete Ausprägung von `git-branch-strategie` → „Mit welchem Konto": dort
steht der Mechanismus mit den Platzhaltern `<Bot-Konto>` / `<Admin-Konto>`, hier steht,
wie du sie füllst.

Ergibt die Abfrage nicht genau ein `admin` und ein `write`, ist die Annahme dieses Skills
verletzt — dann fragen statt raten.

## Repositories in der Organisation

Organisation: **f-reiser**. Aktuelle Liste immer über

```bash
gh repo list f-reiser --limit 100
```

- **Stoffverteilungsplan** — das laufende Projekt, an dem alle Strukturen (Skills,
  Workflows) entstehen und erprobt werden, bevor sie verallgemeinert werden.
- **claude-skills** — verwaltet die Plugins `reiser-workflow` (überall geladen) und
  `reiser-lokal` (nur lokal, dieses hier). Öffentliches Repository — deshalb keine
  Kontennamen, Schulnamen oder sonstigen personenbezogenen Daten hineinschreiben (siehe
  `repo-hygiene`).

## Wenn eine Strukturaufgabe die Skills selbst betrifft

Das geht ins Repository `claude-skills`, nach dem üblichen Workflow (Branch, Pull
Request, Merge durch den Nutzer) — auch eine Änderung an *diesem* Skill hier, denn er
liegt jetzt selbst dort. Welches der beiden Plugins zuständig ist, entscheidet eine
Frage: **Dürfte ein unbeaufsichtigter Lauf das lesen und danach handeln?**

- ja → `reiser-workflow`
- nein, das gilt nur am eigenen Rechner → `reiser-lokal`

## Release-Befehle

Der Ablauf eines Releases steht in `reiser-workflow:semver-und-releases` — **welche Sätze
des Nutzers eines auslösen, steht nur hier.** Ein unbeaufsichtigter Lauf baut keine
Releases; eine Befehlsliste hätte dort nichts zu suchen und wäre eine Angriffsfläche mehr.

### Zwei Begriffe

**Versionsnummer** — `MAJOR.MINOR.PATCH`. Wo sie im Projekt steht: `semver-und-releases` →
„Wo die Version steht".

**Release-Name** — der Namensteil vor der Nummer, im Tag `<name>--v<version>`. Er ist
**optional**: ist keiner gesetzt, heißt der Tag schlicht `v<version>` und das Release trägt
nur die Nummer. Welcher gerade gilt, verrät `git tag --list` und die Datei, die ihn führt
(in `claude-skills` sind das die Plugin-Namen in `plugin.json` und `marketplace.json`).

### Ein Release auslösen

Alle Formen sind gleichwertig — „Erstelle X", „X erstellen", teils „X releasen".

| Befehl | was passiert |
|---|---|
| **Erstelle Release** | Release mit der Nummer, die **aktuell in den Dateien steht**. Nicht hochzählen. |
| **Erstelle Minor Release** | MINOR + 1, PATCH auf 0, dann Release. |
| **Erstelle Fix Release** · **Fix releasen** | PATCH + 1, MINOR unverändert, dann Release. |
| **Erstelle Release 1.2.3** · **1.2.3 releasen** | genau diese Nummer, ohne Ableitung. |
| **Erstelle Release reiser-workflow 1.2.3** | benanntes Release: Name **und** Nummer. |

Beim benannten Release **zuerst prüfen, ob sich der Name gegenüber dem vorigen Release
geändert hat** (`git tag --list`). Hat er sich geändert, wird er vor dem Release in *allen*
Dateien nachgezogen, die ihn führen — nicht nur dort, wo er zufällig auffällt.

Ohne Nummer im Befehl gilt die Ableitung aus `semver-und-releases` → „Welche Stelle
steigt". Trägt sie nicht, wird nichts getan und gefragt — auch das steht dort.

### Nur vorbereiten, noch nicht veröffentlichen

Diese Befehle ändern **nur die Dateien**. Kein Tag, kein Release.

| Befehl | was passiert |
|---|---|
| **Nächstes Release 1.2.3** | Versionsnummer auf 1.2.3 setzen. |
| **Nächstes Release reiser-workflow** | Release-Namen auf `reiser-workflow` setzen. |
| **Nächstes Release reiser-workflow 1.2.3** | beides. |

### Die Auflistung auf Verlangen

Fragt der Nutzer **„Wie kann ich releasen?"**, gib die beiden Tabellen oben wieder — jeden
Befehl mit dem, was du dabei tun würdest, und dazu die drei Punkte: dass ohne Nummer
abgeleitet wird, dass MAJOR immer bei ihm liegt, und was aktuell in den Dateien steht
(Name und Nummer). Kein Release, keine Änderung — nur die Antwort.

### Die eine Ausnahme von „gemergt wird nur vom Nutzer"

Ein Pull Request, der **ausschließlich** Versionsnummern und/oder den Release-Namen ändert,
darf **selbst gemergt** werden. Diese Erlaubnis gilt für genau diese Art Pull Request und
für keine andere — sie ist keine Lockerung von `git-branch-strategie`, sondern eine eng
umrissene Ausnahme davon.

Die Grenze ist wörtlich zu nehmen. Vor dem Merge nachsehen, nicht annehmen:

```bash
gh pr diff <nr>
```

Steht darin **irgendetwas** außer geänderten Versionsnummern und Namen — eine
Doku-Anpassung, ein Verweis, ein nachgezogener Kommentar, eine Zeile in der Prüfung —, ist
die Ausnahme verbraucht und es gilt wieder: **der Nutzer mergt.** Im Zweifel nicht mergen;
ein wartender Pull Request kostet nichts, ein selbst gemergter zu viel Inhalt lässt sich
nicht zurücknehmen.

**Kam der Befehl aus der Spalte „Ein Release auslösen"**, folgt nach diesem Merge
unmittelbar das Release nach `semver-und-releases`. Kam er aus „Nur vorbereiten", endet es
hier.

### Was in diesem Repository dazukommt

`claude-skills` veröffentlicht **zwei** Plugins unter derselben Nummer (`README.md` →
„Versionierung"). Ein Release heißt hier deshalb: vier Stellen ziehen, zwei Tags setzen,
**ein** GitHub-Release. Und „Release-Name" ist hier nicht eindeutig — es gibt zwei
Plugin-Namen. Nennt ein Befehl einen Namen, der nach einer Umbenennung aussieht, ist das
eine Rückfrage wert statt eines Ratens.
