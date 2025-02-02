{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    python-3-12-8-nixpkgs.url = "github:NixOS/nixpkgs/3df3c47c19dc90fec35359e89ffb52b34d2b0e94";
    poetry2nix.url = "github:nix-community/poetry2nix";
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
      python = inputs.python-3-12-8-nixpkgs.legacyPackages.${system}.python3;
      poetry = inputs.nixpkgs.legacyPackages.${system}.poetry;
      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
    in
    {
      devShells.${system} = {
        default = pkgs.mkShell {
          packages = [
            python
            poetry
          ];
          shellHook = ''
            # Set the PS1 variable to indicate dev environment
            PS1="\[\033[1m\]\[$(tput setaf 51)\][\[\e]0;\u@devshell: \w\a\]\u@devshell:\w]\$\[\033[0m\] "
            eval $(poetry env activate)
          '';
          installPhase = ''
            poetry install
          '';
          PYTHONPATH=self;
        };

      };
    };
}
