# Auslöse-Test für repo-hygiene

`trigger-evals.json` enthält 20 realistische Anfragen: zehn, bei denen der Skill
greifen soll, und zehn Beinahe-Treffer, bei denen er es nicht soll (Git-Aufgaben ohne
Hygienebezug, sowie eine Anonymisierung, die an `xlsx` gehört).

## Wie er gefahren wird

Der Optimierer des skill-creator (`scripts/run_loop.py`) braucht die `claude`-CLI. Auf
diesem Rechner liegt nur die Linux-Fassung für die Cowork-VM, die unter Windows nicht
läuft. Ersatzverfahren: drei unabhängige Subagenten bekommen die Skill-Liste (mit den
Beschreibungen, ohne Hinweis darauf, welcher Skill geprüft wird) und alle 20 Anfragen
und routen jede einzeln. Drei Durchgänge, weil eine einzelne Entscheidung schwankt.

Wichtig ist, dass die konkurrierenden Skills realistisch mitgegeben werden — sonst
misst man nur, ob die Beschreibung zum Thema passt, nicht ob sie sich gegen die
Nachbarn durchsetzt.

## Stand 06.09.2026

| Fassung | Auslöser erkannt | Fehlauslösungen |
|---|---|---|
| erste Beschreibung | 27/30 (90 %) | 0/30 |
| überarbeitet | **30/30** | **0/30** |

Die erste Fassung verfehlte zwei Fälle, und beide zeigten eine echte inhaltliche Lücke,
nicht nur eine Formulierungsschwäche:

- **„API-Keys schon committet und gepusht"** (1/3). Die Beschreibung endete beim
  *vorher*. Zwei Agenten schrieben ausdrücklich „kein Skill für Incident Response".
  Daraufhin kam der Abschnitt „Es ist schon passiert" dazu — der Fall, in dem der Skill
  am meisten wert ist.
- **„Datei landet nicht im Repo trotz `git add -A`"** (2/3). Die Diagnoserichtung fehlte;
  genannt war nur das *Anlegen* einer `.gitignore`. Daraufhin kam der Abschnitt
  „Wenn eine Datei nicht im Repository landet" dazu.

Merksatz daraus: Ein verfehlter Auslöser ist zuerst ein Hinweis auf fehlenden Inhalt und
erst danach auf eine schwache Beschreibung. Wer nur die Beschreibung nachschärft,
bekommt einen Skill, der zwar greift, aber dann nichts zu sagen hat.
