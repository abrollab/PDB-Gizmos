# loading of file contents into memory from a file 

def extract_contents(filename):
    contents = []
    with open(filename, "r") as file:
        for lines in file:
            contents.append(lines.strip("\n"))            
    
    return contents