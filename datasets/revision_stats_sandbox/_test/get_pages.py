#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import popen2
import sys
import re

# 1578|29640

import codecs

links_regex = re.compile(r"\[\[([A-Za-z0-9_: ]+)\]\]", re.IGNORECASE)
cat_regex = re.compile(r"\[\[Category:([A-Za-z0-9_ ]+)\]\]", re.IGNORECASE)
tag_regex = re.compile(r"</?\w+>", re.IGNORECASE)
lang_regex = re.compile(r"\[\[(aa:.+|ab:.+|af:.+|ak:.+|als:.+|am:.+|ang:.+|an:.+|arc:.+|ar:.+|arz:.+|ast:.+|as:.+|av:.+|ay:.+|az:.+|bar:.+|bat_smg:.+|ba:.+|bcl:.+|be:.+|be_x_old:.+|bg:.+|bh:.+|bi:.+|bm:.+|bn:.+|bo:.+|bpy:.+|br:.+|bs:.+|bug:.+|bxr:.+|ca:.+|cbk_zam:.+|cdo:.+|ceb:.+|ce:.+|cho:.+|chr:.+|ch:.+|chy:.+|co:.+|crh:.+|cr:.+|csb:.+|cs:.+|cu:.+|cv:.+|cy:.+|da:.+|diq:.+|dsb:.+|dv:.+|dz:.+|ee:.+|el:.+|eml:.+|eo:.+|es:.+|et:.+|eu:.+|ext:.+|fa:.+|ff:.+|fiu_vro:.+|fi:.+|fj:.+|fo:.+|frp:.+|fur:.+|fy:.+|gan:.+|ga:.+|gd:.+|glk:.+|gl:.+|gn:.+|got:.+|gu:.+|gv:.+|hak:.+|ha:.+|haw:.+|he:.+|hif:.+|hi:.+|ho:.+|hr:.+|hsb:.+|ht:.+|hu:.+|hy:.+|hz:.+|ia:.+|id:.+|ie:.+|ig:.+|ii:.+|ik:.+|ilo:.+|io:.+|is:.+|it:.+|iu:.+|ja:.+|jbo:.+|jv:.+|kaa:.+|kab:.+|ka:.+|kg:.+|ki:.+|kj:.+|kk:.+|kl:.+|km:.+|kn:.+|ko:.+|kr:.+|ksh:.+|ks:.+|ku:.+|kv:.+|kw:.+|ky:.+|la:.+|lbe:.+|lb:.+|lg:.+|lij:.+|li:.+|lmo:.+|ln:.+|lo:.+|lt:.+|lv:.+|map_bms:.+|mdf:.+|mg:.+|mhr:.+|mh:.+|mi:.+|mk:.+|ml:.+|mn:.+|mo:.+|mr:.+|ms:.+|mt:.+|mus:.+|myv:.+|my:.+|mzn:.+|nah:.+|nap:.+|na:.+|nds_nl:.+|nds:.+|ne:.+|new:.+|ng:.+|nn:.+|nov:.+|no:.+|nrm:.+|nv:.+|ny:.+|oc:.+|om:.+|or:.+|os:.+|pag:.+|pam:.+|pap:.+|pa:.+|pdc:.+|pih:.+|pi:.+|pl:.+|pms:.+|pnt:.+|ps:.+|pt:.+|qu:.+|rm:.+|rmy:.+|rn:.+|roa_rup:.+|roa_tara:.+|ro:.+|ru:.+|rw:.+|sah:.+|sa:.+|scn:.+|sco:.+|sc:.+|sd:.+|se:.+|sg:.+|sh:.+|simple:.+|si:.+|sk:.+|sl:.+|sm:.+|sn:.+|so:.+|sq:.+|srn:.+|sr:.+|ss:.+|stq:.+|st:.+|su:.+|sv:.+|sw:.+|szl:.+|ta:.+|tet:.+|te:.+|tg:.+|th:.+|ti:.+|tk:.+|tl:.+|tn:.+|tokipona:.+|to:.+|tpi:.+|tr:.+|ts:.+|tt:.+|tum:.+|tw:.+|ty:.+|udm:.+|ug:.+|uk:.+|ur:.+|uz:.+|vec:.+|ve:.+|vi:.+|vls:.+|vo:.+|war:.+|wa:.+|wo:.+|wuu:.+|xal:.+|xh:.+|yi:.+|yo:.+|za:.+|zea:.+|zh_classical:.+|zh_min_nan:.+|zh:.+|zh_yue:.+|zu:.+)\]\]", re.IGNORECASE)

