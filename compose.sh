# sudo mkdir /run/secrets
# sudo touch /run/secrets/statalytics.env
compose2nix --project=statalytics --inputs=./docker-compose.prod.yml --output=./docker-compose.prod.nix --runtime=podman --include_env_files=true --env_files=/run/secrets/statalytics.env --ignore_missing_env_files=true

