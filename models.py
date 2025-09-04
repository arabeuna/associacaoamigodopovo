"""Modelos MongoDB para o sistema da Academia Amigo do Povo"""

from pymongo import MongoClient, ASCENDING
from flask_pymongo import PyMongo
from datetime import datetime, date
from bson import ObjectId
import os
import json
import logging
from typing import Optional, Dict, List, Any
from collections import defaultdict
import uuid

# Configuração do banco de dados MongoDB
from dotenv import load_dotenv
load_dotenv()

# Configurar conexão MongoDB Atlas
MONGO_USERNAME = os.environ.get('MONGO_USERNAME', 'amigodopovoassociacao_db_user')
MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD', 'Lp816oHvdl2nHVeO')
MONGO_CLUSTER = os.environ.get('MONGO_CLUSTER', 'cluster0.mongodb.net')
MONGO_DATABASE = os.environ.get('MONGO_DATABASE', 'amigodopovoassociacao_db')

# Construir URI do MongoDB - usar URI completa primeiro
MONGO_URI = os.environ.get('MONGO_URI')
if not MONGO_URI:
    # Tentar diferentes formatos de cluster
    if not MONGO_CLUSTER.startswith('cluster'):
        MONGO_CLUSTER = f'cluster0.{MONGO_CLUSTER}'
    MONGO_URI = f'mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/{MONGO_DATABASE}?retryWrites=true&w=majority'

print(f'🔗 Conectando ao MongoDB Atlas...')
print(f'📍 Cluster: {MONGO_CLUSTER}')
print(f'🗄️ Database: {MONGO_DATABASE}')

# Cliente MongoDB
client = None
db = None

# Sistema de fallback em memória
USE_MEMORY_FALLBACK = False
memory_db = {
    'alunos': {},
    'atividades': {},
    'turmas': {},
    'presencas': {},
    'usuarios': {},
    'busca_salva': {},
    'log_atividade': {}
}

# Contadores para IDs em memória
memory_counters = defaultdict(int)

def init_mongodb(app=None):
    """Inicializa a conexão com MongoDB"""
    global client, db, USE_MEMORY_FALLBACK
    
    # Tentar diferentes formatos de URI
    uris_para_testar = [
        MONGO_URI,
        f'mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@cluster0.mongodb.net/{MONGO_DATABASE}?retryWrites=true&w=majority',
        f'mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@cluster0.mongodb.net/?retryWrites=true&w=majority'
    ]
    
    for i, uri in enumerate(uris_para_testar):
        try:
            print(f'🔄 Tentativa {i+1}: Testando URI...')
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            db = client[MONGO_DATABASE]
            
            # Testar conexão
            client.admin.command('ping')
            print(f'✅ Conectado ao MongoDB Atlas: {MONGO_DATABASE}')
            USE_MEMORY_FALLBACK = False
            
            # Criar índices
            criar_indices()
            
            return db
        except Exception as e:
            print(f'❌ Tentativa {i+1} falhou: {e}')
            if i < len(uris_para_testar) - 1:
                print('🔄 Tentando próxima URI...')
            continue
    
    print('❌ Todas as tentativas de conexão falharam')
    print('🔄 Ativando sistema de fallback em memória...')
    USE_MEMORY_FALLBACK = True
    
    # Inicializar dados de exemplo em memória
    _init_memory_data()
    
    print('✓ Sistema funcionando com dados em memória')
    print('💡 Possíveis soluções para conectar ao MongoDB:')
    print('   - Verifique se o cluster MongoDB Atlas existe e está ativo')
    print('   - Confirme as credenciais (username/password)')
    print('   - Verifique se o IP está na lista de acesso permitido')
    print('   - Cluster pode estar pausado (M0 clusters pausam após 60 dias de inatividade)')
    return None

