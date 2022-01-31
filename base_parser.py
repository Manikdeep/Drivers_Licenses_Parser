import os
import sys

### Need to connect to DB

### get textfiles that are not parsed based on child parser type
def get_textdoc_paths(folder):
    re = []
    for filename in os.listdir(folder):
        re.append(os.path.join(folder, filename))
    return re

### connect to server and fectch data into local

### read the file and send the text-doc into parser

### get text-doc data and store them on table or rows

# if __name__ == '__main__':



