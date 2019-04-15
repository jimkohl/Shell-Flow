#!/usr/bin/env bash

function funcNoParens {
  echo "in funcNoParens"
}

function funcParens() {
  echo "in funcParens()"
}

funcNoFunction() {
  echo "in funcNoFunction()
}

#function doThis() {
#    local app_name = "$1"
#    a = 5;
#    b = 6;
#
#    doZ
#
#    ls
#}
#
#function doZ() {  }

doThis()

funcNoParens

funcParens

funcNoFunction