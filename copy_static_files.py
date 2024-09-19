import os
import shutil
import re
import glob

# Define the paths
current_directory = os.getcwd()
static_frontend_path = os.path.join(current_directory, 'static', 'frontend')
erp_dist_path = os.path.join(current_directory, '..', 'erp-front', 'dist')
templates_path = os.path.join(current_directory, 'templates', 'admin', 'index_test.html')

# 1. Remove all contents of the static/frontend directory
if os.path.exists(static_frontend_path):
    shutil.rmtree(static_frontend_path)
os.makedirs(static_frontend_path, exist_ok=True)

# 2. Copy all files from erp-front/dist to static/frontend
for item in os.listdir(erp_dist_path):
    s = os.path.join(erp_dist_path, item)
    d = os.path.join(static_frontend_path, item)
    if os.path.isdir(s):
        shutil.copytree(s, d)
    else:
        shutil.copy2(s, d)

# 3. Open static/frontend/index.html and search for the JavaScript file name
index_file_path = os.path.join(static_frontend_path, 'index.html')
if os.path.exists(index_file_path):
    with open(index_file_path, 'r') as file:
        content = file.read()
    
    # Regex to find the JS file name
    match = re.search(r'src="/static/frontend/assets/entry/(.*?\.js)"', content)
    if match:
        js_file_name = match.group(1)
        print(f"JavaScript file found: {js_file_name}")
    else:
        print("No JavaScript file found matching the pattern.")
else:
    print(f"Error: {index_file_path} does not exist.")

# 4. Modify the index_test.html file in templates/admin
if js_file_name and os.path.exists(templates_path):
    with open(templates_path, 'r') as file:
        content = file.read()
    
    # Replace the script line with the new JS file name
    new_script_line = '{% static \'frontend/assets/entry/' + js_file_name + '\' %}'
    content = re.sub(r'src="{% static \'frontend/assets/entry/.*?\.js\' %}"',
                     'src="' + new_script_line + '"', content)
    
    # Save the updated content back to index_test.html
    with open(templates_path, 'w') as file:
        file.write(content)
    print(f"Updated index_test.html with the new JS file name: {js_file_name}")
else:
    if not js_file_name:
        print("JS file name not found, cannot update index_test.html.")
    else:
        print(f"Error: {templates_path} does not exist.")