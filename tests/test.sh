#!/usr/bin/env bash

run_gimp() {
  case "$(uname -s)" in
   Darwin)
     gimp "$@"
     ;;
   Linux)
     gimp "$@"
     ;;
   CYGWIN*|MINGW32*|MSYS*|MINGW*)
     /c/Program\ Files/GIMP\ 2/bin/gimp-console-*.exe "$@"
     ;;
   *)
     echo 'Other OS' 
     ;;
esac
}

# Test image:
# "GEMINI-TITAN-8 - PRELAUNCH ACTIVITY, Closeup view of Armstrong in S/C. CAPE KENNEDY, FL CN" by NASA, public domain
# https://archive.org/details/S66-24489
run_gimp -idf --verbose --batch-interpreter python-fu-eval -b 'execfile("test.py")'
echo retval: $?
if [ ! -f out.png ]; then
    echo "Test failed"
    exit 1
fi
