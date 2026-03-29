# --- MAIN ---
select_window 0
window_root "./"
run_cmd "tmux rename-window 'Statalytics'"
run_cmd "OPEN_NVIM=true DEPENDENCY_GROUP=all nix develop"

split_h 25
select_pane 1
run_cmd "docker compose -f docker-compose.dev.yml up --build bot"

select_pane 0

# --- WEBSITE ---
window_root "./apps/website"
new_window "Statalytics Website"
run_cmd "OPEN_NVIM=true DEPENDENCY_GROUP=website nix develop ../../"

split_h 25
select_pane 1
run_cmd "cd ../../"
run_cmd "docker compose -f docker-compose.dev.yml up --build website"

select_pane 0

# --- UTILS ---
window_root "./apps/utils"
new_window "Statalytics Utils"
run_cmd "OPEN_NVIM=true DEPENDENCY_GROUP=utils nix develop ../../"

split_h 25
select_pane 1
run_cmd "cd ../../"
run_cmd "docker compose -f docker-compose.dev.yml up --build utils"

select_pane 0

# --- CLOUDFLARED ---
window_root "./"
new_window "Cloudflared"
run_cmd "cloudflared tunnel run"

select_window 0
