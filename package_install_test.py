import subprocess
import sys

def install_and_verify(package_name):
    print(f"\nInstalling: {package_name}")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"✅ Successfully installed: {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install: {package_name}")
        print(f"Error:\n{e.stderr}")
        return False

def main():
    tampered_file = "tampered_package_names.txt"
    try:
        with open(tampered_file, "r") as f:
            packages = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"File not found: {tampered_file}")
        return

    success, failure = [], []

    for pkg in packages:
        if install_and_verify(pkg):
            success.append(pkg)
        else:
            failure.append(pkg)

    print("\n=== Summary ===")
    print(f"✅ Installed: {success}")
    print(f"❌ Failed: {failure}")

if __name__ == "__main__":
    main()
