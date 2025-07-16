import os

dirs_to_create = [
    "backend/models",
    "backend/services",
    "backend/routers"
]

for d in dirs_to_create:
    os.makedirs(d, exist_ok=True)
    print(f"Created directory: {d}")
