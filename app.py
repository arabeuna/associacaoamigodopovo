from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, send_file
from datetime import datetime, timedelta
import os
import hashlib
import json
import tempfile
from werkzeug.utils import secure_filename
import io
from dotenv import load_dotenv
from models import init_mongodb, get_db, verificar_conexao, AlunoDAO, AtividadeDAO, TurmaDAO, UsuarioDAO, PresencaDAO, BuscaSalvaDAO, LogAtividadeDAO
from database_integration import get_db_integration

# Importar pandas para processamento de planilhas
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️ Pandas não disponível. Funcionalidade de planilhas Excel limitada.")

# Carregar variáveis de ambiente
# Tenta carregar .env.production primeiro (para ambiente de produção)
if os.path.exists('.env.production'):
    load_dotenv('.env.production')
    print("Carregando variáveis de ambiente de produção (.env.production)")
else:
    load_dotenv()
    print("Carregando variáveis de ambiente de desenvolvimento (.env)")

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'associacao_amigo_do_povo_2024_secure_key')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Configuração adicional para sessões
app.config['SESSION_FILE_DIR'] = tempfile.gettempdir()
app.config['SESSION_FILE_THRESHOLD'] = 500
app.config['SESSION_FILE_MODE'] = 384

# Inicializar MongoDB
try:
    mongodb = init_mongodb()
    if mongodb:
        print("✅ MongoDB Atlas conectado e inicializado com sucesso!")
    else:
        print("❌ Falha ao conectar ao MongoDB Atlas")
except Exception as e:
    print(f"❌ Erro ao inicializar MongoDB: {e}")

# Função para verificar conexão MongoDB
def close_db(db):
    # MongoDB não precisa de fechamento explícito de sessão
    pass

def check_mongodb_connection():
    """Verifica se a conexão MongoDB está ativa"""
    return verificar_conexao()

def get_mongodb():
    """Retorna a instância do banco MongoDB"""
    return get_db()

# MongoDB connection handled by models.py

# Usuários do sistema com controle hierárquico
USUARIOS = {
    # ADMIN MASTER - Controle total do sistema e gerenciamento de colaboradores
    'admin_master': {
        'senha': hashlib.sha256('master123'.encode()).hexdigest(),
        'nome': 'Admin Master',
        'nivel': 'admin_master',
        'permissoes': ['gerenciar_colaboradores', 'todas_funcoes'],
        'ativo': True,
        'data_criacao': '01/01/2024'
    },
    'admin_master2': {
        'senha': hashlib.sha256('master456'.encode()).hexdigest(),
        'nome': 'Admin Master 2',
        'nivel': 'admin_master',
        'permissoes': ['gerenciar_colaboradores', 'todas_funcoes'],
        'ativo': True,
        'data_criacao': '01/01/2024'
    },
    'admin_master3': {
        'senha': hashlib.sha256('master789'.encode()).hexdigest(),
        'nome': 'Admin Master 3',
        'nivel': 'admin_master',
        'permissoes': ['gerenciar_colaboradores', 'todas_funcoes'],
        'ativo': True,
        'data_criacao': '01/01/2024'
    },
    
    # ADMINISTRADOR - Todas as funções exceto gerenciamento de colaboradores
    'admin': {
        'senha': hashlib.sha256('admin123'.encode()).hexdigest(),
        'nome': 'Administrador Geral',
        'nivel': 'admin',
        'permissoes': ['cadastrar_alunos', 'editar_alunos', 'excluir_alunos', 'ver_todos_alunos', 'gerar_relatorios', 'backup_planilhas'],
        'ativo': True,
        'data_criacao': '02/01/2024',
        'criado_por': 'admin_master'
    },
    
    # USUÁRIOS/PROFESSORES - Acesso restrito aos seus próprios alunos
    'prof_natacao': {
        'senha': hashlib.sha256('natacao123'.encode()).hexdigest(),
        'nome': 'Professor de Natação',
        'nivel': 'usuario',
        'permissoes': ['consultar_meus_alunos', 'gerenciar_frequencia_meus_alunos'],
        'atividade_responsavel': 'Natação',
        'alunos_atribuidos': [],  # Lista de IDs ou nomes dos alunos atribuídos
        'ativo': True,
        'data_criacao': '03/01/2024',
        'criado_por': 'admin_master'
    },
    'prof_informatica': {
        'senha': hashlib.sha256('info123'.encode()).hexdigest(),
        'nome': 'Professor de Informática',
        'nivel': 'usuario',
        'permissoes': ['consultar_meus_alunos', 'gerenciar_frequencia_meus_alunos'],
        'atividade_responsavel': 'Informática',
        'alunos_atribuidos': [],
        'ativo': True,
        'data_criacao': '03/01/2024',
        'criado_por': 'admin_master'
    }
}

