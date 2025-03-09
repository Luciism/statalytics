# {
#   description = "Construct development shell from requirements.txt";
#
#   inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
#
#   inputs.pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
#
#   outputs =
#     { nixpkgs, pyproject-nix, ... }:
#     let
#       # Load/parse requirements.txt
#       project = pyproject-nix.lib.project.loadRequirementsTxt { projectRoot = ./dev;  };
#
#       pkgs = nixpkgs.legacyPackages.x86_64-linux;
#       python = pkgs.python3;
#
#       pythonEnv =
#         # Assert that versions from nixpkgs matches what's described in requirements.txt
#         # In projects that are overly strict about pinning it might be best to remove this assertion entirely.
#         # assert project.validators.validateVersionConstraints { inherit python; } == { };
#         (
#           # Render requirements.txt into a Python withPackages environment
#           pkgs.python3.withPackages (project.renderers.withPackages { inherit python; })
#         );
#
#     in
#     {
#       devShells.x86_64-linux.default = pkgs.mkShell { packages = [ pythonEnv ]; };
#     };
# }
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    python-3-11-11-nixpkgs.url = "github:NixOS/nixpkgs/d98abf5cf5914e5e4e9d57205e3af55ca90ffc1d";
  };

  outputs =
    {
      self,
      nixpkgs,
      poetry2nix,
      ...
    }@inputs:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      python = inputs.python-3-11-11-nixpkgs.legacyPackages.${system}.python3;
    in
    {
      devShells.${system} = {
        default = pkgs.mkShell {
          packages = [
            python
          ];
          shellHook = ''
            # Set the PS1 variable to indicate dev environment
            PS1='\[\e[38;5;147m\][\u@\h\[\e[38;5;250m\]:\[\e[38;5;75m\]\w\[\e[38;5;147m\]]\[\e[38;5;250m\]\$ \[\e[0m\]'
            source .venv/bin/activate
            uv sync
            clear
          '';
         PYTHONPATH=self;
        };

      };
    };
}
