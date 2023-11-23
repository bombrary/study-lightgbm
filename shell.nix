# shell.nix
{ pkgs ? import <nixpkgs> {} }:
let
  my-python-packages = ps: with ps; [
    pandas
    selenium
    beautifulsoup4
    numpy
    scikit-learn
    requests
    lightgbm
    matplotlib
    graphviz
    # other python packages
  ];
  my-python = pkgs.python311.withPackages my-python-packages;
in my-python.env
