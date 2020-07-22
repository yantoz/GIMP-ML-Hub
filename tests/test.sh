#!/usr/bin/env bash
set -e

run_gimp() {
  case "$(uname -s)" in
  Darwin)
    # workaround for symlinks to GIMP binaries failing with GIMP 2.10 on macOS
    "$(readlink "$(command -v gimp)" || command -v gimp)" "$@"
    ;;
  CYGWIN* | MINGW32* | MSYS* | MINGW*)
    /c/Program\ Files/GIMP\ 2/bin/gimp-console-*.exe "$@"
    ;;
  *)
    gimp "$@"
    ;;
  esac
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$script_dir"

# Test image:
# "GEMINI-TITAN-8 - PRELAUNCH ACTIVITY, Closeup view of Armstrong in S/C. CAPE KENNEDY, FL CN" by NASA, public domain
# https://archive.org/details/S66-24489
run_gimp -idf --verbose --batch-interpreter python-fu-eval -b 'execfile("test.py")'
echo retval: $?
if [ ! -f out.png ]; then
  echo "Test failed"
  exit 1
else
  echo "Test succeeded. out.png was created."
fi
