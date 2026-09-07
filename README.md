# reiser-skills

Die Arbeitsweise für alle Softwareprojekte, als Claude-Plugin. Eine Quelle, von allen
Projekten referenziert — damit dieselbe Regel nicht in fünf Repositories getrennt altert.

## Was drin ist

| Skill | wofür |
|---|---|
| `github-issue-workflow` | Issues abarbeiten: Auswahl, Ablauf, Label, Typen, Prioritäten, Budget unbeaufsichtigter Läufe |
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

## Versionierung

Semantic Versioning, siehe `semver-und-releases`. Die Nummer steht in
`.claude-plugin/marketplace.json` und in `plugins/reiser-workflow/.claude-plugin/plugin.json`
und wird bei jeder Änderung an den Skills gemeinsam hochgezählt.

Jedes Release bekommt einen annotierten Tag `reiser-workflow--v<version>`
(`claude plugin tag` prüft, dass beide Manifeste übereinstimmen). Projekt-Workflows, die
ein Skript aus diesem Repository ausführen, hängen an diesem Tag — nicht an einem Branch.
