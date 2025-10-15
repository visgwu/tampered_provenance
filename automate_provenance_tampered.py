import os
import subprocess

# Load 50 package names from your file
with open('tampered_package_names.txt', 'r') as f:
    packages = [line.strip() for line in f if line.strip()]

base_branch = 'main'

for i, package in enumerate(packages):
    version_tag = f"v0.1.{i+1}"

    # 1. Update requirements.txt
    with open('requirements.txt', 'w') as req:
        req.write(f"{package}\n")

    # 2. Commit the change
    subprocess.run(['git', 'checkout', base_branch])
    subprocess.run(['git', 'add', 'requirements.txt'])
    subprocess.run(['git', 'commit', '-m', f"Add {package} for build {version_tag}"])

    # 3. Create tag and push
    subprocess.run(['git', 'tag', version_tag])
    subprocess.run(['git', 'push'])
    subprocess.run(['git', 'push', 'origin', version_tag])

    print(f"Pushed build for: {package} with tag {version_tag}")