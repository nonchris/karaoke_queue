{ lib
, buildPythonPackage

  # propagates
, fastapi
, uvicorn
}:
buildPythonPackage rec {

  pname = "karaoke_queue";

  # get version from version.py
  version = (lib.strings.removePrefix ''__version__ = "''
    (lib.strings.removeSuffix ''
      "
    ''
      (builtins.readFile ./src/karaoke_queue/version.py)));

  src = ./.;

  propagatedBuildInputs = [
    fastapi
    uvicorn
  ];

  doCheck = false;

  meta = with lib; {
    description = "A queue for karaoke";
    homepage = "https://github.com/nonchris/karaoke_queuei";
    maintainers = with maintainers; [ nonchris ];
  };

}
