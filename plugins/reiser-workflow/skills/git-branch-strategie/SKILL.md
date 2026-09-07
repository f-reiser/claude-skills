---
name: git-branch-strategie
description: >
  Verbindlicher Feature-Branch-Workflow für alle Softwareprojekte: von main abzweigen und
  nach main zurück, Aktualisieren ausnahmslos per Rebase, Sonderfall blockierter Issues,
  hierarchische Parent-Branches, Aufräumen der Historie vor dem Pull Request, Squash gegen
  Merge-Commit, eigenständiges Lösen von Merge-Konflikten — und mit welchem GitHub-Konto
  gearbeitet wird. Nutze diesen Skill, bevor du einen Branch anlegst, committest, pushst,
  einen Pull Request erstellst oder mergst; wenn zu klären ist, ob rebased, gesquasht oder
  gemergt wird; wenn ein Branch länger offen ist; bei jedem Merge-Konflikt; und immer, wenn
  zwei Änderungen voneinander abhängen. Ebenso bei Fragen nach Branch-Namen,
  Merge-Reihenfolge, Commit-Identität oder dem zu verwendenden GitHub-Konto.
---

# Branch-Strategie

## Grundform

Feature-Branch-Workflow, ausnahmslos. Ein Branch trägt genau ein Issue.

```bash
git fetch origin
git checkout -b issue-<nr>-<kurzer-slug> origin/main
```

Nie direkt auf `main` committen.

## Aktualisieren: immer Rebase, nie Merge

Ein Feature-Branch wird **ausnahmslos per Rebase** auf den Stand seines Quellbranchs
gebracht — nie per Merge. Merge-Commits aus dem Quellbranch erzeugen einen
Historien-Salat, in dem später niemand mehr etwas eingrenzen kann.

```bash
git fetch origin
git rebase origin/main          # Quellbranch; bei Child-Branches der Parent-Branch
git push --force-with-lease
```

Pflicht an drei Stellen:

- **mindestens einmal täglich**, solange der Branch offen ist
- **bevor du neue Arbeit** an einem bestehenden Branch aufnimmst
- **vor dem finalen Commit**, dem nur noch der Pull Request folgt

Je länger ein Branch wegdriftet, desto teurer der Konflikt — und desto wahrscheinlicher
fällt er erst im Pull Request auf, wo er den Prüfer trifft statt dich.

**`--force-with-lease`, nie `--force`:** Es bricht ab, wenn jemand anderes zwischenzeitlich
gepusht hat, statt dessen Arbeit zu überschreiben. Auf `main` wird nie force-gepusht.

## Merge-Konflikte löst du

Du bist der Hauptentwickler. Konflikte gehören zu deiner Arbeit, nicht zu der des Nutzers.
Er kommt mit der Menge Code, die hier entsteht, zeitlich nicht mit — ihn einen Konflikt
lösen zu lassen ist auf seiner Seite teuer und der Ausnahmefall.

Also: den Konflikt verstehen, beide Seiten im Kontext lesen, auflösen, Tests laufen
lassen. Erst wenn du nach ernsthaftem Versuch nicht sicher entscheiden kannst, **welches
Verhalten gewollt ist** — nicht: wie man es technisch löst —, geht die Frage an den Nutzer,
mit beiden Fassungen und deiner Empfehlung.

Das wirkt auch nach vorn: Bevorzuge Vorgehensweisen, die Konflikte gar nicht erst
entstehen lassen — häufig rebasen, Änderungen klein und thematisch geschnitten halten,
nicht nebenbei formatieren.

## Wie Issues zusammenhängen — drei verschiedene Dinge

| GitHub | Bedeutung | Wirkung auf die Reihenfolge |
|---|---|---|
| **Add parent** / Sub-Issues | echte Hierarchie: großes Feature, zerlegt in Teile | Parent-Branch ist für die Children der Quellbranch |
| **Mark as blocked by / blocking** | eigenständige Features, die aber in einer Reihenfolge müssen | blockierendes Issue zuerst |
| **Add relates to** | thematisch verwandt, z. B. Doku-Task zu einem Feature | **keine** — für die Reihenfolge ignorieren |

Die Begriffe nicht vermischen: **Parent** heißt Hierarchie, sonst nichts. Ein Issue, das
ein anderes blockiert, ist kein Parent.

## Blockierte Issues

Zuerst das Issue, das von keinem offenen Issue blockiert wird. Erst wenn dessen Änderungen
in `main` sind, ist der Normalfall wiederhergestellt.

Muss das blockierte Issue vorher begonnen werden, **zweigt sein Branch vom blockierenden
Branch ab** statt von `main`:

```bash
git fetch origin
git checkout -b issue-<nr>-<slug> origin/issue-<blocker-nr>-<slug>
```

Der blockierende Branch ist damit sein Quellbranch — Aktualisieren heißt Rebase auf ihn,
und sobald er in `main` gelandet ist, Rebase auf `origin/main`.

> Früher stand hier: von `main` abzweigen und den blockierenden Branch hineinmergen. Das
> erzeugt genau den Merge-Commit, den die Rebase-Regel vermeiden soll. Inhaltlich ist
> Abzweigen vom Blocker dasselbe, nur linear.

Erlaubt ist das nur, wenn **beides** zutrifft:

- Das blockierende Feature ist nach bestem Wissen fertig — es fehlt nur noch der Pull
  Request, oder es sind Kleinigkeiten offen (etwa eine Doku-Ergänzung), die auf eine
  Rückfrage warten.
