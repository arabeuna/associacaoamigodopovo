#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar problemas no cadastro de alunos
"""

import os
import sys
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv('.env.production')

from database_integration import DatabaseIntegration
from models import Atividade, Turma, Aluno

def debug_cadastro_aluno():
    """Testa o cadastro de um aluno e identifica problemas"""
    print("🔍 Iniciando debug do cadastro de aluno...")
    
    try:
        # Inicializar integração com banco
        db_integration = DatabaseIntegration()
        print("✅ Conexão com banco estabelecida")
        
        # Verificar atividades disponíveis
        print("\n📋 Verificando atividades disponíveis:")
        atividades = db_integration.db.query(Atividade).all()
        if atividades:
            for atividade in atividades[:5]:  # Mostrar apenas as primeiras 5
                print(f"  - {atividade.nome} (ID: {atividade.id})")
        else:
            print("  ❌ Nenhuma atividade encontrada!")
            return
        
        # Verificar turmas disponíveis
        print("\n🏫 Verificando turmas disponíveis:")
        turmas = db_integration.db.query(Turma).all()
        if turmas:
            for turma in turmas[:5]:  # Mostrar apenas as primeiras 5
                print(f"  - {turma.nome} (ID: {turma.id}, Atividade: {turma.atividade.nome if turma.atividade else 'N/A'})")
        else:
            print("  ❌ Nenhuma turma encontrada!")
            return
        
        # Testar cadastro de aluno
        print("\n👤 Testando cadastro de aluno...")
        dados_teste = {
            'nome': 'Teste Debug Usuario',
            'telefone': '11999888777',
            'email': 'teste.debug@email.com',
            'endereco': 'Rua de Teste, 123',
            'data_nascimento': '1990-01-01',
            'titulo_eleitor': '123456789',
            'atividade': atividades[0].nome,  # Usar primeira atividade
            'turma': turmas[0].nome,  # Usar primeira turma
            'status_frequencia': 'Ativo',
            'observacoes': 'Teste de debug'
        }
        
        print(f"Dados do teste: {dados_teste}")
        
        # Tentar salvar
        aluno_id = db_integration.salvar_aluno_db(dados_teste)
        
        if aluno_id:
            print(f"✅ Aluno salvo com sucesso! ID: {aluno_id}")
            
            # Verificar se foi realmente salvo
            aluno_salvo = db_integration.db.query(Aluno).filter(Aluno.id == aluno_id).first()
            if aluno_salvo:
                print(f"✅ Confirmado: Aluno '{aluno_salvo.nome}' está no banco")
                
                # Remover aluno de teste
                db_integration.db.delete(aluno_salvo)
                db_integration.db.commit()
                print("🗑️ Aluno de teste removido")
            else:
                print("❌ Aluno não foi encontrado no banco após salvamento")
        else:
            print("❌ Falha ao salvar aluno")
            
    except Exception as e:
        print(f"❌ Erro durante debug: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            db_integration.db.close()
        except:
            pass

if __name__ == "__main__":
    debug_cadastro_aluno()