def _init_memory_data():
    """Inicializa dados de exemplo em memória"""
    global memory_db, memory_counters
    
    # Dados de exemplo para atividades
    atividades_exemplo = [
        {'_id': '1', 'nome': 'Informática', 'descricao': 'Curso de informática básica', 'ativo': True},
        {'_id': '2', 'nome': 'Fisioterapia', 'descricao': 'Sessões de fisioterapia', 'ativo': True},
        {'_id': '3', 'nome': 'Dança', 'descricao': 'Aulas de dança', 'ativo': True},
        {'_id': '4', 'nome': 'Hidroginástica', 'descricao': 'Exercícios aquáticos', 'ativo': True},
        {'_id': '5', 'nome': 'Funcional', 'descricao': 'Treinamento funcional', 'ativo': True}
    ]
    
    for atividade in atividades_exemplo:
        memory_db['atividades'][atividade['_id']] = atividade
    
    memory_counters['atividades'] = len(atividades_exemplo)
    memory_counters['alunos'] = 0
    memory_counters['turmas'] = 0
    memory_counters['presencas'] = 0
    memory_counters['usuarios'] = 0
    memory_counters['busca_salva'] = 0
    memory_counters['log_atividade'] = 0

def get_db():
    """Retorna a instância do banco de dados MongoDB"""
    global db
    if USE_MEMORY_FALLBACK:
        return None  # Indica que está usando fallback
    if db is None:
        db = init_mongodb()
    return db

def criar_indices():
    """Cria índices necessários nas coleções"""
    try:
        # Índices para usuários
        db.usuarios.create_index('username', unique=True)
        db.usuarios.create_index('nivel')
        
        # Índices para atividades
        db.atividades.create_index('nome', unique=True)
        db.atividades.create_index('ativa')
        
        # Índices para alunos
        db.alunos.create_index('id_unico', unique=True)
        db.alunos.create_index('nome')
        db.alunos.create_index('ativo')
        
        # Índices para presenças
        db.presencas.create_index([('aluno_id', 1), ('data_presenca', -1)])
        db.presencas.create_index('data_presenca')
        
        # Índices para logs
        db.logs_atividades.create_index([('timestamp', -1)])
        db.logs_atividades.create_index('usuario')
        
        print('✅ Índices MongoDB criados com sucesso')
    except Exception as e:
        print(f'⚠️ Erro ao criar índices: {e}')

def verificar_conexao():
    """Verifica se a conexão com o banco está funcionando"""
    try:
        client.admin.command('ping')
        return True
    except Exception as e:
        print(f'Erro na conexão com o MongoDB: {e}')
        return False

# Classes DAO para operações MongoDB
class UsuarioDAO:
    """Data Access Object para operações com usuários"""
    
    def criar(self, dados):
        """Cria um novo usuário"""
        dados['data_criacao'] = datetime.utcnow()
        dados['ultimo_acesso'] = None
        result = db.usuarios.insert_one(dados)
        return result.inserted_id
    
    def buscar_por_username(self, username):
        """Busca usuário por username"""
        return db.usuarios.find_one({'username': username})
    
    def listar_todos(self):
        """Lista todos os usuários"""
        return list(db.usuarios.find())

