#!/bin/bash 

curl --header "Content-Type: application/x-www-form-urlencoded" \
--request POST \
--data "grant_type=password&username=superadmin&password=erebus" \
--user "ui:uiman" \
http://10.10.0.59:8080/uat/sso/oauth/token