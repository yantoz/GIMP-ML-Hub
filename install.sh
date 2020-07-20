#!/bin/bash
set -e

cpuonly=0
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --cpuonly) cpuonly=1;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [ -d "gimpenv" ]; then
  echo "Environment already set up!"
  exit
fi

echo -e "\n-----------Installing GIMP-ML-----------\n"

case "$(uname -s)" in
  Linux)
    if [[ $(lsb_release -is) == "Ubuntu" ]]; then
      if ! command -v pip3 &> /dev/null; then
        echo "pip3 missing, installing..."
        sudo apt-get install -y python3-pip
      fi
    elif [[ $(lsb_release -is) == "Debian" ]]; then
      if ! dpkg -s gimp-python &> /dev/null; then
        echo "gimp-python missing, installing..."
        sudo apt-get install -y gimp-python
      fi
      if ! command -v pip3 &> /dev/null; then
        echo "pip3 missing, installing..."
        sudo apt-get install -y python3-pip
      fi
    else
      echo "Warning: unknown Linux distribution '$(lsb_release -is)'"
    fi
    ;;
  Darwin) # MacOS
    ;;
  CYGWIN*|MINGW32*|MSYS*|MINGW*)
    echo 'Use install.ps1 for installation on Windows. Exiting.'
    exit 1
    ;;
  *)
    echo "Warning: unsupported operating system '$(uname)'"
    ;;
esac

python3 -m pip install --user --upgrade virtualenv
python3 -m virtualenv -p python3 gimpenv
source gimpenv/bin/activate
if ! command -v python | grep gimpenv -q; then
  echo "Error: failed to activate gimpenv"
  exit 1
fi

if [ $cpuonly ]; then
  get_cpu_version() {
    python -m pip install "$1==" -f https://download.pytorch.org/whl/torch_stable.html 2>&1 \
      | grep -iPo '(?<=from versions: )[^)]+' | tr ', ' "\n" | grep +cpu | sort -n | tail -1
  }
  python -m pip install torch=="$(get_cpu_version torch)" torchvision=="$(get_cpu_version torchvision)" -f https://download.pytorch.org/whl/torch_stable.html
fi

python -m pip install -r requirements.txt
python -c "import sys; print(f'python3_executable = \'{sys.executable}\'')" > plugins/_config.py
deactivate

echo -e "\n-----------Installed GIMP-ML------------\n"
