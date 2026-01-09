{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    python-3-nixpkgs.url =
      "github:NixOS/nixpkgs/d98abf5cf5914e5e4e9d57205e3af55ca90ffc1d";
  };

  outputs = { self, nixpkgs, poetry2nix, ... }@inputs:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      python = inputs.python-3-nixpkgs.legacyPackages.${system}.python3;
    in {
      devShells.${system} = {
        default = pkgs.mkShell {
          packages = [ python ];

          shellHook = ''
              # Set the PS1 variable to indicate dev environment
              PS1='\[\e[38;5;147m\][\u@\h\[\e[38;5;250m\]:\[\e[38;5;75m\]\w\[\e[38;5;147m\]]\[\e[38;5;250m\]\$ \[\e[0m\]'

              # Find the topmost git directory (not submodule)
              PRJ_ROOT="$(git rev-parse --show-superproject-working-tree 2>/dev/null)"
              if [ -z "$PRJ_ROOT" ]; then
                PRJ_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
              fi
              source $PRJ_ROOT/.venv/bin/activate

              uv sync
              clear

            if [ "$OPEN_NVIM" = "true" ]; then
              nvim -c 'Neotree focus left'
            fi

          '';
          PYTHONPATH = self;
        };

      };
    };
}
