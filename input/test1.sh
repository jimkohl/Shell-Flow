#!/usr/bin/env bash

function pcf_app_exists {
    local app_name="$1"
    local output=`cf app ${app_name}`

    if [[ $(contains_string "${output}" "FAILED") == "true" ]]; then
        echo false
    else
        echo true
    fi
}

pcf_app_exists("stuff")