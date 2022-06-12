tmux	new-session \; \
	send-keys "cd e*/src" enter "python3 service.py" \; \
	split-window -h \; \
	send-keys "cd a*/src" enter "python3 service.py" \; \
	split-window -v \; \
	send-keys "cd user-m*/src" enter "python3 service.py" \; \
	select-pane -t 0 \; \
	split-window -v \; \
	send-keys "cd user-d*/src" enter "python3 service.py" \; \
	rename-window "services" \; \
\
	new-window -n "db&test" \; \
	send-keys "sudo docker start mysqlcontainer" \; \
	split-window -h \; \
	send-keys "python3 maintest.py " \;
