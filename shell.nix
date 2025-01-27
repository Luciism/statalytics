{ pkgs ? import <nixpkgs> {} }:

let
  python = pkgs.python311Full;

  statalibRequirements = python.overrideDerivation (old: {
    pname = "statalibRequirements";
    buildInputs = [ pkgs.python311 ];
    src = ./statalib/requirements.txt;
  });

  botRequirements = python.overrideDerivation (old: {
    pname = "botRequirements";
    buildInputs = [ pkgs.python311 ];
    src = ./apps/bot/requirements.txt;
  });

  trackersRequirements = python.overrideDerivation (old: {
    pname = "trackersRequirements";
    buildInputs = [ pkgs.python311 ];
    src = ./apps/trackers/requirements.txt;
  });

  utilsRequirements = python.overrideDerivation (old: {
    pname = "utilsRequirements";
    buildInputs = [ pkgs.python311 ];
    src = ./apps/utils/requirements.txt;
  });

  websiteRequirements = python.overrideDerivation (old: {
    pname = "websiteRequirements";
    buildInputs = [ pkgs.python311 ];
    src = ./apps/website/requirements.txt;
  });

in pkgs.mkShell {
  name = "statalytics-development-environment";
  buildInputs = [
    python
    statalibRequirements
    botRequirements
    trackersRequirements
    utilsRequirements
    websiteRequirements
  ];
}