class Revision:
    def __extract__(self, line):
        return line.split(">")[1].split("<")[0]
    
    def __init__(self, data):
        if type(data) == type([]):
            self.__parse_lines__(data)
            return
        
        fields = data.strip().split('|')
        
        title = fields[0]
        page_id = fields[1]
        self.id = fields[2]
        self.date = fields[3]
        self.time = fields[4]
        self.contributor = fields[5]
        
        if fields[5] == "None":
            self.comment = None
        else:
            self.comment = fields[6]
            
        self.major = eval(fields[7])
        
        count = int(fields[8])
        
        offset = 0
        
        if count != 0:
            self.links = fields[9:9+count]
            
            if count >= 2:
                offset += count+1
            else:
                offset += 2
        else:
            self.links = []
            offset += 2
        
        count = int(fields[8+offset])
        
        if count != 0:
            self.categories = fields[9+offset:9+offset+count]
            
            if count >= 2:
                offset += count + 1
            else:
                offset += 2
        else:
            self.categories = []
            offset += 2
        
        count = int(fields[8+offset])
        
        if count != 0:
            self.languages = fields[9+offset:9+offset+count]
            
            if count >= 2:
                offset += count + 1
        else:
            self.languages = []
            offset += 2
            
        return
        
    
    def __parse_lines__(self, lines):    
        self.contributor = None
        self.id = None
        self.timestamp = None
        self.major = True
        self.comment = None
        self.links = []
        self.categories = []
        self.languages = []
        
        for line in lines:
            tags = tag_regex.findall(line)
            
            if len(tags) == 0:
                continue
                
            if tags[0] == "<id>" and not self.id:
                self.id = self.__extract__(line)
            
            elif tags[0] == "<ip>":
                self.contributor = self.__extract__(line)
            
            elif tags[0] == "<username>":
                self.contributor = self.__extract__(line)
                
            elif tags[0] == "<timestamp>":
                self.date = self.__extract__(line).split('T')[0]
                self.time = self.__extract__(line).split('T')[1][:-1]
                
            elif tags[0] == "<comment>":
                self.comment = self.__extract__(line)
                
            elif tags[0] == "<minor />":
                self.major = False
                
        buffer = " ".join(lines)
        
        self.links = list(set(links_regex.findall(buffer)))
        self.categories = list(set(cat_regex.findall(buffer)))
        self.languages = list(set(lang_regex.findall(buffer)))
    
    def __repr__(self):
        line = "%s|%s|%s|%s|%s|%s|%u|%s|%u|%s|%u|%s" % (
            self.id, 
            self.date,
            self.time,
            self.contributor,
            self.comment,
            self.major,
            len(self.links),
            "|".join(self.links),
            len(self.categories),
            "|".join(self.categories),
            len(self.languages),
            "|".join(self.languages))
            
        return line
    
    def __str__(self):
        return self.__repr__()
        

class Page(list):
    def __init__(self, title):
        self.title = title
        self.id = None
        pass

def get_pages(r):
    lines = []
    pages = []
    
    current = None
    page = False
    
    for line in r:
        if line.strip() == "</page>":
            lines.append(line.strip())
            pages.append(current)
            continue
        
        tags = tag_regex.findall(line)
        
        if len(tags) == 0:
            continue
        
        if tags[0] == "<title>":
            current = Page(line.split(">")[1].split("<")[0])
            print >> sys.stderr, line.strip()
            page = True
            
        elif tags[0] == "<id>" and page:
            current.id = line.split(">")[1].split("<")[0]
            page = False
        
        elif tags[0] == "<revision>":
            lines = []
        
        elif tags[0] == "</revision>":
            lines.append(line.strip())
            rev = Revision(lines)
            current.append(rev)
            continue
        
        lines.append(line.strip())
    
    return pages
    
if __name__ == "__main__":
    r, w, e = popen2.popen3('7za e -so ' + sys.argv[1])
    
    pages = get_pages(r)
    
    print >> sys.stderr, "Found", len(pages), "pages"
    
    fp = open(sys.argv[1] + ".pages.dat", "w")
    
    for page in pages:
        for rev in page:
            line = "%s|%s|%s" % (page.title, page.id, rev)
            print >> fp, line
