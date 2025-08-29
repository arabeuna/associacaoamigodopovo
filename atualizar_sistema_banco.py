#!/usr/bin/env python3
"""
Script para atualizar o sistema para usar banco de dados PostgreSQL
Academia Amigo do Povo
"""

import os
import json
from datetime import datetime
from sqlalchemy import text
from models import SessionLocal, Usuario, Aluno, Atividade, Presenca, Turma

def criar_sistema_banco():
    """Cria uma nova classe SistemaAcademia que usa banco de dados"""
    
    codigo_novo = '''
class SistemaAcademia:
    def __init__(self):
        self.db = SessionLocal()
        print("🗄️ Sistema conectado ao banco de dados PostgreSQL")
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def carregar_alunos(self):
        """Carrega alunos do banco de dados"""
        try:
            alunos = self.db.query(Aluno).filter(Aluno.ativo == True).all()
            return [
                {
                    'id': aluno.id,
                    'nome': aluno.nome,
                    'telefone': aluno.telefone,
                    'endereco': aluno.endereco,
                    'email': aluno.email,
                    'data_nascimento': aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'A definir',
                    'data_cadastro': aluno.data_cadastro.strftime('%d/%m/%Y') if aluno.data_cadastro else 'A definir',
                    'atividade': aluno.atividade.nome if aluno.atividade else 'A definir',
                    'turma': aluno.turma.nome if aluno.turma else 'A definir',
                    'status_frequencia': aluno.status_frequencia or 'Sem dados',
                    'observacoes': aluno.observacoes or ''
                }
                for aluno in alunos
            ]
        except Exception as e:
            print(f"❌ Erro ao carregar alunos: {e}")
            return []
    
    def adicionar_aluno(self, dados_aluno):
        """Adiciona um novo aluno no banco de dados"""
        try:
            # Buscar atividade
            atividade_id = None
            if dados_aluno.get('atividade') and dados_aluno['atividade'] != 'A definir':
                atividade = self.db.query(Atividade).filter(Atividade.nome == dados_aluno['atividade']).first()
                if atividade:
                    atividade_id = atividade.id
            
            # Converter data de nascimento
            data_nascimento = None
            if dados_aluno.get('data_nascimento') and dados_aluno['data_nascimento'] != 'A definir':
                try:
                    if '/' in dados_aluno['data_nascimento']:
                        data_nascimento = datetime.strptime(dados_aluno['data_nascimento'], '%d/%m/%Y').date()
                    else:
                        data_nascimento = datetime.strptime(dados_aluno['data_nascimento'], '%Y-%m-%d').date()
                except:
                    pass
            
            # Converter data de cadastro
            data_cadastro = None
            if dados_aluno.get('data_cadastro'):
                try:
                    if '/' in dados_aluno['data_cadastro']:
                        data_cadastro = datetime.strptime(dados_aluno['data_cadastro'], '%d/%m/%Y').date()
                    else:
                        data_cadastro = datetime.strptime(dados_aluno['data_cadastro'], '%Y-%m-%d').date()
                except:
                    data_cadastro = datetime.now().date()
            
            # Criar aluno
            novo_aluno = Aluno(
                nome=dados_aluno['nome'],
                telefone=dados_aluno.get('telefone'),
                endereco=dados_aluno.get('endereco'),
                email=dados_aluno.get('email'),
                data_nascimento=data_nascimento,
                data_cadastro=data_cadastro,
                atividade_id=atividade_id,
                turma_id=None,
                status_frequencia=dados_aluno.get('status_frequencia', 'Novo cadastro'),
                observacoes=dados_aluno.get('observacoes'),
                ativo=True,
                data_criacao=datetime.now(),
                criado_por=dados_aluno.get('criado_por', 'sistema')
            )
            
            self.db.add(novo_aluno)
            self.db.commit()
            self.db.refresh(novo_aluno)
            
            print(f"✅ Aluno {dados_aluno['nome']} adicionado com sucesso!")
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erro ao adicionar aluno: {e}")
            return False
    
    def atualizar_aluno(self, aluno_id, dados_atualizados):
        """Atualiza um aluno existente no banco de dados"""
        try:
            aluno = self.db.query(Aluno).filter(Aluno.id == aluno_id).first()
            if not aluno:
                return False
            
            # Buscar atividade
            atividade_id = None
            if dados_atualizados.get('atividade') and dados_atualizados['atividade'] != 'A definir':
                atividade = self.db.query(Atividade).filter(Atividade.nome == dados_atualizados['atividade']).first()
                if atividade:
                    atividade_id = atividade.id
            
            # Atualizar campos
            if 'nome' in dados_atualizados:
                aluno.nome = dados_atualizados['nome']
            if 'telefone' in dados_atualizados:
                aluno.telefone = dados_atualizados['telefone']
            if 'email' in dados_atualizados:
                aluno.email = dados_atualizados['email']
            if 'endereco' in dados_atualizados:
                aluno.endereco = dados_atualizados['endereco']
            if 'observacoes' in dados_atualizados:
                aluno.observacoes = dados_atualizados['observacoes']
            
            # Atualizar atividade
            if atividade_id is not None:
                aluno.atividade_id = atividade_id
            
            # Converter data de nascimento
            if dados_atualizados.get('data_nascimento') and dados_atualizados['data_nascimento'] != 'A definir':
                try:
                    if '/' in dados_atualizados['data_nascimento']:
                        aluno.data_nascimento = datetime.strptime(dados_atualizados['data_nascimento'], '%d/%m/%Y').date()
                    else:
                        aluno.data_nascimento = datetime.strptime(dados_atualizados['data_nascimento'], '%Y-%m-%d').date()
                except:
                    pass
            
            self.db.commit()
            print(f"✅ Aluno {aluno.nome} atualizado com sucesso!")
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erro ao atualizar aluno: {e}")
            return False
    
    def remover_aluno(self, aluno_id):
        """Remove um aluno (marca como inativo)"""
        try:
            aluno = self.db.query(Aluno).filter(Aluno.id == aluno_id).first()
            if not aluno:
                return False
            
            aluno.ativo = False
            self.db.commit()
            print(f"✅ Aluno {aluno.nome} removido com sucesso!")
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erro ao remover aluno: {e}")
            return False
    
    def registrar_presenca(self, nome_aluno, data_hora=None, observacoes=''):
        """Registra presença de um aluno no banco de dados"""
        try:
            if not data_hora:
                data_hora = datetime.now()
            
            # Buscar aluno
            aluno = self.db.query(Aluno).filter(
                Aluno.nome.ilike(f"%{nome_aluno}%"),
                Aluno.ativo == True
            ).first()
            
            if not aluno:
                return False, "Aluno não encontrado"
            
            # Verificar se já existe presença para esta data
            data_presenca = data_hora.date()
            presenca_existente = self.db.query(Presenca).filter(
                Presenca.aluno_id == aluno.id,
                Presenca.data_presenca == data_presenca
            ).first()
            
            if presenca_existente:
                return False, f"Presença já registrada para {nome_aluno} em {data_presenca.strftime('%d/%m/%Y')}"
            
            # Criar presença
            nova_presenca = Presenca(
                aluno_id=aluno.id,
                data_presenca=data_presenca,
                horario=data_hora.time(),
                turma_id=aluno.turma_id,
                atividade_id=aluno.atividade_id,
                status='P',
                observacoes=observacoes,
                tipo_registro='MANUAL',
                data_registro=datetime.now(),
                registrado_por='sistema'
            )
            
            self.db.add(nova_presenca)
            self.db.commit()
            
            print(f"✅ Presença registrada: {nome_aluno} em {data_presenca.strftime('%d/%m/%Y')}")
            return True, f"Presença registrada com sucesso para {nome_aluno}!"
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erro ao registrar presença: {e}")
            return False, f"Erro ao registrar presença: {str(e)}"
    
    def carregar_presencas(self, data_inicio=None, data_fim=None):
        """Carrega presenças do banco de dados"""
        try:
            query = self.db.query(Presenca).join(Aluno)
            
            if data_inicio:
                query = query.filter(Presenca.data_presenca >= data_inicio)
            if data_fim:
                query = query.filter(Presenca.data_presenca <= data_fim)
            
            presencas = query.all()
            
            return [
                {
                    'id': presenca.id,
                    'aluno_nome': presenca.aluno.nome,
                    'data_presenca': presenca.data_presenca.strftime('%d/%m/%Y'),
                    'horario': presenca.horario.strftime('%H:%M') if presenca.horario else '',
                    'status': presenca.status,
                    'observacoes': presenca.observacoes or '',
                    'registrado_por': presenca.registrado_por or 'sistema'
                }
                for presenca in presencas
            ]
            
        except Exception as e:
            print(f"❌ Erro ao carregar presenças: {e}")
            return []
    
    def get_estatisticas(self, filtro_atividade=None):
        """Obtém estatísticas do banco de dados"""
        try:
            stats = {
                'total_alunos': 0,
                'total_atividades': 0,
                'total_presencas_hoje': 0,
                'atividades': []
            }
            
            # Total de alunos
            query_alunos = self.db.query(Aluno).filter(Aluno.ativo == True)
            if filtro_atividade:
                query_alunos = query_alunos.join(Atividade).filter(Atividade.nome == filtro_atividade)
            stats['total_alunos'] = query_alunos.count()
            
            # Total de atividades
            stats['total_atividades'] = self.db.query(Atividade).filter(Atividade.ativa == True).count()
            
            # Presenças de hoje
            hoje = datetime.now().date()
            query_presencas = self.db.query(Presenca).filter(Presenca.data_presenca == hoje)
            if filtro_atividade:
                query_presencas = query_presencas.join(Aluno).join(Atividade).filter(Atividade.nome == filtro_atividade)
            stats['total_presencas_hoje'] = query_presencas.count()
            
            # Atividades com contadores
            atividades = self.db.query(Atividade).filter(Atividade.ativa == True).all()
            for atividade in atividades:
                total_alunos_atividade = self.db.query(Aluno).filter(
                    Aluno.atividade_id == atividade.id,
                    Aluno.ativo == True
                ).count()
                
                presencas_hoje_atividade = self.db.query(Presenca).join(Aluno).filter(
                    Presenca.data_presenca == hoje,
                    Aluno.atividade_id == atividade.id
                ).count()
                
                stats['atividades'].append({
                    'nome': atividade.nome,
                    'total_alunos': total_alunos_atividade,
                    'presencas_hoje': presencas_hoje_atividade
                })
            
            return stats
            
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            return {
                'total_alunos': 0,
                'total_atividades': 0,
                'total_presencas_hoje': 0,
                'atividades': []
            }
'''
    
    return codigo_novo

