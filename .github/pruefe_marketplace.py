#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft den Marketplace auf die Zusagen, die das Plugin-Format nicht selbst haelt.

    1. Jeder Marketplace-Eintrag hat eine plugin.json, und beide nennen dieselbe Version.
    2. Alle Plugins des Repositories tragen DIESELBE Version (Begruendung: README,
       Abschnitt "Versionierung" - die Plugins werden zusammen veroeffentlicht).
    3. Jedes Plugin hat mindestens einen Skill, und jeder Skill hat name+description.
    4. Der Skillname im Frontmatter entspricht dem Verzeichnisnamen.

WARUM ES DIESE DATEI GIBT
    "claude plugin tag" prueft Punkt 1 - aber erst beim Release, also an der Stelle, an
    der ein Fehler am teuersten auffaellt. Punkt 2 prueft es gar nicht: es sieht je
    Aufruf nur EIN Plugin. Seit es zwei gibt, ist der Gleichlauf zwischen ihnen eine
    Zusage, die sonst niemand haelt.
"""
import io
import json
import os
import re
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def lies_json(pfad):
    with io.open(pfad, encoding="utf-8") as f:
        return json.load(f)


def frontmatter(text):
    """Die name/description-Paare aus dem YAML-Kopf - ohne YAML-Abhaengigkeit.

    Bewusst grob: geprueft wird nur, DASS die beiden Felder da sind und was in "name"
    steht. Eine vollstaendige YAML-Auswertung waere mehr Code fuer dieselbe Aussage.
    """
    if not text.startswith("---"):
        return {}
    ende = text.find(chr(10) + "---", 3)
    if ende < 0:
        return {}
    kopf = text[3:ende]
    felder = {}
    for schluessel in ("name", "description"):
        m = re.search(r"^" + schluessel + r":\s*(.*)$", kopf, re.M)
        if m:
            felder[schluessel] = m.group(1).strip()
    return felder


def pruefe(wurzel=WURZEL):
    """Liste der Befunde - leer heisst gruen."""
    fehler = []
    mpfad = os.path.join(wurzel, ".claude-plugin", "marketplace.json")
    try:
        markt = lies_json(mpfad)
    except (OSError, ValueError) as ex:
        return ["marketplace.json nicht lesbar: %s" % ex]

    eintraege = markt.get("plugins") or []
    if not eintraege:
        return ["marketplace.json nennt kein Plugin."]

    versionen = {}
    for e in eintraege:
        name = e.get("name") or "(ohne Namen)"
        quelle = (e.get("source") or "").lstrip("./")
        ppfad = os.path.join(wurzel, quelle, ".claude-plugin", "plugin.json")
        if not os.path.isfile(ppfad):
            fehler.append("%s: plugin.json fehlt unter %s" % (name, quelle))
            continue
        try:
            plugin = lies_json(ppfad)
        except ValueError as ex:
            fehler.append("%s: plugin.json nicht lesbar: %s" % (name, ex))
            continue

        if plugin.get("name") != name:
            fehler.append("%s: plugin.json nennt sich %r" % (name, plugin.get("name")))
        if plugin.get("version") != e.get("version"):
            fehler.append("%s: Version %r im Marketplace, %r in plugin.json"
                          % (name, e.get("version"), plugin.get("version")))
        versionen[name] = e.get("version")

        skills = os.path.join(wurzel, quelle, "skills")
        namen = sorted(d for d in os.listdir(skills)) if os.path.isdir(skills) else []
        if not namen:
            fehler.append("%s: kein einziger Skill." % name)
        for s in namen:
            spfad = os.path.join(skills, s, "SKILL.md")
            if not os.path.isfile(spfad):
                fehler.append("%s/%s: SKILL.md fehlt." % (name, s))
                continue
            fm = frontmatter(io.open(spfad, encoding="utf-8").read())
            for feld in ("name", "description"):
                if not fm.get(feld):
                    fehler.append("%s/%s: %s fehlt im Frontmatter." % (name, s, feld))
            if fm.get("name") and fm["name"] != s:
                fehler.append("%s/%s: Frontmatter nennt sich %r."
                              % (name, s, fm["name"]))

    if len(set(versionen.values())) > 1:
        fehler.append("Plugins laufen auseinander: %s - sie werden zusammen "
                      "veroeffentlicht, siehe README." %
                      ", ".join("%s=%s" % kv for kv in sorted(versionen.items())))
    return fehler


def main():
    fehler = pruefe()
    for f in fehler:
        print("FEHLER: " + f)
    print("Marketplace: %d Befund(e)." % len(fehler))
    return 1 if fehler else 0


def selbsttest():
    """Baut Marketplaces im Tempverzeichnis und prueft, dass jeder Befund anschlaegt.

    Von Hand einmal rot gesehen zu haben genuegt nicht: Wer den naechsten Befund
    hinzufuegt, soll sehen, dass die bestehenden noch feuern. Die Baeume werden hier
    Feld fuer Feld aufgebaut, nicht mit derselben Funktion gelesen, die geprueft wird.
    """
    import shutil
    import tempfile

    fehler = []
    NL = chr(10)

    def schreib(pfad, text):
        with io.open(pfad, "w", encoding="utf-8", newline="") as f:
            f.write(text)

    def baue(basis, plugins, skills=None):
        """plugins: [(name, marktversion, pluginversion)]

        skills: {plugin: [(verzeichnis, frontmatter-name, mit_description)]}
        """
        os.makedirs(os.path.join(basis, ".claude-plugin"))
        markt = {"name": "t", "plugins": [
            {"name": n, "source": "./plugins/" + n, "version": mv}
            for n, mv, _ in plugins]}
        schreib(os.path.join(basis, ".claude-plugin", "marketplace.json"),
                json.dumps(markt))
        for n, _, pv in plugins:
            d = os.path.join(basis, "plugins", n, ".claude-plugin")
            os.makedirs(d)
            schreib(os.path.join(d, "plugin.json"),
                    json.dumps({"name": n, "version": pv}))
            for sdir, fmname, mit_desc in (skills or {}).get(n, [("s", "s", True)]):
                sd = os.path.join(basis, "plugins", n, "skills", sdir)
                os.makedirs(sd)
                kopf = "---" + NL + "name: " + fmname + NL
                if mit_desc:
                    kopf += "description: irgendwas" + NL
                schreib(os.path.join(sd, "SKILL.md"), kopf + "---" + NL + "Text" + NL)

    def lauf(name, plugins, skills, erwartet_teil):
        basis = tempfile.mkdtemp()
        try:
            baue(basis, plugins, skills)
            befunde = pruefe(basis)
            if erwartet_teil is None:
                if befunde:
                    fehler.append("%s: sollte gruen sein, meldet %r" % (name, befunde))
            elif not any(erwartet_teil in b for b in befunde):
                fehler.append("%s: %r nicht gemeldet, stattdessen %r"
                              % (name, erwartet_teil, befunde))
        finally:
            shutil.rmtree(basis, ignore_errors=True)

    gut = [("a", "1.0.0", "1.0.0"), ("b", "1.0.0", "1.0.0")]
    lauf("der saubere Fall ist gruen", gut, None, None)

    #  Der Befund, den "claude plugin tag" strukturell nicht finden kann: je Plugin
    #  stimmt alles, nur untereinander nicht.
    lauf("Plugins laufen auseinander",
         [("a", "1.0.0", "1.0.0"), ("b", "1.1.0", "1.1.0")], None,
         "laufen auseinander")

    lauf("Marketplace gegen plugin.json",
         [("a", "1.0.0", "1.0.0"), ("b", "1.0.0", "2.0.0")], None,
         "in plugin.json")

    lauf("Frontmatter-Name weicht vom Verzeichnis ab", gut,
         {"a": [("richtig", "falsch", True)]}, "Frontmatter nennt sich")

    lauf("description fehlt", gut, {"a": [("s", "s", False)]}, "description fehlt")

    lauf("Plugin ohne Skill", gut, {"a": []}, "kein einziger Skill")

    #  Ein Plugin ohne plugin.json: der Marketplace verspricht etwas, das es nicht gibt.
    basis = tempfile.mkdtemp()
    try:
        baue(basis, gut, None)
        shutil.rmtree(os.path.join(basis, "plugins", "b"))
        if not any("plugin.json fehlt" in b for b in pruefe(basis)):
            fehler.append("fehlendes Plugin wird nicht gemeldet")
    finally:
        shutil.rmtree(basis, ignore_errors=True)

    gesamt = 7
    for f in fehler:
        print("FEHLER: " + f)
    print("%d von %d Pruefungen bestanden." % (gesamt - len(fehler), gesamt))
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(selbsttest() if "--selbsttest" in sys.argv else main())
