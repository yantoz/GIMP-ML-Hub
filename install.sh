#!/bin/bash
set -e

cpuonly=0
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --cpuonly) cpuonly=1;;
    *) echo "Unknown parameter passed: $1"; exit 1;;
  esac
  shift
done

if [ -d "gimpenv" ]; then
  echo "Environment already set up!"
  exit
fi

echo -e "\n-----------Installing GIMP-ML-----------\n"

# Make sure python3, pip3, python2 and gimp-python are installed
case "$(uname -s)" in
Linux)
  if ! command -v gimp &>/dev/null; then
    echo "Please install GIMP first. Exiting."
    exit 1
  fi

  if [[ $(lsb_release -is) == "Ubuntu" ]]; then
    if ! command -v pip3 &>/dev/null; then
      echo "pip3 missing, installing..."
      sudo apt-get install -y python3-pip
    fi
    if ! command -v python2 &>/dev/null; then
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
    if ! dpkg -s gimp-python &>/dev/null; then
      echo "gimp-python missing, installing..."
      if ! sudo apt-get install -y gimp-python; then
        echo "Error: gimp-python not available from apt. Exiting."
        exit 1
      fi
    fi
    if ! command -v pip3 &>/dev/null; then
      echo "pip3 missing, installing..."
      sudo apt-get install -y python3-pip
    fi

  elif [[ $(lsb_release -is) == "Arch" ]]; then
    if ! command -v pip3 &>/dev/null; then
      echo "pip3 missing, installing..."
      sudo pacman -S python-pip --noconfirm
    fi
    if ! command -v python2 &>/dev/null; then
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
  if ! command -v gimp &>/dev/null; then
    echo "Please install GIMP first. Exiting."
    exit 1
  fi
  echo "Checking that Python 2 and Python 3 are installed..."
  python2 --version
  python3 --version
  # workaround for symlinks to GIMP binaries failing with GIMP 2.10 on macOS
  alias gimp="$(readlink "$(command -v gimp)" || command -v gimp)"
  ;;
CYGWIN* | MINGW32* | MSYS* | MINGW*)
  echo 'Use install.ps1 for installation on Windows. Exiting.'
  exit 1
  ;;
*)
  echo "Warning: unsupported operating system '$(uname)'"
  ;;
esac

# Create gimpenv with requirements.txt packages
# --user fails in Travis CI
python3 -m pip install --user -U virtualenv || python3 -m pip install -U virtualenv
python3 -m virtualenv -p python3 gimpenv
source gimpenv/bin/activate
if ! command -v python | grep gimpenv -q; then
  echo "Error: failed to activate gimpenv"
  exit 1
fi

if [ $cpuonly ] && [ "$(uname -s)" != Darwin ]; then
  get_cpu_version() {
    python -m pip install "$1==" -f https://download.pytorch.org/whl/torch_stable.html 2>&1 \
      | grep -iEo 'from versions: [^)]+' | grep -Eo '[0-9].+' | tr ', ' "\n" | grep +cpu | sort -n | tail -1
  }
  python -m pip install torch=="$(get_cpu_version torch)" torchvision=="$(get_cpu_version torchvision)" -f https://download.pytorch.org/whl/torch_stable.html
elif [ ! $cpuonly ] && [ "$(uname -s)" == Darwin ]; then
  echo "Warning: PyTorch binaries on macOS do not include CUDA support. Install from source if CUDA is needed."
fi

python -m pip install -r requirements.txt
python -c "import sys; print(f'python3_executable = \'{sys.executable}\'')" > plugins/_config.py
deactivate

# Register the plugins directory in GIMP settings
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
plugins_dir=$script_dir/plugins
echo "Determining gimprc location..."
gimprc_path=$(gimp -idf -b '(gimp-quit 1)' --verbose 2>/dev/null | grep -Eo "Parsing '$HOME/.+gimprc" | grep -Eo '/.+' | head -1)
if [ -z "$gimprc_path" ]; then
  echo ---
  gimp -idf -b '(gimp-quit 1)' --verbose
  echo ---
  echo "Could not determine gimprc location. Exiting."
  exit 1
fi
echo "Registering plugins directory in $gimprc_path..."
if [ ! -f "$gimprc_path" ]; then
  mkdir -p "$(dirname "$gimprc_path")"
  touch "$gimprc_path"
fi
if ! grep plug-in-path "$gimprc_path" -q; then
  echo '(plug-in-path "${gimp_dir}/plug-ins:${gimp_plug_in_dir}/plug-ins:'"$plugins_dir"'")' > "$gimprc_path"
elif ! grep -q "$plugins_dir" "$gimprc_path"; then
  sed -i'' -e 's|plug-in-path "|plug-in-path "'"$plugins_dir"':|' "$gimprc_path"
else
  echo "Plugins directory already registered"
fi
grep "$plugins_dir" "$gimprc_path" -q || (
  echo "Error: failed to register plugins dir in gimprc"
  exit 1
)

echo -e "\n-----------Installed GIMP-ML------------\n"
