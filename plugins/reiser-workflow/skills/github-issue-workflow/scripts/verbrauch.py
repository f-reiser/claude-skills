#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kassenbuch fuer unbeaufsichtigte Claude-Laeufe.

WARUM ES DIESE DATEI GIBT
    Siehe ../references/verbrauch.md - dort steht die Begruendung samt
    Belegen, hier nur der Aufruf.

AUFRUF
    verbrauch.py entscheidung --prioritaet High
        Beantwortet die einzige Frage, die im Lauf zaehlt: noch einen
        Vorgang anfangen, ja oder nein. Die Schwellen stehen HIER im
        Code und nirgends sonst - eine Schwelle, die nur als Prosa in
        einer Anweisung steht, wird irgendwann ueberlesen.

    verbrauch.py bericht
        Die Zahlen dahinter, fuer den Menschen und fuer die
        Job-Zusammenfassung.

    verbrauch.py fortschreiben <execution_file>
        Haengt den Verbrauch des gerade beendeten Laufs an. Muss auch
        laufen, wenn der Lauf gescheitert ist - verbraucht hat er trotzdem.

    verbrauch.py --selbsttest
        Prueft die Rechenwege ohne Netz und ohne echten Lauf.

BUDGET
    Umgebungsvariablen, gesetzt im Workflow:
        BUDGET_KURZ_USD / BUDGET_LANG_USD      (5 Stunden / 7 Tage)
        BUDGET_KURZ_TOKEN / BUDGET_LANG_TOKEN  Ersatz, wenn keine Kosten
                                               ausgewiesen werden
