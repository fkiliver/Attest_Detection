$ErrorActionPreference = "Stop"
python -B -m py_compile (Get-ChildItem -Recurse -File eviclone_prototype,scripts -Filter *.py | ForEach-Object { $_.FullName })
@'
import eviclone_prototype
from eviclone_prototype.config import DEFAULT_MODEL, DEFAULT_BASE_URL
print("eviclone_prototype import: ok")
print("default_model:", DEFAULT_MODEL)
print("default_base_url:", DEFAULT_BASE_URL)
'@ | python -B -
