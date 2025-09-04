#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database_integration_robusto import get_db_integration
import sys

print("🔍 Testando SistemaAcademia e carregamento de dados...")

try:
    # Testar get_db_integration
    print("\n📊 Testando get_db_integration()...")
    db_integration = get_db_integration()
    print(f"DB Integration: {db_integration}")
    print(f"Tipo: {type(db_integration)}")
    
    # Testar se os DAOs estão funcionando
    print("\n🔍 Testando DAOs...")
    alunos = db_integration.aluno_dao.listar_todos()
    print(f"Total de alunos via DAO: {len(alunos)}")
    
    if len(alunos) > 0:
        print("\n👥 Primeiros 3 alunos via DAO:")
        for i, aluno in enumerate(alunos[:3]):
            print(f"{i+1}. Nome: {aluno.get('nome', 'N/A')}")
            print(f"   Atividade: {aluno.get('atividade', 'N/A')}")
            print()
    
    # Agora testar a classe SistemaAcademia
    print("\n🏫 Testando SistemaAcademia...")
    
    # Importar a classe
    from app import SistemaAcademia
    
    # Criar instância
    print("Criando instância do SistemaAcademia...")
    academia_test = SistemaAcademia()
    
    print(f"Academia criada: {academia_test}")
    print(f"Alunos reais carregados: {len(academia_test.alunos_reais)}")
    
    if len(academia_test.alunos_reais) > 0:
        print("\n👥 Primeiros 3 alunos via SistemaAcademia:")
        for i, aluno in enumerate(academia_test.alunos_reais[:3]):
            print(f"{i+1}. Nome: {aluno.get('nome', 'N/A')}")
            print(f"   Atividade: {aluno.get('atividade', 'N/A')}")
            print()
    
    # Testar get_estatisticas
    print("\n📊 Testando get_estatisticas()...")
    stats = academia_test.get_estatisticas()
    print(f"Estatísticas: {stats}")
    
except Exception as e:
    print(f"❌ Erro durante teste: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Teste concluído!")