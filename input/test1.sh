#!/usr/bin/env bash

function doSomething() {
    local app_name = "$1"
    a = 5;
    b = 6;

    doSomethingElse

    ls
}

function doSomethingElse() {  }

doSomething "myappname"