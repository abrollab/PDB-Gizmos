import requests
from moltools.pdbeditor.PdbEditor import PdbEditor

r = requests.get('https://files.rcsb.org/view/3SN6.pdb')
with open("3SN6.pdb", 'w') as f:
    f.write(r.text)

    

editor = PdbEditor("3SN6.pdb")
x = editor.pdbfile
print(x) # displays all content 

