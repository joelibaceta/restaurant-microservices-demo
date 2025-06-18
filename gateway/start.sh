#!/bin/bash

# Primer render del template
consul-template \
  -consul-addr=consul:8500 \
  -template="/etc/consul-template/nginx.ctmpl:/etc/nginx/nginx.conf:nginx -s reload" \
  &
nginx -g "daemon off;"