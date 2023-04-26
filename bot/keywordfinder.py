import os
def get_lines_keyword(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                with open(filepath, 'r') as f:
                    for i, line in enumerate(f):
                        if './database/autofill.db' in line:
                            print(f'file: {filename}:{i+1}')

get_lines_keyword(os.getcwd())
