#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kassenbuch fuer unbeaufsichtigte Claude-Laeufe.

WARUM ES DIESE DATEI GIBT
    Siehe ../references/verbrauch.md - dort steht die Begruendung samt
    Belegen, hier nur der Aufruf.

AUFRUF
    verbrauch.py bericht
        Liest verbrauch.json und meldet, wie voll die beiden rollenden
        Fenster sind. Das ist die Zahl, gegen die die Schwellen aus
        SKILL.md geprueft werden - was bei "kassenbuch=fehlt" gilt,
        steht ebenfalls dort.

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