def atualizar_app_py():
    """Atualiza o app.py para usar o banco de dados"""
    try:
        # Ler o arquivo atual
        with open('app.py', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Substituir a classe SistemaAcademia
        inicio_classe = conteudo.find('class SistemaAcademia:')
        if inicio_classe == -1:
            print("❌ Classe SistemaAcademia não encontrada no app.py")
            return False
        
        # Encontrar o final da classe
        fim_classe = conteudo.find('\n\n', inicio_classe)
        if fim_classe == -1:
            fim_classe = len(conteudo)
        
        # Substituir a classe
        nova_classe = criar_sistema_banco()
        conteudo_atualizado = (
            conteudo[:inicio_classe] + 
            nova_classe + 
            conteudo[fim_classe:]
        )
        
        # Fazer backup do arquivo original
        with open('app_backup.py', 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        # Salvar o arquivo atualizado
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(conteudo_atualizado)
        
        print("✅ app.py atualizado com sucesso!")
        print("📁 Backup salvo como app_backup.py")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar app.py: {e}")
        return False

def atualizar_rotas():
    """Atualiza as rotas para usar o banco de dados"""
    try:
        # Ler o arquivo atual
        with open('app.py', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Atualizar rota de cadastrar aluno
        conteudo = conteudo.replace(
            'sucesso = academia.adicionar_aluno(novo_aluno)',
            'sucesso = academia.adicionar_aluno(novo_aluno)'
        )
        
        # Atualizar rota de editar aluno
        conteudo = conteudo.replace(
            'sucesso = academia.atualizar_aluno(aluno_id, dados_atualizados)',
            'sucesso = academia.atualizar_aluno(aluno_id, dados_atualizados)'
        )
        
        # Atualizar rota de marcar presença
        conteudo = conteudo.replace(
            'sucesso, mensagem = academia.registrar_presenca_manual(nome_aluno)',
            'sucesso, mensagem = academia.registrar_presenca(nome_aluno)'
        )
        
        # Salvar o arquivo atualizado
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print("✅ Rotas atualizadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar rotas: {e}")
        return False

def criar_arquivo_env():
    """Cria o arquivo .env com as configurações do banco"""
    try:
        conteudo_env = '''# Configurações do Banco de Dados PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=academia_amigo_povo

# URL completa do banco de dados (alternativa)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/academia_amigo_povo

# Configurações do Flask
SECRET_KEY=associacao_amigo_do_povo_2024_secure_key
FLASK_ENV=development
FLASK_DEBUG=True

# Configurações de Upload
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
'''
        
        # Tentar criar o arquivo .env
        try:
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(conteudo_env)
            print("✅ Arquivo .env criado com sucesso!")
        except:
            print("⚠️ Não foi possível criar o arquivo .env (pode estar no .gitignore)")
            print("📝 Crie manualmente o arquivo .env com o seguinte conteúdo:")
            print(conteudo_env)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivo .env: {e}")
        return False

def main():
    """Função principal"""
    print("=== ATUALIZAÇÃO DO SISTEMA PARA BANCO DE DADOS ===")
    print("Academia Amigo do Povo")
    print()
    
    print("⚠️ ATENÇÃO: Este script irá modificar o app.py")
    print("Um backup será criado automaticamente")
    print()
    
    # 1. Criar arquivo .env
    print("1. Criando arquivo .env...")
    criar_arquivo_env()
    
    # 2. Atualizar app.py
    print("\n2. Atualizando app.py...")
    if not atualizar_app_py():
        print("❌ Falha ao atualizar app.py")
        return False
    
    # 3. Atualizar rotas
    print("\n3. Atualizando rotas...")
    if not atualizar_rotas():
        print("❌ Falha ao atualizar rotas")
        return False
    
    print("\n✅ ATUALIZAÇÃO CONCLUÍDA!")
    print("\nPróximos passos:")
    print("1. Execute: python configurar_banco.py")
    print("2. Execute: python app.py")
    print("3. Teste as funcionalidades")
    print("4. Os dados agora serão salvos no banco PostgreSQL")
    
    return True

if __name__ == "__main__":
    main()
