#!/bin/bash

opt_user=false
opt_help=false
opt_error=false

while getopts "uh" flag; do
    case $flag in
        u) opt_user=true;;
        h) opt_help=true;;
        \?) opt_error=true; break;;
    esac
done

shift $(( $OPTIND - 1 ))

if $opt_help && $opt_error; then
    cat >&2 <<EOS
usage: $0 [-uh]

    Divide stdin authkeys into each public keys.
    -u : left user name
    -h : show this help
EOS
    $opt_error && exit 1
    exit 0
fi

while read line; do
    if $opt_user; then
        echo "$line" > `echo $line | grep -Eo '[^ ]*$'`.pub
    else
        echo "$line" > `echo $line | grep -Eo '[-.a-zA-Z0-9]*$'`.pub
    fi
done
