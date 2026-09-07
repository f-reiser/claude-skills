# reiser-skills

Die Arbeitsweise für alle Softwareprojekte, als Claude-Plugin. Eine Quelle, von allen
Projekten referenziert — damit dieselbe Regel nicht in fünf Repositories getrennt altert.

## Was drin ist

| Skill | wofür |
|---|---|
| `github-issue-workflow` | Issues abarbeiten: Auswahl, Ablauf, Label, Typen, Prioritäten |
| `git-branch-strategie` | Feature-Branches, Rebase, Merge-Konflikte, Pull Requests, GitHub-Konten |
| `semver-und-releases` | Versionsnummern, Tags, GitHub-Releases |
| `erklaeren-mit-mass` | wie viel Erklärung ein Text verdient |
| `repo-hygiene` | was in ein Repository gehört und was nicht |

## Verwendung in einem Projekt

Im Workflow des Projekts:

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    plugin_marketplaces: "https://github.com/f-reiser/claude-skills.git"
    plugins: "reiser-workflow@reiser-skills"
    prompt: "/github-issue-workflow"
```

Lokal in Claude Code stehen dieselben Skills über das Konto zur Verfügung. **Beide
Fassungen müssen zusammen geändert werden** — sonst arbeitet die Automatik nach anderen
Regeln als die Sitzung am Rechner.

## Versionierung

Semantic Versioning, siehe `semver-und-releases`. Die Nummer steht in
`.claude-plugin/marketplace.json` und in `plugins/reiser-workflow/.claude-plugin/plugin.json`
und wird bei jeder Änderung an den Skills gemeinsam hochgezählt.
