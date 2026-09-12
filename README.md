# reiser-skills

Die Arbeitsweise für alle Softwareprojekte, als Claude-Plugin. Eine Quelle, von allen
Projekten referenziert — damit dieselbe Regel nicht in fünf Repositories getrennt altert.

## Was drin ist

| Skill | wofür |
|---|---|
| `github-issue-workflow` | Issues abarbeiten: Auswahl, Ablauf, Label, Typen, Prioritäten, Regeln für unbeaufsichtigte Läufe |
| `git-branch-strategie` | Feature-Branches, Rebase, Merge-Konflikte, Pull Requests, GitHub-Konten |
| `test-driven-development` | erst der rote Test, dann der Code; Mutationstest für bestehende Suiten |
| `fremde-gegenlese` | Tests und Auslegungen durch einen unabhängigen Agenten prüfen lassen |
| `semver-und-releases` | Versionsnummern, Tags, GitHub-Releases |
| `erklaeren-mit-mass` | wie viel Erklärung ein Text verdient |
| `repo-hygiene` | was in ein Repository gehört und was nicht |

## Verwendung

**In einem Projekt-Workflow:**

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    plugin_marketplaces: "https://github.com/f-reiser/claude-skills.git"
    plugins: "reiser-workflow@reiser-skills"
    prompt: "/github-issue-workflow"
```

**Lokal in Claude Code:**

```bash
claude plugin marketplace add f-reiser/claude-skills
claude plugin install reiser-workflow@reiser-skills
```

Beides liest **dasselbe Repository**. Deshalb gibt es diese Skills nicht zusätzlich als
Konto-Skills: Zwei Fassungen bedeuten zwangsläufig, dass eine davon veraltet ist, und man
merkt es erst, wenn die Automatik nach anderen Regeln arbeitet als die Sitzung am Rechner.
Eine Regel ändert man hier, über einen Pull Request.

Was der Marketplace nicht abdeckt: claude.ai im Browser und auf dem Handy. Skills, die
dort gebraucht werden, bleiben Konto-Skills — sie haben mit Softwareprojekten
üblicherweise nichts zu tun.

## Was hier noch hinkommt

Die Workflows, mit denen ein Projekt diese Skills überhaupt anwendet, liegen heute in
jedem Projekt einzeln — obwohl in rund 300 Zeilen Auftragsworkflow genau **zwei** Zeilen
projektspezifisch sind. Damit gilt für sie dasselbe Argument wie für die Skills selbst:
eine Quelle, sonst altert dieselbe Regel getrennt.

Der Befund, die Empfehlung und die offenen Fragen stehen in
[`Doku/Entscheidung_Workflows_hierher.md`](Doku/Entscheidung_Workflows_hierher.md).
**Vorschlag, nicht umgesetzt.**

## Versionierung

Semantic Versioning und Releases: `semver-und-releases`. Tag-Schema hier:
`reiser-workflow--v<version>`.

Beim Release sind **zwei** Stellen zu ziehen, beide vom Plugin-Format erzwungen:

1. `.claude-plugin/marketplace.json`
2. `plugins/reiser-workflow/.claude-plugin/plugin.json`

`claude plugin tag` prüft sie gegeneinander und verweigert das Release, wenn sie
auseinanderliegen. Dieses Repository enthält bewusst **keinen ausführbaren Code**, den ein
Projekt-Workflow über einen Tag holen müsste — es gibt also keine dritte Stelle, die beim
Hochzählen vergessen werden kann.
