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
    ("gemessen immer wahr",
     '"gemessen": erg is not None,', '"gemessen": True,',
     "Eintrag ohne Messung"),
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
