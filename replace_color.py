import os
import glob

directory = r"C:\Projects\invest_in_georgia"
files_to_check = []

for root, dirs, files in os.walk(directory):
    if 'staticfiles' in root or 'temp_extract' in root or 'venv' in root or '.git' in root:
        continue
    for file in files:
        if file.endswith('.html') or file.endswith('.css') or file.endswith('.js'):
            files_to_check.append(os.path.join(root, file))

for file_path in files_to_check:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '#ec1c24' in content or '#EC1C24' in content:
            new_content = content.replace('#ec1c24', '#cb2c39').replace('#EC1C24', '#cb2c39')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {file_path}")
    except Exception as e:
        print(f"Failed to read/write {file_path}: {e}")