"""
import io
import json
import os
import sys
import time

DATEI = "verbrauch.json"
KURZ_H = 5
LANG_H = 24 * 7
AUFHEBEN_H = 24 * 8          # etwas mehr als das lange Fenster

#  Ab welchem Anteil des LANGEN Budgets ein Vorgang dieser Prioritaet
#  zurueckgestellt wird. Je wichtiger, desto weiter darf er gehen.
SCHWELLEN = {"low": 0.50, "medium": 0.60, "high": 0.70, "urgent": 0.80}
STANDARD_PRIORITAET = "medium"

#  Das kurze Fenster gehoert dem Nutzer: Wer sich gerade hinsetzt, soll
#  nicht feststellen, dass die Automatik ihm das Fenster leergeraeumt hat.
KURZ_GRENZE = 0.50

#  Low laeuft nur nachts. Ortszeit des Nutzers, nicht UTC - der Runner
#  steht in UTC und laege im Sommer zwei Stunden daneben.
LOW_VON, LOW_BIS = 0, 4
ZEITZONE = "Europe/Berlin"


# ---------------------------------------------------------------- lesen

def _ereignisse(roh):
    """Der Log ist mal ein JSON-Array, mal eine Zeile je Ereignis."""
    roh = roh.strip()
    if not roh:
        return []
    if roh[0] == "[":
        try:
            return json.loads(roh)
        except ValueError:
            return []
    aus = []
    for z in roh.splitlines():
        z = z.strip()
        if not z:
            continue
        try:
            aus.append(json.loads(z))
        except ValueError:
            continue
    return aus


def ergebnis(roh):
    """Verbrauch aus einem Ereignis-Log. None, wenn keiner drinsteht.

    Von HINTEN gesucht: bei --resume oder einem Wiederholungsversuch
    stehen mehrere result-Eintraege drin, und nur der letzte beschreibt
    den ganzen Lauf.
    """
    for e in reversed(_ereignisse(roh)):
        if isinstance(e, dict) and e.get("type") == "result":
            u = e.get("usage") or {}
            #  Cache-Lesen bleibt aussen vor: es kostet einen Bruchteil
            #  eines Ausgabe-Tokens, wuerde die Summe aber dominieren und
            #  jeden Lauf teuer aussehen lassen.
            token = (int(u.get("input_tokens") or 0)
                     + int(u.get("output_tokens") or 0)
                     + int(u.get("cache_creation_input_tokens") or 0))
            return {"usd": float(e.get("total_cost_usd") or 0.0),
                    "token": token}
    return None


def lade(pfad=DATEI):
    try:
        with io.open(pfad, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        return None
    if not isinstance(d, dict) or not isinstance(d.get("eintraege"), list):
        return None
    return d


# --------------------------------------------------------------- rechnen

def summe(eintraege, jetzt, stunden):
    """usd, token und Zahl der Vorgaenge im rollenden Fenster."""
    ab = jetzt - stunden * 3600
    usd = token = vorg = 0.0
    for e in eintraege:
        try:
            if float(e["t"]) < ab:
                continue
            usd += float(e.get("usd") or 0.0)
            token += float(e.get("token") or 0.0)
            vorg += float(e.get("vorgaenge") or 0.0)
        except (KeyError, TypeError, ValueError):
            #  Ein unlesbarer Eintrag darf das Kassenbuch nicht kippen -
            #  aber er darf auch nicht als "nichts verbraucht" durchgehen.
            #  Deshalb faellt er auf, indem er die Vorgaenge nicht erhoeht:
            #  der Schnitt steigt, die Schaetzung wird vorsichtiger.
            continue
    return usd, token, vorg


def einheit(eintraege, jetzt):
    """usd, sobald im langen Fenster Kosten ausgewiesen sind - sonst token.

    Gemischt wird nie: ein Fenster, in dem beide Arten vorkommen, waere
    in beiden Einheiten falsch summiert.
    """
    usd, _, _ = summe(eintraege, jetzt, LANG_H)
    if usd > 0 and os.environ.get("BUDGET_LANG_USD"):
        return "usd"
    return "token"


def _budget(name, ersatz=0.0):
    try:
        return float(os.environ.get(name) or 0.0)
    except ValueError:
        return ersatz


def bericht_zeilen(d, jetzt):
    if d is None:
        return ["kassenbuch=fehlt"]
    e = d["eintraege"]
    art = einheit(e, jetzt)
    zeilen = ["kassenbuch=vorhanden", "eintraege=%d" % len(e), "einheit=%s" % art]
    for kennung, stunden, bud in (("kurz", KURZ_H, "BUDGET_KURZ_%s"),
                                  ("lang", LANG_H, "BUDGET_LANG_%s")):
        usd, token, _ = summe(e, jetzt, stunden)
        ist = usd if art == "usd" else token
        soll = _budget(bud % art.upper())
        if soll > 0:
            zeilen.append("%s=%.1f%% (%.4g von %.4g %s)"
                          % (kennung, 100.0 * ist / soll, ist, soll, art))
        else:
            zeilen.append("%s=KEIN BUDGET GESETZT (%.4g %s verbraucht)"
                          % (kennung, ist, art))
    usd, token, vorg = summe(e, jetzt, LANG_H)
    ist = usd if art == "usd" else token
    if vorg > 0:
        schnitt = ist / vorg
        soll = _budget("BUDGET_LANG_%s" % art.upper())
        zeilen.append("schnitt_pro_vorgang=%.4g %s%s"
                      % (schnitt, art,
                         (" (%.1f%% des langen Budgets)"
                          % (100.0 * schnitt / soll)) if soll > 0 else ""))
    else:
        zeilen.append("schnitt_pro_vorgang=unbekannt")
    return zeilen


# ------------------------------------------------------------ entscheiden

def ortsstunde(jetzt):
    """Stunde in der Zeitzone des Nutzers, oder None.

    None ist ein eigenes Ergebnis, kein Ersatzwert: Ohne Zeitzonendaten
    (tzdata fehlt, etwa unter Windows) waere jede angenommene Stunde
    geraten, und geraten wuerde hier bedeuten, nachts zu arbeiten, wenn
    es Nachmittag ist.
    """
    try:
        from datetime import datetime, timezone
        from zoneinfo import ZoneInfo
        return datetime.fromtimestamp(jetzt, timezone.utc).astimezone(
            ZoneInfo(ZEITZONE)).hour
    except Exception:
        return None


def entscheidung(d, jetzt, prioritaet, stunde=None):
    """(ja, grund) - darf jetzt ein Vorgang dieser Prioritaet beginnen?

    Der Schnitt aus dem Kassenbuch wird VOLL angerechnet: Was der
    laufende Durchgang gerade verbraucht, ist von innen nicht lesbar,
    also muss der naechste Vorgang geschaetzt werden, bevor er beginnt.
    """
    p = (prioritaet or "").strip().lower()
    if p not in SCHWELLEN:
        p = STANDARD_PRIORITAET

    if p == "low":
        h = ortsstunde(jetzt) if stunde is None else stunde
        if h is None:
            return False, "Ortszeit nicht bestimmbar, und Low laeuft nur nachts"
        if not (LOW_VON <= h < LOW_BIS):
            return False, ("Low laeuft nur zwischen %d:00 und %d:00 %s, es ist %d Uhr"
                           % (LOW_VON, LOW_BIS, ZEITZONE, h))

    if d is None:
        #  Der erste Vorgang ist erlaubt - ohne Kassenbuch gibt es nichts
        #  zu messen, und gar nicht zu arbeiten waere die teurere Antwort.
        return True, "kein Kassenbuch: dieser eine Vorgang, danach Schluss"

    e = d["eintraege"]
    art = einheit(e, jetzt)
    soll_lang = _budget("BUDGET_LANG_%s" % art.upper())
    soll_kurz = _budget("BUDGET_KURZ_%s" % art.upper())
    if soll_lang <= 0 or soll_kurz <= 0:
        return False, "kein Budget in %s gesetzt" % art

    kurz = summe(e, jetzt, KURZ_H)[0 if art == "usd" else 1]
    if kurz > KURZ_GRENZE * soll_kurz:
        return False, ("kurzes Fenster bei %.0f%%, Grenze %.0f%%"
                       % (100.0 * kurz / soll_kurz, 100.0 * KURZ_GRENZE))

    usd, token, vorg = summe(e, jetzt, LANG_H)
    lang = usd if art == "usd" else token
    schnitt = (lang / vorg) if vorg > 0 else 0.0
    anteil = (lang + schnitt) / soll_lang
    if anteil >= SCHWELLEN[p]:
        return False, ("langes Fenster kaeme auf %.0f%%, Schwelle fuer %s ist %.0f%%"
                       % (100.0 * anteil, p, 100.0 * SCHWELLEN[p]))
    return True, ("langes Fenster kaeme auf %.0f%%, Schwelle fuer %s ist %.0f%%"
                  % (100.0 * anteil, p, 100.0 * SCHWELLEN[p]))


# ------------------------------------------------------------ schreiben

def fortschreiben(logpfad, pfad=DATEI, jetzt=None, vorgaenge=None):
    jetzt = time.time() if jetzt is None else jetzt
    d = lade(pfad) or {"eintraege": []}

    try:
        with io.open(logpfad, encoding="utf-8", errors="replace") as f:
            erg = ergebnis(f.read())
    except Exception:
        erg = None

    if vorgaenge is None:
        try:
            with io.open("vorgaenge.txt", encoding="utf-8") as f:
                vorgaenge = int(f.read().strip())
        except Exception:
            vorgaenge = 1

    #  Ein Lauf ohne lesbaren Verbrauch wird trotzdem eingetragen. Ihn
    #  wegzulassen hiesse, ihn als kostenlos zu verbuchen - und genau die
    #  gescheiterten Laeufe sind oft die teuren.
    d["eintraege"].append({
        "t": round(jetzt),
        "usd": (erg or {}).get("usd", 0.0),
        "token": (erg or {}).get("token", 0),
        "gemessen": erg is not None,
        "vorgaenge": vorgaenge,
        "lauf": os.environ.get("GITHUB_RUN_ID", ""),
    })
    ab = jetzt - AUFHEBEN_H * 3600
    d["eintraege"] = [e for e in d["eintraege"]
                      if isinstance(e.get("t"), (int, float)) and e["t"] >= ab]
    with io.open(pfad, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=1))
    return d


# ----------------------------------------------------------- selbsttest

def selbsttest():
    fehler = []
    gezaehlt = [0]

    def pruefe(name, fn):
        #  Gezaehlt statt festgeschrieben: eine Zahl im Text waere beim
        #  naechsten neuen Check schon falsch.
        gezaehlt[0] += 1
        #  fn ist ein Aufruf, keine fertige Bedingung: Eine Pruefung, die
        #  eine Ausnahme wirft, soll als FEHLER gelten und die restlichen
        #  Pruefungen weiterlaufen lassen. Sonst verdeckt der erste
        #  Absturz alles, was danach kommt.
        try:
            ok = bool(fn())
        except Exception as ex:
            ok = False
            name = "%s (%s)" % (name, ex.__class__.__name__)
        if not ok:
            fehler.append(name)

    #  1-3: beide Logformate, und der LETZTE result-Eintrag gewinnt
    ein = ('{"type":"assistant"}\n'
           '{"type":"result","total_cost_usd":0.1,"usage":'
           '{"input_tokens":1,"output_tokens":2,'
           '"cache_creation_input_tokens":3,"cache_read_input_tokens":9999}}\n'
           '{"type":"result","total_cost_usd":0.5,"usage":{"output_tokens":10}}\n')
    pruefe("jsonl letzter result", lambda: ergebnis(ein)["usd"] == 0.5)
    pruefe("array", lambda: ergebnis(json.dumps(
        [{"type": "result", "total_cost_usd": 0.25, "usage": {}}]))["usd"] == 0.25)
    pruefe("cache_read zaehlt nicht", lambda: ergebnis(
        '{"type":"result","usage":{"input_tokens":1,"output_tokens":2,'
        '"cache_creation_input_tokens":3,"cache_read_input_tokens":9999}}'
    )["token"] == 6)

    #  4-5: kein Verbrauch im Log, kaputter Log
    pruefe("ohne result", lambda: ergebnis('{"type":"assistant"}') is None)
    pruefe("muell", lambda: ergebnis("kein json") is None)

    #  6-7: das rollende Fenster schneidet nach Zeit ab
    jetzt = 1_000_000.0
    e = [{"t": jetzt - 3600, "usd": 1.0, "token": 10, "vorgaenge": 1},
         {"t": jetzt - 6 * 3600, "usd": 2.0, "token": 20, "vorgaenge": 1},
         {"t": jetzt - 40 * 24 * 3600, "usd": 99.0, "token": 990, "vorgaenge": 1}]
    pruefe("kurzes Fenster", lambda: summe(e, jetzt, KURZ_H)[0] == 1.0)
    pruefe("langes Fenster", lambda: summe(e, jetzt, LANG_H)[0] == 3.0)

    #  8: ein unlesbarer Eintrag erhoeht die Vorgaenge nicht
    pruefe("kaputter Eintrag", lambda: summe(
        e + [{"t": "spaeter", "usd": 5.0, "vorgaenge": 5}], jetzt, LANG_H)[2] == 2.0)

    #  9-10: Einheitenwahl
    alt = dict(os.environ)
    try:
        os.environ["BUDGET_LANG_USD"] = "10"
        pruefe("usd, wenn Kosten da sind", lambda: einheit(e, jetzt) == "usd")
        pruefe("token ohne Kosten", lambda: einheit(
            [{"t": jetzt, "usd": 0.0, "token": 5, "vorgaenge": 1}], jetzt) == "token")
    finally:
        os.environ.clear()
        os.environ.update(alt)

    #  11: fehlendes Kassenbuch ist eine Aussage, kein Absturz
    pruefe("kein Kassenbuch",
           lambda: bericht_zeilen(None, jetzt)[0] == "kassenbuch=fehlt")

    #  12-14: Fortschreiben legt an, kuerzt und traegt auch Ungemessenes ein
    import tempfile
    p = os.path.join(tempfile.mkdtemp(), DATEI)
    d = fortschreiben(os.devnull, p, jetzt, 2)
    pruefe("Eintrag ohne Messung", lambda: d["eintraege"][-1]["gemessen"] is False)
    pruefe("Vorgaenge uebernommen", lambda: d["eintraege"][-1]["vorgaenge"] == 2)
    d2 = fortschreiben(os.devnull, p, jetzt + AUFHEBEN_H * 3600 + 10, 1)
    pruefe("Altes faellt raus", lambda: len(d2["eintraege"]) == 1)

    #  15-24: die Entscheidung. Budget so gesetzt, dass 60 Token schon
    #  60 % des langen Budgets sind - ein Vorgang kostet im Schnitt 10,
    #  die Schaetzung hebt also jede Antwort um genau eine Stufe.
    alt = dict(os.environ)
    try:
        os.environ["BUDGET_LANG_TOKEN"] = "100"
        os.environ["BUDGET_KURZ_TOKEN"] = "100"
        os.environ.pop("BUDGET_LANG_USD", None)
        os.environ.pop("BUDGET_KURZ_USD", None)

        def buch(token, vorgaenge=1, alter_h=20):
            return {"eintraege": [{"t": jetzt - alter_h * 3600, "usd": 0.0,
                                   "token": token, "vorgaenge": vorgaenge}]}

        #  50 verbraucht + 50/1 geschaetzt = 100 % -> ueber jeder Schwelle
        pruefe("teuer: Urgent nein",
               lambda: entscheidung(buch(50), jetzt, "Urgent")[0] is False)
        #  20 + 20 = 40 % -> unter jeder Schwelle
        pruefe("guenstig: Low ja",
               lambda: entscheidung(buch(20), jetzt, "Low", stunde=2)[0] is True)
        #  30 + 30 = 60 % -> Medium (60) nein, High (70) ja
        pruefe("Schwelle trennt Medium",
               lambda: entscheidung(buch(30), jetzt, "Medium")[0] is False)
        pruefe("Schwelle trennt High",
               lambda: entscheidung(buch(30), jetzt, "High")[0] is True)
        pruefe("unbekannte Prioritaet gilt als Medium",
               lambda: entscheidung(buch(30), jetzt, "Quatsch")[0] is False)
        pruefe("Low tagsueber nein",
               lambda: entscheidung(buch(20), jetzt, "Low", stunde=14)[0] is False)
        #  Zeitzone absichtlich unauffindbar machen, statt die Erwartung
        #  aus LOW_VON/LOW_BIS zu berechnen: ein Test, der mit denselben
        #  Konstanten rechnet wie der Code, prueft nur sich selbst.
        zz = globals()["ZEITZONE"]
        try:
            globals()["ZEITZONE"] = "Nirgendwo/Nirgends"
            pruefe("Low ohne Ortszeit nein",
                   lambda: entscheidung(buch(20), jetzt, "low")[0] is False)
        finally:
            globals()["ZEITZONE"] = zz

        #  Langes Budget hier absichtlich weit, damit wirklich das kurze
        #  Fenster die Antwort gibt und nicht nebenbei das lange.
        os.environ["BUDGET_LANG_TOKEN"] = "10000"
        pruefe("kurzes Fenster schlaegt Prioritaet",
               lambda: entscheidung(buch(60, 1, 1), jetzt, "Urgent")[0] is False)
        os.environ["BUDGET_LANG_TOKEN"] = "100"
        pruefe("ohne Kassenbuch ein Vorgang",
               lambda: entscheidung(None, jetzt, "Medium")[0] is True)
        os.environ["BUDGET_LANG_TOKEN"] = "0"
        pruefe("ohne Budget nein",
               lambda: entscheidung(buch(1), jetzt, "Urgent")[0] is False)
    finally:
        os.environ.clear()
        os.environ.update(alt)

    for f in fehler:
        print("FEHLER: %s" % f)
    print("%d von %d Pruefungen bestanden."
          % (gezaehlt[0] - len(fehler), gezaehlt[0]))
    return 1 if fehler else 0


def main(argv):
    if "--selbsttest" in argv:
        return selbsttest()
    if len(argv) > 1 and argv[1] == "bericht":
        for z in bericht_zeilen(lade(), time.time()):
            print(z)
        return 0
    if len(argv) > 1 and argv[1] == "entscheidung":
        p = argv[argv.index("--prioritaet") + 1] if "--prioritaet" in argv else ""
        ja, grund = entscheidung(lade(), time.time(), p)
        print("entscheidung=%s" % ("ja" if ja else "nein"))
        print("grund=%s" % grund)
        #  Rueckgabewert bleibt 0: Ein "nein" ist das erwartete Ergebnis
        #  und kein Fehler - ein Workflow-Schritt duerfte daran nicht
        #  scheitern.
        return 0
    if len(argv) > 2 and argv[1] == "fortschreiben":
        d = fortschreiben(argv[2])
        e = d["eintraege"][-1]
        print("eingetragen: usd=%s token=%s gemessen=%s vorgaenge=%s"
              % (e["usd"], e["token"], e["gemessen"], e["vorgaenge"]))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
