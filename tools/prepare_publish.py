"""One-time, idempotent cleanup for the current publication data."""
from db import execute


TEAM_ORDER = [
    "Mirelis Arocho Salgado", "Coralys Vélez", "Luis O. Díaz",
    "Denitza Tejada", "Winedys Caraballo", "Jeannette Rodríguez",
    "Ashley Echevarría", "Paola Muñoz", "Thaís Huertas",
    "Jorealys Valentín", "Pamela Cancel", "Khiara Rivera",
    "Grissheina Martínez", "Fabiola Berrocal", "Andrea García",
    "Dra. Rocío Martínez", "Elba Méndez Barrios", "Mayra Pagán",
    "Keishla M. Sanabria", "Nathan R. Lugo",
]

for position, name in enumerate(TEAM_ORDER):
    execute("UPDATE team SET sort=? WHERE name=?", (position, name))

# Retain accidental duplicate posts as editable drafts instead of deleting data.
execute(
    "UPDATE articles SET status='draft' WHERE slug IN (?, ?)",
    ("jugar-con-burbujas-para-el-soplo-2", "jugar-con-burbujas-para-el-soplo-3"),
)
