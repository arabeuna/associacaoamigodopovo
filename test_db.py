#!/usr/bin/env python3
"""
Script de teste para verificar o funcionamento do banco de dados PostgreSQL
"""

import os
import sys
from datetime import datetime, date
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_imports():
    """Testa se todas as dependências estão instaladas"""
    print("🔍 Testando imports...")
    
    try:
        import psycopg2
        print("✓ psycopg2 importado com sucesso")
    except ImportError as e:
        print(f"✗ Erro ao importar psycopg2: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✓ SQLAlchemy importado com sucesso")
    except ImportError as e:
        print(f"✗ Erro ao importar SQLAlchemy: {e}")
        return False
    
    try:
        from models import SessionLocal, Usuario, Atividade, Turma, Aluno, Presenca
        print("✓ Modelos importados com sucesso")
    except ImportError as e:
        print(f"✗ Erro ao importar modelos: {e}")
        return False
    
    return True

def test_connection():
    """Testa conexão com o banco de dados"""
    print("\n🔌 Testando conexão com o banco...")
    
    try:
        from models import SessionLocal, verificar_conexao
        
        if verificar_conexao():
            print("✓ Conexão com banco de dados estabelecida")
            return True
        else:
            print("✗ Falha na conexão com banco de dados")
            return False
            
    except Exception as e:
        print(f"✗ Erro ao testar conexão: {e}")
        return False

def test_tables():
    """Testa se as tabelas existem e têm dados"""
    print("\n📋 Testando tabelas...")
    
    try:
        from models import SessionLocal, Usuario, Atividade, Turma, Aluno, Presenca
        
        db = SessionLocal()
        
        # Testar tabela usuarios
        total_usuarios = db.query(Usuario).count()
        print(f"✓ Tabela usuarios: {total_usuarios} registros")
        
        # Testar tabela atividades
        total_atividades = db.query(Atividade).count()
        print(f"✓ Tabela atividades: {total_atividades} registros")
        
        # Testar tabela turmas
        total_turmas = db.query(Turma).count()
        print(f"✓ Tabela turmas: {total_turmas} registros")
        
        # Testar tabela alunos
        total_alunos = db.query(Aluno).count()
        print(f"✓ Tabela alunos: {total_alunos} registros")
        
        # Testar tabela presencas
        total_presencas = db.query(Presenca).count()
        print(f"✓ Tabela presencas: {total_presencas} registros")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"✗ Erro ao testar tabelas: {e}")
        return False

