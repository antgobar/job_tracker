import os


path = os.path.abspath(os.path.join(os.getcwd(), ".env"))

with open(path) as f:
    vars = f.readlines()

for var in vars:
    stripped = var.strip()
    eq_idx = stripped.find("=")
    key = stripped[:eq_idx]
    val = stripped[eq_idx + 1:][1: -1]
    os.environ[key] = val
