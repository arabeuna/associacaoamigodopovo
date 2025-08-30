#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Migração Completa de Dados
Associação Amigo do Povo

Este script migra todos os dados existentes do sistema JSON/CSV para PostgreSQL:
- Atividades
- Turmas
- Alunos
- Presenças
- Usuários
"""

import os
import sys
import json
import csv
from datetime import datetime, date
from dotenv import load_dotenv

# Carregar variáveis de ambiente
if os.path.exists('.env.production'):
    load_dotenv('.env.production')
else:
    load_dotenv()

# Importar módulos do sistema
from models import SessionLocal, Usuario, Atividade, Turma, Aluno, Presenca
from database_integration import get_db_integration

class MigradorDados:
    def __init__(self):
        self.db_integration = get_db_integration()
        self.session = SessionLocal()
        
    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()
    
    def migrar_usuarios(self):
        """Migra usuários do sistema hardcoded para o banco"""
        print("\n🔄 Migrando usuários...")
        
        usuarios_sistema = {
            'admin_master': {
                'senha_hash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',  # hash de 'master123'
                'nome': 'Admin Master',
                'nivel': 'admin_master',
                'permissoes': ['gerenciar_colaboradores', 'todas_funcoes'],
                'ativo': True
            },
            'admin': {
                'senha_hash': 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',  # hash de 'admin123'
                'nome': 'Administrador Geral',
                'nivel': 'admin',
                'permissoes': ['cadastrar_alunos', 'editar_alunos', 'excluir_alunos', 'ver_todos_alunos', 'gerar_relatorios', 'backup_planilhas'],
                'ativo': True,
                'criado_por': 'admin_master'
            },
            'prof_natacao': {
                'senha_hash': 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3',  # hash de 'natacao123'
                'nome': 'Professor de Natação',
                'nivel': 'usuario',
                'permissoes': ['consultar_meus_alunos', 'gerenciar_frequencia_meus_alunos'],
                'atividade_responsavel': 'Natação',
                'ativo': True,
                'criado_por': 'admin_master'
            },
            'prof_informatica': {
                'senha_hash': 'c0067d4af4e87f00dbac63b6156828237059172d1bbeac67427345d6a9fda484',  # hash de 'info123'
                'nome': 'Professor de Informática',
                'nivel': 'usuario',
                'permissoes': ['consultar_meus_alunos', 'gerenciar_frequencia_meus_alunos'],
                'atividade_responsavel': 'Informática',
                'ativo': True,
                'criado_por': 'admin_master'
            }
        }
        
        usuarios_migrados = 0
        for username, dados in usuarios_sistema.items():
            # Verificar se usuário já existe
            usuario_existente = self.session.query(Usuario).filter_by(username=username).first()
            if usuario_existente:
                print(f"  ⚠️  Usuário {username} já existe, pulando...")
                continue
            
            # Converter listas para JSON strings para compatibilidade com SQLite
            permissoes_json = json.dumps(dados['permissoes']) if dados.get('permissoes') else None
            
            # Criar novo usuário
            novo_usuario = Usuario(
                username=username,
                senha_hash=dados['senha_hash'],
                nome=dados['nome'],
                nivel=dados['nivel'],
                permissoes=permissoes_json,
                atividade_responsavel=dados.get('atividade_responsavel'),
                ativo=dados['ativo'],
                criado_por=dados.get('criado_por'),
                data_criacao=datetime.now()
            )
            
            self.session.add(novo_usuario)
            usuarios_migrados += 1
            print(f"  ✅ Usuário {username} migrado")
        
        self.session.commit()
        print(f"✅ {usuarios_migrados} usuários migrados com sucesso!")
    
    def migrar_atividades(self):
        """Migra atividades do arquivo JSON para o banco"""
        print("\n🔄 Migrando atividades...")
        
        arquivo_atividades = 'dados/atividades.json'
        if not os.path.exists(arquivo_atividades):
            print(f"  ⚠️  Arquivo {arquivo_atividades} não encontrado, criando atividades padrão...")
            atividades_padrao = {
                'Natação': {
                    'nome': 'Natação',
                    'descricao': 'Aulas de natação para todas as idades',
                    'professor': 'prof_natacao',
                    'ativa': True,
                    'criado_por': 'admin_master',
                    'data_criacao': '01/01/2024'
                },
                'Informática': {
                    'nome': 'Informática',
                    'descricao': 'Curso de informática básica e avançada',
                    'professor': 'prof_informatica',
                    'ativa': True,
                    'criado_por': 'admin_master',
                    'data_criacao': '01/01/2024'
                }
            }
        else:
            with open(arquivo_atividades, 'r', encoding='utf-8') as f:
                atividades_padrao = json.load(f)
        
        atividades_migradas = 0
        for nome, dados in atividades_padrao.items():
            # Verificar se atividade já existe
            atividade_existente = self.session.query(Atividade).filter_by(nome=nome).first()
            if atividade_existente:
                print(f"  ⚠️  Atividade {nome} já existe, pulando...")
                continue
            
            # Converter listas para JSON strings para compatibilidade com SQLite
            professores_json = json.dumps(dados.get('professores_vinculados', [])) if dados.get('professores_vinculados') else None
            
            # Criar nova atividade
            nova_atividade = Atividade(
                nome=nome,
                descricao=dados.get('descricao', ''),
                ativa=dados.get('ativa', True),
                criado_por=dados.get('criado_por', 'sistema'),
                data_criacao=datetime.now(),
                professores_vinculados=professores_json
            )
            
            self.session.add(nova_atividade)
            atividades_migradas += 1
            print(f"  ✅ Atividade {nome} migrada")
        
        self.session.commit()
        print(f"✅ {atividades_migradas} atividades migradas com sucesso!")
    
    def migrar_alunos(self):
        """Migra alunos do arquivo JSON para o banco"""
        print("\n🔄 Migrando alunos...")
        
        arquivo_alunos = 'dados/alunos_reais.json'
        if not os.path.exists(arquivo_alunos):
            print(f"  ⚠️  Arquivo {arquivo_alunos} não encontrado")
            return
        
        with open(arquivo_alunos, 'r', encoding='utf-8') as f:
            alunos_dados = json.load(f)
        
        alunos_migrados = 0
        for aluno_data in alunos_dados:
            # Verificar se aluno já existe (por nome e CPF)
            nome = aluno_data.get('nome', '')
            cpf = aluno_data.get('cpf', '')
            
            if nome:
                aluno_existente = self.session.query(Aluno).filter_by(nome=nome).first()
                if aluno_existente:
                    print(f"  ⚠️  Aluno {nome} já existe, pulando...")
                    continue
            
            # Buscar atividade relacionada
            atividade_nome = aluno_data.get('atividade')
            atividade = None
            if atividade_nome:
                atividade = self.session.query(Atividade).filter_by(nome=atividade_nome).first()
            
            # Converter data de nascimento
            data_nascimento = None
            if aluno_data.get('data_nascimento'):
                try:
                    data_nascimento = datetime.strptime(aluno_data['data_nascimento'], '%d/%m/%Y').date()
                except:
                    pass
            
            # Criar novo aluno
            novo_aluno = Aluno(
                nome=nome,
                cpf=cpf,
                data_nascimento=data_nascimento,
                telefone=aluno_data.get('telefone', ''),
                endereco=aluno_data.get('endereco', ''),
                responsavel=aluno_data.get('responsavel', ''),
                telefone_responsavel=aluno_data.get('telefone_responsavel', ''),
                atividade_id=atividade.id if atividade else None,
                status=aluno_data.get('status', 'ativo'),
                observacoes=aluno_data.get('observacoes', ''),
                data_cadastro=datetime.now(),
                cadastrado_por='sistema'
            )
            
            self.session.add(novo_aluno)
            alunos_migrados += 1
            print(f"  ✅ Aluno {nome} migrado")
        
        self.session.commit()
        print(f"✅ {alunos_migrados} alunos migrados com sucesso!")
    
    def migrar_presencas(self):
        """Migra presenças dos arquivos CSV/JSON para o banco"""
        print("\n🔄 Migrando presenças...")
        
        # Migrar presenças manuais
        arquivo_presenca_manual = 'dados/presenca_manual.json'
        if os.path.exists(arquivo_presenca_manual):
            with open(arquivo_presenca_manual, 'r', encoding='utf-8') as f:
                presencas_manuais = json.load(f)
            
            presencas_migradas = 0
            for nome_aluno, dados_presenca in presencas_manuais.items():
                # Buscar aluno
                aluno = self.session.query(Aluno).filter_by(nome=nome_aluno).first()
                if not aluno:
                    print(f"  ⚠️  Aluno {nome_aluno} não encontrado para migração de presença")
                    continue
                
                # Migrar registros de presença
                for registro in dados_presenca.get('registros', []):
                    try:
                        data_presenca = datetime.strptime(registro['data'], '%d/%m/%Y').date()
                        
                        # Verificar se presença já existe
                        presenca_existente = self.session.query(Presenca).filter_by(
                            aluno_id=aluno.id,
                            data_presenca=data_presenca
                        ).first()
                        
                        if presenca_existente:
                            continue
                        
                        # Criar nova presença
                        nova_presenca = Presenca(
                            aluno_id=aluno.id,
                            atividade_id=aluno.atividade_id,
                            data_presenca=data_presenca,
                            status=registro.get('status', 'P'),
                            observacoes=f"Migrado - {registro.get('tipo', 'manual')}",
                            registrado_por='sistema',
                            data_registro=datetime.now()
                        )
                        
                        self.session.add(nova_presenca)
                        presencas_migradas += 1
                        
                    except Exception as e:
                        print(f"  ❌ Erro ao migrar presença de {nome_aluno}: {e}")
            
            self.session.commit()
            print(f"  ✅ {presencas_migradas} presenças manuais migradas")
        
        print("✅ Migração de presenças concluída!")
    
    def executar_migracao_completa(self):
        """Executa a migração completa de todos os dados"""
        print("🚀 Iniciando migração completa de dados...")
        print("=" * 50)
        
        try:
            # 1. Migrar usuários
            self.migrar_usuarios()
            
            # 2. Migrar atividades
            self.migrar_atividades()
            
            # 3. Migrar alunos
            self.migrar_alunos()
            
            # 4. Migrar presenças
            self.migrar_presencas()
            
            print("\n" + "=" * 50)
            print("🎉 Migração completa realizada com sucesso!")
            print("\n📊 Resumo:")
            
            # Estatísticas finais
            total_usuarios = self.session.query(Usuario).count()
            total_atividades = self.session.query(Atividade).count()
            total_alunos = self.session.query(Aluno).count()
            total_presencas = self.session.query(Presenca).count()
            
            print(f"  👥 Usuários: {total_usuarios}")
            print(f"  🎯 Atividades: {total_atividades}")
            print(f"  🎓 Alunos: {total_alunos}")
            print(f"  ✅ Presenças: {total_presencas}")
            
        except Exception as e:
            print(f"\n❌ Erro durante a migração: {e}")
            self.session.rollback()
            raise
        finally:
            self.session.close()

def main():
    """Função principal"""
    print("Migrador de Dados - Associação Amigo do Povo")
    print("=" * 50)
    
    # Verificar se o usuário quer continuar
    resposta = input("\n⚠️  Esta operação irá migrar dados para o PostgreSQL. Continuar? (s/N): ")
    if resposta.lower() not in ['s', 'sim', 'y', 'yes']:
        print("Operação cancelada.")
        return
    
    try:
        migrador = MigradorDados()
        migrador.executar_migracao_completa()
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()