def test_queries():
    """Testa consultas básicas"""
    print("\n🔍 Testando consultas...")
    
    try:
        from models import SessionLocal, Aluno, Atividade, Turma, AlunoDAO, AtividadeDAO
        
        db = SessionLocal()
        
        # Testar busca de alunos
        alunos_ativos = db.query(Aluno).filter(Aluno.ativo == True).count()
        print(f"✓ Alunos ativos: {alunos_ativos}")
        
        # Testar busca de atividades
        atividades_ativas = db.query(Atividade).filter(Atividade.ativa == True).count()
        print(f"✓ Atividades ativas: {atividades_ativas}")
        
        # Testar busca por nome
        if alunos_ativos > 0:
            primeiro_aluno = db.query(Aluno).first()
            alunos_encontrados = AlunoDAO.buscar_por_nome(db, primeiro_aluno.nome[:10])
            print(f"✓ Busca por nome: {len(alunos_encontrados)} resultados")
        
        # Testar busca de atividades
        if atividades_ativas > 0:
            primeira_atividade = db.query(Atividade).first()
            atividade_encontrada = AtividadeDAO.buscar_por_nome(db, primeira_atividade.nome)
            if atividade_encontrada:
                print(f"✓ Busca de atividade: {atividade_encontrada.nome}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"✗ Erro ao testar consultas: {e}")
        return False

def test_relationships():
    """Testa relacionamentos entre tabelas"""
    print("\n🔗 Testando relacionamentos...")
    
    try:
        from models import SessionLocal, Aluno, Atividade, Turma
        
        db = SessionLocal()
        
        # Testar relacionamento aluno -> atividade
        aluno_com_atividade = db.query(Aluno).filter(Aluno.atividade_id.isnot(None)).first()
        if aluno_com_atividade and aluno_com_atividade.atividade:
            print(f"✓ Relacionamento aluno -> atividade: {aluno_com_atividade.nome} -> {aluno_com_atividade.atividade.nome}")
        
        # Testar relacionamento turma -> atividade
        turma_com_atividade = db.query(Turma).filter(Turma.atividade_id.isnot(None)).first()
        if turma_com_atividade and turma_com_atividade.atividade:
            print(f"✓ Relacionamento turma -> atividade: {turma_com_atividade.nome} -> {turma_com_atividade.atividade.nome}")
        
        # Testar relacionamento aluno -> turma
        aluno_com_turma = db.query(Aluno).filter(Aluno.turma_id.isnot(None)).first()
        if aluno_com_turma and aluno_com_turma.turma:
            print(f"✓ Relacionamento aluno -> turma: {aluno_com_turma.nome} -> {aluno_com_turma.turma.nome}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"✗ Erro ao testar relacionamentos: {e}")
        return False

def test_insert_update():
    """Testa operações de inserção e atualização"""
    print("\n✏️ Testando operações de escrita...")
    
    try:
        from models import SessionLocal, Aluno, PresencaDAO
        from datetime import date
        
        db = SessionLocal()
        
        # Testar inserção de aluno de teste
        aluno_teste = Aluno(
            nome="ALUNO TESTE - REMOVER",
            telefone="62 999999999",
            email="teste@teste.com",
            data_cadastro=date.today(),
            criado_por="teste_sistema"
        )
        db.add(aluno_teste)
        db.commit()
        db.refresh(aluno_teste)
        print(f"✓ Aluno de teste inserido: ID {aluno_teste.id}")
        
        # Testar atualização
        aluno_teste.observacoes = "Aluno criado para teste - remover após teste"
        db.commit()
        print("✓ Aluno de teste atualizado")
        
        # Testar inserção de presença
        presenca = PresencaDAO.registrar_presenca(
            db=db,
            aluno_id=aluno_teste.id,
            data_presenca=date.today(),
            status='P',
            registrado_por='teste_sistema'
        )
        print(f"✓ Presença de teste registrada: ID {presenca.id}")
        
        # Limpar dados de teste
        db.delete(aluno_teste)
        db.commit()
        print("✓ Dados de teste removidos")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"✗ Erro ao testar operações de escrita: {e}")
        return False

def test_performance():
    """Testa performance básica"""
    print("\n⚡ Testando performance...")
    
    try:
        from models import SessionLocal, Aluno, Atividade
        import time
        
        db = SessionLocal()
        
        # Testar tempo de consulta simples
        start_time = time.time()
        total_alunos = db.query(Aluno).count()
        query_time = time.time() - start_time
        print(f"✓ Consulta de contagem de alunos: {query_time:.3f}s")
        
        # Testar tempo de consulta com filtro
        start_time = time.time()
        alunos_ativos = db.query(Aluno).filter(Aluno.ativo == True).all()
        filter_time = time.time() - start_time
        print(f"✓ Consulta com filtro: {filter_time:.3f}s ({len(alunos_ativos)} resultados)")
        
        # Testar tempo de consulta com relacionamento
        start_time = time.time()
        alunos_com_atividade = db.query(Aluno).filter(Aluno.atividade_id.isnot(None)).all()
        relation_time = time.time() - start_time
        print(f"✓ Consulta com relacionamento: {relation_time:.3f}s ({len(alunos_com_atividade)} resultados)")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"✗ Erro ao testar performance: {e}")
        return False

def test_backup_restore():
    """Testa funcionalidade de backup (simulado)"""
    print("\n💾 Testando funcionalidade de backup...")
    
    try:
        from models import SessionLocal, Aluno, Atividade, Turma
        import json
        
        db = SessionLocal()
        
        # Simular backup de dados
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'total_alunos': db.query(Aluno).count(),
            'total_atividades': db.query(Atividade).count(),
            'total_turmas': db.query(Turma).count()
        }
        
        # Salvar backup simulado
        with open('backup_teste.json', 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"✓ Backup simulado criado: {backup_data['total_alunos']} alunos, {backup_data['total_atividades']} atividades")
        
        # Limpar arquivo de teste
        os.remove('backup_teste.json')
        print("✓ Arquivo de backup de teste removido")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"✗ Erro ao testar backup: {e}")
        return False

def main():
    """Função principal de teste"""
    print("=== Teste do Sistema de Banco de Dados PostgreSQL ===")
    print("Academia Amigo do Povo")
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Conexão", test_connection),
        ("Tabelas", test_tables),
        ("Consultas", test_queries),
        ("Relacionamentos", test_relationships),
        ("Operações de Escrita", test_insert_update),
        ("Performance", test_performance),
        ("Backup", test_backup_restore)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Erro inesperado no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSOU" if result else "✗ FALHOU"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print("-"*50)
    print(f"Total: {total} testes")
    print(f"Passou: {passed} testes")
    print(f"Falhou: {total - passed} testes")
    print(f"Taxa de sucesso: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("O sistema de banco de dados está funcionando corretamente.")
        return True
    else:
        print(f"\n⚠️ {total - passed} TESTE(S) FALHARAM")
        print("Verifique os erros acima e corrija os problemas.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
