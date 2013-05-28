#!/usr/bin/python -u

import sys
import subprocess
import BeautifulSoup

def get_cities(filename):
    begin_tag = "<node "
    end_tag = "</node>"
    found = False
    
    seen = set([])
    line_count = 0
    
    fp_in = subprocess.Popen(['bunzip2', '-c', filename], stdout=subprocess.PIPE)
    
    for line in fp_in.stdout:
        line = line.strip()
        
        line_count += 1
        
        if found:
            node.append(line)
        
        if line[:len(begin_tag)] == begin_tag and line[-2:] != "/>":
            found = True
            node = [line.strip()]
            
        if found and line[:len(end_tag)] == end_tag:
            found = False
            node = "\n".join(node)
            soup = BeautifulSoup.BeautifulSoup(node)
            
            for tag in soup.findAll("tag"):
                if tag["k"] == "is_in":
                    print node
                    
    print line_count
    
if __name__ == "__main__":
    get_cities(sys.argv[1])