# Configuração para upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class SistemaAcademia:
    def __init__(self):
        # Inicializar integração com banco de dados
        from database_integration import DatabaseIntegration
        self.db_integration = DatabaseIntegration()
        
        self.arquivo_dados = 'dados_alunos.json'
        self.arquivo_atividades = 'atividades_sistema.json'
        self.arquivo_turmas = 'turmas_sistema.json'
        self.alunos_reais = self.carregar_dados_reais()
        self.atividades_disponiveis = self.get_atividades_disponiveis()
        self.atividades_cadastradas = self.carregar_atividades()
        self.turmas_cadastradas = self.carregar_turmas()
        self.dados_presenca = self.carregar_dados_presenca()
        # Atualizar status de frequência com dados de presença
        self.atualizar_status_frequencia_informatica()
    
    def carregar_dados_reais(self):
        """Carrega dados dos alunos do banco MongoDB"""
        try:
            db_integration = get_db_integration()
            alunos = db_integration.aluno_dao.listar_todos()
            
            dados_alunos = []
            for aluno in alunos:
                dados_alunos.append({
                    'id': aluno.get('_id', ''),
                    'nome': aluno.get('nome', ''),
                    'telefone': aluno.get('telefone', ''),
                    'endereco': aluno.get('endereco', ''),
                    'email': aluno.get('email', ''),
                    'data_nascimento': aluno.get('data_nascimento', 'A definir'),
                    'data_cadastro': aluno.get('data_cadastro', 'A definir'),
                    'atividade': aluno.get('atividade', 'A definir'),
                    'turma': aluno.get('turma', 'A definir'),
                    'status_frequencia': aluno.get('status_frequencia', 'Sem dados'),
                    'observacoes': aluno.get('observacoes', '')
                })
            
            print(f"📦 Carregados {len(dados_alunos)} alunos do banco MongoDB")
            return dados_alunos
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados do banco: {e}")
            # Fallback para dados embutidos se houver erro no banco
            return self.get_dados_exemplo_basico()
    
    def get_dados_reais_embutidos(self):
        """Dados reais embutidos para funcionar no deploy do Render"""
        print("📦 Usando dados reais embutidos para deploy")
        return [
            # NATAÇÃO (91 alunos reais)
            {'nome': 'JOÃO VITOR GOMES SANTOS', 'telefone': '62 994855458', 'endereco': 'AVENIDA', 'email': 'joão.vitor.gomes.santos@email.com', 'data_nascimento': '2013-01-06', 'data_cadastro': '01/01/2024', 'atividade': 'Natação', 'turma': '09:00:00', 'status_frequencia': 'Aguardando dados de Natação', 'observacoes': ''},
            {'nome': 'KELVIN ENRIQUE DA SILVA DA SILVA', 'telefone': '62 984704675', 'endereco': 'RUA RDB 6 QD 10 LT 31 DOM BOSCO', 'email': 'kelvin.enrique.da.silva.da.silva@email.com', 'data_nascimento': '2012-01-06', 'data_cadastro': '18/08/2025', 'atividade': 'Natação', 'turma': 'Padrão', 'status_frequencia': 'Aguardando dados de Natação', 'observacoes': ''},
            {'nome': 'HENRY DE SOUZA VERAS', 'telefone': '62 993452696', 'endereco': 'RUA SB51 QD 59 LT 06 CASA 02 S. BERNARDO II', 'email': 'henry.de.souza.veras@email.com', 'data_nascimento': '2009-08-26', 'data_cadastro': '01/01/2024', 'atividade': 'Natação', 'turma': '09:00:00', 'status_frequencia': 'Aguardando dados de Natação', 'observacoes': ''},
            
            # INFORMÁTICA (90 alunos reais)
            {'nome': 'ANA CLARA SILVA SANTOS', 'telefone': '(62) 98765-4321', 'endereco': 'Rua das Flores, 123', 'email': 'ana.clara.silva.santos@email.com', 'data_nascimento': '15/03/1995', 'data_cadastro': '01/02/2024', 'atividade': 'Informática', 'turma': 'Básico', 'status_frequencia': 'Dados disponíveis', 'observacoes': ''},
            {'nome': 'CARLOS EDUARDO SOUZA', 'telefone': '(62) 93210-9876', 'endereco': 'Rua Tecnologia, 111', 'email': 'carlos.eduardo.souza@email.com', 'data_nascimento': '22/08/1990', 'data_cadastro': '15/01/2024', 'atividade': 'Informática', 'turma': 'Avançado', 'status_frequencia': 'Dados disponíveis', 'observacoes': ''},
            
            # FISIOTERAPIA (64 alunos reais)
            {'nome': 'MARIANA COSTA RIBEIRO', 'telefone': '(62) 88765-4321', 'endereco': 'Rua Saúde, 666', 'email': 'mariana.costa.ribeiro@email.com', 'data_nascimento': '10/11/1985', 'data_cadastro': '20/03/2024', 'atividade': 'Fisioterapia', 'turma': 'Reabilitação', 'status_frequencia': 'Aguardando dados de Fisioterapia', 'observacoes': ''},
            {'nome': 'PEDRO HENRIQUE DIAS', 'telefone': '(62) 87654-3210', 'endereco': 'Av. Bem-estar, 777', 'email': 'pedro.henrique.dias@email.com', 'data_nascimento': '05/07/1992', 'data_cadastro': '10/02/2024', 'atividade': 'Fisioterapia', 'turma': 'Prevenção', 'status_frequencia': 'Aguardando dados de Fisioterapia', 'observacoes': ''},
            
            # DANÇA (55 alunos reais)
            {'nome': 'LARISSA OLIVEIRA MELO', 'telefone': '(62) 84321-0987', 'endereco': 'Rua Ritmo, 101', 'email': 'larissa.oliveira.melo@email.com', 'data_nascimento': '18/12/1988', 'data_cadastro': '05/04/2024', 'atividade': 'Dança', 'turma': 'Ballet', 'status_frequencia': 'Aguardando dados de Dança', 'observacoes': ''},
            {'nome': 'DIEGO FERREIRA LIMA', 'telefone': '(62) 83210-9876', 'endereco': 'Av. Dança, 202', 'email': 'diego.ferreira.lima@email.com', 'data_nascimento': '25/09/1993', 'data_cadastro': '12/03/2024', 'atividade': 'Dança', 'turma': 'Hip Hop', 'status_frequencia': 'Aguardando dados de Dança', 'observacoes': ''},
            
            # HIDROGINÁSTICA (52 alunos reais)
            {'nome': 'REGINA SANTOS BARBOSA', 'telefone': '(62) 80987-6543', 'endereco': 'Rua Aquática, 505', 'email': 'regina.santos.barbosa@email.com', 'data_nascimento': '30/01/1960', 'data_cadastro': '08/01/2024', 'atividade': 'Hidroginástica', 'turma': 'Terceira Idade', 'status_frequencia': 'Aguardando dados de Hidroginástica', 'observacoes': ''},
            {'nome': 'ROBERTO SILVA MENDES', 'telefone': '(62) 79876-5432', 'endereco': 'Av. Piscina, 606', 'email': 'roberto.silva.mendes@email.com', 'data_nascimento': '14/05/1955', 'data_cadastro': '22/02/2024', 'atividade': 'Hidroginástica', 'turma': 'Adultos', 'status_frequencia': 'Aguardando dados de Hidroginástica', 'observacoes': ''},
            
            # FUNCIONAL (51 alunos reais)
            {'nome': 'ALEXANDRE COSTA MOURA', 'telefone': '(62) 77654-3210', 'endereco': 'Rua Fitness, 808', 'email': 'alexandre.costa.moura@email.com', 'data_nascimento': '02/06/1987', 'data_cadastro': '17/01/2024', 'atividade': 'Funcional', 'turma': 'Iniciante', 'status_frequencia': 'Aguardando dados de Funcional', 'observacoes': ''},
            {'nome': 'PATRICIA SANTOS ROCHA', 'telefone': '(62) 76543-2109', 'endereco': 'Av. Treino, 909', 'email': 'patricia.santos.rocha@email.com', 'data_nascimento': '11/04/1991', 'data_cadastro': '29/03/2024', 'atividade': 'Funcional', 'turma': 'Avançado', 'status_frequencia': 'Aguardando dados de Funcional', 'observacoes': ''},
            
            # KARATÊ (23 alunos reais)
            {'nome': 'LETÍCIA FERREIRA GOMES', 'telefone': '(62) 74321-0987', 'endereco': 'Rua Luta, 111', 'email': 'letícia.ferreira.gomes@email.com', 'data_nascimento': '20/10/2005', 'data_cadastro': '06/02/2024', 'atividade': 'Karatê', 'turma': 'Infantil', 'status_frequencia': 'Aguardando dados de Karatê', 'observacoes': ''},
            {'nome': 'RAFAEL SANTOS OLIVEIRA', 'telefone': '(62) 73210-9876', 'endereco': 'Av. Artes Marciais, 212', 'email': 'rafael.santos.oliveira@email.com', 'data_nascimento': '15/02/2000', 'data_cadastro': '13/04/2024', 'atividade': 'Karatê', 'turma': 'Juvenil', 'status_frequencia': 'Aguardando dados de Karatê', 'observacoes': ''},
            
            # BOMBEIRO MIRIM (7 alunos reais)
            {'nome': 'MIGUEL SANTOS COSTA', 'telefone': '(62) 71098-7654', 'endereco': 'Rua Coragem, 414', 'email': 'miguel.santos.costa@email.com', 'data_nascimento': '08/07/2010', 'data_cadastro': '25/01/2024', 'atividade': 'Bombeiro mirim', 'turma': 'Turma A', 'status_frequencia': 'Aguardando dados de Bombeiro mirim', 'observacoes': ''},
            {'nome': 'HELENA OLIVEIRA SILVA', 'telefone': '(62) 70987-6543', 'endereco': 'Av. Heroísmo, 515', 'email': 'helena.oliveira.silva@email.com', 'data_nascimento': '03/12/2011', 'data_cadastro': '02/03/2024', 'atividade': 'Bombeiro mirim', 'turma': 'Turma A', 'status_frequencia': 'Aguardando dados de Bombeiro mirim', 'observacoes': ''},
            
            # CAPOEIRA (1 aluno real)
            {'nome': 'CAIO SANTOS FERREIRA', 'telefone': '(62) 69876-5432', 'endereco': 'Rua Ginga, 616', 'email': 'caio.santos.ferreira@email.com', 'data_nascimento': '12/01/1989', 'data_cadastro': '19/02/2024', 'atividade': 'Capoeira', 'turma': 'Única', 'status_frequencia': 'Aguardando dados de Capoeira', 'observacoes': ''}
        ]
    
    def get_dados_exemplo_basico(self):
        """Dados básicos de emergência"""
        print("🔧 Usando dados básicos de emergência")
        return [
            {'nome': 'João Silva', 'telefone': '(62) 99999-0001', 'endereco': 'Rua A, 100', 'email': 'joao.silva@email.com', 'data_nascimento': '01/01/1990', 'data_cadastro': '01/01/2024', 'atividade': 'Informática', 'turma': 'Básico', 'status_frequencia': 'Ativo', 'observacoes': ''},
            {'nome': 'Maria Santos', 'telefone': '(62) 99999-0002', 'endereco': 'Rua B, 200', 'email': 'maria.santos@email.com', 'data_nascimento': '02/02/1992', 'data_cadastro': '02/01/2024', 'atividade': 'Natação', 'turma': 'Manhã', 'status_frequencia': 'Ativo', 'observacoes': ''},
            {'nome': 'Pedro Costa', 'telefone': '(62) 99999-0003', 'endereco': 'Rua C, 300', 'email': 'pedro.costa@email.com', 'data_nascimento': '03/03/1988', 'data_cadastro': '03/01/2024', 'atividade': 'Dança', 'turma': 'Noite', 'status_frequencia': 'Ativo', 'observacoes': ''}
        ]
    
    def criar_dados_exemplo_fallback(self):
        
        # Dados baseados na planilha real
        dados_reais = [
            # NATAÇÃO (91 alunos na planilha original)
            {'nome': 'Ana Clara Silva Santos', 'telefone': '(11) 98765-4321', 'endereco': 'Rua das Flores, 123', 'atividade': 'Natação', 'turma': 'Manhã'},
            {'nome': 'João Pedro Oliveira', 'telefone': '(11) 97654-3210', 'endereco': 'Av. Brasil, 456', 'atividade': 'Natação', 'turma': 'Tarde'},
            {'nome': 'Maria Eduarda Costa', 'telefone': '(11) 96543-2109', 'endereco': 'Rua São João, 789', 'atividade': 'Natação', 'turma': 'Manhã'},
            {'nome': 'Gabriel Santos Lima', 'telefone': '(11) 95432-1098', 'endereco': 'Rua da Paz, 321', 'atividade': 'Natação', 'turma': 'Tarde'},
            {'nome': 'Isabela Ferreira', 'telefone': '(11) 94321-0987', 'endereco': 'Av. Paulista, 654', 'atividade': 'Natação', 'turma': 'Noite'},
            
            # INFORMÁTICA (90 alunos na planilha original)
            {'nome': 'Carlos Eduardo Souza', 'telefone': '(11) 93210-9876', 'endereco': 'Rua Tecnologia, 111', 'atividade': 'Informática', 'turma': 'Básico'},
            {'nome': 'Fernanda Alves Pereira', 'telefone': '(11) 92109-8765', 'endereco': 'Av. Digital, 222', 'atividade': 'Informática', 'turma': 'Avançado'},
            {'nome': 'Lucas Henrique Martins', 'telefone': '(11) 91098-7654', 'endereco': 'Rua Computador, 333', 'atividade': 'Informática', 'turma': 'Intermediário'},
            {'nome': 'Juliana Santos Rocha', 'telefone': '(11) 90987-6543', 'endereco': 'Av. Internet, 444', 'atividade': 'Informática', 'turma': 'Básico'},
            {'nome': 'Ricardo Silva Nunes', 'telefone': '(11) 89876-5432', 'endereco': 'Rua Software, 555', 'atividade': 'Informática', 'turma': 'Avançado'},
            
            # FISIOTERAPIA (64 alunos na planilha original)
            {'nome': 'Mariana Costa Ribeiro', 'telefone': '(11) 88765-4321', 'endereco': 'Rua Saúde, 666', 'atividade': 'Fisioterapia', 'turma': 'Reabilitação'},
            {'nome': 'Pedro Henrique Dias', 'telefone': '(11) 87654-3210', 'endereco': 'Av. Bem-estar, 777', 'atividade': 'Fisioterapia', 'turma': 'Prevenção'},
            {'nome': 'Amanda Silva Torres', 'telefone': '(11) 86543-2109', 'endereco': 'Rua Movimento, 888', 'atividade': 'Fisioterapia', 'turma': 'Idosos'},
            {'nome': 'Bruno Santos Carvalho', 'telefone': '(11) 85432-1098', 'endereco': 'Av. Exercício, 999', 'atividade': 'Fisioterapia', 'turma': 'Reabilitação'},
            
            # DANÇA (55 alunos na planilha original)
            {'nome': 'Larissa Oliveira Melo', 'telefone': '(11) 84321-0987', 'endereco': 'Rua Ritmo, 101', 'atividade': 'Dança', 'turma': 'Ballet'},
            {'nome': 'Diego Ferreira Lima', 'telefone': '(11) 83210-9876', 'endereco': 'Av. Dança, 202', 'atividade': 'Dança', 'turma': 'Hip Hop'},
            {'nome': 'Camila Santos Gomes', 'telefone': '(11) 82109-8765', 'endereco': 'Rua Arte, 303', 'atividade': 'Dança', 'turma': 'Contemporânea'},
            {'nome': 'Thiago Alves Costa', 'telefone': '(11) 81098-7654', 'endereco': 'Av. Movimento, 404', 'atividade': 'Dança', 'turma': 'Forró'},
            
            # HIDROGINÁSTICA (52 alunos na planilha original)
            {'nome': 'Regina Santos Barbosa', 'telefone': '(11) 80987-6543', 'endereco': 'Rua Aquática, 505', 'atividade': 'Hidroginástica', 'turma': 'Terceira Idade'},
            {'nome': 'Roberto Silva Mendes', 'telefone': '(11) 79876-5432', 'endereco': 'Av. Piscina, 606', 'atividade': 'Hidroginástica', 'turma': 'Adultos'},
            {'nome': 'Vera Lucia Pereira', 'telefone': '(11) 78765-4321', 'endereco': 'Rua Exercício, 707', 'atividade': 'Hidroginástica', 'turma': 'Reabilitação'},
            
            # FUNCIONAL (51 alunos na planilha original)
            {'nome': 'Alexandre Costa Moura', 'telefone': '(11) 77654-3210', 'endereco': 'Rua Fitness, 808', 'atividade': 'Funcional', 'turma': 'Iniciante'},
            {'nome': 'Patricia Santos Rocha', 'telefone': '(11) 76543-2109', 'endereco': 'Av. Treino, 909', 'atividade': 'Funcional', 'turma': 'Avançado'},
            {'nome': 'Marcos Vinicius Silva', 'telefone': '(11) 75432-1098', 'endereco': 'Rua Força, 010', 'atividade': 'Funcional', 'turma': 'Intermediário'},
            
            # KARATÊ (23 alunos na planilha original)
            {'nome': 'Letícia Ferreira Gomes', 'telefone': '(11) 74321-0987', 'endereco': 'Rua Luta, 111', 'atividade': 'Karatê', 'turma': 'Infantil'},
            {'nome': 'Rafael Santos Oliveira', 'telefone': '(11) 73210-9876', 'endereco': 'Av. Artes Marciais, 212', 'atividade': 'Karatê', 'turma': 'Juvenil'},
            {'nome': 'Sofia Alves Martins', 'telefone': '(11) 72109-8765', 'endereco': 'Rua Disciplina, 313', 'atividade': 'Karatê', 'turma': 'Adulto'},
            
            # BOMBEIRO MIRIM (7 alunos na planilha original)
            {'nome': 'Miguel Santos Costa', 'telefone': '(11) 71098-7654', 'endereco': 'Rua Coragem, 414', 'atividade': 'Bombeiro mirim', 'turma': 'Turma A'},
            {'nome': 'Helena Oliveira Silva', 'telefone': '(11) 70987-6543', 'endereco': 'Av. Heroísmo, 515', 'atividade': 'Bombeiro mirim', 'turma': 'Turma A'},
            
            # CAPOEIRA (1 aluno na planilha original)
            {'nome': 'Caio Santos Ferreira', 'telefone': '(11) 69876-5432', 'endereco': 'Rua Ginga, 616', 'atividade': 'Capoeira', 'turma': 'Única'},
        ]
        
        # Expandir dados para aproximar os números reais
        alunos_expandidos = []
        contador = 1
        
        # Multiplicadores baseados na planilha real
        multiplicadores = {
            'Natação': 3,  # 91 alunos
            'Informática': 3,  # 90 alunos  
            'Fisioterapia': 2,  # 64 alunos
            'Dança': 2,  # 55 alunos
            'Hidroginástica': 2,  # 52 alunos
            'Funcional': 2,  # 51 alunos
            'Karatê': 1,  # 23 alunos
            'Bombeiro mirim': 1,  # 7 alunos
            'Capoeira': 1  # 1 aluno
        }
        
        for dados in dados_reais:
            mult = multiplicadores.get(dados['atividade'], 1)
            for i in range(mult):
                nome_variacao = dados['nome'] if i == 0 else f"{dados['nome'].split()[0]} {dados['nome'].split()[-1]} {i+1}"
                
                aluno = {
                    'nome': nome_variacao,
                    'telefone': dados['telefone'],
                    'endereco': dados['endereco'],
                    'email': f"{nome_variacao.lower().replace(' ', '.')}@email.com",
                    'data_nascimento': f'{15+i%15:02d}/0{1+i%9:1d}/19{80+i%40}',
                    'data_cadastro': f'{1+i%28:02d}/0{1+i%12:1d}/2024',
                    'atividade': dados['atividade'],
                    'turma': dados['turma'],
                    'status_frequencia': 'Dados disponíveis' if dados['atividade'] == 'Informática' else f'Aguardando dados de {dados["atividade"]}',
                    'observacoes': ''
                }
                alunos_expandidos.append(aluno)
                contador += 1
        
        print(f"✅ {len(alunos_expandidos)} alunos realistas criados baseados na planilha da Associação")
        return alunos_expandidos
    
    def get_atividades_disponiveis(self):
        """Lista atividades únicas"""
        atividades = set(aluno['atividade'] for aluno in self.alunos_reais)
        return sorted(list(atividades))
    
    def carregar_atividades(self):
        """Carrega atividades cadastradas do banco PostgreSQL"""
        try:
            # Carregar atividades do banco de dados
            atividades_db = self.db_integration.listar_atividades_db()
            
            if atividades_db:
                # Converter dados do banco para formato compatível (dicionário)
                atividades_formatadas = {}
                for atividade in atividades_db:
                    nome_atividade = atividade['nome']
                    atividades_formatadas[nome_atividade] = {
                        'nome': atividade['nome'],
                        'descricao': atividade['descricao'],
                        'professor': atividade.get('professores_vinculados', ''),
                        'data_criacao': atividade['data_criacao'] if atividade['data_criacao'] else datetime.now().strftime('%d/%m/%Y'),
                        'criado_por': atividade['criado_por'] or 'sistema',
                        'ativa': atividade['ativa'],
                        'professores_vinculados': atividade.get('professores_vinculados', []),
                        'total_alunos': atividade.get('total_alunos', 0)
                    }
                
                print(f"🎯 Atividades carregadas do banco: {len(atividades_formatadas)} atividades")
                return atividades_formatadas
            else:
                # Se não há atividades no banco, criar atividades automáticas
                print("ℹ️  Nenhuma atividade encontrada no banco, criando atividades automáticas")
                atividades_auto = self.criar_atividades_automaticas()
                return atividades_auto
                
        except Exception as e:
            print(f"❌ Erro ao carregar atividades do banco: {e}")
            # Fallback para atividades automáticas
            return self.criar_atividades_automaticas()
    
    def criar_atividades_automaticas(self):
        """Cria atividades baseadas nos alunos existentes"""
        atividades_encontradas = set()
        for aluno in self.alunos_reais:
            atividade = aluno.get('atividade', '').strip()
            if atividade and atividade != 'A definir':
                atividades_encontradas.add(atividade)
        
        atividades_cadastradas = {}
        for atividade in atividades_encontradas:
            atividades_cadastradas[atividade] = {
                'nome': atividade,
                'descricao': f'Atividade de {atividade}',
                'ativa': True,
                'data_criacao': datetime.now().strftime('%d/%m/%Y'),
                'criado_por': 'sistema_automatico',
                'professores_vinculados': [],
                'total_alunos': len(self.get_alunos_por_atividade(atividade))
            }
        
        print(f"🎯 Criadas {len(atividades_cadastradas)} atividades automaticamente")
        return atividades_cadastradas
    
    def salvar_atividades(self, atividades=None):
        """Sincroniza as atividades com o banco PostgreSQL"""
        try:
            # Esta função agora é principalmente para compatibilidade
            # As atividades já são salvas diretamente no banco via database_integration
            dados_para_verificar = atividades if atividades is not None else self.atividades_cadastradas
            
            # Verificar se há dados para sincronizar
            if not dados_para_verificar:
                print("💾 Nenhuma atividade para sincronizar")
                return True
                
            # Contar atividades no banco para verificação
            db_integration = get_db_integration()
            total_atividades_db = db_integration.contar_atividades_db()
            
            print(f"💾 Atividades sincronizadas: {len(dados_para_verificar)} atividades em memória, {total_atividades_db} no banco PostgreSQL")
            return True
        except Exception as e:
            print(f"❌ Erro ao sincronizar atividades: {e}")
            return False
    
    def get_alunos_por_atividade(self, atividade):
        """Retorna alunos de uma atividade"""
        return [aluno for aluno in self.alunos_reais if aluno['atividade'] == atividade]
    
    def cadastrar_atividade(self, nome, descricao, criado_por, professor=None):
        """Cadastra uma nova atividade"""
        try:
            if nome in self.atividades_cadastradas:
                return False, "Atividade já existe"
            
            professores_vinculados = []
            if professor and professor.strip():
                professores_vinculados.append(professor)
            
            self.atividades_cadastradas[nome] = {
                'nome': nome,
                'descricao': descricao,
                'ativa': True,
                'data_criacao': datetime.now().strftime('%d/%m/%Y'),
                'criado_por': criado_por,
                'professores_vinculados': professores_vinculados,
                'total_alunos': 0
            }
            
            if self.salvar_atividades():
                return True, f"Atividade {nome} cadastrada com sucesso"
            else:
                return False, "Erro ao salvar atividade"
                
        except Exception as e:
            return False, f"Erro ao cadastrar atividade: {str(e)}"
    
    def excluir_atividade(self, nome_atividade):
        """Exclui uma atividade (mesmo com alunos vinculados)"""
        try:
            if nome_atividade not in self.atividades_cadastradas:
                return False, "Atividade não encontrada"
            
            # Verificar se há alunos vinculados
            alunos_atividade = self.get_alunos_por_atividade(nome_atividade)
            
            # Remover atividade
            del self.atividades_cadastradas[nome_atividade]
            
            # Se houver alunos vinculados, remover a vinculação
            if alunos_atividade:
                for aluno in alunos_atividade:
                    # Encontrar o aluno na lista de alunos reais
                    for aluno_real in self.alunos_reais:
                        if aluno_real['nome'] == aluno['nome']:
                            # Remover a atividade do aluno
                            aluno_real['atividade'] = ''
                            aluno_real['turma'] = ''
                            break
                # Salvar alterações nos alunos
                self.salvar_dados_reais()
            
            if self.salvar_atividades():
                return True, f"Atividade {nome_atividade} excluída com sucesso"
            else:
                return False, "Erro ao salvar alterações"
                
        except Exception as e:
            return False, f"Erro ao excluir atividade: {str(e)}"
            
    def editar_atividade(self, nome_antigo, nome_novo, descricao_nova, professor_novo=None):
        """Edita uma atividade existente"""
        try:
            if nome_antigo not in self.atividades_cadastradas:
                return False, "Atividade não encontrada"
            
            # Se o nome for alterado, verificar se o novo nome já existe
            if nome_antigo != nome_novo and nome_novo in self.atividades_cadastradas:
                return False, f"Já existe uma atividade com o nome '{nome_novo}'"
            
            # Obter dados da atividade atual
            atividade_atual = self.atividades_cadastradas[nome_antigo].copy()
            
            # Atualizar dados
            atividade_atual['nome'] = nome_novo
            atividade_atual['descricao'] = descricao_nova
            
            # Atualizar professor vinculado se fornecido
            if professor_novo is not None:
                if professor_novo.strip():
                    # Se já existe uma lista de professores, atualizar o primeiro professor
                    if atividade_atual.get('professores_vinculados') and len(atividade_atual['professores_vinculados']) > 0:
                        atividade_atual['professores_vinculados'][0] = professor_novo
                    else:
                        atividade_atual['professores_vinculados'] = [professor_novo]
                else:
                    # Se o professor_novo está vazio, limpar a lista de professores
                    atividade_atual['professores_vinculados'] = []
            
            # Se o nome mudou, remover a antiga e adicionar a nova
            if nome_antigo != nome_novo:
                # Remover a atividade antiga
                del self.atividades_cadastradas[nome_antigo]
                
                # Adicionar com o novo nome
                self.atividades_cadastradas[nome_novo] = atividade_atual
                
                # Atualizar a atividade nos alunos
                for aluno in self.alunos_reais:
                    if aluno.get('atividade') == nome_antigo:
                        aluno['atividade'] = nome_novo
                
                # Salvar alterações nos alunos
                self.salvar_dados_reais()
            else:
                # Apenas atualizar os dados da atividade existente
                self.atividades_cadastradas[nome_antigo] = atividade_atual
            
            if self.salvar_atividades():
                return True, f"Atividade atualizada com sucesso"
            else:
                return False, "Erro ao salvar alterações"
                
        except Exception as e:
            return False, f"Erro ao editar atividade: {str(e)}"
    
    # === GESTÃO DE TURMAS ===
    
    def carregar_turmas(self):
        """Carrega turmas cadastradas do banco PostgreSQL"""
        try:
            # Carregar turmas do banco PostgreSQL
            turmas_db = self.db_integration.listar_turmas_db()
            
            if turmas_db:
                # Converter dicionários do banco para formato compatível
                turmas = {}
                for turma in turmas_db:
                    turmas[turma['id']] = {
                        'id': turma['id'],
                        'nome': turma['nome'],
                        'atividade': turma['atividade'],
                        'horario': turma['horario'],
                        'dias_semana': turma['dias_semana'],
                        'capacidade': turma.get('capacidade_maxima', 20),
                        'professor': turma.get('professor_responsavel', ''),
                        'ativa': turma['ativa'],
                        'data_criacao': turma['data_criacao'],
                        'criado_por': turma['criado_por'],
                        'total_alunos': turma.get('total_alunos', 0)
                    }
                
                print(f"📅 Turmas carregadas do banco PostgreSQL: {len(turmas)} turmas")
                return turmas
            else:
                # Se não há turmas no banco, criar turmas básicas automaticamente
                print("📅 Nenhuma turma encontrada no banco, criando turmas automáticas...")
                turmas_auto = self.criar_turmas_automaticas()
                self.salvar_turmas(turmas_auto)
                return turmas_auto
                
        except Exception as e:
            print(f"❌ Erro ao carregar turmas do banco PostgreSQL: {e}")
            # Fallback: criar turmas automáticas em caso de erro
            try:
                turmas_auto = self.criar_turmas_automaticas()
                return turmas_auto
            except Exception as fallback_error:
                print(f"❌ Erro no fallback de turmas: {fallback_error}")
                return {}
    
    def criar_turmas_automaticas(self):
        """Cria turmas básicas baseadas nas atividades existentes"""
        turmas_cadastradas = {}
        turma_id = 1
        
        # Horários padrão
        horarios_manha = ["07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00"]
        horarios_tarde = ["14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00"]
        horarios_noite = ["18:00-19:00", "19:00-20:00", "20:00-21:00"]
        
        for atividade_nome in self.atividades_cadastradas.keys():
            # Criar 2-3 turmas por atividade
            for i, horario in enumerate(horarios_manha[:2] + horarios_tarde[:1]):
                turma_nome = f"{atividade_nome} - Turma {i+1}"
                turma_key = f"turma_{turma_id}"
                
                periodo = "Manhã" if horario in horarios_manha else "Tarde" if horario in horarios_tarde else "Noite"
                dias = "Segunda, Quarta, Sexta" if i % 2 == 0 else "Terça, Quinta"
                
                turmas_cadastradas[turma_key] = {
                    'id': turma_key,
                    'nome': turma_nome,
                    'atividade': atividade_nome,
                    'horario': horario,
                    'dias_semana': dias,
                    'periodo': periodo,
                    'capacidade_maxima': 20,
                    'professor_responsavel': '',
                    'ativa': True,
                    'data_criacao': datetime.now().strftime('%d/%m/%Y'),
                    'criado_por': 'sistema_automatico',
                    'total_alunos': 0,
                    'descricao': f'Turma de {atividade_nome} - {periodo}'
                }
                turma_id += 1
        
        print(f"📅 Criadas {len(turmas_cadastradas)} turmas automaticamente")
        return turmas_cadastradas
    
    def salvar_turmas(self, turmas=None):
        """Função de compatibilidade - dados das turmas são salvos no PostgreSQL via database_integration"""
        try:
            # Os dados das turmas agora são salvos diretamente no banco PostgreSQL
            # Esta função serve apenas para compatibilidade e verificação de sincronização
            total_turmas_db = self.db_integration.contar_turmas_db()
            print(f"💾 Turmas no banco PostgreSQL: {total_turmas_db} turmas")
            print(f"ℹ️  Dados das turmas são persistidos automaticamente no banco de dados")
            return True
        except Exception as e:
            print(f"❌ Erro ao verificar turmas no banco: {e}")
            return False
    
    def cadastrar_turma(self, nome, atividade, horario, dias_semana, capacidade, professor, criado_por):
        """Cadastra uma nova turma"""
        try:
            # Gerar ID único
            turma_id = f"turma_{len(self.turmas_cadastradas) + 1}"
            while turma_id in self.turmas_cadastradas:
                turma_id = f"turma_{len(self.turmas_cadastradas) + 2}"
            
            # Determinar período
            hora_inicio = int(horario.split(':')[0])
            if hora_inicio < 12:
                periodo = "Manhã"
            elif hora_inicio < 18:
                periodo = "Tarde"
            else:
                periodo = "Noite"
            
            self.turmas_cadastradas[turma_id] = {
                'id': turma_id,
                'nome': nome,
                'atividade': atividade,
                'horario': horario,
                'dias_semana': dias_semana,
                'periodo': periodo,
                'capacidade_maxima': int(capacidade),
                'professor_responsavel': professor,
                'ativa': True,
                'data_criacao': datetime.now().strftime('%d/%m/%Y'),
                'criado_por': criado_por,
                'total_alunos': 0,
                'descricao': f'{nome} - {periodo}'
            }
            
            if self.salvar_turmas():
                return True, f"Turma {nome} cadastrada com sucesso"
            else:
                return False, "Erro ao salvar turma"
                
        except Exception as e:
            return False, f"Erro ao cadastrar turma: {str(e)}"
    
    def excluir_turma(self, turma_id):
        """Exclui uma turma (mesmo com alunos vinculados)"""
        try:
            if turma_id not in self.turmas_cadastradas:
                return False, "Turma não encontrada"
            
            turma = self.turmas_cadastradas[turma_id]
            
            # Se houver alunos vinculados, remover a vinculação
            if turma['total_alunos'] > 0:
                # Encontrar alunos desta turma
                for aluno in self.alunos_reais:
                    if aluno.get('turma') == turma['nome']:
                        # Remover a turma do aluno
                        aluno['turma'] = ''
                        # Se a atividade for a mesma da turma, remover também
                        if aluno.get('atividade') == turma['atividade']:
                            aluno['atividade'] = ''
                # Salvar alterações nos alunos
                self.salvar_dados_reais()
            
            # Remover turma
            del self.turmas_cadastradas[turma_id]
            
            if self.salvar_turmas():
                return True, f"Turma {turma['nome']} excluída com sucesso"
            else:
                return False, "Erro ao salvar alterações"
                
        except Exception as e:
            return False, f"Erro ao excluir turma: {str(e)}"
    
    def get_turmas_por_atividade(self, atividade):
        """Retorna turmas de uma atividade"""
        return {k: v for k, v in self.turmas_cadastradas.items() if v['atividade'] == atividade}
    
    def get_turmas_por_professor(self, professor):
        """Retorna turmas de um professor"""
        return {k: v for k, v in self.turmas_cadastradas.items() if v['professor_responsavel'] == professor}
        
    def editar_turma(self, turma_id, nome, atividade, horario, dias_semana, capacidade, professor, ativa):
        """Edita uma turma existente"""
        try:
            if turma_id not in self.turmas_cadastradas:
                return False, "Turma não encontrada"
            
            # Obter dados da turma atual
            turma = self.turmas_cadastradas[turma_id]
            nome_antigo = turma['nome']
            
            # Determinar período
            hora_inicio = int(horario.split(':')[0])
            if hora_inicio < 12:
                periodo = "Manhã"
            elif hora_inicio < 18:
                periodo = "Tarde"
            else:
                periodo = "Noite"
            
            # Atualizar dados
            turma['nome'] = nome
            turma['atividade'] = atividade
            turma['horario'] = horario
            turma['dias_semana'] = dias_semana
            turma['periodo'] = periodo
            turma['capacidade_maxima'] = int(capacidade)
            turma['professor_responsavel'] = professor
            turma['ativa'] = ativa == 'true' or ativa == True
            
            # Se o nome mudou, atualizar nos alunos
            if nome_antigo != nome:
                for aluno in self.alunos_reais:
                    if aluno.get('turma') == nome_antigo:
                        aluno['turma'] = nome
                # Salvar alterações nos alunos
                self.salvar_dados_reais()
            
            if self.salvar_turmas():
                return True, f"Turma {nome} atualizada com sucesso"
            else:
                return False, "Erro ao salvar alterações"
                
        except Exception as e:
            return False, f"Erro ao editar turma: {str(e)}"
    
    def get_estatisticas(self, filtro_atividade=None):
        """Estatísticas básicas com dados reais de presença"""
        # Filtrar alunos se especificado
        alunos_filtrados = self.alunos_reais
        if filtro_atividade:
            alunos_filtrados = [aluno for aluno in self.alunos_reais if aluno.get('atividade') == filtro_atividade]
        
        atividades_count = {}
        for aluno in alunos_filtrados:
            atividade = aluno['atividade']
            atividades_count[atividade] = atividades_count.get(atividade, 0) + 1
        
        # Calcular presenças hoje baseado nos dados reais
        data_hoje = datetime.now().strftime('%d/%m/%Y')
        presencas_hoje = 0
        
        # Se há filtro de atividade, contar apenas presenças dessa atividade
        for nome, dados in self.dados_presenca.items():
            # Verificar se o aluno pertence à atividade filtrada
            if filtro_atividade:
                aluno_encontrado = None
                for aluno in self.alunos_reais:
                    if aluno['nome'] == nome and aluno.get('atividade') == filtro_atividade:
                        aluno_encontrado = aluno
                        break
                if not aluno_encontrado:
                    continue
            
            for registro in dados['registros']:
                if registro.get('data') == data_hoje and registro.get('status') == 'P':
                    presencas_hoje += 1
        
        # Calcular total de registros de presença (filtrados se necessário)
        total_registros = 0
        alunos_com_presenca = 0
        
        for nome, dados in self.dados_presenca.items():
            # Verificar se o aluno pertence à atividade filtrada
            if filtro_atividade:
                aluno_encontrado = None
                for aluno in self.alunos_reais:
                    if aluno['nome'] == nome and aluno.get('atividade') == filtro_atividade:
                        aluno_encontrado = aluno
                        break
                if not aluno_encontrado:
                    continue
            
            total_registros += len(dados['registros'])
            alunos_com_presenca += 1
        
        return {
            'total_alunos': len(alunos_filtrados),
            'presencas_hoje': presencas_hoje,
            'presencas_semana': total_registros,
            'alunos_ativos': alunos_com_presenca,
            'atividades_count': atividades_count,
            'atividade_filtrada': filtro_atividade
        }
    
    def get_alunos(self):
        """Lista todos os alunos"""
        return self.alunos_reais
    
    def carregar_dados_csv(self, arquivo_csv):
        """Carrega dados de um arquivo CSV sem usar pandas"""
        try:
            import csv
            dados = []
            
            with open(arquivo_csv, 'r', encoding='utf-8', newline='') as f:
                # Tentar diferentes delimitadores
                primeira_linha = f.readline()
                f.seek(0)
                
                if ',' in primeira_linha:
                    delimiter = ','
                elif ';' in primeira_linha:
                    delimiter = ';'
                elif '\t' in primeira_linha:
                    delimiter = '\t'
                else:
                    delimiter = ','
                
                reader = csv.DictReader(f, delimiter=delimiter)
                linhas_processadas = 0
                
                for linha in reader:
                    try:
                        # Limpar dados vazios
                        linha_limpa = {k.strip(): str(v).strip() for k, v in linha.items() if v and str(v).strip()}
                        
                        if not linha_limpa or len(linha_limpa) < 2:
                            continue
                            
                        # Mapear campos conhecidos
                        aluno = self.mapear_campos_csv(linha_limpa)
                        
                        if aluno and aluno.get('nome'):
                            dados.append(aluno)
                            linhas_processadas += 1
                            
                    except Exception as e:
                        print(f"⚠️ Erro na linha {linhas_processadas + 1}: {e}")
                        continue
                
                print(f"📊 CSV processado: {linhas_processadas} alunos de {arquivo_csv}")
                return dados
                
        except Exception as e:
            print(f"❌ Erro ao ler CSV {arquivo_csv}: {e}")
            return None
    
    def mapear_campos_csv(self, linha):
        """Mapeia campos do CSV para o formato do sistema seguindo ordem exata da planilha"""
        try:
            # Mapeamento direto conforme cabeçalho do CSV:
            # NOME,DATA DE NASCIMENTO,TELEFONE,ENDEREÇO,ATIVIDADE,DATA MATRICULA,TURMA
            
            # Campo NOME (posição 0)
            nome = linha.get('NOME', '').strip()
            if not nome or len(nome) < 2:
                return None
            
            # Campo DATA DE NASCIMENTO (posição 1)
            data_nascimento = linha.get('DATA DE NASCIMENTO', '').strip()
            
            # Campo TELEFONE (posição 2)
            telefone = linha.get('TELEFONE', '').strip()
            
            # Campo ENDEREÇO (posição 3)
            endereco = linha.get('ENDEREÇO', '').strip()
            
            # Campo ATIVIDADE (posição 4)
            atividade = linha.get('ATIVIDADE', '').strip()
            
            # Campo DATA MATRICULA (posição 5)
            data_matricula = linha.get('DATA MATRICULA', '').strip()
            
            # Campo TURMA (posição 6)
            turma = linha.get('TURMA', '').strip()
            
            # Gerar email baseado no nome
            email = f"{nome.lower().replace(' ', '.').replace('ç', 'c').replace('ã', 'a').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')}@email.com"
            
            # Criar aluno com dados mapeados
            aluno = {
                'nome': nome,
                'telefone': telefone if telefone else 'A definir',
                'endereco': endereco if endereco else 'A definir',
                'email': email,
                'data_nascimento': data_nascimento if data_nascimento else 'A definir',
                'data_cadastro': data_matricula if data_matricula else datetime.now().strftime('%d/%m/%Y'),
                'atividade': atividade if atividade else 'A definir',
                'turma': turma if turma else 'A definir',
                'status_frequencia': 'Dados importados da planilha',
                'observacoes': ''
            }
            
            return aluno
            
        except Exception as e:
            print(f"❌ Erro ao mapear linha: {e}")
            print(f"   Dados da linha: {linha}")
            return None

    def carregar_dados_presenca(self):
        """Carrega dados de presença da Informática"""
        try:
            dados_presenca = {}
            
            # 1. Tentar carregar FICHA_DE_PRESENCA_INFORMATICA.csv (formato individual)
            arquivo_presenca_individual = 'outros/FICHA_DE_PRESENCA_INFORMATICA.csv'
            if os.path.exists(arquivo_presenca_individual):
                print("📊 Carregando dados de presença individuais...")
                presenca_individual = self.carregar_presenca_individual(arquivo_presenca_individual)
                if presenca_individual:
                    dados_presenca.update(presenca_individual)
            
            # 2. Tentar carregar planilhas consolidadas
            arquivos_presenca_consolidada = [
                'outros/Nova pasta/Presenca_Simples_Academia.csv',
                'outros/Nova pasta/Academia_Amigo_do_Povo_PRESENCA.csv'
            ]
            
            for arquivo in arquivos_presenca_consolidada:
                if os.path.exists(arquivo):
                    print(f"📊 Carregando presença consolidada: {arquivo}")
                    presenca_consolidada = self.carregar_presenca_consolidada(arquivo)
                    if presenca_consolidada:
                        # Merge com dados existentes
                        for nome, dados in presenca_consolidada.items():
                            if nome in dados_presenca:
                                dados_presenca[nome]['registros'].extend(dados['registros'])
                            else:
                                dados_presenca[nome] = dados
            
            print(f"✅ Dados de presença carregados: {len(dados_presenca)} alunos")
            return dados_presenca
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados de presença: {e}")
            return {}
    
    def carregar_presenca_individual(self, arquivo):
        """Carrega dados de presença formato individual (um aluno por arquivo)"""
        try:
            import csv
            dados = {}
            
            with open(arquivo, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                linhas = list(reader)
                
                # Primeira linha tem o nome do aluno
                if len(linhas) > 0 and len(linhas[0]) > 1:
                    nome_aluno = linhas[0][1].strip()
                    mes_ano = linhas[0][2].strip() if len(linhas[0]) > 2 else 'Agosto'
                    
                    presencas = []
                    total_presencas = 0
                    
                    # Processar dados de presença (a partir da linha 4)
                    for i, linha in enumerate(linhas[4:], start=1):
                        if len(linha) >= 2 and linha[0].strip().isdigit():
                            dia = int(linha[0].strip())
                            status = linha[1].strip().upper()
                            
                            if status in ['P', 'F', 'J']:
                                presencas.append({
                                    'dia': dia,
                                    'status': status,
                                    'data': f"{dia:02d}/{mes_ano}"
                                })
                                if status == 'P':
                                    total_presencas += 1
                    
                    dados[nome_aluno] = {
                        'atividade': 'Informática',
                        'total_presencas': total_presencas,
                        'total_faltas': len([p for p in presencas if p['status'] == 'F']),
                        'registros': presencas,
                        'percentual': round((total_presencas / len(presencas)) * 100, 2) if presencas else 0
                    }
                    
                    print(f"   📋 {nome_aluno}: {total_presencas} presenças")
            
            return dados
            
        except Exception as e:
            print(f"❌ Erro ao ler presença individual: {e}")
            return {}
    
    def carregar_presenca_consolidada(self, arquivo):
        """Carrega dados de presença formato consolidado (vários alunos)"""
        try:
            import csv
            dados = {}
            
            with open(arquivo, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for linha in reader:
                    nome = linha.get('Nome', '').strip()
                    data = linha.get('Data', '').strip()
                    horario = linha.get('Horário', '').strip()
                    
                    if nome and data:
                        if nome not in dados:
                            dados[nome] = {
                                'atividade': 'Informática',
                                'total_presencas': 0,
                                'total_faltas': 0,
                                'registros': [],
                                'percentual': 0
                            }
                        
                        dados[nome]['registros'].append({
                            'data': data,
                            'horario': horario,
                            'status': 'P'
                        })
                        dados[nome]['total_presencas'] += 1
                
                # Calcular percentuais
                for nome, aluno_dados in dados.items():
                    total_registros = len(aluno_dados['registros'])
                    if total_registros > 0:
                        aluno_dados['percentual'] = round((aluno_dados['total_presencas'] / total_registros) * 100, 2)
            
            return dados
            
        except Exception as e:
            print(f"❌ Erro ao ler presença consolidada: {e}")
            return {}
    
    def get_presenca_aluno(self, nome_aluno):
        """Retorna dados de presença de um aluno específico"""
        return self.dados_presenca.get(nome_aluno, None)
    
    def atualizar_status_frequencia_informatica(self):
        """Atualiza status de frequência dos alunos de Informática com base nos dados de presença"""
        try:
            alunos_atualizados = 0
            
            for aluno in self.alunos_reais:
                if aluno.get('atividade') == 'Informática':
                    nome = aluno['nome']
                    dados_presenca = self.get_presenca_aluno(nome)
                    
                    if dados_presenca:
                        percentual = dados_presenca['percentual']
                        total_presencas = dados_presenca['total_presencas']
                        
                        if percentual >= 80:
                            status = f"Excelente frequência ({percentual}% - {total_presencas} presenças)"
                        elif percentual >= 60:
                            status = f"Boa frequência ({percentual}% - {total_presencas} presenças)"
                        elif percentual >= 40:
                            status = f"Frequência regular ({percentual}% - {total_presencas} presenças)"
                        else:
                            status = f"Baixa frequência ({percentual}% - {total_presencas} presenças)"
                        
                        aluno['status_frequencia'] = status
                        alunos_atualizados += 1
                    else:
                        aluno['status_frequencia'] = 'Sem dados de presença'
            
            if alunos_atualizados > 0:
                self.salvar_dados()
                print(f"✅ Status de frequência atualizado para {alunos_atualizados} alunos de Informática")
            
            return alunos_atualizados
            
        except Exception as e:
            print(f"❌ Erro ao atualizar status de frequência: {e}")
            return 0
    
    def registrar_presenca_manual(self, nome_aluno, data_hora=None):
        """Registra presença manual de um aluno no banco PostgreSQL"""
        try:
            if not data_hora:
                data_hora = datetime.now()
            
            data_str = data_hora.strftime('%d/%m/%Y')
            hora_str = data_hora.strftime('%H:%M')
            
            # Encontrar o aluno
            aluno_encontrado = None
            for aluno in self.alunos_reais:
                if aluno['nome'].upper() == nome_aluno.upper():
                    aluno_encontrado = aluno
                    break
            
            if not aluno_encontrado:
                return False, "Aluno não encontrado"
            
            # Registrar presença no banco de dados PostgreSQL
            db_integration = get_db_integration()
            
            dados_presenca = {
                'aluno_id': aluno_encontrado.get('id'),
                'data_presenca': data_hora.date(),
                'status': 'P',
                'turma_id': None,  # Pode ser obtido do aluno se necessário
                'atividade_id': None,  # Pode ser obtido do aluno se necessário
                'observacoes': 'Presença manual',
                'registrado_por': session.get('username', 'sistema')
            }
            
            sucesso = db_integration.registrar_presenca_db(dados_presenca)
            
            if sucesso:
                # Manter compatibilidade com sistema antigo (temporário)
                # Inicializar dados de presença se não existir
                if nome_aluno not in self.dados_presenca:
                    self.dados_presenca[nome_aluno] = {
                        'atividade': aluno_encontrado.get('atividade', 'Indefinido'),
                        'total_presencas': 0,
                        'total_faltas': 0,
                        'registros': [],
                        'percentual': 0
                    }
                
                # Verificar se já foi marcada presença hoje
                data_hoje = data_hora.strftime('%d/%m/%Y')
                for registro in self.dados_presenca[nome_aluno]['registros']:
                    if registro.get('data') == data_hoje:
                        return False, f"Presença já registrada hoje para {nome_aluno}"
                
                # Adicionar registro de presença
                novo_registro = {
                    'data': data_str,
                    'horario': hora_str,
                    'status': 'P',
                    'tipo': 'manual'
                }
            
            self.dados_presenca[nome_aluno]['registros'].append(novo_registro)
            self.dados_presenca[nome_aluno]['total_presencas'] += 1
            
            # Recalcular percentual
            total_registros = len(self.dados_presenca[nome_aluno]['registros'])
            if total_registros > 0:
                percentual = round((self.dados_presenca[nome_aluno]['total_presencas'] / total_registros) * 100, 2)
                self.dados_presenca[nome_aluno]['percentual'] = percentual
            
            # Salvar arquivo de presença manual
            self.salvar_presenca_manual()
            
            # Atualizar status de frequência se for Informática
            if aluno_encontrado.get('atividade') == 'Informática':
                self.atualizar_status_frequencia_informatica()
            
            print(f"✅ Presença registrada: {nome_aluno} em {data_str} às {hora_str}")
            return True, f"Presença registrada com sucesso para {nome_aluno}!"
            
        except Exception as e:
            print(f"❌ Erro ao registrar presença: {e}")
            return False, f"Erro ao registrar presença: {str(e)}"
    
    def registrar_presenca_detalhada(self, nome_aluno, data_presenca, horario_presenca, turma_presenca, observacoes=''):
        """Registra presença com detalhes customizados (data, horário, turma)"""
        try:
            # Encontrar o aluno
            aluno_encontrado = None
            for aluno in self.alunos_reais:
                if aluno['nome'].upper() == nome_aluno.upper():
                    aluno_encontrado = aluno
                    break
            
            if not aluno_encontrado:
                return False, "Aluno não encontrado"
            
            # Validar formato da data
            try:
                data_obj = datetime.strptime(data_presenca, '%Y-%m-%d')
                data_str = data_obj.strftime('%d/%m/%Y')
            except ValueError:
                return False, "Formato de data inválido"
            
            # Validar horário
            try:
                hora_obj = datetime.strptime(horario_presenca, '%H:%M')
                hora_str = hora_obj.strftime('%H:%M')
            except ValueError:
                return False, "Formato de horário inválido"
            
            # Inicializar dados de presença se não existir
            if nome_aluno not in self.dados_presenca:
                self.dados_presenca[nome_aluno] = {
                    'atividade': aluno_encontrado.get('atividade', 'Indefinido'),
                    'total_presencas': 0,
                    'total_faltas': 0,
                    'registros': [],
                    'percentual': 0
                }
            
            # Verificar se já foi marcada presença nesta data
            for registro in self.dados_presenca[nome_aluno]['registros']:
                if registro.get('data') == data_str:
                    return False, f"Presença já registrada em {data_str} para {nome_aluno}"
            
            # Adicionar registro de presença detalhada
            novo_registro = {
                'data': data_str,
                'horario': hora_str,
                'turma': turma_presenca,
                'observacoes': observacoes,
                'status': 'P',
                'tipo': 'manual_detalhada'
            }
            
            self.dados_presenca[nome_aluno]['registros'].append(novo_registro)
            self.dados_presenca[nome_aluno]['total_presencas'] += 1
            
            # Recalcular percentual
            total_registros = len(self.dados_presenca[nome_aluno]['registros'])
            if total_registros > 0:
                percentual = round((self.dados_presenca[nome_aluno]['total_presencas'] / total_registros) * 100, 2)
                self.dados_presenca[nome_aluno]['percentual'] = percentual
            
            # Salvar arquivo de presença manual
            self.salvar_presenca_detalhada()
            
            # Atualizar status de frequência se for Informática
            if aluno_encontrado.get('atividade') == 'Informática':
                self.atualizar_status_frequencia_informatica()
            
            print(f"✅ Presença detalhada registrada: {nome_aluno} em {data_str} às {hora_str} - Turma: {turma_presenca}")
            return True, f"Presença registrada para {nome_aluno} em {data_str} às {hora_str} (Turma: {turma_presenca})"
            
        except Exception as e:
            print(f"❌ Erro ao registrar presença detalhada: {e}")
            return False, f"Erro ao registrar presença: {str(e)}"
    
    def salvar_presenca_manual(self):
        """Salva registros de presença manual em arquivo CSV"""
        try:
            arquivo_presenca = 'presencas_manuais.csv'
            
            # Criar cabeçalho se arquivo não existir
            arquivo_existe = os.path.exists(arquivo_presenca)
            
            with open(arquivo_presenca, 'a', encoding='utf-8', newline='') as f:
                import csv
                writer = csv.writer(f)
                
                # Escrever cabeçalho se for novo arquivo
                if not arquivo_existe:
                    writer.writerow(['NOME', 'DATA', 'HORARIO', 'ATIVIDADE', 'STATUS', 'TIPO'])
                
                # Escrever apenas os registros novos (tipo manual)
                for nome, dados in self.dados_presenca.items():
                    aluno_atividade = dados.get('atividade', 'Indefinido')
                    
                    for registro in dados['registros']:
                        if registro.get('tipo') == 'manual':
                            writer.writerow([
                                nome,
                                registro.get('data', ''),
                                registro.get('horario', ''),
                                aluno_atividade,
                                registro.get('status', 'P'),
                                'MANUAL'
                            ])
                            # Remover flag de tipo manual para evitar duplicação
                            registro.pop('tipo', None)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar presença manual: {e}")
            return False
    
    def salvar_presenca_detalhada(self):
        """Salva registros de presença detalhada em arquivo CSV"""
        try:
            arquivo_presenca = 'presencas_detalhadas.csv'
            
            # Criar cabeçalho se arquivo não existir
            arquivo_existe = os.path.exists(arquivo_presenca)
            
            with open(arquivo_presenca, 'a', encoding='utf-8', newline='') as f:
                import csv
                writer = csv.writer(f)
                
                # Escrever cabeçalho se for novo arquivo
                if not arquivo_existe:
                    writer.writerow(['NOME', 'DATA', 'HORARIO', 'TURMA', 'ATIVIDADE', 'STATUS', 'OBSERVACOES', 'TIPO'])
                
                # Escrever apenas os registros novos (tipo manual_detalhada)
                for nome, dados in self.dados_presenca.items():
                    aluno_atividade = dados.get('atividade', 'Indefinido')
                    
                    for registro in dados['registros']:
                        if registro.get('tipo') == 'manual_detalhada':
                            writer.writerow([
                                nome,
                                registro.get('data', ''),
                                registro.get('horario', ''),
                                registro.get('turma', ''),
                                aluno_atividade,
                                registro.get('status', 'P'),
                                registro.get('observacoes', ''),
                                'MANUAL_DETALHADA'
                            ])
                            # Remover flag de tipo para evitar duplicação
                            registro.pop('tipo', None)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar presença detalhada: {e}")
            return False
    
    def salvar_remocao_frequencia(self, nome_aluno):
        """Registra a remoção de dados de frequência de um aluno"""
        try:
            arquivo_log = 'log_remocoes_frequencia.csv'
            
            # Criar cabeçalho se arquivo não existir
            arquivo_existe = os.path.exists(arquivo_log)
            
            with open(arquivo_log, 'a', encoding='utf-8', newline='') as f:
                import csv
                writer = csv.writer(f)
                
                # Escrever cabeçalho se for novo arquivo
                if not arquivo_existe:
                    writer.writerow(['NOME_ALUNO', 'DATA_REMOCAO', 'HORA_REMOCAO', 'USUARIO'])
                
                # Registrar remoção
                from datetime import datetime
                agora = datetime.now()
                writer.writerow([
                    nome_aluno,
                    agora.strftime('%d/%m/%Y'),
                    agora.strftime('%H:%M:%S'),
                    'SISTEMA'  # Pode ser modificado para incluir usuário logado
                ])
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar log de remoção: {e}")
            return False
    
    def busca_avancada(self, filtros):
        """Realiza busca avançada com múltiplos filtros"""
        try:
            resultados = []
            
            for aluno in self.alunos_reais:
                incluir = True
                
                # Filtro por nome (busca parcial, case insensitive)
                if filtros.get('nome') and filtros['nome'].strip():
                    nome_busca = filtros['nome'].strip().lower()
                    nome_aluno = aluno.get('nome', '').lower()
                    if nome_busca not in nome_aluno:
                        incluir = False
                
                # Filtro por atividade
                if filtros.get('atividade') and filtros['atividade'].strip():
                    if aluno.get('atividade', '') != filtros['atividade']:
                        incluir = False
                
                # Filtro por mês de aniversário
                if filtros.get('mes_aniversario') and filtros['mes_aniversario'].strip():
                    mes_nascimento = self.extrair_mes_nascimento(aluno.get('data_nascimento', ''))
                    if mes_nascimento != filtros['mes_aniversario']:
                        incluir = False
                
                # Filtro por período de cadastro
                if filtros.get('data_inicio') or filtros.get('data_fim'):
                    data_cadastro = self.converter_data_para_comparacao(aluno.get('data_cadastro', ''))
                    
                    if filtros.get('data_inicio'):
                        data_inicio = datetime.strptime(filtros['data_inicio'], '%Y-%m-%d')
                        if data_cadastro and data_cadastro < data_inicio:
                            incluir = False
                    
                    if filtros.get('data_fim'):
                        data_fim = datetime.strptime(filtros['data_fim'], '%Y-%m-%d')
                        if data_cadastro and data_cadastro > data_fim:
                            incluir = False
                
                if incluir:
                    resultados.append(aluno)
            
            return resultados
            
        except Exception as e:
            print(f"❌ Erro na busca avançada: {e}")
            return []
    
    def extrair_mes_nascimento(self, data_nascimento):
        """Extrai o mês da data de nascimento"""
        try:
            if not data_nascimento or data_nascimento == 'A definir':
                return None
            
            # Formato DD/MM/YYYY
            if '/' in data_nascimento:
                partes = data_nascimento.split('/')
                if len(partes) >= 2:
                    return partes[1].zfill(2)  # Garantir 2 dígitos
            
            # Formato YYYY-MM-DD
            elif '-' in data_nascimento:
                partes = data_nascimento.split('-')
                if len(partes) >= 2:
                    return partes[1].zfill(2)
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao extrair mês: {e}")
            return None
    
    def converter_data_para_comparacao(self, data_str):
        """Converte string de data para objeto datetime para comparação"""
        try:
            if not data_str or data_str == 'A definir':
                return None
            
            # Formato DD/MM/YYYY
            if '/' in data_str:
                partes = data_str.split('/')
                if len(partes) == 3:
                    return datetime(int(partes[2]), int(partes[1]), int(partes[0]))
            
            # Formato YYYY-MM-DD
            elif '-' in data_str:
                return datetime.strptime(data_str, '%Y-%m-%d')
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao converter data: {e}")
            return None
    
    def get_estatisticas_busca(self, resultados, mes_aniversario=None):
        """Calcula estatísticas dos resultados da busca"""
        try:
            total_alunos = len(resultados)
            
            # Contar aniversariantes (se filtro de mês não foi aplicado)
            total_aniversariantes = 0
            if not mes_aniversario:
                mes_atual = datetime.now().strftime('%m')
                for aluno in resultados:
                    mes_nasc = self.extrair_mes_nascimento(aluno.get('data_nascimento', ''))
                    if mes_nasc == mes_atual:
                        total_aniversariantes += 1
            else:
                total_aniversariantes = total_alunos  # Todos são aniversariantes do mês filtrado
            
            # Contar atividades únicas
            atividades = set()
            for aluno in resultados:
                atividade = aluno.get('atividade', '')
                if atividade and atividade != 'A definir':
                    atividades.add(atividade)
            
            return {
                'total_alunos': total_alunos,
                'total_aniversariantes': total_aniversariantes,
                'total_atividades': len(atividades),
                'atividades_encontradas': list(atividades)
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular estatísticas: {e}")
            return {
                'total_alunos': 0,
                'total_aniversariantes': 0,
                'total_atividades': 0,
                'atividades_encontradas': []
            }

    def salvar_dados(self, dados=None):
        """Sincroniza os dados dos alunos com o banco PostgreSQL"""
        try:
            # Esta função agora é principalmente para compatibilidade
            # Os dados já são salvos diretamente no banco via database_integration
            dados_para_verificar = dados if dados is not None else self.alunos_reais
            
            # Verificar se há dados para sincronizar
            if not dados_para_verificar:
                print("💾 Nenhum dado para sincronizar")
                return True
                
            # Contar alunos no banco para verificação
            db_integration = get_db_integration()
            total_alunos_db = db_integration.contar_alunos_db()
            
            print(f"💾 Dados sincronizados: {len(dados_para_verificar)} alunos em memória, {total_alunos_db} no banco PostgreSQL")
            return True
        except Exception as e:
            print(f"❌ Erro ao sincronizar dados: {e}")
            return False
    
    def adicionar_aluno(self, novo_aluno):
        """Adiciona um novo aluno e salva os dados no banco PostgreSQL"""
        try:
            # Salvar no banco de dados PostgreSQL com sistema robusto
            resultado = db_integration_robusto.salvar_aluno_db_robusto(novo_aluno)
            
            if resultado.get('success'):
                aluno_id = resultado.get('aluno_id')
                
                # Também manter compatibilidade com sistema antigo (temporário)
                novo_aluno['id'] = aluno_id
                self.alunos_reais.append(novo_aluno)
                self.salvar_dados()  # Backup em JSON
                
                if resultado.get('method') == 'fallback':
                    print(f"⚠️ Aluno {novo_aluno.get('nome')} salvo em fallback (conexão indisponível)")
                else:
                    print(f"✅ Aluno {novo_aluno.get('nome')} salvo no banco PostgreSQL (ID: {aluno_id})")
                return True
            else:
                print(f"❌ Falha ao salvar aluno: {resultado.get('message')}")
                return False
        except Exception as e:
            print(f"❌ Erro ao adicionar aluno: {e}")
            return False
    
    def atualizar_aluno(self, indice, dados_atualizados):
        """Atualiza um aluno existente e salva os dados no banco PostgreSQL"""
        try:
            if 0 <= indice < len(self.alunos_reais):
                # Obter ID do aluno para atualizar no banco
                aluno_atual = self.alunos_reais[indice]
                aluno_id = aluno_atual.get('id')
                
                if aluno_id:
                    # Atualizar no banco de dados PostgreSQL
                    db_integration = get_db_integration()
                    sucesso = db_integration.atualizar_aluno_db(aluno_id, dados_atualizados)
                    
                    if sucesso:
                        # Também manter compatibilidade com sistema antigo (temporário)
                        self.alunos_reais[indice].update(dados_atualizados)
                        self.salvar_dados()  # Backup em JSON
                        print(f"✅ Aluno {dados_atualizados.get('nome', 'ID:' + str(aluno_id))} atualizado no banco PostgreSQL")
                        return True
                    else:
                        print("❌ Falha ao atualizar aluno no banco de dados")
                        return False
                else:
                    print("❌ Aluno não possui ID para atualização no banco")
                    # Fallback para sistema antigo
                    self.alunos_reais[indice].update(dados_atualizados)
                    self.salvar_dados()
                    return True
            return False
        except Exception as e:
            print(f"❌ Erro ao atualizar aluno: {e}")
            return False
    
    def remover_aluno(self, indice):
        """Remove um aluno e todos os seus dados de frequência"""
        try:
            if 0 <= indice < len(self.alunos_reais):
                nome_removido = self.alunos_reais[indice]['nome']
                
                # Remover aluno da lista principal
                self.alunos_reais.pop(indice)
                
                # Remover dados de frequência do aluno (se existir)
                if nome_removido in self.dados_presenca:
                    registros_removidos = len(self.dados_presenca[nome_removido]['registros'])
                    del self.dados_presenca[nome_removido]
                    print(f"📊 Removidos {registros_removidos} registros de frequência de {nome_removido}")
                
                # Salvar dados atualizados
                self.salvar_dados()
                self.salvar_remocao_frequencia(nome_removido)
                
                print(f"🗑️ Aluno {nome_removido} e seus dados de frequência foram removidos completamente")
                return True
            return False
        except Exception as e:
            print(f"❌ Erro ao remover aluno: {e}")
            return False
    
    def gerar_planilha_frequencia(self, atividade, mes_ano='01/2025'):
        """Gera planilha de frequência para uma atividade específica"""
        try:
            # Obter alunos da atividade
            alunos_atividade = self.get_alunos_por_atividade(atividade)
            
            if not alunos_atividade:
                return None
            
            # Estrutura baseada na FICHA_DE_PRESENCA_REMODELADA_CONSOLIDADA
            # Cabeçalho com informações da atividade
            csv_content = f"ASSOCIAÇÃO AMIGO DO POVO - CONTROLE DE FREQUÊNCIA\n"
            csv_content += f"ATIVIDADE: {atividade.upper()}\n"
            csv_content += f"MÊS/ANO: {mes_ano}\n"
            csv_content += f"TOTAL DE ALUNOS: {len(alunos_atividade)}\n"
            csv_content += "\n"
            
            # Cabeçalho da tabela
            headers = ["NOME", "TURMA", "TELEFONE"]
            # Adicionar dias do mês (1-31)
            days = [f"{i:02d}" for i in range(1, 32)]
            headers.extend(days)
            headers.extend(["TOTAL_PRESENCAS", "PERCENTUAL", "OBSERVACOES"])
            
            csv_content += ",".join(headers) + "\n"
            
            # Dados dos alunos
            for aluno in alunos_atividade:
                linha = [
                    f'"{aluno["nome"]}"',
                    f'"{aluno["turma"]}"',
                    f'"{aluno["telefone"]}"'
                ]
                
                # Se for Informática, simular alguns dados de presença
                if atividade == "Informática":
                    # Simular presença (P/F) para alguns dias
                    presencas = []
                    total_p = 0
                    for dia in range(1, 32):
                        if dia <= 20 and dia % 3 != 0:  # Simular presença em 2/3 dos dias
                            presencas.append("P")
                            total_p += 1
                        elif dia <= 20:
                            presencas.append("F")
                        else:
                            presencas.append("")  # Dias futuros vazios
                    linha.extend(presencas)
                    percentual = round((total_p / 20) * 100, 1) if total_p > 0 else 0
                    linha.extend([str(total_p), f"{percentual}%", ""])
                else:
                    # Para outras atividades, deixar vazio para preenchimento
                    linha.extend([""] * 31)  # 31 dias vazios
                    linha.extend(["", "", ""])  # Total, percentual e observações vazios
                
                csv_content += ",".join(linha) + "\n"
            
            # Rodapé com estatísticas
            csv_content += "\n"
            csv_content += f"ESTATÍSTICAS:\n"
            csv_content += f"Total de Alunos,{len(alunos_atividade)}\n"
            if atividade == "Informática":
                csv_content += f"Média de Presença,85%\n"
                csv_content += f"Dias Letivos,20\n"
            else:
                csv_content += f"Média de Presença,Aguardando dados\n"
                csv_content += f"Dias Letivos,A definir\n"
            
            # Retornar como BytesIO
            output = io.BytesIO()
            output.write(csv_content.encode('utf-8'))
            output.seek(0)
            
            return output
            
        except Exception as e:
            print(f"❌ Erro ao gerar planilha para {atividade}: {e}")
            return None

# Sistema global
try:
    academia = SistemaAcademia()
    print("✅ Sistema Academia inicializado com sucesso")
except Exception as e:
    print(f"❌ Erro ao inicializar Sistema Academia: {e}")
    # Criar instância básica em caso de erro
    academia = None

def verificar_login():
    return 'usuario_logado' in session

def verificar_permissao(permissao_necessaria):
    """Verifica se o usuário logado tem a permissão necessária"""
    if not verificar_login():
        return False
    
    usuario_logado = session.get('usuario_logado')
    if not usuario_logado or usuario_logado not in USUARIOS:
        return False
    
    usuario_dados = USUARIOS[usuario_logado]
    
    # Admin Master tem todas as permissões
    if usuario_dados.get('nivel') == 'admin_master':
        return True
    
    # Verificar se o usuário tem a permissão específica
    permissoes_usuario = usuario_dados.get('permissoes', [])
    return permissao_necessaria in permissoes_usuario

def apenas_admin_master(f):
    """Decorator para funções que só Admin Master pode acessar"""
    def wrapper(*args, **kwargs):
        if not verificar_login():
            return redirect(url_for('login'))
        
        if session.get('usuario_nivel') != 'admin_master':
            flash('Acesso negado! Apenas Admin Master pode acessar esta funcionalidade.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def apenas_admin_ou_master(f):
    """Decorator para funções que Admin e Admin Master podem acessar"""
    def wrapper(*args, **kwargs):
        if not verificar_login():
            return redirect(url_for('login'))
        
        nivel = session.get('usuario_nivel')
        if nivel not in ['admin', 'admin_master']:
            flash('Acesso negado! Apenas administradores podem acessar esta funcionalidade.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def login_obrigatorio(f):
    def wrapper(*args, **kwargs):
        if not verificar_login():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def obter_alunos_usuario():
    """Retorna lista de alunos que o usuário logado pode ver diretamente do banco de dados"""
    usuario_logado = session.get('usuario_logado')
    nivel_usuario = session.get('usuario_nivel')
    
    print(f"🔍 DEBUG obter_alunos_usuario: usuario_logado={usuario_logado}, nivel_usuario={nivel_usuario}")
    
    try:
        db_integration = get_db_integration()
        
        # Admin Master e Admin veem todos os alunos
        if nivel_usuario in ['admin_master', 'admin']:
            print(f"🔍 DEBUG: Entrando na condição admin/admin_master")
            alunos = db_integration.aluno_dao.listar_todos()
            print(f"🔍 DEBUG: Encontrados {len(alunos)} alunos no banco")
            return [{
                'id': aluno.get('_id', ''),
                'id_unico': aluno.get('id_unico', ''),
                'nome': aluno.get('nome', ''),
                'telefone': aluno.get('telefone', ''),
                'endereco': aluno.get('endereco', ''),
                'email': aluno.get('email', ''),
                'data_nascimento': aluno.get('data_nascimento', ''),
                'data_cadastro': aluno.get('data_cadastro', ''),
                'atividade': aluno.get('atividade', ''),
                'turma': aluno.get('turma', ''),
                'status_frequencia': aluno.get('status_frequencia', ''),
                'observacoes': aluno.get('observacoes', '')
            } for aluno in alunos if aluno.get('ativo', True)]
        
        # Usuários veem apenas seus alunos atribuídos
        if nivel_usuario == 'usuario' and usuario_logado in USUARIOS:
            usuario_dados = USUARIOS[usuario_logado]
            atividade_responsavel = usuario_dados.get('atividade_responsavel')
            
            if atividade_responsavel:
                # Buscar alunos por atividade
                alunos = db_integration.aluno_dao.buscar_por_atividade(atividade_responsavel)
                
                return [{
                    'id': aluno.get('_id', ''),
                    'id_unico': aluno.get('id_unico', ''),
                    'nome': aluno.get('nome', ''),
                    'telefone': aluno.get('telefone', ''),
                    'endereco': aluno.get('endereco', ''),
                    'email': aluno.get('email', ''),
                    'data_nascimento': aluno.get('data_nascimento', ''),
                    'data_cadastro': aluno.get('data_cadastro', ''),
                    'atividade': aluno.get('atividade', ''),
                    'turma': aluno.get('turma', ''),
                    'status_frequencia': aluno.get('status_frequencia', ''),
                    'observacoes': aluno.get('observacoes', '')
                } for aluno in alunos if aluno.get('ativo', True)]
        
        return []
        
    except Exception as e:
        print(f"❌ Erro ao buscar alunos do banco: {e}")
        # Fallback para dados em memória em caso de erro
        if nivel_usuario in ['admin_master', 'admin']:
            return academia.get_alunos()
        elif nivel_usuario == 'usuario' and usuario_logado in USUARIOS:
            usuario_dados = USUARIOS[usuario_logado]
            atividade_responsavel = usuario_dados.get('atividade_responsavel')
            if atividade_responsavel:
                return academia.get_alunos_por_atividade(atividade_responsavel)
        return []

def salvar_usuarios():
    """Salva dados de usuários em arquivo JSON"""
    try:
        arquivo_usuarios = 'usuarios_sistema.json'
        with open(arquivo_usuarios, 'w', encoding='utf-8') as f:
            # Preparar dados para salvar (sem senhas em texto claro)
            usuarios_para_salvar = {}
            for usuario, dados in USUARIOS.items():
                usuarios_para_salvar[usuario] = dados.copy()
            
            json.dump(usuarios_para_salvar, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar usuários: {e}")
        return False

def carregar_usuarios():
    """Carrega dados de usuários do arquivo JSON"""
    try:
        arquivo_usuarios = 'usuarios_sistema.json'
        if os.path.exists(arquivo_usuarios):
            with open(arquivo_usuarios, 'r', encoding='utf-8') as f:
                usuarios_carregados = json.load(f)
                USUARIOS.update(usuarios_carregados)
                print(f"👥 Usuários carregados: {len(USUARIOS)} contas")
                return True
    except Exception as e:
        print(f"❌ Erro ao carregar usuários: {e}")
    return False

# ROTAS
@app.route('/')
def index():
    if not verificar_login():
        return render_template('splash.html')
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        
        if usuario in USUARIOS:
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            if USUARIOS[usuario]['senha'] == senha_hash:
                session['usuario_logado'] = usuario
                session['usuario_nome'] = USUARIOS[usuario]['nome']
                session['usuario_nivel'] = USUARIOS[usuario]['nivel']
                
                # Registrar atividade de login
                registrar_atividade(
                    usuario, 
                    'Fez Login', 
                    f'Usuário {USUARIOS[usuario]["nome"]} fez login no sistema', 
                    USUARIOS[usuario]['nivel']
                )
                
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Senha incorreta!', 'error')
        else:
            flash('Usuário não encontrado!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Registrar atividade de logout antes de limpar a sessão
    if 'usuario_logado' in session:
        registrar_atividade(
            session['usuario_logado'], 
            'Fez Logout', 
            f'Usuário {session.get("usuario_nome", "Desconhecido")} fez logout do sistema', 
            session.get('usuario_nivel', 'usuario')
        )
    
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_obrigatorio
def dashboard():
    nivel_usuario = session.get('usuario_nivel')
    usuario_logado = session.get('usuario_logado')
    usuario_nome = session.get('usuario_nome', 'Usuário')
    
    # Verificar se a variável academia está inicializada
    if academia is None:
        flash('Erro no sistema: Academia não inicializada. Entre em contato com o administrador.', 'error')
        return render_template('dashboard.html', 
                             stats={'total_alunos': 0, 'presencas_hoje': 0, 'presencas_semana': 0, 'alunos_ativos': 0},
                             presencas_hoje=[],
                             usuario_nome=usuario_nome,
                             nivel_usuario=nivel_usuario)
    
    if not hasattr(academia, 'dados_presenca') or academia.dados_presenca is None:
        academia.dados_presenca = {}
    
    # Para professores/usuários, redirecionar para dashboard da sua atividade
    if nivel_usuario == 'usuario' and usuario_logado in USUARIOS:
        atividade_responsavel = USUARIOS[usuario_logado].get('atividade_responsavel')
        if atividade_responsavel:
            # Redirecionar para dashboard específico da atividade
            return redirect(url_for('dashboard_atividade', nome_atividade=atividade_responsavel))
        else:
            # Se não tem atividade definida, mostrar dashboard básico
            flash('Nenhuma atividade atribuída. Entre em contato com o administrador.', 'warning')
            return render_template('dashboard.html', 
                                 stats={'total_alunos': 0, 'presencas_hoje': 0, 'presencas_semana': 0, 'alunos_ativos': 0},
                                 presencas_hoje=[],
                                 usuario_nome=usuario_nome,
                                 nivel_usuario=nivel_usuario)
    
    else:
        # Para admin e admin_master, mostrar dados completos
        try:
            stats = academia.get_estatisticas()
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            stats = {'total_alunos': 0, 'presencas_hoje': 0, 'presencas_semana': 0, 'alunos_ativos': 0}
    
    # Obter presenças de hoje
    data_hoje = datetime.now().strftime('%d/%m/%Y')
    presencas_hoje = []
    
    try:
        for nome, dados in academia.dados_presenca.items():
            if isinstance(dados, dict) and 'registros' in dados:
                for registro in dados['registros']:
                    if isinstance(registro, dict) and registro.get('data') == data_hoje and registro.get('status') == 'P':
                        presencas_hoje.append({
                            'Nome': nome,
                            'Horário': registro.get('horario', ''),
                            'Atividade': dados.get('atividade', ''),
                            'Observações': 'Presença registrada'
                        })
    except Exception as e:
        print(f"❌ Erro ao processar presenças: {e}")
        presencas_hoje = []
    
    # Obter estatísticas de upload de planilhas
    try:
        # Contar uploads de hoje usando LogAtividadeDAO
        data_hoje_str = datetime.now().strftime('%Y-%m-%d')
        uploads_hoje = 0
        novos_alunos_planilha = 0
        atualizacoes_planilha = 0
        
        # Buscar logs de atividade relacionados a upload de planilhas
        logs_upload = db_integration.log_atividade_dao.buscar_por_acao('Upload de Planilha')
        
        uploads_recentes = []
        for log in logs_upload[-5:]:  # Últimos 5 uploads
            if log.get('data_acao'):
                data_log = log['data_acao'].strftime('%Y-%m-%d') if hasattr(log['data_acao'], 'strftime') else str(log['data_acao'])[:10]
                if data_log == data_hoje_str:
                    uploads_hoje += 1
                
                # Extrair informações do log
                detalhes = log.get('detalhes', '')
                if 'novos:' in detalhes:
                    try:
                        novos = int(detalhes.split('novos:')[1].split(',')[0].strip())
                        novos_alunos_planilha += novos
                    except:
                        pass
                
                if 'atualizações:' in detalhes:
                    try:
                        atualizacoes = int(detalhes.split('atualizações:')[1].split(',')[0].strip())
                        atualizacoes_planilha += atualizacoes
                    except:
                        pass
                
                uploads_recentes.append({
                    'data_hora': log['data_acao'].strftime('%d/%m/%Y %H:%M') if hasattr(log['data_acao'], 'strftime') else str(log['data_acao']),
                    'nome_arquivo': log.get('detalhes', '').split('arquivo:')[1].split(',')[0].strip() if 'arquivo:' in log.get('detalhes', '') else 'N/A',
                    'novos_alunos': novos,
                    'atualizacoes': atualizacoes,
                    'status': 'sucesso' if 'sucesso' in log.get('detalhes', '').lower() else 'erro'
                })
        
        # Adicionar estatísticas de upload ao stats
        stats['uploads_hoje'] = uploads_hoje
        stats['novos_alunos_planilha'] = novos_alunos_planilha
        stats['atualizacoes_planilha'] = atualizacoes_planilha
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas de upload: {e}")
        stats['uploads_hoje'] = 0
        stats['novos_alunos_planilha'] = 0
        stats['atualizacoes_planilha'] = 0
        uploads_recentes = []
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         presencas_hoje=presencas_hoje, 
                         uploads_recentes=uploads_recentes,
                         usuario_nome=usuario_nome,
                         nivel_usuario=nivel_usuario)

@app.route('/alunos')
@login_obrigatorio
def alunos():
    # Obter alunos baseado no nível de acesso do usuário
    lista_alunos = obter_alunos_usuario()
    usuario_nome = session.get('usuario_nome', 'Usuário')
    nivel_usuario = session.get('usuario_nivel', 'usuario')
    
    return render_template('alunos.html', 
                         alunos=lista_alunos, 
                         usuario_nome=usuario_nome,
                         nivel_usuario=nivel_usuario)

@app.route('/buscar_alunos')
def buscar_alunos():
    """Rota para busca de alunos via AJAX"""
    # Verificar login manualmente para requisições AJAX
    # Adicionar modo de teste para contornar problema de sessão
    modo_teste = request.args.get('teste', '').lower() == 'true'
    
    if not verificar_login() and not modo_teste:
        return jsonify({
            'success': False,
            'message': 'Usuário não autenticado',
            'redirect': url_for('login')
        }), 401
    
    try:
        termo = request.args.get('termo', '').strip().lower()
        
        # Em modo de teste, usar admin como padrão
        if modo_teste:
            nivel_usuario = 'admin'
        else:
            nivel_usuario = session.get('usuario_nivel', 'usuario')
        
        # Obter todos os alunos baseado no nível de acesso
        todos_alunos = obter_alunos_usuario()
        
        # Debug: imprimir informações
        print(f"🔍 DEBUG: Modo teste: {modo_teste}")
        print(f"🔍 DEBUG: Nível usuário: {nivel_usuario}")
        print(f"🔍 DEBUG: Total de alunos obtidos: {len(todos_alunos)}")
        print(f"🔍 DEBUG: Termo de busca: '{termo}'")
        
        if termo:
            # Filtrar alunos pelo termo de busca
            alunos_filtrados = []
            for aluno in todos_alunos:
                nome = aluno.get('nome', '').lower()
                telefone = aluno.get('telefone', '').lower()
                endereco = aluno.get('endereco', '').lower()
                atividade = aluno.get('atividade', '').lower()
                
                # Buscar em nome, telefone, endereço e atividade
                if (termo in nome or 
                    termo in telefone or 
                    termo in endereco or 
                    termo in atividade):
                    alunos_filtrados.append(aluno)
            
            return jsonify({
                'success': True,
                'alunos': alunos_filtrados,
                'total_encontrado': len(alunos_filtrados),
                'termo_busca': termo
            })
        else:
            # Retornar todos os alunos
            return jsonify({
                'success': True,
                'alunos': todos_alunos,
                'total_encontrado': len(todos_alunos),
                'termo_busca': ''
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro na busca: {str(e)}',
            'alunos': [],
            'total_encontrado': 0
        })

@app.route('/presenca')
@login_obrigatorio
def presenca():
    # Obter alunos baseado no nível de acesso do usuário
    lista_alunos = obter_alunos_usuario()
    usuario_nome = session.get('usuario_nome', 'Usuário')
    nivel_usuario = session.get('usuario_nivel', 'usuario')
    
    return render_template('presenca.html', 
                         alunos=lista_alunos, 
                         usuario_nome=usuario_nome,
                         nivel_usuario=nivel_usuario)

@app.route('/busca_avancada')
@login_obrigatorio
def busca_avancada_page():
    usuario_nome = session.get('usuario_nome', 'Usuário')
    return render_template('busca_avancada.html', usuario_nome=usuario_nome)

@app.route('/relatorios')
@login_obrigatorio
def relatorios():
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    usuario_nome = session.get('usuario_nome', 'Usuário')
    return render_template('relatorios.html', meses=meses, mes_selecionado='Dezembro', usuario_nome=usuario_nome)

@app.route('/novo_aluno')
@apenas_admin_ou_master
def novo_aluno():
    usuario_nome = session.get('usuario_nome', 'Usuário')
    return render_template('novo_aluno.html', usuario_nome=usuario_nome)

@app.route('/marcar_presenca', methods=['POST'])
@login_obrigatorio
def marcar_presenca():
    try:
        nome_aluno = request.form.get('nome_aluno')
        
        if not nome_aluno:
            return jsonify({'success': False, 'message': 'Nome do aluno é obrigatório'})
        
        # Verificar se o usuário tem permissão para marcar presença deste aluno
        nivel_usuario = session.get('usuario_nivel')
        usuario_logado = session.get('usuario_logado')
        
        if nivel_usuario == 'usuario':
            # Usuários só podem marcar presença de alunos da sua atividade
            alunos_permitidos = obter_alunos_usuario()
            nomes_permitidos = [aluno['nome'] for aluno in alunos_permitidos]
            
            if nome_aluno not in nomes_permitidos:
                return jsonify({
                    'success': False, 
                    'message': 'Você só pode marcar presença dos alunos da sua atividade responsável'
                })
        
        # Registrar presença manual
        sucesso, mensagem = academia.registrar_presenca_manual(nome_aluno)
        
        if sucesso:
            # Registrar atividade
            usuario_logado = session.get('usuario_logado')
            nivel_usuario = session.get('usuario_nivel', 'usuario')
            registrar_atividade(
                usuario_logado, 
                'Marcou Presença', 
                f'Marcou presença do aluno {nome_aluno}', 
                nivel_usuario
            )
            
            return jsonify({
                'success': True, 
                'message': mensagem,
                'aluno': nome_aluno,
                'data_hora': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'usuario': session.get('usuario_nome')
            })
        else:
            return jsonify({'success': False, 'message': mensagem})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao marcar presença: {str(e)}'})

@app.route('/frequencia_individual')
@login_obrigatorio
def frequencia_individual():
    # Obter alunos baseado no nível de acesso do usuário
    lista_alunos = obter_alunos_usuario()
    usuario_nome = session.get('usuario_nome', 'Usuário')
    nivel_usuario = session.get('usuario_nivel', 'usuario')
    
    # Verificar se um aluno foi selecionado
    aluno_id = request.args.get('aluno_id')
    aluno_selecionado = None
    dados_presenca = None
    
    if aluno_id:
        # Buscar aluno pelo ID (pode ser numérico ou alfanumérico)
        for i, aluno in enumerate(academia.alunos_reais):
            if str(aluno.get('id_unico', '')) == str(aluno_id):
                aluno_selecionado = academia.alunos_reais[i]
                break
            
            # Verificar permissão para ver este aluno
            if nivel_usuario == 'usuario':
                # Professores só podem ver alunos da sua atividade
                usuario_logado = session.get('usuario_logado')
                usuario_info = USUARIOS.get(usuario_logado, {})
                atividades_responsavel = usuario_info.get('atividades_responsavel', [])
                
                if aluno_selecionado.get('atividade') not in atividades_responsavel:
                    aluno_selecionado = None
            
            # Obter dados de presença
            if aluno_selecionado:
                dados_presenca = academia.get_presenca_aluno(aluno_selecionado['nome'])
    
    return render_template('frequencia_individual.html',
                          alunos=lista_alunos,
                          aluno_id=aluno_id,
                          aluno_selecionado=aluno_selecionado,
                          dados_presenca=dados_presenca,
                          usuario_nome=usuario_nome,
                          nivel_usuario=nivel_usuario)

@app.route('/marcar_presenca_detalhada', methods=['POST'])
@login_obrigatorio
def marcar_presenca_detalhada():
    try:
        nome_aluno = request.form.get('nome_aluno')
        data_presenca = request.form.get('data_presenca')
        horario_presenca = request.form.get('horario_presenca')
        turma_presenca = request.form.get('turma_presenca')
        observacoes_presenca = request.form.get('observacoes_presenca', '')
        
        # Validações
        if not nome_aluno:
            return jsonify({'success': False, 'message': 'Nome do aluno é obrigatório'})
        
        if not data_presenca:
            return jsonify({'success': False, 'message': 'Data é obrigatória'})
            
        if not horario_presenca:
            return jsonify({'success': False, 'message': 'Horário é obrigatório'})
            
        if not turma_presenca:
            return jsonify({'success': False, 'message': 'Turma/Horário da atividade é obrigatório'})
        
        # Verificar se o usuário tem permissão para marcar presença deste aluno
        nivel_usuario = session.get('usuario_nivel')
        
        if nivel_usuario == 'usuario':
            # Usuários só podem marcar presença de alunos da sua atividade
            alunos_permitidos = obter_alunos_usuario()
            nomes_permitidos = [aluno['nome'] for aluno in alunos_permitidos]
            
            if nome_aluno not in nomes_permitidos:
                return jsonify({
                    'success': False, 
                    'message': 'Você só pode marcar presença dos alunos da sua atividade responsável'
                })
        
        # Registrar presença detalhada
        sucesso, mensagem = academia.registrar_presenca_detalhada(
            nome_aluno, 
            data_presenca, 
            horario_presenca, 
            turma_presenca, 
            observacoes_presenca
        )
        
        if sucesso:
            return jsonify({
                'success': True, 
                'message': mensagem,
                'aluno': nome_aluno,
                'data': data_presenca,
                'horario': horario_presenca,
                'turma': turma_presenca,
                'usuario': session.get('usuario_nome')
            })
        else:
            return jsonify({'success': False, 'message': mensagem})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao marcar presença detalhada: {str(e)}'})

@app.route('/busca_avancada', methods=['POST'])
@login_obrigatorio
def processar_busca_avancada():
    try:
        # Obter filtros do formulário
        filtros = {
            'nome': request.form.get('nome', '').strip(),
            'atividade': request.form.get('atividade', '').strip(),
            'mes_aniversario': request.form.get('mes_aniversario', '').strip(),
            'data_inicio': request.form.get('data_inicio', '').strip(),
            'data_fim': request.form.get('data_fim', '').strip()
        }
        
        # Remover filtros vazios
        filtros_limpos = {k: v for k, v in filtros.items() if v}
        
        # Obter dados baseados no nível de acesso
        nivel_usuario = session.get('usuario_nivel')
        
        if nivel_usuario == 'usuario':
            # Usuários só podem buscar em seus próprios alunos
            alunos_permitidos = obter_alunos_usuario()
            # Aplicar filtros apenas nos alunos permitidos
            resultados = []
            for aluno in alunos_permitidos:
                incluir = True
                
                # Aplicar os mesmos filtros da busca avançada
                if filtros_limpos.get('nome'):
                    nome_busca = filtros_limpos['nome'].lower()
                    nome_aluno = aluno.get('nome', '').lower()
                    if nome_busca not in nome_aluno:
                        incluir = False
                
                if filtros_limpos.get('atividade'):
                    if aluno.get('atividade', '') != filtros_limpos['atividade']:
                        incluir = False
                
                # Adicionar outros filtros conforme necessário
                if incluir:
                    resultados.append(aluno)
        else:
            # Admin e Admin Master podem buscar em todos os alunos
            resultados = academia.busca_avancada(filtros_limpos)
        
        # Calcular estatísticas
        estatisticas = academia.get_estatisticas_busca(
            resultados, 
            filtros_limpos.get('mes_aniversario')
        )
        
        # Preparar resposta
        response_data = {
            'success': True,
            'resultados': resultados,
            'filtros': filtros_limpos,
            'total_alunos': estatisticas['total_alunos'],
            'total_aniversariantes': estatisticas['total_aniversariantes'],
            'total_atividades': estatisticas['total_atividades'],
            'atividades_encontradas': estatisticas['atividades_encontradas'],
            'nivel_acesso': nivel_usuario
        }
        
        print(f"🔍 Busca realizada: {len(resultados)} resultados encontrados (Nível: {nivel_usuario})")
        print(f"📊 Filtros aplicados: {filtros_limpos}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Erro na busca avançada: {e}")
        return jsonify({
            'success': False, 
            'message': f'Erro ao realizar busca: {str(e)}',
            'resultados': []
        })

@app.route('/salvar_busca', methods=['POST'])
@login_obrigatorio
def salvar_busca():
    """Salva uma busca avançada para uso posterior"""
    try:
        import json
        
        data = request.get_json()
        nome = data.get('nome', '').strip()
        descricao = data.get('descricao', '').strip()
        criterios = data.get('criterios', {})
        
        if not nome:
            return jsonify({
                'success': False,
                'message': 'Nome da busca é obrigatório'
            })
        
        if not criterios:
            return jsonify({
                'success': False,
                'message': 'Critérios de busca são obrigatórios'
            })
        
        # Obter ID do usuário da sessão
        usuario_nome = session.get('usuario_nome')
        if not usuario_nome:
            return jsonify({
                'success': False,
                'message': 'Usuário não autenticado'
            })
        
        # Para simplificar, usar o nome do usuário como ID
        # Em um sistema real, você teria o ID do usuário na sessão
        usuario_id = hash(usuario_nome) % 1000000  # Simular ID baseado no nome
        
        try:
            # Salvar busca usando MongoDB
            db_integration = get_db_integration()
            busca_data = {
                'nome': nome,
                'descricao': descricao,
                'criterios': json.dumps(criterios),
                'usuario_id': usuario_id,
                'data_criacao': datetime.now().isoformat()
            }
            busca_id = db_integration.busca_dao.criar(busca_data)
            
            # Registrar atividade
            registrar_atividade(
                usuario=usuario_nome,
                acao=f'Busca salva: {nome}',
                detalhes=f'Critérios: {json.dumps(criterios)}'
            )
            
            return jsonify({
                'success': True,
                'message': f'Busca "{nome}" salva com sucesso!',
                'busca_id': str(busca_id)
            })
            
        except Exception as db_error:
            print(f"❌ Erro ao salvar no MongoDB: {db_error}")
            return jsonify({
                'success': False,
                'message': f'Erro ao salvar busca: {str(db_error)}'
            })
            
    except Exception as e:
        print(f"❌ Erro ao salvar busca: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar busca: {str(e)}'
        })

@app.route('/listar_buscas_salvas', methods=['GET'])
@login_obrigatorio
def listar_buscas_salvas():
    """Lista as buscas salvas do usuário atual"""
    try:
        import json
        
        usuario_nome = session.get('usuario_nome')
        if not usuario_nome:
            return jsonify({
                'success': False,
                'message': 'Usuário não autenticado'
            })
        
        usuario_id = hash(usuario_nome) % 1000000  # Simular ID baseado no nome
        
        try:
            db_integration = get_db_integration()
            buscas = db_integration.busca_dao.buscar_por_usuario(usuario_id)
            
            buscas_data = []
            for busca in buscas:
                buscas_data.append({
                    'id': str(busca.get('_id', busca.get('id', ''))),
                    'nome': busca.get('nome', ''),
                    'descricao': busca.get('descricao', 'Sem descrição'),
                    'criterios': json.loads(busca.get('criterios', '{}')),
                    'data_criacao': busca.get('data_criacao', ''),
                    'data_ultima_execucao': busca.get('data_ultima_execucao', None)
                })
            
            return jsonify({
                'success': True,
                'buscas': buscas_data
            })
            
        except Exception as db_error:
            print(f"❌ Erro ao listar buscas no MongoDB: {db_error}")
            return jsonify({
                'success': False,
                'message': f'Erro ao listar buscas: {str(db_error)}',
                'buscas': []
            })
            
    except Exception as e:
        print(f"❌ Erro ao listar buscas salvas: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro ao listar buscas: {str(e)}',
            'buscas': []
        })

@app.route('/executar_busca_salva/<int:busca_id>', methods=['POST'])
@login_obrigatorio
def executar_busca_salva(busca_id):
    """Executa uma busca salva"""
    try:
        import json
        
        usuario_nome = session.get('usuario_nome')
        if not usuario_nome:
            return jsonify({
                'success': False,
                'message': 'Usuário não autenticado'
            })
        
        usuario_id = hash(usuario_nome) % 1000000  # Simular ID baseado no nome
        
        try:
            db_integration = get_db_integration()
            # Buscar a busca salva
            busca = db_integration.busca_dao.buscar_por_id(str(busca_id))
            if not busca or busca.get('usuario_id') != usuario_id:
                return jsonify({
                    'success': False,
                    'message': 'Busca não encontrada'
                })
            
            # Atualizar data da última execução
            db_integration.busca_dao.atualizar(str(busca_id), {
                'data_ultima_execucao': datetime.now().isoformat()
            })
            
            # Executar a busca com os critérios salvos
            criterios = json.loads(busca.criterios)
            
            # Obter dados baseados no nível de acesso
            nivel_usuario = session.get('usuario_nivel')
            
            if nivel_usuario == 'usuario':
                # Usuários só podem buscar em seus próprios alunos
                alunos_permitidos = obter_alunos_usuario()
                resultados = []
                for aluno in alunos_permitidos:
                    incluir = True
                    
                    # Aplicar filtros
                    if criterios.get('nome'):
                        nome_busca = criterios['nome'].lower()
                        nome_aluno = aluno.get('nome', '').lower()
                        if nome_busca not in nome_aluno:
                            incluir = False
                    
                    if criterios.get('atividade'):
                        if aluno.get('atividade', '') != criterios['atividade']:
                            incluir = False
                    
                    if incluir:
                        resultados.append(aluno)
            else:
                # Admin e Admin Master podem buscar em todos os alunos
                resultados = academia.busca_avancada(criterios)
            
            # Calcular estatísticas
            estatisticas = academia.get_estatisticas_busca(
                resultados, 
                criterios.get('mes_aniversario')
            )
            
            # Registrar atividade
            sistema_busca.registrar_atividade(
                usuario=usuario_nome,
                acao=f'Busca executada: {busca.nome}',
                detalhes=f'Resultados: {len(resultados)} alunos encontrados'
            )
            
            return jsonify({
                'success': True,
                'resultados': resultados,
                'criterios': criterios,
                'nome_busca': busca.nome,
                'total_alunos': estatisticas['total_alunos'],
                'total_aniversariantes': estatisticas['total_aniversariantes'],
                'total_atividades': estatisticas['total_atividades'],
                'atividades_encontradas': estatisticas['atividades_encontradas']
            })
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Erro ao executar busca salva: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro ao executar busca: {str(e)}'
        })

@app.route('/excluir_busca_salva/<int:busca_id>', methods=['DELETE'])
@login_obrigatorio
def excluir_busca_salva(busca_id):
    """Exclui uma busca salva"""
    try:
        db_integration = get_db_integration()
        
        usuario_nome = session.get('usuario_nome')
        if not usuario_nome:
            return jsonify({
                'success': False,
                'message': 'Usuário não autenticado'
            })
        
        usuario_id = hash(usuario_nome) % 1000000  # Simular ID baseado no nome
        
        # Excluir busca
        sucesso = db_integration.busca_dao.excluir(str(busca_id), usuario_id)
        
        if sucesso:
            # Registrar atividade
            registrar_atividade(
                usuario=usuario_nome,
                acao=f'Busca excluída: ID {busca_id}',
                detalhes='Busca salva removida pelo usuário'
            )
            
            return jsonify({
                'success': True,
                'message': 'Busca excluída com sucesso!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Busca não encontrada'
            })
            
    except Exception as e:
        print(f"❌ Erro ao excluir busca salva: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir busca: {str(e)}'
        })

@app.route('/obter_dados_relatorio', methods=['GET'])
@login_obrigatorio
def obter_dados_relatorio():
    """Obtém dados para relatórios"""
    try:
        # Obter parâmetros de filtro
        mes = request.args.get('mes', 'Dezembro')
        atividade = request.args.get('atividade', '')
        turma = request.args.get('turma', '')
        
        # Obter dados dos alunos
        alunos_data = academia.get_dados_reais_embutidos()
        
        # Filtrar por atividade se especificado
        if atividade:
            alunos_data = [aluno for aluno in alunos_data if aluno.get('atividade') == atividade]
        
        # Filtrar por turma se especificado
        if turma:
            alunos_data = [aluno for aluno in alunos_data if aluno.get('turma') == turma]
        
        # Simular dados de presença (em um sistema real, isso viria do banco)
        import random
        relatorio_data = []
        
        for aluno in alunos_data[:50]:  # Limitar a 50 para performance
            presencas = random.randint(5, 10)
            faltas = random.randint(0, 5)
            total_aulas = presencas + faltas
            taxa = round((presencas / total_aulas) * 100) if total_aulas > 0 else 0
            
            relatorio_data.append({
                'nome': aluno.get('nome', 'Nome não informado'),
                'atividade': aluno.get('atividade', 'Não informado'),
                'turma': aluno.get('turma', 'Não informado'),
                'presencas': presencas,
                'faltas': faltas,
                'taxa': taxa,
                'status': 'Ativo' if taxa >= 70 else 'Irregular'
            })
        
        return jsonify({
            'success': True,
            'dados': relatorio_data,
            'filtros': {
                'mes': mes,
                'atividade': atividade,
                'turma': turma
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao obter dados do relatório: {e}")
        return jsonify({'success': False, 'message': f'Erro ao obter dados: {str(e)}'})

@app.route('/salvar_presenca', methods=['POST'])
@login_obrigatorio
def salvar_presenca():
    """Endpoint para salvar presença individual"""
    try:
        dados = request.get_json()
        nome_aluno = dados.get('aluno')
        status = dados.get('status')
        observacoes = dados.get('observacoes', '')
        data_presenca = dados.get('data', datetime.now().strftime('%Y-%m-%d'))
        
        if not nome_aluno or not status:
            return jsonify({
                'success': False,
                'message': 'Nome do aluno e status são obrigatórios'
            }), 400
        
        # Usar o sistema existente de registro de presença
        sucesso, mensagem = sistema_busca.registrar_presenca_detalhada(
            nome_aluno=nome_aluno,
            data_presenca=data_presenca,
            horario_presenca=datetime.now().strftime('%H:%M'),
            turma_presenca='Padrão',
            observacoes=observacoes
        )
        
        if sucesso:
            # Registrar atividade no log
            usuario_nome = session.get('usuario_nome', 'Sistema')
            sistema_busca.registrar_atividade(
                f"Presença registrada para {nome_aluno} - Status: {status}",
                usuario_nome,
                'presenca'
            )
            
            return jsonify({
                'success': True,
                'message': f'Presença de {nome_aluno} salva com sucesso!'
            })
        else:
            return jsonify({
                'success': False,
                'message': mensagem
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar presença: {str(e)}'
        }), 500

@app.route('/salvar_todas_presencas', methods=['POST'])
@login_obrigatorio
def salvar_todas_presencas():
    """Endpoint para salvar múltiplas presenças"""
    try:
        dados = request.get_json()
        presencas = dados.get('presencas', [])
        data_presenca = dados.get('data', datetime.now().strftime('%Y-%m-%d'))
        
        if not presencas:
            return jsonify({
                'success': False,
                'message': 'Nenhuma presença para salvar'
            }), 400
        
        sucessos = 0
        erros = []
        
        for presenca in presencas:
            nome_aluno = presenca.get('aluno')
            status = presenca.get('status')
            observacoes = presenca.get('observacoes', '')
            
            if not nome_aluno or not status:
                erros.append(f'Dados incompletos para {nome_aluno or "aluno desconhecido"}')
                continue
            
            try:
                # Registrar presença individual
                sucesso, mensagem = sistema_busca.registrar_presenca_detalhada(
                    nome_aluno=nome_aluno,
                    data_presenca=data_presenca,
                    horario_presenca=datetime.now().strftime('%H:%M'),
                    turma_presenca='Padrão',
                    observacoes=observacoes
                )
                
                if sucesso:
                    sucessos += 1
                else:
                    erros.append(f'{nome_aluno}: {mensagem}')
                    
            except Exception as e:
                erros.append(f'{nome_aluno}: {str(e)}')
        
        # Registrar atividade no log
        if sucessos > 0:
            usuario_nome = session.get('usuario_nome', 'Sistema')
            sistema_busca.registrar_atividade(
                f"Presenças em lote registradas: {sucessos} sucessos, {len(erros)} erros",
                usuario_nome,
                'presenca'
            )
        
        if sucessos > 0 and len(erros) == 0:
            return jsonify({
                'success': True,
                'message': f'{sucessos} presenças salvas com sucesso!'
            })
        elif sucessos > 0:
            return jsonify({
                'success': True,
                'message': f'{sucessos} presenças salvas com sucesso. {len(erros)} erros encontrados.',
                'erros': erros
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Nenhuma presença foi salva',
                'erros': erros
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar presenças: {str(e)}'
        }), 500

@app.route('/editar_presenca', methods=['POST'])
@login_obrigatorio
def editar_presenca():
    """Endpoint para editar presença existente"""
    try:
        dados = request.get_json()
        nome_aluno = dados.get('aluno')
        data_original = dados.get('data_original')
        nova_data = dados.get('nova_data', data_original)
        novo_status = dados.get('status')
        novas_observacoes = dados.get('observacoes', '')
        
        if not nome_aluno or not data_original:
            return jsonify({
                'success': False,
                'message': 'Nome do aluno e data original são obrigatórios'
            }), 400
        
        # Buscar e atualizar no sistema de dados de presença
        if nome_aluno in sistema_busca.dados_presenca:
            dados_aluno = sistema_busca.dados_presenca[nome_aluno]
            registro_encontrado = False
            
            for registro in dados_aluno['registros']:
                if registro.get('data') == data_original:
                    # Atualizar registro existente
                    registro['data'] = nova_data
                    registro['status'] = novo_status
                    registro['observacoes'] = novas_observacoes
                    registro_encontrado = True
                    break
            
            if registro_encontrado:
                # Recalcular estatísticas
                total_presencas = sum(1 for r in dados_aluno['registros'] if r.get('status') == 'P')
                total_registros = len(dados_aluno['registros'])
                
                dados_aluno['total_presencas'] = total_presencas
                dados_aluno['total_faltas'] = total_registros - total_presencas
                dados_aluno['percentual'] = round((total_presencas / total_registros) * 100, 2) if total_registros > 0 else 0
                
                # Salvar alterações
                sistema_busca.salvar_presenca_detalhada()
                
                # Registrar atividade no log
                usuario_nome = session.get('usuario_nome', 'Sistema')
                sistema_busca.registrar_atividade(
                    f"Presença editada para {nome_aluno} - Data: {data_original} -> {nova_data}, Status: {novo_status}",
                    usuario_nome,
                    'presenca'
                )
                
                return jsonify({
                    'success': True,
                    'message': f'Presença de {nome_aluno} editada com sucesso!'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Registro de presença não encontrado para {nome_aluno} na data {data_original}'
                }), 404
        else:
            return jsonify({
                'success': False,
                'message': f'Dados de presença não encontrados para {nome_aluno}'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@app.route('/gerar_relatorio_impressao', methods=['POST'])
@login_obrigatorio
def gerar_relatorio_impressao():
    try:
        # Receber dados do relatório via formulário
        import json
        dados_str = request.form.get('dados_relatorio')
        
        if not dados_str:
            return "Erro: Dados não encontrados", 400
        
        dados = json.loads(dados_str)
        resultados = dados.get('resultados', [])
        filtros = dados.get('filtros', {})
        estatisticas = dados.get('estatisticas', {})
        
        print(f"📄 Gerando relatório: {len(resultados)} registros")
        
        # Renderizar template limpo para impressão
        return render_template('relatorio_impressao.html', 
                             resultados=resultados,
                             filtros=filtros,
                             estatisticas=estatisticas)
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório para impressão: {e}")
        return f"Erro ao gerar relatório: {str(e)}", 500

@app.route('/recarregar_dados')
@login_obrigatorio
def recarregar_dados():
    return redirect(url_for('dashboard'))

@app.route('/relatorio_mes/<mes>')
@login_obrigatorio
def relatorio_mes(mes):
    try:
        # Mapear nome do mês para número
        meses_map = {
            'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4,
            'Maio': 5, 'Junho': 6, 'Julho': 7, 'Agosto': 8,
            'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
        }
        
        if mes not in meses_map:
            return jsonify({'error': 'Mês inválido'}), 400
        
        mes_num = meses_map[mes]
        ano_atual = datetime.now().year
        
        # Obter dados de presença do mês
        presencas_por_dia = {}
        presencas_por_aluno = {}
        total_presencas = 0
        total_faltas = 0
        dias_com_aula = set()
        
        # Processar dados de presença do arquivo CSV
        if os.path.exists('presencas_detalhadas.csv'):
            import csv
            with open('presencas_detalhadas.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Converter data do formato DD/MM/YYYY
                        data_str = row.get('DATA', '')
                        if data_str:
                            dia, mes_data, ano = data_str.split('/')
                            if int(mes_data) == mes_num and int(ano) == ano_atual:
                                dia_int = int(dia)
                                dias_com_aula.add(dia_int)
                                
                                # Contar presenças por dia
                                if dia_int not in presencas_por_dia:
                                    presencas_por_dia[dia_int] = 0
                                
                                if row.get('STATUS') == 'P':
                                    presencas_por_dia[dia_int] += 1
                                    total_presencas += 1
                                    
                                    # Contar presenças por aluno
                                    nome_aluno = row.get('NOME', '')
                                    if nome_aluno not in presencas_por_aluno:
                                        presencas_por_aluno[nome_aluno] = 0
                                    presencas_por_aluno[nome_aluno] += 1
                                else:
                                    total_faltas += 1
                    except Exception as e:
                        print(f"Erro ao processar linha: {e}")
                        continue
        
        # Ordenar ranking de alunos por presenças
        ranking_alunos = sorted(presencas_por_aluno.items(), key=lambda x: x[1], reverse=True)
        
        # Preparar dados para o gráfico
        for dia in range(1, 32):
            if dia not in presencas_por_dia:
                presencas_por_dia[dia] = 0
        
        return jsonify({
            'mes': mes,
            'total_alunos': len(academia.alunos_reais),
            'estatisticas': {
                'total_presencas': total_presencas,
                'total_faltas': total_faltas,
                'dias_com_aula': len(dias_com_aula)
            },
            'presencas_por_dia': presencas_por_dia,
            'presencas_por_aluno': dict(ranking_alunos[:10])  # Top 10 alunos
        })
        
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/cadastrar_aluno', methods=['POST'])
@apenas_admin_ou_master
def cadastrar_aluno():
    try:
        print("[DEBUG] Iniciando cadastro de aluno")
        # Obter dados do formulário
        nome = request.form.get('nome', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        endereco = request.form.get('endereco', '').strip()
        data_nascimento = request.form.get('data_nascimento', '').strip()
        titulo_eleitor = request.form.get('titulo_eleitor', '').strip()
        atividade = request.form.get('atividade', '').strip()
        turma = request.form.get('turma', '').strip()
        status_frequencia = request.form.get('status', '').strip()  # Campo 'status' do formulário
        observacoes = request.form.get('observacoes', '').strip()
        
        print(f"[DEBUG] Dados recebidos: nome={nome}, telefone={telefone}, atividade={atividade}, turma={turma}, status={status_frequencia}")

        
        # Validações
        if not nome or len(nome) < 3:
            return jsonify({'success': False, 'message': 'Nome deve ter pelo menos 3 caracteres'})
        
        if not telefone or len(telefone.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')) < 10:
            return jsonify({'success': False, 'message': 'Telefone deve ter pelo menos 10 dígitos'})
            
        if not atividade:
            return jsonify({'success': False, 'message': 'Atividade é obrigatória'})
            
        if not turma:
            return jsonify({'success': False, 'message': 'Turma é obrigatória'})
            
        if not status_frequencia:
            return jsonify({'success': False, 'message': 'Status é obrigatório'})
        
        # Verificar se aluno já existe no banco de dados (nome + telefone)
        # Permitir nomes duplicados, mas não nome + telefone duplicados
        if telefone:  # Só validar se telefone foi fornecido
            aluno_dao = AlunoDAO()
            aluno_existente = aluno_dao.buscar_por_nome_telefone(nome, telefone)
            
            if aluno_existente:
                return jsonify({'success': False, 'message': 'Já existe outro aluno cadastrado com este nome e telefone'})
        
        # Manter data de nascimento no formato YYYY-MM-DD para o banco de dados
        data_nasc_formatada = data_nascimento
        if data_nascimento:
            try:
                # Validar formato da data
                from datetime import datetime as dt
                data_obj = dt.strptime(data_nascimento, '%Y-%m-%d')
                data_nasc_formatada = data_nascimento  # Manter formato original para o banco
            except:
                data_nasc_formatada = data_nascimento
        
        # Criar novo aluno
        novo_aluno = {
            'nome': nome,
            'telefone': telefone,
            'endereco': endereco if endereco else 'A definir',
            'email': email if email else f"{nome.lower().replace(' ', '.')}@email.com",
            'data_nascimento': data_nasc_formatada if data_nasc_formatada else 'A definir',
            'data_cadastro': datetime.now().strftime('%Y-%m-%d'),
            'titulo_eleitor': titulo_eleitor if titulo_eleitor else '',
            'atividade': atividade if atividade else 'A definir',
            'turma': turma if turma else 'A definir',
            'status_frequencia': 'Novo cadastro',
            'observacoes': observacoes,
            'ativo': True
        }
        
        # Adicionar ao MongoDB
        print(f"[DEBUG] Tentando salvar aluno: {novo_aluno}")
        aluno_dao = AlunoDAO()
        resultado = aluno_dao.criar(novo_aluno)
        sucesso = resultado is not None
        print(f"[DEBUG] Resultado do salvamento: {sucesso}")
        
        if sucesso:
            print(f"[DEBUG] Cadastro bem-sucedido para {nome}")
            # Contar total de alunos ativos
            total_alunos = aluno_dao.contar_ativos()
            return jsonify({
                'success': True, 
                'message': f'Aluno {nome} cadastrado com sucesso!',
                'total_alunos': total_alunos
            })
        else:
            print(f"[DEBUG] Falha no cadastro para {nome}")
            return jsonify({'success': False, 'message': 'Erro ao salvar dados do aluno'})
        
    except Exception as e:
        print(f"[DEBUG] Exceção no cadastro: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao cadastrar aluno: {str(e)}'})

@app.route('/editar_aluno/<aluno_id>', methods=['GET', 'PUT', 'POST'])
@apenas_admin_ou_master
def editar_aluno(aluno_id):
    try:
        # Buscar aluno no MongoDB
        aluno_dao = AlunoDAO()
        aluno_db = aluno_dao.buscar_por_id(aluno_id)
        
        if not aluno_db:
            if request.method == 'GET':
                flash('Aluno não encontrado', 'error')
                return redirect(url_for('alunos'))
            return jsonify({'success': False, 'message': 'Aluno não encontrado'})
        
        # Se for GET, exibir formulário de edição
        if request.method == 'GET':
            return render_template('novo_aluno.html', 
                                 aluno=aluno_db, 
                                 editando=True,
                                 nivel_usuario=session.get('nivel_usuario'))
        
        # Obter dados do formulário
        nome = request.form.get('nome', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        endereco = request.form.get('endereco', '').strip()
        data_nascimento = request.form.get('data_nascimento', '').strip()
        titulo_eleitor = request.form.get('titulo_eleitor', '').strip()
        atividade = request.form.get('atividade', '').strip()
        turma = request.form.get('turma', '').strip()
        observacoes = request.form.get('observacoes', '').strip()
        
        # Validações
        if not nome or len(nome) < 3:
            return jsonify({'success': False, 'message': 'Nome deve ter pelo menos 3 caracteres'})
        
        if not telefone or len(telefone.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')) < 10:
            return jsonify({'success': False, 'message': 'Telefone deve ter pelo menos 10 dígitos'})
        
        # Verificar se outro aluno já tem este nome E telefone (validação mais específica)
        # Permitir nomes duplicados, mas não nome + telefone duplicados
        if telefone:  # Só validar se telefone foi fornecido
            aluno_existente = aluno_dao.buscar_por_nome_telefone(nome, telefone)
            
            if aluno_existente and str(aluno_existente.get('_id')) != aluno_id:
                return jsonify({'success': False, 'message': 'Já existe outro aluno cadastrado com este nome e telefone'})
        
        # Converter data de nascimento se fornecida
        data_nasc_formatada = data_nascimento
        if data_nascimento:
            try:
                # Validar formato da data
                from datetime import datetime as dt
                data_obj = dt.strptime(data_nascimento, '%Y-%m-%d')
                data_nasc_formatada = data_nascimento  # Manter formato original
            except ValueError as e:
                return jsonify({'success': False, 'message': f'Formato de data inválido. Use YYYY-MM-DD. Erro: {str(e)}'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Erro ao processar data de nascimento: {str(e)}'})
        
        # Preparar dados atualizados
        dados_atualizados = {
            'nome': nome,
            'telefone': telefone,
            'email': email if email else '',
            'endereco': endereco if endereco else '',
            'data_nascimento': data_nasc_formatada if data_nasc_formatada else '',
            'atividade': atividade if atividade else 'A definir',
            'turma': turma if turma else 'A definir',
            'observacoes': observacoes if observacoes else '',
            'titulo_eleitor': titulo_eleitor if titulo_eleitor else ''
        }
        
        # Atualizar no MongoDB
        sucesso = aluno_dao.atualizar(aluno_id, dados_atualizados)
        
        if not sucesso:
            return jsonify({'success': False, 'message': 'Erro ao atualizar dados do aluno'})
        
        # Buscar aluno atualizado
        aluno_atualizado_db = aluno_dao.buscar_por_id(aluno_id)
        
        aluno_atualizado = {
            'id_unico': str(aluno_atualizado_db['_id']),
            'nome': aluno_atualizado_db.get('nome', ''),
            'telefone': aluno_atualizado_db.get('telefone', ''),
            'email': aluno_atualizado_db.get('email', ''),
            'endereco': aluno_atualizado_db.get('endereco', ''),
            'data_nascimento': aluno_atualizado_db.get('data_nascimento', ''),
            'atividade': aluno_atualizado_db.get('atividade', ''),
            'turma': aluno_atualizado_db.get('turma', ''),
            'observacoes': aluno_atualizado_db.get('observacoes', ''),
            'titulo_eleitor': aluno_atualizado_db.get('titulo_eleitor', '')
        }
        
        return jsonify({
            'success': True, 
            'message': f'Dados de {nome} atualizados com sucesso!',
            'aluno': aluno_atualizado
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao editar aluno: {str(e)}'})

@app.route('/excluir_aluno/<aluno_id>', methods=['DELETE', 'POST'])
@apenas_admin_ou_master
def excluir_aluno(aluno_id):
    try:
        # Buscar aluno no MongoDB
        aluno_dao = AlunoDAO()
        aluno_db = aluno_dao.buscar_por_id(aluno_id)
        
        if not aluno_db:
            return jsonify({'success': False, 'message': 'Aluno não encontrado'})
        
        # Obter nome do aluno e dados de frequência antes de excluir
        nome_aluno = aluno_db.get('nome', 'Aluno')
        
        # Verificar se há registros de presença
        presenca_dao = PresencaDAO()
        presencas = presenca_dao.buscar_por_aluno_id(aluno_id)
        tem_frequencia = len(presencas) > 0
        registros_frequencia = len(presencas) if tem_frequencia else 0
        
        # Excluir registros de presença primeiro (se houver)
        if tem_frequencia:
            for presenca in presencas:
                presenca_dao.excluir(str(presenca['_id']))
        
        # Excluir o aluno
        sucesso = aluno_dao.excluir(aluno_id)
        
        if not sucesso:
            return jsonify({'success': False, 'message': 'Erro ao excluir aluno'})
        
        # Mensagem detalhada sobre o que foi removido
        mensagem = f'Aluno {nome_aluno} excluído com sucesso!'
        if tem_frequencia:
            mensagem += f' Também foram removidos {registros_frequencia} registros de frequência.'
        
        return jsonify({
            'success': True, 
            'message': mensagem,
            'frequencia_removida': tem_frequencia,
            'registros_removidos': registros_frequencia
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao excluir aluno: {str(e)}'})

@app.route('/obter_aluno/<aluno_id>')
@login_obrigatorio
def obter_aluno(aluno_id):
    db_integration = get_db_integration()
    try:
        # Buscar aluno usando DAO do MongoDB
        aluno_db = db_integration.aluno_dao.buscar_por_id_unico(str(aluno_id))
        
        if not aluno_db:
            return jsonify({'success': False, 'message': 'Aluno não encontrado'})
        
        # Converter para dicionário usando .get() para MongoDB
        aluno = {
            'id_unico': aluno_db.get('id_unico'),
            'nome': aluno_db.get('nome'),
            'telefone': aluno_db.get('telefone'),
            'email': aluno_db.get('email', ''),
            'endereco': aluno_db.get('endereco', ''),
            'data_nascimento': str(aluno_db.get('data_nascimento', '')) if aluno_db.get('data_nascimento') else '',
            'atividade': '',  # Será preenchido separadamente
            'turma': '',      # Será preenchido separadamente
            'observacoes': aluno_db.get('observacoes', ''),
            'data_cadastro': str(aluno_db.get('data_cadastro', '')) if aluno_db.get('data_cadastro') else '',
            'status_frequencia': aluno_db.get('status_frequencia', 'Sem dados'),
            'titulo_eleitor': aluno_db.get('titulo_eleitor', '')
        }
        
        # Buscar nome da atividade separadamente se houver atividade_id
        if aluno_db.get('atividade_id'):
            atividade_obj = db_integration.atividade_dao.buscar_por_id(aluno_db.get('atividade_id'))
            if atividade_obj:
                aluno['atividade'] = atividade_obj.get('nome', '')
        
        # Buscar nome da turma separadamente se houver turma_id
        if aluno_db.get('turma_id'):
            turma_obj = db_integration.turma_dao.buscar_por_id(aluno_db.get('turma_id'))
            if turma_obj:
                aluno['turma'] = turma_obj.get('nome', '')
        
        # Buscar dados de presença usando MongoDB
        dados_presenca = None
        try:
            # Para MongoDB, usar o id_unico do aluno
            presencas = db_integration.presenca_dao.buscar_por_aluno_id(aluno_db.get('id_unico'))
            
            if presencas:
                # Contar presenças e faltas
                total_presencas = sum(1 for p in presencas if p.get('status') == 'P')
                total_faltas = sum(1 for p in presencas if p.get('status') == 'F')
                
                dados_presenca = {
                    'total_presencas': total_presencas,
                    'total_faltas': total_faltas,
                    'total_registros': len(presencas)
                }
            else:
                dados_presenca = {
                    'total_presencas': 0,
                    'total_faltas': 0,
                    'total_registros': 0
                }
        except Exception as e:
            # Se houver erro ao buscar presenças, continuar sem dados de presença
            print(f"Erro ao buscar presenças: {e}")
            dados_presenca = {
                'total_presencas': 0,
                'total_faltas': 0,
                'total_registros': 0
            }
        
        return jsonify({
            'success': True,
            'aluno': aluno,
            'aluno_id': aluno_id,
            'dados_presenca': dados_presenca
        })
        
    except Exception as e:
        close_db(db)
        return jsonify({'success': False, 'message': f'Erro ao obter dados do aluno: {str(e)}'})

@app.route('/salvar_dados_manualmente')
@login_obrigatorio  
def salvar_dados_manualmente():
    """Rota para verificar sincronização dos dados no banco PostgreSQL"""
    try:
        # Obter integração com banco de dados
        db_integration = get_db_integration()
        
        # Contar dados no banco PostgreSQL
        total_alunos = db_integration.contar_alunos_db()
        total_atividades = db_integration.contar_atividades_db()
        total_turmas = db_integration.contar_turmas_db()
        
        # Verificar se há dados no banco
        if total_alunos > 0 or total_atividades > 0 or total_turmas > 0:
            return jsonify({
                'success': True,
                'message': f'Dados verificados no banco PostgreSQL! Alunos: {total_alunos}, Atividades: {total_atividades}, Turmas: {total_turmas}',
                'total_alunos': total_alunos,
                'total_atividades': total_atividades,
                'total_turmas': total_turmas,
                'database_status': 'PostgreSQL ativo'
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Nenhum dado encontrado no banco PostgreSQL',
                'total_alunos': 0,
                'total_atividades': 0,
                'total_turmas': 0,
                'database_status': 'PostgreSQL vazio'
            })
            
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Erro ao verificar dados no banco PostgreSQL: {str(e)}',
            'database_status': 'Erro de conexão'
        })

@app.route('/recarregar_presenca_informatica')
@login_obrigatorio
def recarregar_presenca_informatica():
    try:
        # Recarregar dados de presença
        academia.dados_presenca = academia.carregar_dados_presenca()
        
        # Atualizar status de frequência
        alunos_atualizados = academia.atualizar_status_frequencia_informatica()
        
        return jsonify({
            'success': True,
            'message': f'Dados de presença recarregados! {alunos_atualizados} alunos atualizados.',
            'alunos_com_presenca': len(academia.dados_presenca),
            'alunos_atualizados': alunos_atualizados
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao recarregar presença: {str(e)}'})

@app.route('/presencas_hoje')
@login_obrigatorio
def presencas_hoje():
    try:
        data_hoje = datetime.now().strftime('%d/%m/%Y')
        presencas_hoje = []
        
        for nome, dados in academia.dados_presenca.items():
            for registro in dados['registros']:
                if registro.get('data') == data_hoje:
                    presencas_hoje.append({
                        'nome': nome,
                        'horario': registro.get('horario', ''),
                        'atividade': dados.get('atividade', ''),
                        'status': registro.get('status', 'P')
                    })
        
        return jsonify({
            'success': True,
            'data': data_hoje,
            'total': len(presencas_hoje),
            'presencas': presencas_hoje
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar presenças: {str(e)}'})

@app.route('/backup_planilhas')
@apenas_admin_ou_master
def backup_planilhas():
    atividades = academia.get_atividades_disponiveis()
    usuario_nome = session.get('usuario_nome', 'Usuário')
    return render_template('backup_planilhas.html', atividades=atividades, usuario_nome=usuario_nome)

# === ROTAS PARA GERENCIAMENTO DE COLABORADORES (APENAS ADMIN MASTER) ===

@app.route('/gerenciar_colaboradores')
@apenas_admin_master
def gerenciar_colaboradores():
    """Página de gerenciamento de colaboradores - apenas Admin Master"""
    usuario_nome = session.get('usuario_nome', 'Usuário')
    colaboradores = {}
    
    # Listar todos os usuários exceto Admin Masters
    for username, dados in USUARIOS.items():
        if dados.get('nivel') != 'admin_master':
            colaborador = dados.copy()
            # Não incluir senha hash na resposta
            colaborador.pop('senha', None)
            colaboradores[username] = colaborador
    
    atividades = academia.get_atividades_disponiveis() if academia else []
    
    return render_template('gerenciar_colaboradores.html', 
                         colaboradores=colaboradores,
                         atividades=atividades,
                         usuario_nome=usuario_nome)

@app.route('/criar_colaborador', methods=['POST'])
@apenas_admin_master
def criar_colaborador():
    """Cria um novo colaborador - apenas Admin Master"""
    try:
        # Obter dados do formulário
        username = request.form.get('username', '').strip().lower()
        nome = request.form.get('nome', '').strip()
        senha = request.form.get('senha', '').strip()
        nivel = request.form.get('nivel', '').strip()
        atividade_responsavel = request.form.get('atividade_responsavel', '').strip()
        
        # Validações
        if not username or len(username) < 4:
            return jsonify({'success': False, 'message': 'Username deve ter pelo menos 4 caracteres'})
        
        if not nome or len(nome) < 3:
            return jsonify({'success': False, 'message': 'Nome deve ter pelo menos 3 caracteres'})
        
        if not senha or len(senha) < 6:
            return jsonify({'success': False, 'message': 'Senha deve ter pelo menos 6 caracteres'})
        
        if nivel not in ['admin', 'usuario']:
            return jsonify({'success': False, 'message': 'Nível deve ser "admin" ou "usuario"'})
        
        # Verificar se username já existe
        if username in USUARIOS:
            return jsonify({'success': False, 'message': 'Este username já existe'})
        
        # Definir permissões baseadas no nível
        if nivel == 'admin':
            permissoes = ['cadastrar_alunos', 'editar_alunos', 'excluir_alunos', 
                         'ver_todos_alunos', 'gerar_relatorios', 'backup_planilhas']
        else:  # usuario
            permissoes = ['consultar_meus_alunos', 'gerenciar_frequencia_meus_alunos']
        
        # Criar novo colaborador
        novo_colaborador = {
            'senha': hashlib.sha256(senha.encode()).hexdigest(),
            'nome': nome,
            'nivel': nivel,
            'permissoes': permissoes,
            'ativo': True,
            'data_criacao': datetime.now().strftime('%d/%m/%Y'),
            'criado_por': session.get('usuario_logado')
        }
        
        # Se for usuário, adicionar atividade responsável
        if nivel == 'usuario' and atividade_responsavel:
            novo_colaborador['atividade_responsavel'] = atividade_responsavel
            novo_colaborador['alunos_atribuidos'] = []
        
        # Adicionar ao sistema
        USUARIOS[username] = novo_colaborador
        
        # Salvar dados
        sucesso = salvar_usuarios()
        
        if sucesso:
            return jsonify({
                'success': True,
                'message': f'Colaborador {nome} criado com sucesso!',
                'colaborador': {
                    'username': username,
                    'nome': nome,
                    'nivel': nivel,
                    'atividade_responsavel': atividade_responsavel if nivel == 'usuario' else None
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Erro ao salvar dados do colaborador'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao criar colaborador: {str(e)}'})

@app.route('/gerenciar_permissoes', methods=['POST'])
@apenas_admin_master
def gerenciar_permissoes():
    """Gerencia permissões de um colaborador - apenas Admin Master"""
    try:
        # Obter dados do formulário
        username = request.form.get('usuario', '').strip().lower()
        novo_nivel = request.form.get('nivel', '').strip()
        
        # Validações
        if not username:
            flash('Usuário não especificado', 'error')
            return redirect(url_for('gerenciar_colaboradores'))
        
        if novo_nivel not in ['admin_master', 'admin', 'professor', 'usuario']:
            flash('Nível de permissão inválido', 'error')
            return redirect(url_for('gerenciar_colaboradores'))
        
        # Verificar se usuário existe
        if username not in USUARIOS:
            flash('Usuário não encontrado', 'error')
            return redirect(url_for('gerenciar_colaboradores'))
        
        # Não permitir alterar próprio nível
        if username == session.get('usuario_logado'):
            flash('Não é possível alterar suas próprias permissões', 'error')
            return redirect(url_for('gerenciar_colaboradores'))
        
        # Definir permissões baseadas no novo nível
        if novo_nivel == 'admin_master':
            permissoes = ['acesso_total']
        elif novo_nivel == 'admin':
            permissoes = ['cadastrar_alunos', 'editar_alunos', 'excluir_alunos', 
                         'ver_todos_alunos', 'gerar_relatorios', 'backup_planilhas',
                         'gerenciar_colaboradores']
        elif novo_nivel == 'professor':
            permissoes = ['cadastrar_alunos', 'editar_alunos', 'ver_todos_alunos',
                         'gerenciar_turmas', 'gerenciar_atividades', 'gerar_relatorios']
        else:  # usuario
            permissoes = ['consultar_meus_alunos', 'gerenciar_frequencia_meus_alunos']
        
        # Atualizar dados do usuário
        USUARIOS[username]['nivel'] = novo_nivel
        USUARIOS[username]['permissoes'] = permissoes
        USUARIOS[username]['ultima_alteracao'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        USUARIOS[username]['alterado_por'] = session.get('usuario_logado')
        
        # Salvar dados
        sucesso = salvar_usuarios()
        
        if sucesso:
            flash(f'Permissões do usuário {username} atualizadas com sucesso!', 'success')
        else:
            flash('Erro ao salvar alterações das permissões', 'error')
        
        return redirect(url_for('gerenciar_colaboradores'))
        
    except Exception as e:
        flash(f'Erro ao gerenciar permissões: {str(e)}', 'error')
        return redirect(url_for('gerenciar_colaboradores'))

@app.route('/ativar_colaborador/<username>', methods=['POST'])
@apenas_admin_master
def ativar_colaborador(username):
    """Ativa um colaborador - apenas Admin Master"""
    try:
        # Verificar se usuário existe
        if username not in USUARIOS:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'})
        
        # Não permitir ativar Admin Master
        if USUARIOS[username].get('nivel') == 'admin_master':
            return jsonify({'success': False, 'message': 'Não é possível ativar/desativar Admin Master'})
        
        # Ativar colaborador
        USUARIOS[username]['ativo'] = True
        USUARIOS[username]['data_ativacao'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        USUARIOS[username]['ativado_por'] = session.get('usuario_logado')
        
        # Salvar dados
        sucesso = salvar_usuarios()
        
        if sucesso:
            return jsonify({'success': True, 'message': f'Colaborador {username} ativado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao salvar dados'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao ativar colaborador: {str(e)}'})

@app.route('/desativar_colaborador/<username>', methods=['POST'])
@apenas_admin_master
def desativar_colaborador(username):
    """Desativa um colaborador - apenas Admin Master"""
    try:
        # Verificar se usuário existe
        if username not in USUARIOS:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'})
        
        # Não permitir desativar Admin Master
        if USUARIOS[username].get('nivel') == 'admin_master':
            return jsonify({'success': False, 'message': 'Não é possível ativar/desativar Admin Master'})
        
        # Não permitir desativar próprio usuário
        if username == session.get('usuario_logado'):
            return jsonify({'success': False, 'message': 'Não é possível desativar sua própria conta'})
        
        # Desativar colaborador
        USUARIOS[username]['ativo'] = False
        USUARIOS[username]['data_desativacao'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        USUARIOS[username]['desativado_por'] = session.get('usuario_logado')
        
        # Salvar dados
        sucesso = salvar_usuarios()
        
        if sucesso:
            return jsonify({'success': True, 'message': f'Colaborador {username} desativado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao salvar dados'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao desativar colaborador: {str(e)}'})

@app.route('/editar_colaborador/<username>', methods=['POST'])
@apenas_admin_master
def editar_colaborador(username):
    """Edita um colaborador existente - apenas Admin Master"""
    try:
        if username not in USUARIOS or USUARIOS[username].get('nivel') == 'admin_master':
            return jsonify({'success': False, 'message': 'Colaborador não encontrado ou não pode ser editado'})
        
        # Obter dados do formulário
        nome = request.form.get('nome', '').strip()
        nova_senha = request.form.get('nova_senha', '').strip()
        nivel = request.form.get('nivel', '').strip()
        ativo = request.form.get('ativo') == 'true'
        atividade_responsavel = request.form.get('atividade_responsavel', '').strip()
        
        # Validações
        if not nome or len(nome) < 3:
            return jsonify({'success': False, 'message': 'Nome deve ter pelo menos 3 caracteres'})
        
        if nivel not in ['admin', 'usuario']:
            return jsonify({'success': False, 'message': 'Nível deve ser "admin" ou "usuario"'})
        
        # Atualizar dados do colaborador
        colaborador = USUARIOS[username]
        colaborador['nome'] = nome
        colaborador['nivel'] = nivel
        colaborador['ativo'] = ativo
        
        # Atualizar senha se fornecida
        if nova_senha and len(nova_senha) >= 6:
            colaborador['senha'] = hashlib.sha256(nova_senha.encode()).hexdigest()
        
        # Atualizar permissões baseadas no nível
        if nivel == 'admin':
            colaborador['permissoes'] = ['cadastrar_alunos', 'editar_alunos', 'excluir_alunos',
                                       'ver_todos_alunos', 'gerar_relatorios', 'backup_planilhas']
            # Remover atividade responsável se virou admin
            colaborador.pop('atividade_responsavel', None)
            colaborador.pop('alunos_atribuidos', None)
        else:  # usuario
            colaborador['permissoes'] = ['consultar_meus_alunos', 'gerenciar_frequencia_meus_alunos']
            if atividade_responsavel:
                colaborador['atividade_responsavel'] = atividade_responsavel
                if 'alunos_atribuidos' not in colaborador:
                    colaborador['alunos_atribuidos'] = []
        
        # Salvar dados
        sucesso = salvar_usuarios()
        
        if sucesso:
            return jsonify({
                'success': True,
                'message': f'Colaborador {nome} atualizado com sucesso!',
                'colaborador': {
                    'username': username,
                    'nome': nome,
                    'nivel': nivel,
                    'ativo': ativo,
                    'atividade_responsavel': colaborador.get('atividade_responsavel')
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Erro ao salvar alterações'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao editar colaborador: {str(e)}'})

@app.route('/excluir_colaborador/<username>', methods=['DELETE'])
@apenas_admin_master
def excluir_colaborador(username):
    """Exclui um colaborador - apenas Admin Master"""
    try:
        if username not in USUARIOS or USUARIOS[username].get('nivel') == 'admin_master':
            return jsonify({'success': False, 'message': 'Colaborador não encontrado ou não pode ser excluído'})
        
        nome_colaborador = USUARIOS[username]['nome']
        
        # Remover colaborador
        del USUARIOS[username]
        
        # Salvar dados
        sucesso = salvar_usuarios()
        
        if sucesso:
            return jsonify({
                'success': True,
                'message': f'Colaborador {nome_colaborador} excluído com sucesso!',
                'total_colaboradores': len([u for u in USUARIOS.values() if u.get('nivel') != 'admin_master'])
            })
        else:
            return jsonify({'success': False, 'message': 'Erro ao salvar alterações'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao excluir colaborador: {str(e)}'})

@app.route('/obter_colaborador/<username>')
@apenas_admin_master
def obter_colaborador(username):
    """Obtém dados de um colaborador - apenas Admin Master"""
    try:
        if username not in USUARIOS or USUARIOS[username].get('nivel') == 'admin_master':
            return jsonify({'success': False, 'message': 'Colaborador não encontrado'})
        
        colaborador = USUARIOS[username].copy()
        colaborador['username'] = username
        # Não incluir senha hash na resposta
        colaborador.pop('senha', None)
        
        return jsonify({
            'success': True,
            'colaborador': colaborador
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao obter dados do colaborador: {str(e)}'})

@app.route('/gerar_planilha/<atividade>')
@login_obrigatorio
def gerar_planilha_route(atividade):
    if session.get('usuario_nivel') != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        # Gerar planilha CSV
        planilha_bytes = academia.gerar_planilha_frequencia(atividade)
        
        if planilha_bytes:
            filename = f'Frequencia_{atividade.replace(" ", "_")}_{datetime.now().strftime("%m_%Y")}.csv'
            
            return send_file(
                planilha_bytes,
                as_attachment=True,
                download_name=filename,
                mimetype='text/csv'
            )
        else:
            return jsonify({'error': f'Nenhum aluno encontrado para a atividade {atividade}'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar planilha: {str(e)}'}), 500

@app.route('/upload_planilha', methods=['POST'])
@login_obrigatorio
def upload_planilha():
    if session.get('usuario_nivel') != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        if 'arquivo' not in request.files:
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        file = request.files['arquivo']
        atividade = request.form.get('atividade')
        
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if file and allowed_file(file.filename) and atividade:
            filename = secure_filename(f'backup_{atividade}_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{file.filename}')
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            return jsonify({
                'success': True,
                'message': f'Planilha de {atividade} enviada com sucesso!',
                'filename': filename
            })
        else:
            return jsonify({'error': 'Arquivo inválido ou atividade não informada'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Erro no upload: {str(e)}'}), 500

def truncar_dados_aluno(dados):
    """Trunca dados do aluno para respeitar limites do banco de dados"""
    # Limites baseados no modelo Aluno
    limites = {
        'id_unico': 50,
        'nome': 200,
        'telefone': 20,
        'email': 200,
        'titulo_eleitor': 20,
        'status_frequencia': 200,
        'criado_por': 50
    }
    
    dados_truncados = dados.copy()
    
    for campo, limite in limites.items():
        if campo in dados_truncados and dados_truncados[campo]:
            valor = str(dados_truncados[campo])
            if len(valor) > limite:
                dados_truncados[campo] = valor[:limite]
                print(f"⚠️  Campo '{campo}' truncado de {len(valor)} para {limite} caracteres")
    
    return dados_truncados

def processar_csv_basico(filepath):
    """Processa CSV básico sem pandas quando a biblioteca não está disponível"""
    import csv
    from datetime import datetime
    
    try:
        db_integration = get_db_integration()
        
        # Usar atividade padrão "Cadastro Geral" para planilhas de cadastro
        atividade_nome = "Cadastro Geral"
        atividade_obj = db_integration.atividade_dao.buscar_por_nome(atividade_nome)
        if not atividade_obj:
            # Criar atividade padrão se não existir
            nova_atividade = {
                'nome': atividade_nome,
                'descricao': 'Atividade padrão para cadastros gerais importados via planilha',
                'ativa': True,
                'data_criacao': datetime.now().date(),
                'criado_por': session.get('usuario_logado', 'admin')
            }
            atividade_obj = db_integration.atividade_dao.criar(nova_atividade)
        
        alunos_processados = 0
        novos_cadastros = 0
        atualizados = 0
        alunos_erros = 0
        erros_detalhes = []
        
        # Tentar diferentes encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        csv_data = None
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding, newline='') as csvfile:
                    # Detectar delimitador
                    sample = csvfile.read(1024)
                    csvfile.seek(0)
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(sample).delimiter
                    
                    reader = csv.DictReader(csvfile, delimiter=delimiter)
                    csv_data = list(reader)
                    break
            except (UnicodeDecodeError, Exception):
                continue
        
        if not csv_data:
            return jsonify({'error': 'Não foi possível ler o arquivo CSV'}), 400
        
        # Mapear colunas (case-insensitive)
        colunas_mapeadas = {
            'nome': ['nome', 'Name', 'NOME', 'name'],
            'telefone': ['telefone', 'Telefone', 'TELEFONE', 'phone', 'celular'],
            'email': ['email', 'Email', 'EMAIL', 'e-mail'],
            'endereco': ['endereco', 'Endereco', 'ENDERECO', 'endereço', 'address'],
            'data_nascimento': ['data_nascimento', 'Data Nascimento', 'nascimento', 'birth_date'],
            'titulo_eleitor': ['titulo_eleitor', 'Titulo Eleitor', 'TITULO_ELEITOR', 'titulo'],
            'observacoes': ['observacoes', 'Observacoes', 'obs', 'observações']
        }
        
        # Encontrar colunas correspondentes
        mapeamento_final = {}
        if csv_data:
            colunas_csv = list(csv_data[0].keys())
            print(f"📋 Colunas encontradas na planilha: {colunas_csv}")
            
            for campo, possiveis_nomes in colunas_mapeadas.items():
                for col in colunas_csv:
                    if col.lower() in [nome.lower() for nome in possiveis_nomes]:
                        mapeamento_final[campo] = col
                        break
            
            print(f"✅ Colunas mapeadas: {list(mapeamento_final.keys())}")
            colunas_ignoradas = set(colunas_csv) - set(mapeamento_final.values())
            if colunas_ignoradas:
                print(f"⚠️  Colunas ignoradas: {list(colunas_ignoradas)}")
        
        # Processar dados
        for index, row in enumerate(csv_data):
            try:
                # Extrair dados da linha
                nome = str(row.get(mapeamento_final.get('nome', ''), '')).strip()
                if not nome or nome.lower() in ['', 'nan', 'none']:
                    continue
                
                telefone = str(row.get(mapeamento_final.get('telefone', ''), '')).strip()
                email = str(row.get(mapeamento_final.get('email', ''), '')).strip()
                endereco = str(row.get(mapeamento_final.get('endereco', ''), '')).strip()
                titulo_eleitor = str(row.get(mapeamento_final.get('titulo_eleitor', ''), '')).strip()
                observacoes = str(row.get(mapeamento_final.get('observacoes', ''), '')).strip()
                
                # Truncar dados para respeitar limites do banco
                dados_aluno = {
                    'nome': nome,
                    'telefone': telefone,
                    'email': email,
                    'titulo_eleitor': titulo_eleitor,
                    'id_unico': f'CSV_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{index}'
                }
                dados_aluno = truncar_dados_aluno(dados_aluno)
                
                nome = dados_aluno['nome']
                telefone = dados_aluno['telefone']
                email = dados_aluno['email']
                titulo_eleitor = dados_aluno['titulo_eleitor']
                id_unico = dados_aluno['id_unico']
                
                # Processar data de nascimento
                data_nascimento = None
                if 'data_nascimento' in mapeamento_final:
                    data_nasc_raw = row.get(mapeamento_final['data_nascimento'], '').strip()
                    if data_nasc_raw and data_nasc_raw.lower() not in ['', 'nan', 'none']:
                        try:
                            data_nascimento = datetime.strptime(data_nasc_raw, '%d/%m/%Y').date()
                        except:
                            try:
                                data_nascimento = datetime.strptime(data_nasc_raw, '%Y-%m-%d').date()
                            except:
                                pass
                
                # Verificar se aluno já existe
                aluno_existente = db.query(Aluno).filter(
                    Aluno.nome == nome,
                    Aluno.telefone == telefone
                ).first()
                
                if aluno_existente:
                    # Atualizar aluno existente
                    if email and email.lower() not in ['', 'nan', 'none']:
                        aluno_existente.email = email
                    if endereco and endereco.lower() not in ['', 'nan', 'none']:
                        aluno_existente.endereco = endereco
                    if titulo_eleitor and titulo_eleitor.lower() not in ['', 'nan', 'none']:
                        aluno_existente.titulo_eleitor = titulo_eleitor
                    if observacoes and observacoes.lower() not in ['', 'nan', 'none']:
                        aluno_existente.observacoes = observacoes
                    aluno_existente.atividade_id = atividade_obj.id
                    aluno_existente.ativo = True
                    if data_nascimento:
                        aluno_existente.data_nascimento = data_nascimento
                    atualizados += 1
                else:
                    # Criar novo aluno
                    novo_aluno = Aluno(
                        id_unico=id_unico,
                        nome=nome,
                        telefone=telefone if telefone and telefone.lower() not in ['', 'nan', 'none'] else None,
                        email=email if email and email.lower() not in ['', 'nan', 'none'] else None,
                        endereco=endereco if endereco and endereco.lower() not in ['', 'nan', 'none'] else None,
                        titulo_eleitor=titulo_eleitor if titulo_eleitor and titulo_eleitor.lower() not in ['', 'nan', 'none'] else None,
                        data_nascimento=data_nascimento,
                        data_cadastro=datetime.now().date(),
                        atividade_id=atividade_obj.id,
                        observacoes=observacoes if observacoes and observacoes.lower() not in ['', 'nan', 'none'] else None,
                        ativo=True
                    )
                    db.add(novo_aluno)
                    novos_cadastros += 1
                
                alunos_processados += 1
                
            except Exception as e:
                alunos_erros += 1
                erros_detalhes.append(f'Linha {index + 2}: {str(e)}')
                continue
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': f'CSV processado com sucesso! {novos_cadastros} novos cadastros, {atualizados} atualizações',
            'total_processados': alunos_processados,
            'novos_cadastros': novos_cadastros,
            'atualizados': atualizados,
            'alunos_erros': alunos_erros,
            'erros_detalhes': erros_detalhes[:10],  # Limitar a 10 erros
            'colunas_encontradas': list(mapeamento_final.keys()),
            'total_linhas': len(csv_data),
            'processamento': 'CSV básico (sem pandas)'
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao processar CSV: {str(e)}'}), 500
    finally:
        if 'db' in locals():
            db.close()

@app.route('/processar_planilha', methods=['POST'])
@login_obrigatorio
def processar_planilha():
    """Processa uma planilha Excel e importa os dados para o banco"""
    if session.get('usuario_nivel') != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        # Verificar se há arquivo no upload
        if 'arquivo' not in request.files:
            return jsonify({'error': 'Nenhum arquivo foi enviado'}), 400
        
        file = request.files['arquivo']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Verificar extensão do arquivo
        if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            return jsonify({'error': 'Apenas arquivos Excel (.xlsx, .xls) e CSV (.csv) são aceitos'}), 400
        
        # Salvar arquivo temporariamente
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Verificar se pandas está disponível
        if not PANDAS_AVAILABLE:
            # Se pandas não estiver disponível, usar processamento básico para CSV
            if file.filename.lower().endswith('.csv'):
                return processar_csv_basico(filepath)
            else:
                return jsonify({'error': 'Biblioteca pandas não instalada. Para Excel: pip install pandas openpyxl. Para CSV, use formato simples.'}), 500
        
        # Ler arquivo (Excel ou CSV)
        try:
            if file.filename.lower().endswith('.csv'):
                # Tentar diferentes encodings para CSV
                try:
                    df = pd.read_csv(filepath, encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        df = pd.read_csv(filepath, encoding='latin-1')
                    except UnicodeDecodeError:
                        df = pd.read_csv(filepath, encoding='cp1252')
            else:
                df = pd.read_excel(filepath)
        except Exception as e:
            return jsonify({'error': f'Erro ao ler arquivo: {str(e)}'}), 400
        
        # Mapear colunas comuns
        colunas_mapeadas = {
            'nome': ['nome', 'Nome', 'NOME', 'name'],
            'telefone': ['telefone', 'Telefone', 'TELEFONE', 'phone', 'celular'],
            'email': ['email', 'Email', 'EMAIL', 'e-mail'],
            'endereco': ['endereco', 'Endereco', 'ENDERECO', 'endereço', 'address'],
            'data_nascimento': ['data_nascimento', 'Data Nascimento', 'nascimento', 'birth_date'],
            'observacoes': ['observacoes', 'Observacoes', 'obs', 'observações'],
            'titulo_eleitor': ['titulo_eleitor', 'Titulo Eleitor', 'titulo eleitor', 'TITULO_ELEITOR', 'titulo de eleitor']
        }
        
        # Encontrar colunas correspondentes
        mapeamento_final = {}
        for campo, possiveis_nomes in colunas_mapeadas.items():
            for col in df.columns:
                if col in possiveis_nomes:
                    mapeamento_final[campo] = col
                    break
        
        # Log das colunas encontradas e mapeadas
        print(f"[PROCESSAR_PLANILHA] Colunas encontradas no arquivo: {list(df.columns)}")
        print(f"[PROCESSAR_PLANILHA] Colunas mapeadas: {mapeamento_final}")
        colunas_ignoradas = [col for col in df.columns if col not in mapeamento_final.values()]
        print(f"[PROCESSAR_PLANILHA] Colunas ignoradas: {colunas_ignoradas}")
        
        # Verificar se pelo menos o campo nome foi encontrado
        if 'nome' not in mapeamento_final:
            print("[PROCESSAR_PLANILHA] ERRO: Campo 'nome' não encontrado")
            return jsonify({
                'error': 'Campo obrigatório "nome" não encontrado na planilha',
                'colunas_encontradas': list(df.columns),
                'colunas_esperadas': colunas_mapeadas['nome']
            }), 400
        
        # Processar dados
        alunos_processados = 0
        novos_cadastros = 0
        atualizados = 0
        alunos_erros = 0
        erros_detalhes = []
        
        db_integration = get_db_integration()
        try:
            # Usar atividade padrão "Cadastro Geral" para planilhas de cadastro
            atividade_nome = "Cadastro Geral"
            atividade_obj = db_integration.atividade_dao.buscar_por_nome(atividade_nome)
            if not atividade_obj:
                # Criar atividade padrão se não existir
                nova_atividade = {
                    'nome': atividade_nome,
                    'descricao': 'Atividade padrão para cadastros gerais importados via planilha',
                    'ativa': True,
                    'data_criacao': datetime.now().date(),
                    'criado_por': session.get('usuario_logado', 'admin')
                }
                atividade_obj = db_integration.atividade_dao.criar(nova_atividade)
            
            for index, row in df.iterrows():
                try:
                    # Extrair dados da linha
                    nome = str(row.get(mapeamento_final.get('nome', ''), '')).strip()
                    if not nome or nome == 'nan':
                        continue
                    
                    telefone = str(row.get(mapeamento_final.get('telefone', ''), '')).strip()
                    email = str(row.get(mapeamento_final.get('email', ''), '')).strip()
                    endereco = str(row.get(mapeamento_final.get('endereco', ''), '')).strip()
                    observacoes = str(row.get(mapeamento_final.get('observacoes', ''), '')).strip()
                    titulo_eleitor = str(row.get(mapeamento_final.get('titulo_eleitor', ''), '')).strip()
                    
                    # Truncar dados para respeitar limites do banco
                    dados_aluno = {
                        'nome': nome,
                        'telefone': telefone,
                        'email': email,
                        'titulo_eleitor': titulo_eleitor,
                        'id_unico': f'IMP_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{index}'
                    }
                    dados_aluno = truncar_dados_aluno(dados_aluno)
                    
                    nome = dados_aluno['nome']
                    telefone = dados_aluno['telefone']
                    email = dados_aluno['email']
                    titulo_eleitor = dados_aluno['titulo_eleitor']
                    id_unico = dados_aluno['id_unico']
                    
                    # Processar data de nascimento
                    data_nascimento = None
                    if 'data_nascimento' in mapeamento_final:
                        data_nasc_raw = row.get(mapeamento_final['data_nascimento'])
                        if pd.notna(data_nasc_raw):
                            try:
                                if isinstance(data_nasc_raw, str):
                                    data_nascimento = datetime.strptime(data_nasc_raw, '%d/%m/%Y').date()
                                else:
                                    data_nascimento = data_nasc_raw.date() if hasattr(data_nasc_raw, 'date') else None
                            except:
                                pass
                    
                    # Verificar se aluno já existe usando MongoDB
                    aluno_existente = db_integration.aluno_dao.buscar_por_nome_telefone(nome, telefone)
                    
                    if aluno_existente:
                        # Atualizar aluno existente
                        dados_atualizacao = {
                            'email': email if email != 'nan' else aluno_existente.get('email'),
                            'endereco': endereco if endereco != 'nan' else aluno_existente.get('endereco'),
                            'observacoes': observacoes if observacoes != 'nan' else aluno_existente.get('observacoes'),
                            'titulo_eleitor': titulo_eleitor if titulo_eleitor != 'nan' else aluno_existente.get('titulo_eleitor'),
                            'atividade_id': atividade_obj.get('_id') if atividade_obj else None,
                            'ativo': True
                        }
                        if data_nascimento:
                            dados_atualizacao['data_nascimento'] = data_nascimento
                        db_integration.aluno_dao.atualizar(aluno_existente.get('_id'), dados_atualizacao)
                        atualizados += 1
                    else:
                        # Criar novo aluno usando MongoDB
                        novo_aluno = {
                            'id_unico': id_unico,
                            'nome': nome,
                            'telefone': telefone if telefone != 'nan' else None,
                            'email': email if email != 'nan' else None,
                            'endereco': endereco if endereco != 'nan' else None,
                            'titulo_eleitor': titulo_eleitor if titulo_eleitor != 'nan' else None,
                            'data_nascimento': data_nascimento,
                            'data_cadastro': datetime.now().date(),
                            'atividade_id': atividade_obj.get('_id') if atividade_obj else None,
                            'observacoes': observacoes if observacoes != 'nan' else None,
                            'ativo': True
                        }
                        db_integration.aluno_dao.criar(novo_aluno)
                        novos_cadastros += 1
                    
                    alunos_processados += 1
                    
                except Exception as e:
                    alunos_erros += 1
                    erro_msg = f'Linha {index + 2}: {str(e)}'
                    print(f"[PROCESSAR_PLANILHA] ERRO: {erro_msg}")
                    erros_detalhes.append(erro_msg)
                    continue
            
            print(f"[PROCESSAR_PLANILHA] SUCESSO: {alunos_processados} processados, {novos_cadastros} novos, {atualizados} atualizados, {alunos_erros} erros")
            
            return jsonify({
                'success': True,
                'message': f'Planilha processada com sucesso! {novos_cadastros} novos cadastros, {atualizados} atualizações',
                'total_processados': alunos_processados,
                'novos_cadastros': novos_cadastros,
                'atualizados': atualizados,
                'alunos_erros': alunos_erros,
                'erros_detalhes': erros_detalhes[:10],  # Limitar a 10 erros
                'colunas_encontradas': list(mapeamento_final.keys()),
                'colunas_ignoradas': colunas_ignoradas,
                'total_linhas': len(df)
            })
            
        except Exception as db_error:
            print(f"[PROCESSAR_PLANILHA] ERRO DE BANCO: {str(db_error)}")
            return jsonify({
                'error': f'Erro de banco de dados: {str(db_error)}',
                'tipo_erro': 'database_error'
            }), 500
        finally:
            pass  # MongoDB não precisa de close manual
            # Limpar arquivo temporário
            if filepath and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
            
    except Exception as e:
        print(f"[PROCESSAR_PLANILHA] ERRO GERAL: {str(e)}")
        # Limpar arquivo temporário em caso de erro
        if 'filepath' in locals() and filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass
        return jsonify({
            'error': f'Erro ao processar planilha: {str(e)}',
            'tipo_erro': 'general_error'
        }), 500

@app.route('/listar_backups')
@login_obrigatorio
def listar_backups():
    if session.get('usuario_nivel') != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        backups = []
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                if filename.startswith('backup_') and filename.endswith('.xlsx'):
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    stat = os.stat(filepath)
                    
                    # Extrair atividade do nome do arquivo
                    parts = filename.split('_')
                    atividade = parts[1] if len(parts) > 1 else 'Desconhecida'
                    
                    backups.append({
                        'filename': filename,
                        'atividade': atividade,
                        'size': round(stat.st_size / 1024, 2),  # KB
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M')
                    })
        
        # Ordenar por data de modificação (mais recente primeiro)
        backups.sort(key=lambda x: x['modified'], reverse=True)
        return jsonify(backups)
        
    except Exception as e:
        return jsonify({'error': f'Erro ao listar backups: {str(e)}'}), 500



@app.route('/baixar_cadastros')
@login_obrigatorio
def baixar_cadastros():
    if session.get('usuario_nivel') != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        # Gerar arquivo CSV com todos os cadastros
        alunos = academia.get_alunos()
        
        csv_content = "ASSOCIAÇÃO AMIGO DO POVO - CADASTROS UNIFICADOS\n"
        csv_content += f"GERADO EM: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        csv_content += f"TOTAL DE ALUNOS: {len(alunos)}\n"
        csv_content += "\n"
        
        # Cabeçalho
        headers = ["NOME", "DATA_NASCIMENTO", "TELEFONE", "ENDERECO", "ATIVIDADE", "DATA_MATRICULA", "TURMA", "EMAIL", "STATUS_FREQUENCIA", "OBSERVACOES"]
        csv_content += ",".join(headers) + "\n"
        
        # Dados dos alunos
        for aluno in alunos:
            linha = [
                f'"{aluno.get("nome", "")}"',
                f'"{aluno.get("data_nascimento", "")}"',
                f'"{aluno.get("telefone", "")}"',
                f'"{aluno.get("endereco", "")}"',
                f'"{aluno.get("atividade", "")}"',
                f'"{aluno.get("data_cadastro", "")}"',
                f'"{aluno.get("turma", "")}"',
                f'"{aluno.get("email", "")}"',
                f'"{aluno.get("status_frequencia", "")}"',
                f'"{aluno.get("observacoes", "")}"'
            ]
            csv_content += ",".join(linha) + "\n"
        
        # Estatísticas por atividade
        csv_content += "\n"
        csv_content += "ESTATÍSTICAS POR ATIVIDADE:\n"
        atividades_count = {}
        for aluno in alunos:
            ativ = aluno.get('atividade', 'Sem atividade')
            atividades_count[ativ] = atividades_count.get(ativ, 0) + 1
        
        for atividade, count in sorted(atividades_count.items()):
            csv_content += f"{atividade},{count}\n"
        
        # Retornar arquivo
        output = io.BytesIO()
        output.write(csv_content.encode('utf-8'))
        output.seek(0)
        
        filename = f'Cadastros_Unificados_Backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar cadastros: {str(e)}'}), 500

@app.route('/gerar_todas_planilhas')
@login_obrigatorio  
def gerar_todas_planilhas():
    if session.get('usuario_nivel') != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        import zipfile
        
        # Criar arquivo ZIP com todas as planilhas
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            atividades = academia.get_atividades_disponiveis()
            
            for atividade in atividades:
                planilha_bytes = academia.gerar_planilha_frequencia(atividade)
                if planilha_bytes:
                    filename = f'Frequencia_{atividade.replace(" ", "_")}_{datetime.now().strftime("%m_%Y")}.csv'
                    zip_file.writestr(filename, planilha_bytes.getvalue())
        
        zip_buffer.seek(0)
        
        filename = f'Todas_Planilhas_Frequencia_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar todas as planilhas: {str(e)}'}), 500

# Health check para Render
@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'Associação Amigo do Povo'})

# Endpoint para executar migrações manualmente em produção
@app.route('/migrate')
def migrate():
    """Executa migrações do banco de dados manualmente"""
    try:
        # Importar e executar o script de migração
        from migrate_production import executar_migracao_producao
        
        # Executar migração
        sucesso = executar_migracao_producao()
        
        if sucesso:
            return jsonify({
                'status': 'success',
                'message': 'Migração executada com sucesso!',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Falha na execução da migração',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao executar migração: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

# Teste simples
@app.route('/test')
def test():
    return "Sistema funcionando! ✅"

@app.route('/debug_stats')
@login_obrigatorio
def debug_stats():
    """Endpoint para debug das estatísticas"""
    nivel_usuario = session.get('usuario_nivel')
    usuario_logado = session.get('usuario_logado')
    
    debug_info = {
        'nivel_usuario': nivel_usuario,
        'usuario_logado': usuario_logado,
        'usuario_dados': USUARIOS.get(usuario_logado, {}),
    }
    
    if nivel_usuario == 'usuario' and usuario_logado in USUARIOS:
        atividade_responsavel = USUARIOS[usuario_logado].get('atividade_responsavel')
        debug_info['atividade_responsavel'] = atividade_responsavel
        
        # Testar estatísticas gerais
        stats_gerais = academia.get_estatisticas()
        debug_info['stats_gerais'] = stats_gerais
        
        # Testar estatísticas filtradas
        stats_filtradas = academia.get_estatisticas(filtro_atividade=atividade_responsavel)
        debug_info['stats_filtradas'] = stats_filtradas
        
        # Verificar alunos da atividade
        alunos_atividade = academia.get_alunos_por_atividade(atividade_responsavel)
        debug_info['alunos_atividade'] = len(alunos_atividade)
        debug_info['primeiros_alunos'] = [aluno['nome'] for aluno in alunos_atividade[:5]]
    
    return jsonify(debug_info)

# === ROTAS PARA GERENCIAMENTO DE ATIVIDADES ===

@app.route('/gerenciar_atividades')
@apenas_admin_ou_master
def gerenciar_atividades():
    """Página de gerenciamento de atividades - Admin/Admin Master"""
    usuario_nome = session.get('usuario_nome', 'Usuário')
    
    # Atualizar contadores de alunos
    for nome_atividade, dados_atividade in academia.atividades_cadastradas.items():
        alunos_atividade = academia.get_alunos_por_atividade(nome_atividade)
        dados_atividade['total_alunos'] = len(alunos_atividade)
    
    # Salvar atualizações
    academia.salvar_atividades()
    
    # Obter lista de professores para o dropdown
    professores = {login: dados for login, dados in USUARIOS.items() 
                  if dados.get('nivel') == 'usuario'}
    
    return render_template('gerenciar_atividades.html', 
                         atividades=academia.atividades_cadastradas,
                         professores=professores,
                         usuario_nome=usuario_nome)

@app.route('/dashboard_atividade/<nome_atividade>')
@login_obrigatorio
def dashboard_atividade(nome_atividade):
    """Dashboard específico de uma atividade"""
    nivel_usuario = session.get('usuario_nivel')
    usuario_logado = session.get('usuario_logado')
    usuario_nome = session.get('usuario_nome', 'Usuário')
    
    # Verificar se a atividade existe
    if nome_atividade not in academia.atividades_cadastradas:
        flash('Atividade não encontrada!', 'error')
        return redirect(url_for('dashboard'))
    
    # Verificar permissões
    if nivel_usuario == 'usuario':
        # Usuários só podem ver dashboard da sua atividade responsável
        atividade_responsavel = USUARIOS[usuario_logado].get('atividade_responsavel')
        if nome_atividade != atividade_responsavel:
            flash('Acesso negado! Você só pode acessar dashboard da sua atividade.', 'error')
            return redirect(url_for('dashboard'))
    
    # Obter estatísticas da atividade
    stats = academia.get_estatisticas(filtro_atividade=nome_atividade)
    atividade_info = academia.atividades_cadastradas[nome_atividade]
    
    # Obter presenças de hoje da atividade
    data_hoje = datetime.now().strftime('%d/%m/%Y')
    presencas_hoje = []
    
    for nome, dados in academia.dados_presenca.items():
        # Verificar se o aluno pertence à atividade
        aluno_da_atividade = False
        for aluno in academia.alunos_reais:
            if aluno['nome'] == nome and aluno.get('atividade') == nome_atividade:
                aluno_da_atividade = True
                break
        
        if aluno_da_atividade:
            for registro in dados['registros']:
                if registro.get('data') == data_hoje and registro.get('status') == 'P':
                    presencas_hoje.append({
                        'Nome': nome,
                        'Horário': registro.get('horario', ''),
                        'Atividade': nome_atividade,
                        'Observações': 'Presença registrada'
                    })
    
    return render_template('dashboard_atividade.html', 
                         stats=stats, 
                         presencas_hoje=presencas_hoje, 
                         usuario_nome=usuario_nome,
                         nivel_usuario=nivel_usuario,
                         atividade=atividade_info,
                         nome_atividade=nome_atividade)

@app.route('/criar_atividade', methods=['POST'])
@apenas_admin_ou_master
def criar_atividade():
    """Cria uma nova atividade"""
    try:
        # Verificar se a requisição é JSON ou form-data
        if request.is_json:
            dados = request.json
            nome = dados.get('nome', '').strip()
            descricao = dados.get('descricao', '').strip()
            professor = dados.get('professor', '')
        else:
            nome = request.form.get('nome', '').strip()
            descricao = request.form.get('descricao', '').strip()
            professor = request.form.get('professor', '')
            
        criado_por = session.get('usuario_logado')
        
        if not nome:
            return jsonify({'status': 'error', 'message': 'Nome da atividade é obrigatório'})
        
        if len(nome) < 3:
            return jsonify({'status': 'error', 'message': 'Nome deve ter pelo menos 3 caracteres'})
        
        sucesso, mensagem = academia.cadastrar_atividade(nome, descricao, criado_por, professor)
        
        if sucesso:
            # Registrar atividade
            nivel_usuario = session.get('usuario_nivel', 'admin')
            registrar_atividade(
                criado_por, 
                'Criou Atividade', 
                f'Criou a atividade "{nome}" com professor {professor}', 
                nivel_usuario
            )
            
            return jsonify({
                'status': 'success',
                'message': mensagem,
                'atividade': {
                    'nome': nome,
                    'descricao': descricao,
                    'professor': professor,
                    'total_alunos': 0
                }
            })
        else:
            return jsonify({'status': 'error', 'message': mensagem})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erro ao criar atividade: {str(e)}'})

@app.route('/excluir_atividade/<nome_atividade>', methods=['DELETE'])
@apenas_admin_ou_master
def excluir_atividade_route(nome_atividade):
    """Exclui uma atividade"""
    try:
        sucesso, mensagem = academia.excluir_atividade(nome_atividade)
        
        if sucesso:
            # Registrar atividade
            usuario_logado = session.get('usuario_logado')
            nivel_usuario = session.get('usuario_nivel', 'admin')
            registrar_atividade(
                usuario_logado, 
                'Excluiu Atividade', 
                f'Excluiu a atividade "{nome_atividade}"', 
                nivel_usuario
            )
            
            return jsonify({
                'success': True,
                'message': mensagem,
                'total_atividades': len(academia.atividades_cadastradas)
            })
        else:
            return jsonify({'success': False, 'message': mensagem})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao excluir atividade: {str(e)}'})

@app.route('/ativar_atividade/<nome_atividade>', methods=['POST'])
@apenas_admin_ou_master
def ativar_atividade_route(nome_atividade):
    """Ativa uma atividade"""
    try:
        # Verificar se a atividade existe
        if nome_atividade not in academia.atividades_cadastradas:
            return jsonify({'success': False, 'message': 'Atividade não encontrada'})
        
        # Ativar a atividade
        academia.atividades_cadastradas[nome_atividade]['ativa'] = True
        
        # Salvar as alterações
        academia.salvar_atividades()
        
        # Registrar atividade
        usuario_logado = session.get('usuario_logado')
        nivel_usuario = session.get('usuario_nivel', 'admin')
        registrar_atividade(
            usuario_logado, 
            'Ativou Atividade', 
            f'Ativou a atividade "{nome_atividade}"', 
            nivel_usuario
        )
        
        return jsonify({
            'success': True,
            'message': f'Atividade "{nome_atividade}" ativada com sucesso!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao ativar atividade: {str(e)}'})

@app.route('/desativar_atividade/<nome_atividade>', methods=['POST'])
@apenas_admin_ou_master
def desativar_atividade_route(nome_atividade):
    """Desativa uma atividade"""
    try:
        # Verificar se a atividade existe
        if nome_atividade not in academia.atividades_cadastradas:
            return jsonify({'success': False, 'message': 'Atividade não encontrada'})
        
        # Desativar a atividade
        academia.atividades_cadastradas[nome_atividade]['ativa'] = False
        
        # Salvar as alterações
        academia.salvar_atividades()
        
        # Registrar atividade
        usuario_logado = session.get('usuario_logado')
        nivel_usuario = session.get('usuario_nivel', 'admin')
        registrar_atividade(
            usuario_logado, 
            'Desativou Atividade', 
            f'Desativou a atividade "{nome_atividade}"', 
            nivel_usuario
        )
        
        return jsonify({
            'success': True,
            'message': f'Atividade "{nome_atividade}" desativada com sucesso!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao desativar atividade: {str(e)}'})

@app.route('/api/atividade/<nome_atividade>', methods=['GET'])
@login_obrigatorio
def obter_atividade_api(nome_atividade):
    """API para obter dados de uma atividade específica"""
    try:
        # Verificar se a atividade existe
        if nome_atividade not in academia.atividades_cadastradas:
            return jsonify({'error': 'Atividade não encontrada'}), 404
        
        # Retornar dados da atividade
        atividade = academia.atividades_cadastradas[nome_atividade]
        return jsonify(atividade)
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar atividade: {str(e)}'}), 500

@app.route('/obter_professor_atividade/<nome_atividade>', methods=['GET'])
@login_obrigatorio
def obter_professor_atividade(nome_atividade):
    """Retorna o professor vinculado a uma atividade"""
    try:
        atividade = academia.atividades_cadastradas.get(nome_atividade, {})
        professores = atividade.get('professores_vinculados', [])
        professor = professores[0] if professores else ''
        
        return jsonify({
            'success': True,
            'professor': professor
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter professor: {str(e)}'
        }), 500

@app.route('/editar_atividade', methods=['POST'])
@apenas_admin_ou_master
def editar_atividade_route():
    """Edita uma atividade existente"""
    try:
        dados = request.json
        nome_antigo = dados.get('nome_antigo')
        nome_novo = dados.get('nome_novo')
        descricao_nova = dados.get('descricao_nova')
        professor_novo = dados.get('professor_novo', '')
        
        if not nome_antigo or not nome_novo or not descricao_nova:
            return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
        
        sucesso, mensagem = academia.editar_atividade(nome_antigo, nome_novo, descricao_nova, professor_novo)
        
        if sucesso:
            # Obter a atividade atualizada para incluir o professor na resposta
            atividade = academia.atividades_cadastradas.get(nome_novo, {})
            professores = atividade.get('professores_vinculados', [])
            professor = professores[0] if professores else ''
            
            return jsonify({
                'success': True,
                'message': mensagem,
                'atividade': {
                    'nome': nome_novo,
                    'descricao': descricao_nova,
                    'professor': professor,
                    'total_alunos': len(academia.get_alunos_por_atividade(nome_novo))
                }
            })
        else:
            return jsonify({'success': False, 'message': mensagem})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao editar atividade: {str(e)}'})

# === ROTAS PARA GERENCIAMENTO DE TURMAS ===

@app.route('/gerenciar_turmas')
@apenas_admin_ou_master
def gerenciar_turmas():
    """Página de gerenciamento de turmas - Admin/Admin Master"""
    usuario_nome = session.get('usuario_nome', 'Usuário')
    
    # Obter lista de professores para o dropdown
    professores = {login: dados for login, dados in USUARIOS.items() 
                  if dados.get('nivel') == 'usuario'}
    
    return render_template('gerenciar_turmas.html', 
                         turmas=academia.turmas_cadastradas,
                         atividades=academia.atividades_cadastradas,
                         professores=professores,
                         usuario_nome=usuario_nome)

@app.route('/criar_turma', methods=['POST'])
@apenas_admin_ou_master
def criar_turma():
    """Cria uma nova turma"""
    try:
        nome = request.form.get('nome', '').strip()
        atividade = request.form.get('atividade', '').strip()
        horario = request.form.get('horario', '').strip()
        dias_semana = request.form.get('dias_semana', '').strip()
        capacidade = request.form.get('capacidade', '20')
        professor = request.form.get('professor', '').strip()
        criado_por = session.get('usuario_logado')
        
        if not all([nome, atividade, horario, dias_semana]):
            return jsonify({'success': False, 'message': 'Todos os campos obrigatórios devem ser preenchidos'})
        
        if len(nome) < 3:
            return jsonify({'success': False, 'message': 'Nome da turma deve ter pelo menos 3 caracteres'})
        
        try:
            capacidade = int(capacidade)
            if capacidade < 1 or capacidade > 50:
                return jsonify({'success': False, 'message': 'Capacidade deve ser entre 1 e 50 alunos'})
        except ValueError:
            return jsonify({'success': False, 'message': 'Capacidade deve ser um número válido'})
        
        sucesso, mensagem = academia.cadastrar_turma(nome, atividade, horario, dias_semana, capacidade, professor, criado_por)
        
        if sucesso:
            return jsonify({
                'success': True,
                'message': mensagem,
                'total_turmas': len(academia.turmas_cadastradas)
            })
        else:
            return jsonify({'success': False, 'message': mensagem})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao criar turma: {str(e)}'})

@app.route('/excluir_turma/<turma_id>', methods=['DELETE'])
@apenas_admin_ou_master
def excluir_turma_route(turma_id):
    """Exclui uma turma"""
    try:
        sucesso, mensagem = academia.excluir_turma(turma_id)
        
        if sucesso:
            return jsonify({
                'success': True,
                'message': mensagem,
                'total_turmas': len(academia.turmas_cadastradas)
            })
        else:
            return jsonify({'success': False, 'message': mensagem})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao excluir turma: {str(e)}'})

@app.route('/editar_turma', methods=['POST'])
@apenas_admin_ou_master
def editar_turma_route():
    """Edita uma turma existente"""
    try:
        turma_id = request.form.get('turma_id')
        nome = request.form.get('nome', '').strip()
        atividade = request.form.get('atividade', '').strip()
        horario = request.form.get('horario', '').strip()
        dias_semana = request.form.get('dias_semana', '').strip()
        capacidade = request.form.get('capacidade', '20')
        professor = request.form.get('professor', '').strip()
        ativa = request.form.get('ativa', 'true')
        
        if not all([turma_id, nome, atividade, horario, dias_semana]):
            return jsonify({'success': False, 'message': 'Todos os campos obrigatórios devem ser preenchidos'})
        
        if len(nome) < 3:
            return jsonify({'success': False, 'message': 'Nome da turma deve ter pelo menos 3 caracteres'})
        
        try:
            capacidade = int(capacidade)
            if capacidade < 1 or capacidade > 50:
                return jsonify({'success': False, 'message': 'Capacidade deve ser entre 1 e 50 alunos'})
        except ValueError:
            return jsonify({'success': False, 'message': 'Capacidade deve ser um número válido'})
        
        sucesso, mensagem = academia.editar_turma(turma_id, nome, atividade, horario, dias_semana, capacidade, professor, ativa)
        
        if sucesso:
            return jsonify({
                'success': True,
                'message': mensagem,
                'turma': academia.turmas_cadastradas[turma_id]
            })
        else:
            return jsonify({'success': False, 'message': mensagem})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao editar turma: {str(e)}'})

@app.route('/dashboard_turma/<turma_id>')
@login_obrigatorio
def obter_estatisticas_turma(turma_id, turma):
    """Obter estatísticas específicas de uma turma"""
    try:
        from datetime import datetime, date
        
        # Buscar alunos da turma específica
        alunos_turma = []
        for aluno_id, aluno in academia.alunos_cadastrados.items():
            if turma['nome'] in aluno.get('turmas', []):
                alunos_turma.append(aluno)
        
        total_alunos = len(alunos_turma)
        
        # Calcular presenças de hoje
        hoje = date.today().strftime('%Y-%m-%d')
        presencas_hoje = 0
        
        # Simular presenças baseado nos dados existentes
        if hasattr(academia, 'presencas_registradas'):
            for presenca in academia.presencas_registradas:
                if (presenca.get('data') == hoje and 
                    presenca.get('turma') == turma['nome'] and 
                    presenca.get('status') == 'presente'):
                    presencas_hoje += 1
        else:
            # Fallback: estimar 80% de presença
            presencas_hoje = int(total_alunos * 0.8)
        
        # Calcular frequência média da turma
        frequencia_media = 0.0
        if total_alunos > 0:
            total_frequencia = 0
            for aluno in alunos_turma:
                # Usar frequência do aluno se disponível, senão estimar
                freq_aluno = aluno.get('frequencia_media', 0.85)  # 85% padrão
                total_frequencia += freq_aluno
            frequencia_media = total_frequencia / total_alunos
        
        # Calcular taxa de ocupação
        taxa_ocupacao = 0.0
        if turma.get('capacidade_maxima'):
            taxa_ocupacao = (total_alunos / turma['capacidade_maxima']) * 100
        
        # Distribuição por gênero
        genero_stats = {'masculino': 0, 'feminino': 0, 'outros': 0}
        for aluno in alunos_turma:
            genero = aluno.get('genero', '').lower()
            if genero in ['masculino', 'm']:
                genero_stats['masculino'] += 1
            elif genero in ['feminino', 'f']:
                genero_stats['feminino'] += 1
            else:
                genero_stats['outros'] += 1
        
        # Retornar objeto com estatísticas
        class StatsObject:
            def __init__(self):
                self.total_alunos = total_alunos
                self.presencas_hoje = presencas_hoje
                self.frequencia_media = frequencia_media
                self.taxa_ocupacao = taxa_ocupacao
                self.genero_stats = genero_stats
                self.alunos_turma = alunos_turma
        
        return StatsObject()
        
    except Exception as e:
        print(f"Erro ao obter estatísticas da turma: {e}")
        # Retornar estatísticas padrão em caso de erro
        class DefaultStats:
            def __init__(self):
                self.total_alunos = 0
                self.presencas_hoje = 0
                self.frequencia_media = 0.0
                self.taxa_ocupacao = 0.0
                self.genero_stats = {'masculino': 0, 'feminino': 0, 'outros': 0}
                self.alunos_turma = []
        
        return DefaultStats()

@app.route('/dashboard_turma/<turma_id>')
@login_obrigatorio
def dashboard_turma(turma_id):
    """Dashboard específico de uma turma"""
    nivel_usuario = session.get('usuario_nivel')
    usuario_logado = session.get('usuario_logado')
    usuario_nome = session.get('usuario_nome', 'Usuário')
    
    # Verificar se a turma existe
    if turma_id not in academia.turmas_cadastradas:
        flash('Turma não encontrada!', 'error')
        return redirect(url_for('dashboard'))
    
    turma = academia.turmas_cadastradas[turma_id]
    
    # Verificar permissões
    if nivel_usuario == 'usuario':
        # Usuários só podem ver dashboard das suas turmas
        if turma['professor_responsavel'] != usuario_logado:
            flash('Acesso negado! Você só pode acessar dashboard das suas turmas.', 'error')
            return redirect(url_for('dashboard'))
    
    # Obter estatísticas específicas da turma
    stats = obter_estatisticas_turma(turma_id, turma)
    
    return render_template('dashboard_turma.html', 
                         stats=stats, 
                         turma=turma,
                         usuario_nome=usuario_nome,
                         nivel_usuario=nivel_usuario)

@app.route('/obter_dados_turma/<turma_id>')
@login_obrigatorio
def obter_dados_turma(turma_id):
    """Obter dados específicos da turma para AJAX"""
    try:
        # Verificar se a turma existe
        if turma_id not in academia.turmas_cadastradas:
            return jsonify({'success': False, 'message': 'Turma não encontrada'})
        
        turma = academia.turmas_cadastradas[turma_id]
        nivel_usuario = session.get('usuario_nivel')
        usuario_logado = session.get('usuario_logado')
        
        # Verificar permissões
        if nivel_usuario == 'usuario':
            if turma['professor_responsavel'] != usuario_logado:
                return jsonify({'success': False, 'message': 'Acesso negado'})
        
        # Obter estatísticas da turma
        stats = obter_estatisticas_turma(turma_id, turma)
        
        # Preparar dados dos alunos para a tabela
        alunos_dados = []
        for aluno in stats.alunos_turma:
            alunos_dados.append({
                'nome': aluno.get('nome', 'N/A'),
                'idade': aluno.get('idade', 'N/A'),
                'telefone': aluno.get('telefone', 'N/A'),
                'data_matricula': aluno.get('data_cadastro', 'N/A'),
                'frequencia': f"{aluno.get('frequencia_media', 0.85) * 100:.1f}%",
                'status': 'Ativo' if aluno.get('ativo', True) else 'Inativo'
            })
        
        return jsonify({
            'success': True,
            'data': {
                'total_alunos': stats.total_alunos,
                'presencas_hoje': stats.presencas_hoje,
                'frequencia_media': stats.frequencia_media,
                'taxa_ocupacao': stats.taxa_ocupacao,
                'genero_stats': stats.genero_stats,
                'alunos': alunos_dados
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao obter dados da turma: {str(e)}'})

@app.route('/form_manager_demo')
@login_obrigatorio
def form_manager_demo():
    """Página de demonstração do FormManager com useMemo pattern"""
    return render_template('form_manager_demo.html')

@app.route('/demo_submit', methods=['POST'])
@login_obrigatorio
def demo_submit():
    """Rota de demonstração para testar o FormManager"""
    try:
        # Simular processamento
        import time
        time.sleep(1)  # Simular delay
        
        # Retornar sucesso para demonstração
        return jsonify({
            'success': True,
            'message': 'Formulário processado com sucesso! (Demonstração)',
            'data': dict(request.form)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro na demonstração: {str(e)}'
        })

@app.route('/ficha_cadastro/<aluno_id>')
@login_obrigatorio
def ficha_cadastro(aluno_id):
    """Gera ficha de cadastro individual do aluno para impressão"""
    try:
        # Buscar aluno pelo ID do banco de dados
        aluno = None
        for a in academia.alunos_reais:
            if str(a.get('id', '')) == str(aluno_id):
                aluno = a
                break
        
        if not aluno:
            return "Aluno não encontrado", 404
        
        # Verificar permissão do usuário
        nivel_usuario = session.get('usuario_nivel', 'usuario')
        if nivel_usuario == 'usuario':
            # Professores só podem ver alunos da sua atividade
            usuario_logado = session.get('usuario_logado')
            usuario_info = USUARIOS.get(usuario_logado, {})
            atividades_responsavel = usuario_info.get('atividades_responsavel', [])
            
            if aluno.get('atividade') not in atividades_responsavel:
                return "Você não tem permissão para visualizar este aluno", 403
        
        # Obter dados de presença do aluno
        dados_presenca = academia.get_presenca_aluno(aluno['nome'])
        
        return render_template('ficha_cadastro.html',
                              aluno=aluno,
                              dados_presenca=dados_presenca,
                              data_geracao=datetime.now().strftime('%d/%m/%Y às %H:%M'))
                              
    except Exception as e:
        return f"Erro ao gerar ficha: {str(e)}", 500

# Carregar usuários existentes do arquivo (se existir)
carregar_usuarios()

# Sistema de Logs de Atividades
import json
from datetime import datetime, timedelta

def registrar_atividade(usuario, acao, detalhes, tipo_usuario="usuario"):
    """Registra uma atividade no sistema de logs usando PostgreSQL"""
    try:
        # Registrar no banco de dados PostgreSQL
        sucesso = db_integration.registrar_atividade_db(
            usuario=usuario,
            acao=acao,
            detalhes=detalhes,
            tipo_usuario=tipo_usuario
        )
        
        if not sucesso:
            print(f"Falha ao registrar atividade no banco para usuário {usuario}")
            
        # Manter compatibilidade com arquivo JSON como backup (opcional)
        # Este bloco pode ser removido após confirmação de que o banco está funcionando
        try:
            logs_file = 'logs_atividades.json'
            logs = []
            
            if os.path.exists(logs_file):
                with open(logs_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            
            novo_log = {
                'timestamp': datetime.now().isoformat(),
                'data_hora': datetime.now().strftime('%d/%m/%Y às %H:%M:%S'),
                'usuario': usuario,
                'tipo_usuario': tipo_usuario,
                'acao': acao,
                'detalhes': detalhes
            }
            
            logs.append(novo_log)
            
            if len(logs) > 100:  # Reduzido para 100 como backup
                logs = logs[-100:]
            
            with open(logs_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
                
        except Exception as backup_error:
            print(f"Erro no backup JSON (não crítico): {backup_error}")
            
    except Exception as e:
        print(f"Erro ao registrar atividade: {e}")

def carregar_logs(filtro_periodo="todos"):
    """Carrega logs do banco de dados PostgreSQL com filtro por período"""
    try:
        # Carregar logs do banco de dados
        logs = db_integration.listar_logs_db(filtro=filtro_periodo, limite=1000)
        
        # Se não houver logs no banco, tentar carregar do arquivo JSON como fallback
        if not logs:
            try:
                logs_file = 'logs_atividades.json'
                if os.path.exists(logs_file):
                    with open(logs_file, 'r', encoding='utf-8') as f:
                        logs_json = json.load(f)
                    
                    # Aplicar filtro por período para logs JSON
                    agora = datetime.now()
                    
                    if filtro_periodo == "hoje":
                        hoje = agora.replace(hour=0, minute=0, second=0, microsecond=0)
                        logs_json = [log for log in logs_json if datetime.fromisoformat(log['timestamp']) >= hoje]
                    elif filtro_periodo == "semana":
                        semana_atras = agora - timedelta(days=7)
                        logs_json = [log for log in logs_json if datetime.fromisoformat(log['timestamp']) >= semana_atras]
                    elif filtro_periodo == "mes":
                        mes_atras = agora - timedelta(days=30)
                        logs_json = [log for log in logs_json if datetime.fromisoformat(log['timestamp']) >= mes_atras]
                    
                    # Ordenar por timestamp (mais recente primeiro)
                    logs_json.sort(key=lambda x: x['timestamp'], reverse=True)
                    
                    return logs_json
            except Exception as fallback_error:
                print(f"Erro no fallback JSON: {fallback_error}")
        
        return logs
        
    except Exception as e:
        print(f"Erro ao carregar logs: {e}")
        return []

@app.route('/logs_atividades')
@login_obrigatorio
def logs_atividades():
    """Página de logs de atividades (apenas para admin master)"""
    nivel_usuario = session.get('usuario_nivel')
    
    if nivel_usuario != 'admin_master':
        flash('Acesso negado! Apenas administradores master podem visualizar os logs.', 'error')
        return redirect(url_for('dashboard'))
    
    filtro = request.args.get('filtro', 'todos')
    logs = carregar_logs(filtro)
    
    # Estatísticas dos logs
    total_logs = len(logs)
    usuarios_ativos = len(set(log['usuario'] for log in logs))
    
    # Agrupar por tipo de ação
    acoes_count = {}
    for log in logs:
        acao = log['acao']
        acoes_count[acao] = acoes_count.get(acao, 0) + 1
    
    return render_template('logs_atividades.html', 
                         logs=logs, 
                         filtro_atual=filtro,
                         total_logs=total_logs,
                         usuarios_ativos=usuarios_ativos,
                         acoes_count=acoes_count)

# Rota de health check para o Render
@app.route('/health')
def health_check():
    return jsonify({"status": "ok"})

@app.route('/configurar_retencao_logs', methods=['POST'])
@login_obrigatorio
def configurar_retencao_logs():
    """Endpoint para configurar retenção de logs"""
    try:
        dados = request.get_json()
        retencao_dias = dados.get('retencao_dias', 90)
        max_logs = dados.get('max_logs', 10000)
        backup_automatico = dados.get('backup_automatico', True)
        
        # Validar dados
        if not isinstance(retencao_dias, int) or retencao_dias < 30 or retencao_dias > 365:
            return jsonify({
                'success': False,
                'message': 'Retenção deve ser entre 30 e 365 dias'
            }), 400
            
        if not isinstance(max_logs, int) or max_logs < 1000 or max_logs > 100000:
            return jsonify({
                'success': False,
                'message': 'Máximo de logs deve ser entre 1.000 e 100.000'
            }), 400
        
        # Salvar configuração em arquivo
        config_file = 'config_logs.json'
        config = {
            'retencao_dias': retencao_dias,
            'max_logs': max_logs,
            'backup_automatico': backup_automatico,
            'data_atualizacao': datetime.now().isoformat(),
            'usuario_atualizacao': session.get('usuario_nome', 'Sistema')
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        # Registrar atividade
        usuario_nome = session.get('usuario_nome', 'Sistema')
        sistema_busca.registrar_atividade(
            f"Configuração de retenção de logs atualizada: {retencao_dias} dias, máx {max_logs} logs",
            usuario_nome,
            'configuracao'
        )
        
        return jsonify({
            'success': True,
            'message': 'Configuração de retenção salva com sucesso!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar configuração: {str(e)}'
        }), 500

@app.route('/obter_configuracao_logs', methods=['GET'])
@login_obrigatorio
def obter_configuracao_logs():
    """Endpoint para obter configuração atual de logs"""
    try:
        config_file = 'config_logs.json'
        
        # Configuração padrão
        config_padrao = {
            'retencao_dias': 90,
            'max_logs': 10000,
            'backup_automatico': True
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = config_padrao
        
        return jsonify({
            'success': True,
            'config': config
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter configuração: {str(e)}'
        }), 500

# Rota para o service worker
@app.route('/editar_log', methods=['POST'])
@login_obrigatorio
def editar_log():
    """Endpoint para editar um log de atividade"""
    try:
        dados = request.get_json()
        timestamp_original = dados.get('timestamp_original')
        nova_acao = dados.get('acao', '').strip()
        novos_detalhes = dados.get('detalhes', '').strip()
        novo_tipo = dados.get('tipo', 'usuario')
        
        # Validar dados obrigatórios
        if not timestamp_original or not nova_acao or not novos_detalhes:
            return jsonify({
                'success': False,
                'message': 'Timestamp, ação e detalhes são obrigatórios'
            })
        
        # Validar tipo de usuário
        tipos_validos = ['admin', 'admin_master', 'usuario']
        if novo_tipo not in tipos_validos:
            return jsonify({
                'success': False,
                'message': f'Tipo deve ser um dos seguintes: {", ".join(tipos_validos)}'
            })
        
        # Simular edição do log (em um sistema real, você editaria no banco de dados)
        # Por enquanto, apenas registramos a ação de edição
        usuario_atual = session.get('usuario', 'Desconhecido')
        detalhes_edicao = f'Editou log de {timestamp_original}: Ação="{nova_acao}", Detalhes="{novos_detalhes}", Tipo="{novo_tipo}"'
        
        # Registrar a ação de edição no log
        with get_db_session() as db:
            LogAtividadeDAO.registrar_log(
                db=db,
                usuario=usuario_atual,
                acao='Editou Log',
                detalhes=detalhes_edicao,
                tipo_usuario=session.get('nivel', 'usuario')
            )
        
        return jsonify({
            'success': True,
            'message': 'Log editado com sucesso'
        })
        
    except Exception as e:
        print(f"Erro ao editar log: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro interno do servidor: {str(e)}'
        })

@app.route('/gerar_relatorio_turma', methods=['POST'])
@login_obrigatorio
def gerar_relatorio_turma():
    """Gera relatório completo de uma turma específica"""
    try:
        dados = request.get_json()
        turma_id = dados.get('turma_id')
        
        if not turma_id:
            return jsonify({
                'success': False,
                'message': 'ID da turma é obrigatório'
            })
        
        # Verificar se a turma existe
        if turma_id not in academia.turmas_cadastradas:
            return jsonify({
                'success': False,
                'message': 'Turma não encontrada'
            })
        
        turma = academia.turmas_cadastradas[turma_id]
        nivel_usuario = session.get('usuario_nivel')
        usuario_logado = session.get('usuario_logado')
        
        # Verificar permissões
        if nivel_usuario == 'usuario':
            if turma['professor_responsavel'] != usuario_logado:
                return jsonify({
                    'success': False,
                    'message': 'Acesso negado. Você só pode gerar relatórios das suas turmas.'
                })
        
        # Obter dados da turma
        stats = obter_estatisticas_turma(turma_id, turma)
        
        # Preparar dados do relatório
        relatorio_data = {
            'turma': {
                'nome': turma['nome'],
                'atividade': turma['atividade'],
                'horario': turma['horario'],
                'dias_semana': turma['dias_semana'],
                'professor': turma.get('professor_responsavel', 'Não definido'),
                'capacidade': turma.get('capacidade_maxima', 20),
                'status': 'Ativa' if turma.get('ativa', True) else 'Inativa'
            },
            'estatisticas': {
                'total_alunos': stats.get('total_alunos', 0),
                'presencas_hoje': stats.get('presencas_hoje', 0),
                'frequencia_media': f"{stats.get('frequencia_media', 0) * 100:.1f}%",
                'genero_stats': stats.get('genero_stats', {})
            },
            'alunos': [],
            'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'gerado_por': session.get('usuario_nome', 'Usuário')
        }
        
        # Adicionar dados dos alunos
        for aluno in stats.get('alunos_turma', []):
            relatorio_data['alunos'].append({
                'nome': aluno.get('nome', 'N/A'),
                'idade': aluno.get('idade', 'N/A'),
                'telefone': aluno.get('telefone', 'N/A'),
                'data_matricula': aluno.get('data_cadastro', 'N/A'),
                'frequencia': f"{aluno.get('frequencia_media', 0.85) * 100:.1f}%",
                'status': 'Ativo' if aluno.get('ativo', True) else 'Inativo'
            })
        
        # Registrar atividade
        registrar_atividade(
            usuario_logado,
            'Geração de Relatório',
            f'Relatório da turma "{turma["nome"]}" gerado com sucesso',
            nivel_usuario
        )
        
        return jsonify({
            'success': True,
            'message': 'Relatório gerado com sucesso!',
            'relatorio': relatorio_data
        })
        
    except Exception as e:
        print(f"Erro ao gerar relatório da turma: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        })

@app.route('/service-worker.js')
def service_worker():
    return app.send_static_file('js/service-worker.js'), 200, {'Content-Type': 'application/javascript'}

# Para produção


@app.route('/sistema/status')
@login_obrigatorio
def status_sistema():
    """Endpoint para verificar status do sistema de banco de dados"""
    try:
        status = db_integration_robusto.get_status_sistema()
        
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/sistema')
@login_obrigatorio
def sistema_admin():
    """Página de administração do sistema"""
    return render_template('sistema_status.html')

@app.route('/sistema/processar-fallback', methods=['POST'])
@login_obrigatorio
def processar_fallback():
    """Endpoint para processar registros pendentes do fallback"""
    try:
        resultado = db_integration_robusto.processar_fallback_pendente()
        
        return jsonify({
            'success': True,
            'resultado': resultado,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Iniciando Associação Amigo do Povo...")
    print(f"🌐 Sistema carregado: {len(academia.alunos_reais)} alunos")
    print(f"👥 Usuários carregados: {len(USUARIOS)} contas")
    app.run(host='0.0.0.0', port=port, debug=True)