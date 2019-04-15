function pcf_app_exists {
    local app_name="$1"
    local output=`cf app ${app_name}`

    if [[ $(contains_string "${output}" "FAILED") == "true" ]]; then
        echo false
    else
        echo true
    fi
}

function pcf_bind_service {
    local app_name="$1"
    local service_name="$2"
    local json="$3"

    writeProgress "Binding app '${app_name}' to service '${service_name}'..."
    cf bs ${app_name} ${service_name} -c "${json}" || { \
        writeProgress "App '${app_name}' or service '${service_name}' not found. Cannot bind. Continuing on...";
    }
}

function pcf_create_service {
    local app_name="$1"
    local service_name="$2"
    local service_type="$3"
    local service_plan="$4"
    local delete=${5-false}

    if [[ "${delete}" == "true" ]]; then
        pcf_delete_service ${service_name}
    fi

    writeProgress "Creating service '${service_name}'..."
    cf service ${service_name} || { \
        pcf_unbind_app_from_service ${service_name} ${app_name}
        pcf_delete_service ${service_name}

        cf cs ${service_type} ${service_plan} ${service_name}
        writeProgress "Service '${service_name}' created successfully!"
    }
}

function pcf_delete_job {
    local job_name="$1"

    if [[ "$(pcf_job_exists "${job_name}")" == "true" ]]; then
        writeProgress "Deleting job '${job_name}'..."
        cf delete-job ${job_name} -f
    fi
}

function pcf_delete_service {
    local service_name="$1"

    writeProgress "Deleting service '${service_name}'..."
    cf ds ${service_name} -f || {
        writeProgress "Service '${service_name}' not found. Continuing on...";
    }

    writeProgress "Service '${service_name}' delete operation in progress! Waiting for service to be deleted..."
    until cf service ${service_name} | grep -m 1 -v "Service instance ${service_name} not found"; \
        do : echo "Searching for references to 'Service instance ${service_name} not found'..."; done; \
        writeProgress "Service '${service_name}' deleted successfully!";
}

function pcf_get_recent_logs {
    local app_name="$1"

    writeProgress "Get recent logs for app '${app_name}'..."
    cf logs ${app_name} --recent
}

function pcf_job_exists {
    local job_name="$1"
    local output=`cf jobs`

    if [[ $(contains_string "${output}" "${job_name}") == "true" ]]; then
        echo true
    else
        echo false
    fi
}

function pcf_login {
    local api_endpoint_uri="$1"
    local org_name="$2"
    local space_name="$3"
    local username="$4"
    local password="$5"

    writeProgress "Logging into PCF instance '${api_endpoint_uri}' for org '${org_name}' and space '${space_name}' via CF CLI..."
    cf login \
        -a ${api_endpoint_uri} \
        -o ${org_name} \
        -s ${space_name} \
        -u ${username} \
        -p ${password} \
        --skip-ssl-validation
}

function pcf_push {
    local app_name="$1"
    local app_host_name="$2"
    local artifact_file="$3"
    local manifest_file="$4"
    local manifest_vars_file="$5"
    local no_start="${6-false}"
    local no_route="${7-false}"

    local options=""
    if [[ "${no_route}" == "false" ]]; then
        options+="-n ${app_host_name} "
    fi

    if [[ "${no_start}" == "true" ]]; then
        options+="--no-start "
    fi

    if [[ "${no_route}" == "true" ]]; then
        options+="--no-route "
    fi

    writeProgress "Pushing app '${app_name}' to PCF with host '${app_host_name}' with options '${options}'..."
    cf push ${app_name} \
        -p ${artifact_file} \
        -f ${manifest_file} \
        --vars-file ${manifest_vars_file} \
        ${options}
}

function pcf_rename_service {
    local service_name="$1"
    local new_service_name="$2"

    writeProgress "Renaming service '${service_name}' to '${new_service_name}'..."
    cf rename-service ${service_name} ${new_service_name} || {
        writeProgress "Service '${service_name}' not found. Continuing on...";
    }
}

function pcf_restart_app {
    local app_name="$1"

    writeProgress "Restarting app '${app_name}' in PCF..."
    cf restart ${app_name}
}

function pcf_route_exists {
    local app_route_name="$1"
    local domain_name="$2"

    local pcf_app_uri="${app_route_name}.${domain_name}"
    local output=`cf apps`
    echo $(contains_string "${output}" ${pcf_app_uri})
}

function pcf_service_is_bound_to_app {
    local app_name="$1"
    local service_name="$2"
    local output=`cf service ${service_name}`

    if [[ $(contains_string "${output}" "${app_name}") == "true" ]]; then
        echo true
    else
        echo false
    fi
}

function pcf_service_exists {
    local service_name="$1"
    local output=`cf service ${service_name}`

    if [[ $(contains_string "${output}" "FAILED") == "true" ]]; then
        echo false
    else
        echo true
    fi
}

function pcf_set_health_check {
    local app_name="$1"
    local health_check_endpoint="$2"
    local health_check_invoke_timeout="$3"

    local pcf_health_check_type=http

    writeProgress "Setting PCF health check properties for app '${app_name}'..."
    cf v3-set-health-check ${app_name} ${pcf_health_check_type} \
        --endpoint ${health_check_endpoint} \
        --invocation-timeout ${health_check_invoke_timeout}
}

function pcf_start_app {
    local app_name="$1"

    writeProgress "App '${app_name}' start operation in progress! Waiting for app to start..."
    cf start ${app_name}
}

function pcf_stop_app {
    local app_name="$1"

    writeProgress "App '${app_name}' stop operation in progress! Waiting for app to stop..."
    cf stop ${app_name}
}

function pcf_unbind_app_from_service {
    local service_name="$1"
    local app_name="$2"

    writeProgress "Unbinding app '${app_name}' from service '${service_name}'..."
    cf us ${app_name} ${service_name} || { \
        writeProgress "App '${app_name}' or service '${service_name}' not found. Cannot unbind. Continuing on...";
    }
}

function pcf_unbind_apps_and_delete_service {
    local service_name="$1"
    local apps=("$@")

    pcf_unbind_apps_from_service "${service_name}" "${apps[@]}"
    pcf_delete_service "${service_name}"
}

function pcf_unbind_apps_from_service {
    local service_name="$1"
    local apps=("$@")

    for app_name in ${apps[@]}; do
        pcf_unbind_app_from_service ${service_name} ${app_name}
    done
}

function pcf_update_cups {
    local service_name="$1"
    local json="$2"

    writeProgress "Updating CUPS '${service_name}'..."
    cf uups ${service_name} -p ${json} || {
        writeProgress "CUPS '${service_name}' not found. Continuing on...";
    }
}

function pcf_update_service {
    local service_name="$1"
    local json="$2"

    cf update-service ${service_name} -c "${json}" || {
        writeProgress "Service '${service_name}' not found. Continuing on...";
    }

    if [[ $(pcf_service_exists ${service_name}) == "true" ]]; then
        writeProgress "Service ${service_name} updated successfully! Waiting for service to update to persist..."
        until cf service ${service_name} | grep -m 1 "update succeeded"; \
            do : echo "Searching for 'update succeeded'..."; done; \
            writeProgress "Service '${service_name}' update persisted successfully!";
    fi
}