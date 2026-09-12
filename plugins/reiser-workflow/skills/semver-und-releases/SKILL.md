---
name: semver-und-releases
description: >
  Versionsnummern nach Semantic Versioning und das Bauen von GitHub-Releases mit
  annotierten Tags und Download-Dateien. Regelt, wann MAJOR, MINOR oder PATCH steigt, wer
  das darf, wo die Version im Projekt steht und wie ein Release entsteht. Nutze diesen
  Skill, wenn der Nutzer „Release bauen" sagt oder ein Release, einen Tag, eine neue
  Version oder Release Notes verlangt; wenn zu entscheiden ist, ob eine Änderung MINOR
  oder PATCH ist; wenn eine Versionsnummer irgendwo im Projekt hochgezählt werden soll;
  und wenn ein Projekt noch gar keine Versionierung hat. Gilt für alle Softwareprojekte.
---

# Versionierung und Releases

## Semantic Versioning

`MAJOR.MINOR.PATCH` nach <https://semver.org/>.

| Teil | steigt bei | wer |
|---|---|---|
| **MAJOR** | Bruch der Kompatibilität | **nur der Nutzer** |
| **MINOR** | neue Funktion, abwärtskompatibel | Claude |
| **PATCH** | Fehlerbehebung, abwärtskompatibel | Claude |

MINOR setzt PATCH auf 0, MAJOR setzt beide auf 0.

**Vor dem ersten Release** läuft die Entwicklung ab `0.1.0`. In `0.x` gilt keine
Kompatibilitätszusage; neue Funktionen erhöhen MINOR, Korrekturen PATCH. **Das erste
Release ist immer `1.0.0`** — nie `0.x` als Release veröffentlichen.

Steigt aus deiner Sicht MAJOR an, ist das keine Entscheidung, die du triffst: sag es und
begründe, woran du den Bruch festmachst.

## Wo die Version steht

Genau eine Quelle je Projekt. Gibt es keine natürliche (etwa `package.json`,
`pyproject.toml`, `*.csproj`), dann eine Datei `VERSION` im Wurzelverzeichnis mit der
nackten Nummer und einem Zeilenumbruch.

Muss die Nummer an weiteren Stellen auftauchen, wird sie von dort **abgeleitet**, nicht
abgeschrieben. Eine zweite gepflegte Fassung läuft auseinander — die Frage ist nur, wann.

**Wenn das Format zwei Fassungen erzwingt**, wie bei einem Claude-Plugin
(`.claude-plugin/marketplace.json` und `plugins/<name>/.claude-plugin/plugin.json`), gilt
die Ausnahme nur mit einer **Prüfung, die den Gleichlauf erzwingt** — hier
`claude plugin tag`, das das Release verweigert, wenn beide auseinanderliegen. Ohne
solche Prüfung ist die zweite Fassung kein Sonderfall, sondern der Fehler.

Führe außerdem im Kopf, **wer die Nummer sonst noch liest**. Holt sich irgendwo ein
fremder Workflow etwas aus dem Projekt über einen Tag, hängt er an genau dieser Nummer;
solche Stellen gehören auf die Release-Checkliste, sonst führt er nach dem nächsten
Release weiter die alte Fassung aus. Am billigsten ist es, gar keine zu haben.

Nicht zu verwechseln mit projekteigenen Stand-Angaben, die etwas anderes versionieren
(etwa `ANLEITUNG_STAND` im Stoffverteilungsplan, das nur das Anleitungsblatt betrifft).

## Ein Release bauen

