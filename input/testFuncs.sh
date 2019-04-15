#!/usr/bin/env bash

function funcNoParens {
  echo "in funcNoParens"
}

function funcParens() {
  echo "in funcParens()"
}

funcNoFunction() {
  echo "in funcNoFunction()"
}

function funcWithParams {
  local arg1="$1"
  local arg2="$2"
   echo "in funcWithParams a1=$arg1 a2=$arg2"
}

funcNoParens
funcParens
funcNoFunction
funcWithParams "v1" "v2"