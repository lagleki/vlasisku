#!/bin/bash

chcon -R -t config_home_t systemd/
chcon -t home_bin_t manage.py build_docker.sh fix_selinux.sh kill_docker.sh run_docker.sh setup.sh cron_reload_db.sh run_bots_docker.sh
loginctl show-user sampre_vs | grep Linger=yes || (
	echo -e "\n\n\nUSER LINGER DISABLED FOR THIS USER.  VERY BAD; MUST FIX.\n\n\n" ;
	loginctl enable-linger sampre_vs
)
