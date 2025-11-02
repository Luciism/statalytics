#!/run/current-system/sw/bin/bash

tmux new-session -d -s statalytics && tmux send-keys -t statalytics 'tmuxifier load-window statalytics.window.sh' Enter && tmux attach-session -t statalytics 
