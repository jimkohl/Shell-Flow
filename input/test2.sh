#!/usr/bin/env bash

function doThis() {
    local app_name = "$1"
    a = 5;
    b = 6;

    doThat

    ls
}

function doThat() {  }

doThis "myappname"