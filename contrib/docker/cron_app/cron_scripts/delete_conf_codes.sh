#!/bin/sh

#set -e

process_delete_conf_codes(){
  echo "$(date) - delete conf codes"
  . /app/export_env.sh
  python3.11 /app/manage.py delete_conf_codes
  echo "finished delete conf codes"
}

process_delete_conf_codes

exit 0
