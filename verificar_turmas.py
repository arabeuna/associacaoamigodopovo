#!/usr/bin/env python3
from models import *

# Inicializar conexão
db = get_db()
if db is None:
    print('❌ Não foi possível conectar ao banco de dados')
    exit(1)

print(f'Total de turmas: {db.turmas.count_documents({})}')
turmas = list(db.turmas.find().limit(10))
for t in turmas:
    print(f'- {t.get("nome", "N/A")} (ID: {t["_id"]})')