class AlunoDAO:
    """Data Access Object para Alunos"""
    
    @staticmethod
    def criar(dados_aluno):
        """Cria um novo aluno"""
        try:
            # Converter date para datetime se necessário
            if 'data_nascimento' in dados_aluno and dados_aluno['data_nascimento']:
                from datetime import date
                if isinstance(dados_aluno['data_nascimento'], date):
                    dados_aluno['data_nascimento'] = datetime.combine(dados_aluno['data_nascimento'], datetime.min.time())
            
            if 'data_cadastro' in dados_aluno and dados_aluno['data_cadastro']:
                from datetime import date
                if isinstance(dados_aluno['data_cadastro'], date):
                    dados_aluno['data_cadastro'] = datetime.combine(dados_aluno['data_cadastro'], datetime.min.time())
            
            if USE_MEMORY_FALLBACK:
                # Usar dados em memória
                memory_counters['alunos'] += 1
                aluno_id = str(memory_counters['alunos'])
                dados_aluno['_id'] = aluno_id
                dados_aluno['data_cadastro'] = datetime.now()
                dados_aluno['ativo'] = True
                memory_db['alunos'][aluno_id] = dados_aluno
                return aluno_id
            else:
                # Usar MongoDB
                import uuid
                dados_aluno['data_cadastro'] = datetime.now()
                dados_aluno['ativo'] = True
                # Gerar id_unico se não existir
                if 'id_unico' not in dados_aluno or not dados_aluno['id_unico']:
                    dados_aluno['id_unico'] = str(uuid.uuid4())[:8] + '_' + str(int(datetime.now().timestamp()))
                resultado = db.alunos.insert_one(dados_aluno)
                return str(resultado.inserted_id)
        except Exception as e:
            print(f"Erro ao criar aluno: {e}")
            return None
    
    @staticmethod
    def buscar_por_id(aluno_id):
        """Busca aluno por ID"""
        try:
            if USE_MEMORY_FALLBACK:
                return memory_db['alunos'].get(str(aluno_id))
            else:
                from bson import ObjectId
                return db.alunos.find_one({'_id': ObjectId(aluno_id)})
        except Exception as e:
            print(f"Erro ao buscar aluno: {e}")
            return None
    
    @staticmethod
    def buscar_por_nome(nome):
        """Busca aluno por nome"""
        try:
            if USE_MEMORY_FALLBACK:
                for aluno in memory_db['alunos'].values():
                    if nome.lower() in aluno.get('nome', '').lower():
                        return aluno
                return None
            else:
                return db.alunos.find_one({'nome': {'$regex': nome, '$options': 'i'}})
        except Exception as e:
            print(f"Erro ao buscar aluno por nome: {e}")
            return None
    
    @staticmethod
    def buscar_por_telefone(telefone):
        """Busca aluno por telefone"""
        try:
            if USE_MEMORY_FALLBACK:
                for aluno in memory_db['alunos'].values():
                    if aluno.get('telefone') == telefone:
                        return aluno
                return None
            else:
                return db.alunos.find_one({'telefone': telefone})
        except Exception as e:
            print(f"Erro ao buscar aluno por telefone: {e}")
            return None
    
    @staticmethod
    def buscar_por_nome_telefone(nome, telefone):
        """Busca aluno por nome e telefone"""
        try:
            if USE_MEMORY_FALLBACK:
                for aluno in memory_db['alunos'].values():
                    if (aluno.get('nome', '').lower() == nome.lower() and 
                        aluno.get('telefone') == telefone):
                        return aluno
                return None
            else:
                return db.alunos.find_one({
                    '$or': [
                        {'nome': {'$regex': f'^{nome}$', '$options': 'i'}},
                        {'telefone': telefone}
                    ],
                    'ativo': True
                })
        except Exception as e:
            print(f"Erro ao buscar aluno por nome e telefone: {e}")
            return None
    
    @staticmethod
    def listar_todos():
        """Lista todos os alunos"""
        try:
            if USE_MEMORY_FALLBACK:
                return [aluno for aluno in memory_db['alunos'].values() if aluno.get('ativo', True)]
            else:
                return list(db.alunos.find({'ativo': True}))
        except Exception as e:
            print(f"Erro ao listar alunos: {e}")
            return []
    
    @staticmethod
    def atualizar(aluno_id, dados_atualizacao):
        """Atualiza dados do aluno"""
        try:
            if USE_MEMORY_FALLBACK:
                aluno_id = str(aluno_id)
                if aluno_id in memory_db['alunos']:
                    dados_atualizacao['data_atualizacao'] = datetime.now()
                    memory_db['alunos'][aluno_id].update(dados_atualizacao)
                    return True
                return False
            else:
                from bson import ObjectId
                dados_atualizacao['data_atualizacao'] = datetime.now()
                resultado = db.alunos.update_one(
                    {'_id': ObjectId(aluno_id)},
                    {'$set': dados_atualizacao}
                )
                return resultado.modified_count > 0
        except Exception as e:
            print(f"Erro ao atualizar aluno: {e}")
            return False
    
    @staticmethod
    def excluir(aluno_id):
        """Exclui aluno (soft delete)"""
        try:
            if USE_MEMORY_FALLBACK:
                aluno_id = str(aluno_id)
                if aluno_id in memory_db['alunos']:
                    memory_db['alunos'][aluno_id]['ativo'] = False
                    memory_db['alunos'][aluno_id]['data_exclusao'] = datetime.now()
                    return True
                return False
            else:
                from bson import ObjectId
                resultado = db.alunos.update_one(
                    {'_id': ObjectId(aluno_id)},
                    {'$set': {'ativo': False, 'data_exclusao': datetime.now()}}
                )
                return resultado.modified_count > 0
        except Exception as e:
            print(f"Erro ao excluir aluno: {e}")
            return False
    
    @staticmethod
    def contar_ativos():
        """Conta alunos ativos"""
        try:
            if USE_MEMORY_FALLBACK:
                return len([aluno for aluno in memory_db['alunos'].values() if aluno.get('ativo', True)])
            else:
                return db.alunos.count_documents({'ativo': True})
        except Exception as e:
            print(f"Erro ao contar alunos: {e}")
            return 0

