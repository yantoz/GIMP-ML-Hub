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
    if ! command -v gimp; then
      echo "Please install GIMP first. Exiting"
      exit 1
    fi
    
    if [[ $(lsb_release -is) == "Ubuntu" ]]; then
      if ! command -v pip3 &> /dev/null; then
        echo "pip3 missing, installing..."
        sudo apt-get install -y python3-pip
      fi
      if ! command -v python2 &> /dev/null; then
        echo "python2 missing, installing..."
        sudo apt-get install -y python2-minimal libpython2.7
      fi
      if [ ! -d "/usr/lib/gimp/2.0/python" ]; then
        echo "gimp-python was not included with GIMP, installing..."
        # Ubuntu 20.04 no longer provides python-gtk2 and gimp-python from apt
        # Using versions from eoan as a workaround
        wget 'http://de.archive.ubuntu.com/ubuntu/pool/universe/g/gimp/gimp-python_2.10.8-2_amd64.deb' -O /tmp/gimp-python.deb
        wget 'http://de.archive.ubuntu.com/ubuntu/pool/universe/p/pygtk/python-gtk2_2.24.0-6_amd64.deb' -O /tmp/python-gtk2.deb
        sudo apt-get install -y /tmp/gimp-python.deb /tmp/python-gtk2.deb
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
      
    elif [[ $(lsb_release -is) == "Arch" ]]; then
      if ! command -v pip3 &> /dev/null; then
        echo "pip3 missing, installing..."
        sudo pacman -S python-pip --noconfirm 
      fi
      if ! command -v python2 &> /dev/null; then
        echo "python2 missing, installing..."
        sudo pacman -S python2 --noconfirm 
      fi
      if [ ! -d "/usr/lib/gimp/2.0/python" ]; then
        echo "gimp-python was not included with GIMP, installing..."
        # Arch no longer includes gimp2-python, need to use an AUR as a workaround
        # TODO: maybe support other AUR utilities besides yay also
        yay -S python2-gimp --noconfirm
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

# --user fails in Travis CI
python3 -m pip install --user -U virtualenv || python3 -m pip install -U virtualenv
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

# Register the plugins directory in GIMP settings
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
plugins_dir=$script_dir/plugins
echo Determining gimprc location...
gimprc_path=$(gimp -idf -b '(gimp-quit 1)' --verbose 2>/dev/null | grep -Po $'(?<=Parsing \')'"$HOME"'/.+gimprc' | head -1)
if [ -z "$gimprc_path" ]; then
  echo ---
  gimp -idf -b '(gimp-quit 1)' --verbose
  echo ---
  echo Could not determine gimprc location. Exiting.
  exit 1
fi
echo Registering plugins directory in $gimprc_path...
if [ ! -f "$gimprc_path" ]; then
  touch "$gimprc_path"
fi
if ! grep plug-in-path "$gimprc_path" -q; then
  echo '(plug-in-path "${gimp_dir}/plug-ins:${gimp_plug_in_dir}/plug-ins:'"$plugins_dir"'")' > $gimprc_path
elif ! grep -q "$plugins_dir" "$gimprc_path"; then
  sed -i'' -E -e 's#\(\s*plug-in-path\s+"#\0'"$plugins_dir"':#' "$gimprc_path"
else
  echo Plugins directory already registered
fi

echo -e "\n-----------Installed GIMP-ML------------\n"
