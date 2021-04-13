# Archivo usado para variables y funciones comunes a todos los scripts

import os
import re

# VARIABLES

DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data')


# FUNCIONES

def find_files_regex(filename, search_path):
    files_found = []
    regex = re.compile('.*{}.*'.format(filename))
    for root, dirs, files in os.walk(search_path):
        for file in files:
            if regex.match(file):
                files_found.append(os.path.join(root, file))

    return files_found
