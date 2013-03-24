# coding: utf-8

import web
import re

DEFAULT_SEARCH_TERM = "mana symbols"

urls = (
    '/', 'index',
    '/s=(.+)', 'search',
    '/([0-9]{1,3}(\.[0-9]{1,2}[a-z]?)?)(?:/)?(.+)?', 'single_rule'
    )

section_re = re.compile(r"^[0-9]\. .+")
subsection_re = re.compile(r"^[0-9]{3}\. .+")
rule_re = re.compile(r"^[0-9]{3}\.[0-9]{1,2}[a-z.] .+")
example_re = re.compile(r"^Example: .+")


#parse the rules
section = ""
subsection = ""
rule = ""

rules = []

with open("rules") as rules_file:
    for line in rules_file:
        if section_re.match(line):
            section = line.upper()
        elif subsection_re.match(line):
            subsection = line.upper()
        elif rule_re.match(line):
            rules += [(section, subsection, line)]
        elif example_re.match(line):
            rules[-1] = (rules[-1][0], rules[-1][1], rules[-1][2] + line)

gloss_dict = dict()

what = 0
with open("glossary") as gloss_file:
    for line in gloss_file:
        if len(line.strip()) == 0:
            what = 0
            continue
        if what == 0:
            gloss_name = line.strip().lower()
            what = 1
        elif what == 1:
            gloss_dict[gloss_name] = line.strip()

class single_rule:
    def GET(self, rule_number, _, hl):
        render = web.template.render('templates')
        text = get_single_section(rule_number)
        if hl:
            text = highlight(hl, text)
        return render.search(text)

    def POST(self, a, b, c):
        number = web.data()

        for rule in rules:
            if re.match("^%s" % number, rule[2]):
                result = rule[2]
                break
        
        result = re.sub(r'\{([WBURG2])/([WBURGP])\}', r'<img id="glossary_mana_img" src="static/images/\1\2.jpg">', result)
        result = re.sub(r'\{([GRBUWXPTS]|([0-9]{1,2}))\}', r'<img id="glossary_mana_img" src="static/images/\1.jpg">', result)

        return result

class search:
    def GET(self, search_term):
        render = web.template.render('templates')
        return render.search(search_query(search_term))

class index:
    def GET(self):
        #return filled main page
        render = web.template.render('templates')
        return render.search(search_query(DEFAULT_SEARCH_TERM))

    def POST(self):
        search_term = web.data()
        return search_query(search_term)

def get_single_rule(number):
    for rule in rules:
        if re.match("^%s" % number, rule[2]):
            return rule[2] if len(rule[2].split()) > 4 else ""

def get_single_section(number):
    section_re = re.compile(r"^[0-9]")
    subsection_re = re.compile(r"^[0-9]{3}")
    rule_re = re.compile(r"^[0-9]{3}\.[0-9]{1,2}[a-z]?")

    if rule_re.match(number):
        where = 2
    elif subsection_re.match(number):
        where = 1
    elif section_re.match(number):
        where = 0

    found_rules = dict()
    for rule in rules:
        if re.match("^" + re.escape(number), rule[where]):
            if rule[0] not in found_rules:
                found_rules[rule[0]] = dict()
                found_rules[rule[0]][rule[1]] = [rule[2]]
            elif rule[1] not in found_rules[rule[0]]:
                found_rules[rule[0]][rule[1]] = [rule[2]]
            else:
                found_rules[rule[0]][rule[1]] += [rule[2]]

    result = ""
    for section in sorted(found_rules):
        section_no = re.match("^([0-9])\.", section).group(1)
        result += "<div id='%s' class='section'>%s" % (section_no, section)
        for subsection in sorted(found_rules[section]):
            subsection_no = re.match("^([0-9]{3})\.", subsection).group(1)
            result += "<div id='%s' class='subsection'>%s" % (subsection_no, subsection)
            for rule in sorted(found_rules[section][subsection]):
                rule_no = re.match("^([0-9]{3}\.[0-9]{1,2}[a-z]?)", rule).group(1)
                result += "<div id='%s' class='rule'>%s</div>" % (rule_no, rule)
            result += "</div>"
        result += "</div>"

    result = sub_mana_img(result)

    return result

def search_query(search_term):
        if len(search_term) < 4:
            return "too short"

        found_rules = dict()
        for rule in rules:
            if search_term.lower() in rule[2].lower():
                if rule[0] not in found_rules:
                    found_rules[rule[0]] = dict()
                    found_rules[rule[0]][rule[1]] = [highlight(search_term, rule[2])]
                elif rule[1] not in found_rules[rule[0]]:
                    found_rules[rule[0]][rule[1]] = [highlight(search_term, rule[2])]
                else:
                    found_rules[rule[0]][rule[1]] += [highlight(search_term, rule[2])]

        result = ""

        if search_term in gloss_dict:
            result += "<div class='section'>%s</div>" % gloss_dict[search_term]

        for section in sorted(found_rules):
            section_no = re.match("^([0-9])\.", section).group(1)
            result += "<div id='%s' class='section'>%s" % (section_no, section)
            for subsection in sorted(found_rules[section]):
                subsection_no = re.match("^([0-9]{3})\.", subsection).group(1)
                result += "<div id='%s' class='subsection'>%s" % (subsection_no, subsection)
                for rule in sorted(found_rules[section][subsection]):
                    rule_no = re.match("^([0-9]{3}\.[0-9]{1,2}[a-z]?)", rule).group(1)
                    result += "<div id='%s' class='rule'>%s</div>" % (rule_no, rule)
                result += "</div>"
            result += "</div>"

        result = re.sub('(rule ([0-9]{3}\.[0-9]{1,2}[a-z]?))', r'<div id="glossed" class=\2>\1</div>', result)
        #result = re.sub(r"rule'>([0-9]{3}\.[0-9]{1,2}[a-z]?\.?)", r"rule'><div class='ruleno'>\1</div>", result)
        result = re.sub(r"((sub)?section'>[0-9]{1,3}\. )(.+)", r"\1<div class='sectionno'>\3</div>", result)

        #add glossaries
        glossaries = re.findall("rule ([0-9]{3}\.[0-9]{1,2}[a-z]?)", result)
        seen = set()
        glossaries = [g for g in glossaries if g not in seen and not seen.add(g)]

        for glossary in glossaries:
            rule = get_single_rule(glossary)
            if rule:
                rule = highlight(search_term, rule)
                rule = re.sub(r'^([0-9]{3}\.[0-9]{1,2}[a-z]?\.?)', r'<i>\1</i>', rule)
                result += "<div class=glossary id=%s>%s</div>" % ("g" + glossary, rule)

        result = re.sub(r"_", r"", result)
        result = re.sub(r"\(R\)", r"®", result)
        result = re.sub(r"\(TM\)", r"™", result)
        result = re.sub(r"Example:", r"<br>Example:", result)
        result = sub_mana_img(result)

        return result

def highlight(what, text):
    return re.sub("(?i)(" + what + ")", r"<b>\1</b>", text)

def sub_mana_img(text):
        text = re.sub(r'\{([WBURG2])/([WBURGP])\}', r'<img id="mana_img" src="static/images/\1\2.jpg">', text)
        text = re.sub(r'\{([GRBUWXPTS]|([0-9]{1,2}))\}', r'<img id="mana_img" src="static/images/\1.jpg">', text)
        return text


if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()
