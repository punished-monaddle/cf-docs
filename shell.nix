let
  # To get the sha256:
  # nix-prefetch-url --unpack https://github.com/NixOS/nixpkgs/archive/<the rev>.tar.gz
  rev = "ec942ba042dad5ef097e2ef3a3effc034241f011";
  sha256 = "sha256:01i5lznyfxyb5r7llscybv17nhbnb58p0wi62rag9jdagjwxm6a7";

  pkgs = (import (builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/${rev}.tar.gz";
    inherit sha256;
  }) {});

  pythonBase = pkgs.python314;
  python = pythonBase.withPackages (ps: [
    ps.grpcio-tools
    ps.jinja2
    ps.mypy
    ps.protobuf
    ps.pytest
    ps.pyyaml
    ps.types-protobuf
    ps.types-pyyaml
  ]);
in
pkgs.mkShell {
  packages = [
    pkgs.curl
    pkgs.gh
    pkgs.git
    pkgs.jdk25_headless
    pkgs.ncurses
    pkgs.nodejs_24
    pkgs.ruff
    pkgs.unzip
    python
  ];

  shellHook = ''
    export PATH="$PWD/node_modules/.bin:$HOME/.dpm/bin:$HOME/.daml/bin:$PATH"
    export PYTHONPATH="$PWD/src''${PYTHONPATH:+:$PYTHONPATH}"
    if [ -z "''${NODE_EXTRA_CA_CERTS:-}" ]; then
      export NODE_EXTRA_CA_CERTS="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
      if [ -r "''${NIX_SSL_CERT_FILE:-}" ]; then
        export NODE_EXTRA_CA_CERTS="$NIX_SSL_CERT_FILE"
      fi
    fi

    case " $NODE_OPTIONS " in
      *" --max-old-space-size="*) ;;
      *)
        if [ -z "$NODE_OPTIONS" ]; then
          export NODE_OPTIONS="--max-old-space-size=12288"
        else
          export NODE_OPTIONS="$NODE_OPTIONS --max-old-space-size=12288"
        fi
        ;;
    esac

    if [ "''${SKIP_NPM_INSTALL:-}" != "1" ] && [ -f package.json ] && [ ! -f node_modules/.cf-docs-ready ]; then
      echo "Installing npm dependencies..."
      if [ -f package-lock.json ]; then
        npm ci || { echo "npm install failed; run direnv reload (or re-enter nix-shell) to retry." >&2; exit 1; }
      else
        npm install || { echo "npm install failed; run direnv reload (or re-enter nix-shell) to retry." >&2; exit 1; }
      fi
      touch node_modules/.cf-docs-ready
    fi
  '';
}
