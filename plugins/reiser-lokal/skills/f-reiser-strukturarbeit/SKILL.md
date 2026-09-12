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
