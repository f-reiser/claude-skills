#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutationstest fuer verbrauch.py - siehe Skill test-driven-development.

Verlangt wird, dass GENAU die zustaendige Pruefung anschlaegt: eine
Mutation, die irgendeine andere Pruefung rot macht, ist kein Nachweis.

    python verbrauch_mutation.py
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile

Q = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "verbrauch.py")
ORIG = io.open(Q, encoding="utf-8", newline="").read()

M = [
    # (Name, alt, neu, welche Pruefung MUSS rot werden)
    ("Log vorwaerts statt rueckwaerts",
     "for e in reversed(_ereignisse(roh)):", "for e in _ereignisse(roh):",
     "jsonl letzter result"),
    ("Array-Zweig aus",
     'if roh[0] == "[":', 'if False:',
     "array"),
    ("cache_read mitzaehlen",
     '+ int(u.get("cache_creation_input_tokens") or 0))',
     '+ int(u.get("cache_creation_input_tokens") or 0)'
     '+ int(u.get("cache_read_input_tokens") or 0))',
     "cache_read zaehlt nicht"),
    ("result-Typ egal",
     'if isinstance(e, dict) and e.get("type") == "result":',
     'if isinstance(e, dict):',
     "ohne result"),
    ("Fenster zehnmal zu gross",
     "ab = jetzt - stunden * 3600", "ab = jetzt - stunden * 36000",
     "kurzes Fenster"),
    ("kaputter Eintrag zaehlt mit",
     "        except (KeyError, TypeError, ValueError):\n",
     "        except (KeyError, TypeError, ValueError):\n"
     "            vorg += 1\n",
     "kaputter Eintrag"),
    ("immer usd",
     'if usd > 0 and os.environ.get("BUDGET_LANG_USD"):',
     'if True:',
     "token ohne Kosten"),
    ("gemessen immer falsch",
     '"gemessen": not geschaetzt and erg is not None,', '"gemessen": False,',
     "gemessener Eintrag"),
    ("gemessen immer wahr",
     '"gemessen": not geschaetzt and erg is not None,', '"gemessen": True,',
     "erster Lauf ungemessen zaehlt keinen Vorgang"),
    ("erster Lauf zaehlt doch einen Vorgang",
     "        else:\n            vorgaenge = 0",
     "        else:\n            vorgaenge = 1",
     "erster Lauf ungemessen zaehlt keinen Vorgang"),
    ("Abbruch mit null verbucht",
     'erg = {"usd": u / v, "token": tok / v}',
     'erg = {"usd": 0.0, "token": 0}',
     "Abbruch bekommt den Schnitt angerechnet"),
    ("Abbruch doppelt angerechnet",
     'erg = {"usd": u / v, "token": tok / v}',
     'erg = {"usd": u / v, "token": tok / v * 2}',
     "Abbruch senkt den Schnitt nicht"),
    ("geschaetzt verschwiegen",
     '"geschaetzt": geschaetzt,', '"geschaetzt": False,',
     "Abbruch ist als geschaetzt gekennzeichnet"),
    ("nichts wegwerfen",
     'if isinstance(e.get("t"), (int, float)) and e["t"] >= ab]',
     'if isinstance(e.get("t"), (int, float))]',
     "Altes faellt raus"),
    ("fehlendes Kassenbuch verschweigen",
     'return ["kassenbuch=fehlt"]', 'return ["kassenbuch=egal"]',
     "kein Kassenbuch"),
    ("kaputte Zeile wird zum Ergebnis",
     "        try:\n            aus.append(json.loads(z))\n"
     "        except ValueError:\n            continue\n",
     "        try:\n            aus.append(json.loads(z))\n"
     '        except ValueError:\n            aus.append({"type": "result"})\n',
     "muell"),
    ("langes Fenster zu kurz",
     "LANG_H = 24 * 7", "LANG_H = 5",
     "langes Fenster"),
    ("nie usd",
     '        return "usd"\n    return "token"',
     '        return "token"\n    return "token"',
     "usd, wenn Kosten da sind"),
    ("Vorgaenge verworfen",
     '"vorgaenge": vorgaenge,', '"vorgaenge": 1,',
     "Vorgaenge uebernommen"),

    # --- die Entscheidung -------------------------------------------
    ("Urgent darf alles",
     '"urgent": 0.80}', '"urgent": 1.50}',
     "teuer: Urgent nein"),
    ("Medium und High vertauscht",
     '"medium": 0.60, "high": 0.70', '"medium": 0.70, "high": 0.60',
     "Schwelle trennt Medium"),
    ("High zu streng",
     '"high": 0.70, "urgent"', '"high": 0.55, "urgent"',
     "Schwelle trennt High"),
    ("Unbekanntes gilt als High",
     'STANDARD_PRIORITAET = "medium"', 'STANDARD_PRIORITAET = "high"',
     "unbekannte Prioritaet gilt als Medium"),
    ("Nachtfenster faengt spaeter an",
     "LOW_VON, LOW_BIS = 0, 4", "LOW_VON, LOW_BIS = 3, 4",
     "guenstig: Low ja"),
    ("Nachtfenster gilt den ganzen Tag",
     "LOW_VON, LOW_BIS = 0, 4", "LOW_VON, LOW_BIS = 0, 24",
     "Low tagsueber nein"),
    ("fehlende Ortszeit wird geraten",
     "ZoneInfo(ZEITZONE)).hour\n    except Exception:\n        return None",
     "ZoneInfo(ZEITZONE)).hour\n    except Exception:\n        return 2",
     "Low ohne Ortszeit nein"),
    ("kurzes Fenster ohne Grenze",
     "KURZ_GRENZE = 0.50", "KURZ_GRENZE = 50.0",
     "kurzes Fenster schlaegt Prioritaet"),
    ("Schaetzung des naechsten Vorgangs faellt weg",
     "anteil = (lang + schnitt) / soll_lang", "anteil = lang / soll_lang",
     "Schwelle trennt Medium"),
    ("ohne Kassenbuch gar nichts",
     'return True, "kein Kassenbuch', 'return False, "kein Kassenbuch',
     "ohne Kassenbuch ein Vorgang"),
    ("fehlendes Budget durchwinken",
     'return False, "kein Budget in %s gesetzt" % art',
     'return True, "kein Budget in %s gesetzt" % art',
     "ohne Budget nein"),
]

tmp = tempfile.mkdtemp()
ziel = os.path.join(tmp, "verbrauch.py")
schlecht = 0
for name, alt, neu, erwartet in M:
    if ORIG.count(alt) != 1:
        print("BAUFEHLER %-38s Muster %dx gefunden" % (name, ORIG.count(alt)))
        schlecht += 1
        continue
    io.open(ziel, "w", encoding="utf-8", newline="").write(ORIG.replace(alt, neu, 1))
    p = subprocess.run([sys.executable, ziel, "--selbsttest"],
                       capture_output=True, text=True, cwd=tmp)
    aus = p.stdout + p.stderr
    if p.returncode == 0:
        print("STUMPF    %-38s keine Pruefung wurde rot" % name)
        schlecht += 1
    elif ("FEHLER: " + erwartet) not in aus:
        print("DANEBEN   %-38s erwartet '%s', bekam: %s"
              % (name, erwartet, aus.replace("\n", " | ")))
        schlecht += 1
    else:
        print("ok        %-38s -> %s" % (name, erwartet))

shutil.rmtree(tmp, ignore_errors=True)
print("%d von %d Mutationen wirksam." % (len(M) - schlecht, len(M)))
sys.exit(1 if schlecht else 0)