- Es hat **alle Tests grün** durchlaufen.

Im Pull Request des blockierten Issues muss stehen, von welchem Issue es abhängt und dass
**dessen Pull Request zuerst** bearbeitet werden muss.

## Reihenfolge der Pull Requests

Pull Requests werden in der Reihenfolge ihrer Abhängigkeit bearbeitet. **Ein Pull Request
bringt niemals zwei verschiedene Features nach `main`.**

Die Branch-Historie ist eine Suchhilfe: Wer einen schwer auffindbaren Fehler eingrenzt,
braucht einen konsistenten Stand nach dem anderen. Ein Merge, der zwei unabhängige
Features gleichzeitig einbringt, macht jeden Treffer von `git bisect` mehrdeutig.

## Große Features mit Sub-Issues

Das Parent-Issue bekommt einen eigenen Branch. Für die Children ist **dieser** Branch der
Quellbranch: sie zweigen von ihm ab, rebasen auf ihn und mergen in ihn zurück. Der
Parent-Branch wird seinerseits per Rebase auf `main` aktuell gehalten.

**Achtung, hier greifen zwei Regeln ineinander:** Wird der Parent-Branch rebased, ändern
sich die Commits, auf denen die Children sitzen. Sie müssen danach **in derselben Sitzung**
nachgezogen werden:

```bash
git checkout <parent> && git rebase origin/main && git push --force-with-lease
git checkout <child>  && git rebase <parent>    && git push --force-with-lease   # je Child
```

Deshalb den Parent-Branch nur rebasen, wenn du die offenen Children kennst und
anschließend mitziehst. Lass es, solange jemand anderes auf einem Child arbeitet — dann
erst absprechen.

## Historie aufräumen vor dem Pull Request

Zwischenstände wie „Tippfehler", „doch anders" oder „Test grün" tragen nichts. Vor dem
Pull Request die eigenen Commits zusammenfassen — besonders bei großen Features und immer,
wenn es viel Hin und Her zwischen Nutzer und Claude gab.

```bash
git fetch origin
git rebase -i origin/main
git push --force-with-lease
```

## Wie der Pull Request nach main kommt

| Fall | Modus |
|---|---|
| kleineres Feature, Bugfix | **Squash and merge** |
| großes Feature (hierarchisch über mehrere Issues strukturiert) | **Create a merge commit** |
| immer | **kein Rebase-Merge** |

Beim großen Feature bleibt die innere Struktur sichtbar — genau die Information, die man
beim Eingrenzen braucht. Beim kleinen Fix wäre sie Rauschen.

**Gemergt wird vom Nutzer.** Nur wenn er es hier im Gespräch ausspricht, und dann für
genau diesen einen Pull Request — nicht für den nächsten, nicht als Dauerregel.

## Mit welchem Konto

Drei Schichten, die unabhängig umschalten. Wer nur eine tauscht, bekommt ein Ergebnis,
das falsch aussieht, ohne dass es auffällt.

| Schicht | steuert | umgeschaltet über |
|---|---|---|
| `gh` | wer auf GitHub handelt | `GH_TOKEN` |
| `git push` | wer pushen darf | Credential-Helper (folgt `GH_TOKEN`) |
| Commit-Autor | was die Historie sagt | `user.name` / `user.email` |

**Laufende Arbeit** — Commits, Branches, Issues, Pull Requests — unter dem Bot:

```bash
export GH_TOKEN=$(gh auth token --user reiser-claude-agent)
git -c user.name="reiser-claude-agent" \
    -c user.email="325701350+reiser-claude-agent@users.noreply.github.com" \
    commit -m "..."
```

Die noreply-Adresse ist geprüft: GitHub verknüpft damit erstellte Commits mit dem
Bot-Account, ohne dass eine private Adresse im Repository steht.

**Beim Ändern eines bestehenden Commits zusätzlich `--reset-author`:**

```bash
git -c user.name="…" -c user.email="…" commit --amend --reset-author --no-edit
```

`--amend` behält sonst den ursprünglichen **Autor** — die `-c`-Angaben setzen nur den
Committer. Ohne `--reset-author` steht der Commit weiterhin unter dem, der ihn zuerst
gemacht hat, und das fällt erst auf, wenn jemand die Historie liest. Nach dem Prüfen:
`git log -1 --format='%an <%ae>'`.

Damit `git push` demselben Token folgt, muss der Credential-Helper einmalig je Repository
gesetzt sein:

```bash
git config --local credential.https://github.com.helper ""
git config --local --add credential.https://github.com.helper "!gh auth git-credential"
```

Bewusst repo-lokal, nicht global — sonst laufen auch die eigenen Pushes des Nutzers über
`gh` und die Kontowahl wird ihm aus der Hand genommen.

**Nicht mit dem Bot:** Repositories anlegen, Branch-Schutzregeln, Collaborators, Label und
Issue-Typen einrichten. Der Bot hat dafür bewusst keine Rechte (`push`, kein `admin`).
Solche Arbeiten laufen über den Account des Nutzers und werden vorher angesprochen —
`GH_TOKEN=$(gh auth token --user ReiserFlorian)`.

`gh auth switch` ist hier das falsche Werkzeug: Es setzt einen globalen Zustand, den eine
andere Sitzung verändert haben kann. Ein unbeaufsichtigter Lauf darf nicht davon abhängen.