class AtividadeDAO:
    """Data Access Object para Atividades"""
    
    @staticmethod
    def criar(dados_atividade):
        """Cria uma nova atividade"""
        try:
            if USE_MEMORY_FALLBACK:
                memory_counters['atividades'] += 1
                atividade_id = str(memory_counters['atividades'])
                dados_atividade['_id'] = atividade_id
                dados_atividade['data_criacao'] = datetime.now()
                dados_atividade['ativo'] = True
                memory_db['atividades'][atividade_id] = dados_atividade
                return atividade_id
            else:
                dados_atividade['data_criacao'] = datetime.now()
                dados_atividade['ativo'] = True
                resultado = db.atividades.insert_one(dados_atividade)
                return str(resultado.inserted_id)
        except Exception as e:
            print(f"Erro ao criar atividade: {e}")
            return None
    
    @staticmethod
    def listar_todas():
        """Lista todas as atividades ativas"""
        try:
            if USE_MEMORY_FALLBACK:
                return [atividade for atividade in memory_db['atividades'].values() if atividade.get('ativo', True)]
            else:
                return list(db.atividades.find({'ativo': True}))
        except Exception as e:
            print(f"Erro ao listar atividades: {e}")
            return []
    
    @staticmethod
    def buscar_por_id(atividade_id):
        """Busca atividade por ID"""
        try:
            if USE_MEMORY_FALLBACK:
                return memory_db['atividades'].get(str(atividade_id))
            else:
                from bson import ObjectId
                return db.atividades.find_one({'_id': ObjectId(atividade_id)})
        except Exception as e:
            print(f"Erro ao buscar atividade: {e}")
            return None
    
    @staticmethod
    def buscar_por_nome(nome):
        """Busca atividade por nome"""
        try:
            if USE_MEMORY_FALLBACK:
                for atividade in memory_db['atividades'].values():
                    if nome.lower() in atividade.get('nome', '').lower():
                        return atividade
                return None
            else:
                return db.atividades.find_one({'nome': {'$regex': nome, '$options': 'i'}})
        except Exception as e:
            print(f"Erro ao buscar atividade por nome: {e}")
            return None
    
    @staticmethod
    def atualizar(atividade_id, dados_atualizacao):
        """Atualiza dados de uma atividade"""
        try:
            if USE_MEMORY_FALLBACK:
                atividade_id = str(atividade_id)
                if atividade_id in memory_db['atividades']:
                    dados_atualizacao['data_atualizacao'] = datetime.now()
                    memory_db['atividades'][atividade_id].update(dados_atualizacao)
                    return True
                return False
            else:
                from bson import ObjectId
                dados_atualizacao['data_atualizacao'] = datetime.now()
                resultado = db.atividades.update_one(
                    {'_id': ObjectId(atividade_id)},
                    {'$set': dados_atualizacao}
                )
                return resultado.modified_count > 0
        except Exception as e:
            print(f"Erro ao atualizar atividade: {e}")
            return False
    
    @staticmethod
    def excluir(atividade_id):
        """Exclui atividade (soft delete)"""
        try:
            if USE_MEMORY_FALLBACK:
                atividade_id = str(atividade_id)
                if atividade_id in memory_db['atividades']:
                    memory_db['atividades'][atividade_id]['ativo'] = False
                    memory_db['atividades'][atividade_id]['data_exclusao'] = datetime.now()
                    return True
                return False
            else:
                from bson import ObjectId
                resultado = db.atividades.update_one(
                    {'_id': ObjectId(atividade_id)},
                    {'$set': {'ativo': False, 'data_exclusao': datetime.now()}}
                )
                return resultado.modified_count > 0
        except Exception as e:
            print(f"Erro ao excluir atividade: {e}")
            return False

