#!/bin/bash

chcon -R -t systemd_unit_file_t systemd/
chcon -t home_bin_t build_docker.sh fix_selinux.sh kill_docker.sh run_docker.sh setup.sh cron_reload_db.sh run_bots_docker.sh
chcon -t container_file_t manage.py
loginctl show-user sampre_vs | grep -q Linger=yes || (
	echo -e "\n\n\nUSER LINGER DISABLED FOR THIS USER.  VERY BAD; MUST FIX.\n\n\n" ;
	loginctl enable-linger sampre_vs
)
