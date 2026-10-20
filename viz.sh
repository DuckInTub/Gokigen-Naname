#!/usr/bin/env bash

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <prolog|clp|asp> <board>" >&2
    exit 1
fi

case $1 in 
    prolog)
        time out=$(swipl -g main -t halt gokigen.pl < $2)
    ;;

    clp)
        time out=$(swipl -g main -t halt constraint.pl < $2)
    ;;

    asp)
        b=$2
        time asp=$(clingo -V0 gokigen.lp <(python3 -m gokigen asp gen $b) 1)
        out=$(echo "$asp" | python3 -m gokigen asp parse)
    ;;

    python)
        time out=$(python3 -m gokigen solve < $2)
    ;;

    *)
        echo "Invalid argument: $1" >&2
        echo "Valid arguments are in [prolog|clp|asp]" >&2
        exit 1
esac

python3 -m gokigen draw -o output.png $2 <(echo "$out")
xdg-open output.png