class TurmaDAO:
    """Data Access Object para operações com turmas"""
    
    def criar(self, dados):
        """Cria uma nova turma"""
        dados['data_criacao'] = datetime.utcnow()
        dados['ativa'] = True
        result = db.turmas.insert_one(dados)
        return result.inserted_id
    
    def listar_por_atividade(self, atividade_id):
        """Lista turmas de uma atividade"""
        return list(db.turmas.find({
            'atividade_id': atividade_id,
            'ativa': True
        }))

class PresencaDAO:
    """Data Access Object para Presenças"""
    
    @staticmethod
    def registrar(dados_presenca):
        """Registra presença de um aluno"""
        try:
            if USE_MEMORY_FALLBACK:
                memory_counters['presencas'] += 1
                presenca_id = str(memory_counters['presencas'])
                dados_presenca['_id'] = presenca_id
                dados_presenca['data_registro'] = datetime.now()
                memory_db['presencas'][presenca_id] = dados_presenca
                return presenca_id
            else:
                dados_presenca['data_registro'] = datetime.now()
                resultado = db.presencas.insert_one(dados_presenca)
                return str(resultado.inserted_id)
        except Exception as e:
            print(f"Erro ao registrar presença: {e}")
            return None
    
    @staticmethod
    def buscar_por_aluno(aluno_id):
        """Busca presenças de um aluno"""
        try:
            if USE_MEMORY_FALLBACK:
                aluno_id = str(aluno_id)
                return [presenca for presenca in memory_db['presencas'].values() 
                       if presenca.get('aluno_id') == aluno_id]
            else:
                from bson import ObjectId
                return list(db.presencas.find({'aluno_id': ObjectId(aluno_id)}))
        except Exception as e:
            print(f"Erro ao buscar presenças por aluno: {e}")
            return []
    
    @staticmethod
    def buscar_por_data(data_inicio, data_fim):
        """Busca presenças por período"""
        try:
            if USE_MEMORY_FALLBACK:
                resultado = []
                for presenca in memory_db['presencas'].values():
                    data_presenca = presenca.get('data_presenca')
                    if data_presenca and data_inicio <= data_presenca <= data_fim:
                        resultado.append(presenca)
                return resultado
            else:
                return list(db.presencas.find({
                    'data_presenca': {
                        '$gte': data_inicio,
                        '$lte': data_fim
                    }
                }))
        except Exception as e:
            print(f"Erro ao buscar presenças por data: {e}")
            return []
    
    @staticmethod
    def excluir_por_aluno(aluno_id):
        """Exclui todas as presenças de um aluno"""
        try:
            if USE_MEMORY_FALLBACK:
                aluno_id = str(aluno_id)
                presencas_removidas = 0
                presencas_para_remover = []
                for presenca_id, presenca in memory_db['presencas'].items():
                    if presenca.get('aluno_id') == aluno_id:
                        presencas_para_remover.append(presenca_id)
                
                for presenca_id in presencas_para_remover:
                    del memory_db['presencas'][presenca_id]
                    presencas_removidas += 1
                
                return presencas_removidas
            else:
                from bson import ObjectId
                resultado = db.presencas.delete_many({'aluno_id': ObjectId(aluno_id)})
                return resultado.deleted_count
        except Exception as e:
            print(f"Erro ao excluir presenças por aluno: {e}")
            return 0
    
    @staticmethod
    def excluir(presenca_id):
        """Exclui uma presença"""
        try:
            if USE_MEMORY_FALLBACK:
                presenca_id = str(presenca_id)
                if presenca_id in memory_db['presencas']:
                    del memory_db['presencas'][presenca_id]
                    return True
                return False
            else:
                from bson import ObjectId
                resultado = db.presencas.delete_one({'_id': ObjectId(presenca_id)})
                return resultado.deleted_count > 0
        except Exception as e:
            print(f"Erro ao excluir presença: {e}")
            return False

