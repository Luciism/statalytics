# --- MAIN ---
select_window 0
window_root "./"
run_cmd "tmux rename-window 'Statalytics'"
run_cmd "OPEN_NVIM=true nix develop"

# --- WEBSITE ---
window_root "./apps/website"
new_window "Statalytics Website"
run_cmd "OPEN_NVIM=true nix develop ../../flake.nix"

# --- UTILS ---
window_root "./apps/utils"
new_window "Statalytics Utils"
run_cmd "OPEN_NVIM=true nix develop ../../flake.nix"

select_window 0
