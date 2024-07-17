import os
import platform
import setuptools
import subprocess
import re

# Print out our uname for debugging purposes
uname = platform.uname()
print(uname)

# Function to run a command and print its output
def run_command(command, env=None):
    result = subprocess.run(command, env=env, check=True, capture_output=True, text=True)
    print(result.stdout)
    return result

# Ensure cffi is installed
try:
    import cffi
except ImportError:
    run_command(["pip", "install", "cffi~=1.1"])

# Install Go for OSX or Linux if needed
if uname.system == "Darwin":
    os.system("./scripts/setup-macos.sh")
elif uname.system == "Linux":
    if uname.machine == "aarch64":
        os.system("./scripts/setup-arm64.sh")
    elif uname.machine in ("armv7l", "armv6l"):
        os.system("./scripts/setup-arm6vl.sh")
    elif uname.machine == "x86_64":
        os.system("./scripts/setup-linux-64.sh")
    elif uname.machine == "i686":
        os.system("./scripts/setup-linux-32.sh")

# Add the downloaded Go compiler to PATH
old_path = os.environ["PATH"]
new_path = os.path.join(os.getcwd(), "go", "bin")
env = {"PATH": f"{new_path}:{old_path}"}
env = dict(os.environ, **env)
os.environ["PATH"] = f"{new_path}:{old_path}"

# Initialize a Go module
if not os.path.exists("go.mod"):
    run_command(["go", "mod", "init", "github.com/Isonzo/pybluemonday"], env=env)

# Clean out any existing files
run_command(["make", "clean"], env=env)

# Build the Go shared module for whatever OS we're on
run_command(["make", "so"], env=env)

# Build the CFFI headers
run_command(["make", "ffi"], env=env)

with open("pybluemonday/__init__.py", "r", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

# Setup the package
setuptools.setup(
    name="pybluemonday",
    version=version,
    author="Kevin Chung",
    author_email="kchung@nyu.edu",
    description="Python bindings for the bluemonday HTML sanitizer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Isonzo/pybluemonday",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    build_golang={"root": "github.com/Isonzo/pybluemonday"},
    ext_modules=[setuptools.Extension("pybluemonday/bluemonday", ["bluemonday.go"])],
    setup_requires=["setuptools-golang==2.7.0", "cffi~=1.1"],
    install_requires=["cffi~=1.1"],
)