class BuscaSalvaDAO:
    """Data Access Object para operações com buscas salvas"""
    
    def criar(self, dados):
        """Salva uma nova busca"""
        dados['data_criacao'] = datetime.utcnow()
        dados['ativa'] = True
        result = db.buscas_salvas.insert_one(dados)
        return result.inserted_id
    
    def listar_por_usuario(self, usuario_id):
        """Lista buscas salvas de um usuário"""
        return list(db.buscas_salvas.find({
            'usuario_id': usuario_id,
            'ativa': True
        }).sort('data_criacao', -1))
    
    def excluir(self, busca_id):
        """Exclui uma busca salva"""
        if isinstance(busca_id, str):
            busca_id = ObjectId(busca_id)
        result = db.buscas_salvas.update_one(
            {'_id': busca_id}, 
            {'$set': {'ativa': False}}
        )
        return result.modified_count > 0

class LogAtividadeDAO:
    """Data Access Object para operações com logs de atividades"""
    
    def criar(self, dados):
        """Registra um novo log de atividade"""
        dados['timestamp'] = datetime.utcnow()
        dados['data_registro'] = datetime.utcnow()
        result = db.logs_atividades.insert_one(dados)
        return result.inserted_id
    
    def listar_logs(self, filtro=None, limite=1000):
        """Lista logs de atividades com filtros opcionais"""
        filtro_query = {}
        
        if filtro and filtro != 'todos':
            if filtro == 'hoje':
                hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                filtro_query['timestamp'] = {'$gte': hoje}
            elif filtro == 'semana':
                from datetime import timedelta
                uma_semana_atras = datetime.now() - timedelta(days=7)
                filtro_query['timestamp'] = {'$gte': uma_semana_atras}
            elif filtro == 'mes':
                from datetime import timedelta
                um_mes_atras = datetime.now() - timedelta(days=30)
                filtro_query['timestamp'] = {'$gte': um_mes_atras}
        
        return list(db.logs_atividades.find(filtro_query)
                   .sort('timestamp', -1)
                   .limit(limite))
    
    def buscar_por_acao(self, acao, limite=None):
        """Busca logs por tipo de ação específica"""
        filtro_query = {'acao': acao}
        
        query = db.logs_atividades.find(filtro_query).sort('timestamp', -1)
        
        if limite:
            query = query.limit(limite)
            
        return list(query)

# Inicialização
if __name__ == '__main__':
    print('Inicializando MongoDB...')
    init_mongodb()
    print('MongoDB inicializado com sucesso!')
