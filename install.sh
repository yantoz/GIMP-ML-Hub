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

if [ "$(uname)" == "Linux" ]; then
  if [[ $(lsb_release -rs) == "18.04" ]]; then #for ubuntu 18.04
    sudo apt-get install python3-minimal
  elif [[ $(lsb_release -rs) == "20.04" ]]; then #for ubuntu 20.04
    sudo apt-get install python3-minimal
    wget https://bootstrap.pypa.io/get-pip.py
    python3 get-pip.py
  elif [[ $(lsb_release -rs) == "10" ]]; then #for debian 10
    sudo apt-get install gimp-python
    wget https://bootstrap.pypa.io/get-pip.py
    python3 get-pip.py
  fi
elif [ "$(uname)" != "Darwin" ]; then
  echo "Warning: unsupported system '$(uname)'"
fi

python3 -m pip install --user --upgrade virtualenv
python3 -m virtualenv -p python3 gimpenv
source gimpenv/bin/activate

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
