# --- MAIN ---
select_window 0
window_root "./"
run_cmd "tmux rename-window 'Statalytics'"
run_cmd "OPEN_NVIM=true DEPENDENCY_GROUP=all nix develop"

# --- WEBSITE ---
window_root "./apps/website"
new_window "Statalytics Website"
run_cmd "OPEN_NVIM=true DEPENDENCY_GROUP=website nix develop ../../"

# --- UTILS ---
window_root "./apps/utils"
new_window "Statalytics Utils"
run_cmd "OPEN_NVIM=true DEPENDENCY_GROUP=utils nix develop ../../"

select_window 0
