{ pkgs ? import <nixpkgs> { } }:
let
  python-with-packages = pkgs.python3.withPackages
    (p: with p; [
      fastapi
      uvicorn
    ]);
in
pkgs.mkShell
{

  buildInputs = with pkgs;[
    # only needed for development
    nixpkgs-fmt
    pre-commit

    # also in final package
    python-with-packages
  ];

  shellHook = ''
    export PYTHONPATH=${python-with-packages}/${python-with-packages.sitePackages}
  '';

}