Schlüsselwort des Nutzers: **„Release bauen"**, wahlweise mit Nummer
(„Release bauen 0.3.0"). Ohne Schlüsselwort entsteht kein Release.

### Vorbedingungen

- Der Stand liegt auf **`main`**, nichts Offenes im Arbeitsverzeichnis
- **Alle Tests grün**, auch die CI auf `main`
- Die Version ist gesetzt, committet und gepusht

Ist eine davon verletzt: nicht bauen, sondern sagen welche.

### Ablauf

```bash
# Konto setzen nach git-branch-strategie
git checkout main && git pull --ff-only

# 1. Version festlegen, Nummer bestaetigen lassen, committen

# 2. Annotierter Tag - nie ein Lightweight-Tag
git tag -a <tag> -m "Release <version>"
git push origin <tag>

# 3. Release samt Download-Dateien
gh release create <tag> --title "<version>" --notes-file <datei> <asset> ...
```

**Zwischen Schritt 2 und Schritt 3 darf auf `main` nichts anderes landen.** Der Tag legt
fest, was veröffentlicht wird. Ein Merge, der danach und vor `gh release create`
passiert, steckt schon in `main`, aber nicht im Release — der sichtbare Stand von `main`
und der tatsächlich veröffentlichte Stand laufen auseinander, ohne dass das irgendwo
auffällt, bis jemand sich später darauf verlässt. Deshalb beide Schritte unmittelbar
hintereinander, ohne Lücke für etwas anderes dazwischen.

Passiert es trotzdem — ein Merge landet zwischen Tag und Release auf `main` —, wird der
Tag **nicht** verschoben, um ihn nachträglich einzuschließen. Was zum Zeitpunkt des
Taggens für dieses Release vorgesehen war, bleibt dessen Inhalt, auch wenn `main`
inzwischen weiter ist. Der neue Commit gehört zum nächsten Release: eigene
Versionsnummer, eigener Tag, eigenes `gh release create` — nicht rückwirkend in dieses
hineingezogen.

**Wie `<tag>` heißt.** Im Normalfall `v<version>`, also `v1.4.0`. Enthält ein Repository
**mehrere getrennt veröffentlichte Einheiten** — etwa mehrere Plugins in einem
Marketplace —, trägt der Tag den Namen der Einheit voran: `<name>--v<version>`, also
`reiser-workflow--v0.3.0`. Sonst kollidieren zwei Einheiten beim ersten Mal, an dem sie
dieselbe Nummer erreichen.

Welches Schema ein Repository verwendet, ist nichts, was man raten darf: `git tag --list`
zeigt es, und ein Workflow, der einen Tag als `ref:` festnagelt, zeigt es auch.

**Annotiert (`-a`), nicht leichtgewichtig.** Ein annotierter Tag ist ein eigenes Objekt
mit Autor, Datum und Meldung und lässt sich signieren; ein leichtgewichtiger Tag ist nur
ein Zeiger und sagt später nichts darüber, wer wann was veröffentlicht hat.

**Bei einem Claude-Plugin tritt `claude plugin tag` an die Stelle von `git tag -a`** (es
prüft zusätzlich den Gleichlauf zwischen `plugin.json` und der Marketplace-Datei, siehe
oben). Der Befehl nimmt aber keine Identität als Parameter entgegen wie `git commit
-c user.name=…` — er tagt unter der aktuellen globalen Git-Identität. Für ein Release
unter dem Bot-Konto (`git-branch-strategie` → „Mit welchem Konto") deshalb kurz davor
repo-lokal umstellen und danach wieder entfernen, damit sonstige Arbeit in diesem Klon
nicht stillschweigend unter dem Bot läuft:

```bash
git config --local user.name "<Bot-Konto>"
git config --local user.email "<GitHub-User-ID>+<Bot-Konto>@users.noreply.github.com"
claude plugin tag --message "Release %s" --push
git config --local --unset user.name
git config --local --unset user.email
```

**Ein veröffentlichter Tag wird nie verschoben oder gelöscht.** Wer ihn schon gezogen hat,
bekommt sonst stillschweigend etwas anderes als alle anderen. Ist ein Release falsch, folgt
ein neues mit höherer Nummer.

### Die Dateien zum Herunterladen

Das sind die **Release Assets**: die Dateien, die ein Anwender tatsächlich braucht — nicht
der Quelltext, den GitHub ohnehin automatisch als `.zip` und `.tar.gz` anhängt.

Also das gebaute Ergebnis: die fertige Anwendungsdatei, das Archiv, die auslieferbare
Vorlage. Wo das Ergebnis nicht im Repository liegt (weil es erzeugt wird oder binär ist),
wird es für das Release gebaut und dann angehängt.

Ein Release-Asset geht genauso unwiderruflich hinaus wie ein Commit: **vor dem Anhängen
prüfen nach `repo-hygiene`.**

### Release Notes

Aus dem, was seit dem letzten Tag nach `main` gekommen ist:

```bash
git log --oneline <letzter-tag>..HEAD
gh pr list --state merged --search "merged:>=<datum>" --json number,title
```

Geordnet nach dem, was den Anwender betrifft: neue Funktionen, behobene Fehler, Änderungen
im Verhalten. Verweise auf Issues und Pull Requests statt Wiederholung — dort steht die
Begründung schon.

## Wenn ein Projekt noch keine Versionierung hat

Kein stilles Nachrüsten. Sag, dass die Quelle fehlt, schlage `0.1.0` und die Datei vor,
und lass den Nutzer zustimmen — die erste Nummer legt fest, wie alle folgenden gelesen
werden.
