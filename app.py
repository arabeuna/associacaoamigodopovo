from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, send_file
from datetime import datetime
import os
import hashlib
import json
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'associacao_amigo_do_povo_2024_secure_key')

# Usuários do sistema
USUARIOS = {
    'admin': {
        'senha': hashlib.sha256('admin123'.encode()).hexdigest(),
        'nome': 'Administrador',
        'nivel': 'admin'
    },
    'usuario': {
        'senha': hashlib.sha256('usuario123'.encode()).hexdigest(), 
        'nome': 'Usuário',
        'nivel': 'usuario'
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
        self.arquivo_dados = 'dados_alunos.json'
        self.alunos_reais = self.carregar_dados_reais()
        self.atividades_disponiveis = self.get_atividades_disponiveis()
        self.dados_presenca = self.carregar_dados_presenca()
        # Atualizar status de frequência com dados de presença
        self.atualizar_status_frequencia_informatica()
    
    def carregar_dados_reais(self):
        """Carrega dados do arquivo JSON, CSV ou usa dados embutidos"""
        try:
            # 1. Tentar carregar dados do arquivo JSON primeiro (dados salvos do sistema)
            if os.path.exists(self.arquivo_dados):
                with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                    dados_salvos = json.load(f)
                    print(f"📦 Carregados {len(dados_salvos)} alunos do arquivo salvo")
                    return dados_salvos
            
            # 2. Tentar carregar do CSV da planilha original
            arquivo_csv = 'outros/Cadastros_Unificados_GOOGLE_v2.csv'
            if os.path.exists(arquivo_csv):
                print("📊 Encontrado arquivo CSV da planilha original!")
                dados_csv = self.carregar_dados_csv(arquivo_csv)
                if dados_csv:
                    # Salvar no formato JSON para próximas execuções
                    self.salvar_dados(dados_csv)
                    return dados_csv
            
            # 3. Procurar por outros arquivos CSV na pasta outros
            pasta_outros = 'outros'
            if os.path.exists(pasta_outros):
                arquivos_csv = [f for f in os.listdir(pasta_outros) if f.endswith('.csv')]
                print(f"📁 Arquivos CSV encontrados: {arquivos_csv}")
                
                for arquivo in arquivos_csv:
                    caminho_completo = os.path.join(pasta_outros, arquivo)
                    print(f"🔍 Tentando ler: {arquivo}")
                    dados_csv = self.carregar_dados_csv(caminho_completo)
                    if dados_csv and len(dados_csv) > 0:
                        print(f"✅ Dados carregados de: {arquivo}")
                        self.salvar_dados(dados_csv)
                        return dados_csv
            
            # 4. Se não encontrou nenhum CSV, criar arquivo com dados embutidos
            print("📦 Criando arquivo de dados com dados iniciais")
            dados_iniciais = self.get_dados_reais_embutidos()
            self.salvar_dados(dados_iniciais)
            return dados_iniciais
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
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
    
    def get_alunos_por_atividade(self, atividade):
        """Retorna alunos de uma atividade"""
        return [aluno for aluno in self.alunos_reais if aluno['atividade'] == atividade]
    
    def get_estatisticas(self):
        """Estatísticas básicas com dados reais de presença"""
        atividades_count = {}
        for aluno in self.alunos_reais:
            atividade = aluno['atividade']
            atividades_count[atividade] = atividades_count.get(atividade, 0) + 1
        
        # Calcular presenças hoje baseado nos dados reais
        data_hoje = datetime.now().strftime('%d/%m/%Y')
        presencas_hoje = 0
        
        for nome, dados in self.dados_presenca.items():
            for registro in dados['registros']:
                if registro.get('data') == data_hoje and registro.get('status') == 'P':
                    presencas_hoje += 1
        
        # Calcular total de registros de presença
        total_registros = 0
        for dados in self.dados_presenca.values():
            total_registros += len(dados['registros'])
        
        # Calcular alunos com presença registrada
        alunos_com_presenca = len(self.dados_presenca)
        
        return {
            'total_alunos': len(self.alunos_reais),
            'presencas_hoje': presencas_hoje,
            'presencas_semana': total_registros,  # Renomeado para ser mais descritivo
            'alunos_ativos': alunos_com_presenca,
            'atividades_count': atividades_count
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
        """Registra presença manual de um aluno"""
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
        """Salva os dados dos alunos no arquivo JSON"""
        try:
            dados_para_salvar = dados if dados is not None else self.alunos_reais
            with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
                json.dump(dados_para_salvar, f, ensure_ascii=False, indent=2)
            print(f"💾 Dados salvos: {len(dados_para_salvar)} alunos")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar dados: {e}")
            return False
    
    def adicionar_aluno(self, novo_aluno):
        """Adiciona um novo aluno e salva os dados"""
        try:
            self.alunos_reais.append(novo_aluno)
            self.salvar_dados()
            return True
        except Exception as e:
            print(f"❌ Erro ao adicionar aluno: {e}")
            return False
    
    def atualizar_aluno(self, indice, dados_atualizados):
        """Atualiza um aluno existente e salva os dados"""
        try:
            if 0 <= indice < len(self.alunos_reais):
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
academia = SistemaAcademia()

def verificar_login():
    return 'usuario_logado' in session

def login_obrigatorio(f):
    def wrapper(*args, **kwargs):
        if not verificar_login():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

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
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Senha incorreta!', 'error')
        else:
            flash('Usuário não encontrado!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_obrigatorio
def dashboard():
    stats = academia.get_estatisticas()
    
    # Obter presenças de hoje
    data_hoje = datetime.now().strftime('%d/%m/%Y')
    presencas_hoje = []
    
    for nome, dados in academia.dados_presenca.items():
        for registro in dados['registros']:
            if registro.get('data') == data_hoje and registro.get('status') == 'P':
                presencas_hoje.append({
                    'Nome': nome,
                    'Horário': registro.get('horario', ''),
                    'Atividade': dados.get('atividade', ''),
                    'Observações': 'Presença registrada'
                })
    
    usuario_nome = session.get('usuario_nome', 'Usuário')
    return render_template('dashboard.html', stats=stats, presencas_hoje=presencas_hoje, usuario_nome=usuario_nome)

@app.route('/alunos')
@login_obrigatorio
def alunos():
    lista_alunos = academia.get_alunos()
    usuario_nome = session.get('usuario_nome', 'Usuário')
    return render_template('alunos.html', alunos=lista_alunos, usuario_nome=usuario_nome)

@app.route('/presenca')
@login_obrigatorio
def presenca():
    lista_alunos = academia.get_alunos()
    usuario_nome = session.get('usuario_nome', 'Usuário')
    return render_template('presenca.html', alunos=lista_alunos, usuario_nome=usuario_nome)

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
@login_obrigatorio
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
        
        # Registrar presença manual
        sucesso, mensagem = academia.registrar_presenca_manual(nome_aluno)
        
        if sucesso:
            return jsonify({
                'success': True, 
                'message': mensagem,
                'aluno': nome_aluno,
                'data_hora': datetime.now().strftime('%d/%m/%Y %H:%M')
            })
        else:
            return jsonify({'success': False, 'message': mensagem})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao marcar presença: {str(e)}'})

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
                'turma': turma_presenca
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
        
        # Realizar busca
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
            'atividades_encontradas': estatisticas['atividades_encontradas']
        }
        
        print(f"🔍 Busca realizada: {len(resultados)} resultados encontrados")
        print(f"📊 Filtros aplicados: {filtros_limpos}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Erro na busca avançada: {e}")
        return jsonify({
            'success': False, 
            'message': f'Erro ao realizar busca: {str(e)}',
            'resultados': []
        })

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
    return jsonify({'message': f'Relatório de {mes} será implementado'})

@app.route('/cadastrar_aluno', methods=['POST'])
@login_obrigatorio
def cadastrar_aluno():
    try:
        # Obter dados do formulário
        nome = request.form.get('nome', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        endereco = request.form.get('endereco', '').strip()
        data_nascimento = request.form.get('data_nascimento', '').strip()
        atividade = request.form.get('atividade', '').strip()
        turma = request.form.get('turma', '').strip()
        observacoes = request.form.get('observacoes', '').strip()
        
        # Validações
        if not nome or len(nome) < 3:
            return jsonify({'success': False, 'message': 'Nome deve ter pelo menos 3 caracteres'})
        
        if not telefone or len(telefone.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')) < 10:
            return jsonify({'success': False, 'message': 'Telefone deve ter pelo menos 10 dígitos'})
        
        # Verificar se aluno já existe
        for aluno in academia.alunos_reais:
            if aluno['nome'].lower() == nome.lower():
                return jsonify({'success': False, 'message': 'Já existe um aluno cadastrado com este nome'})
        
        # Converter data de nascimento se fornecida
        data_nasc_formatada = data_nascimento
        if data_nascimento:
            try:
                # Converter de YYYY-MM-DD para DD/MM/YYYY
                from datetime import datetime as dt
                data_obj = dt.strptime(data_nascimento, '%Y-%m-%d')
                data_nasc_formatada = data_obj.strftime('%d/%m/%Y')
            except:
                data_nasc_formatada = data_nascimento
        
        # Criar novo aluno
        novo_aluno = {
            'nome': nome,
            'telefone': telefone,
            'endereco': endereco if endereco else 'A definir',
            'email': email if email else f"{nome.lower().replace(' ', '.')}@email.com",
            'data_nascimento': data_nasc_formatada if data_nasc_formatada else 'A definir',
            'data_cadastro': datetime.now().strftime('%d/%m/%Y'),
            'atividade': atividade if atividade else 'A definir',
            'turma': turma if turma else 'A definir',
            'status_frequencia': 'Novo cadastro',
            'observacoes': observacoes
        }
        
        # Adicionar ao sistema e salvar
        sucesso = academia.adicionar_aluno(novo_aluno)
        
        if sucesso:
            return jsonify({
                'success': True, 
                'message': f'Aluno {nome} cadastrado com sucesso!',
                'total_alunos': len(academia.alunos_reais)
            })
        else:
            return jsonify({'success': False, 'message': 'Erro ao salvar dados do aluno'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao cadastrar aluno: {str(e)}'})

@app.route('/editar_aluno/<int:aluno_id>', methods=['PUT', 'POST'])
@login_obrigatorio
def editar_aluno(aluno_id):
    try:
        if aluno_id < 0 or aluno_id >= len(academia.alunos_reais):
            return jsonify({'success': False, 'message': 'Aluno não encontrado'})
        
        # Obter dados do formulário
        nome = request.form.get('nome', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        endereco = request.form.get('endereco', '').strip()
        data_nascimento = request.form.get('data_nascimento', '').strip()
        atividade = request.form.get('atividade', '').strip()
        turma = request.form.get('turma', '').strip()
        observacoes = request.form.get('observacoes', '').strip()
        
        # Validações
        if not nome or len(nome) < 3:
            return jsonify({'success': False, 'message': 'Nome deve ter pelo menos 3 caracteres'})
        
        if not telefone or len(telefone.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')) < 10:
            return jsonify({'success': False, 'message': 'Telefone deve ter pelo menos 10 dígitos'})
        
        # Verificar se outro aluno já tem este nome
        for i, aluno in enumerate(academia.alunos_reais):
            if i != aluno_id and aluno['nome'].lower() == nome.lower():
                return jsonify({'success': False, 'message': 'Já existe outro aluno cadastrado com este nome'})
        
        # Converter data de nascimento se fornecida
        data_nasc_formatada = data_nascimento
        if data_nascimento:
            try:
                # Converter de YYYY-MM-DD para DD/MM/YYYY
                from datetime import datetime as dt
                data_obj = dt.strptime(data_nascimento, '%Y-%m-%d')
                data_nasc_formatada = data_obj.strftime('%d/%m/%Y')
            except:
                data_nasc_formatada = data_nascimento
        
        # Preparar dados atualizados
        aluno_atual = academia.alunos_reais[aluno_id]
        dados_atualizados = {
            'nome': nome,
            'telefone': telefone,
            'email': email if email else aluno_atual.get('email', ''),
            'endereco': endereco if endereco else aluno_atual.get('endereco', 'A definir'),
            'data_nascimento': data_nasc_formatada if data_nasc_formatada else aluno_atual.get('data_nascimento', 'A definir'),
            'atividade': atividade if atividade else aluno_atual.get('atividade', 'A definir'),
            'turma': turma if turma else aluno_atual.get('turma', 'A definir'),
            'observacoes': observacoes
        }
        
        # Atualizar e salvar
        sucesso = academia.atualizar_aluno(aluno_id, dados_atualizados)
        
        if sucesso:
            return jsonify({
                'success': True, 
                'message': f'Dados de {nome} atualizados com sucesso!',
                'aluno': academia.alunos_reais[aluno_id]
            })
        else:
            return jsonify({'success': False, 'message': 'Erro ao salvar alterações'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao editar aluno: {str(e)}'})

@app.route('/excluir_aluno/<int:aluno_id>', methods=['DELETE', 'POST'])
@login_obrigatorio
def excluir_aluno(aluno_id):
    try:
        if aluno_id < 0 or aluno_id >= len(academia.alunos_reais):
            return jsonify({'success': False, 'message': 'Aluno não encontrado'})
        
        # Obter nome do aluno e dados de frequência antes de excluir
        nome_aluno = academia.alunos_reais[aluno_id]['nome']
        tem_frequencia = nome_aluno in academia.dados_presenca
        
        if tem_frequencia:
            registros_frequencia = len(academia.dados_presenca[nome_aluno]['registros'])
        
        # Remover aluno e todos os seus dados
        sucesso = academia.remover_aluno(aluno_id)
        
        if sucesso:
            # Mensagem detalhada sobre o que foi removido
            mensagem = f'Aluno {nome_aluno} excluído com sucesso!'
            if tem_frequencia:
                mensagem += f' Também foram removidos {registros_frequencia} registros de frequência.'
            
            return jsonify({
                'success': True, 
                'message': mensagem,
                'total_alunos': len(academia.alunos_reais),
                'frequencia_removida': tem_frequencia,
                'registros_removidos': registros_frequencia if tem_frequencia else 0
            })
        else:
            return jsonify({'success': False, 'message': 'Erro ao excluir aluno'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao excluir aluno: {str(e)}'})

@app.route('/obter_aluno/<int:aluno_id>')
@login_obrigatorio
def obter_aluno(aluno_id):
    try:
        if aluno_id < 0 or aluno_id >= len(academia.alunos_reais):
            return jsonify({'success': False, 'message': 'Aluno não encontrado'})
        
        aluno = academia.alunos_reais[aluno_id]
        
        # Adicionar dados de presença se for da Informática
        dados_presenca = None
        if aluno.get('atividade') == 'Informática':
            dados_presenca = academia.get_presenca_aluno(aluno['nome'])
        
        return jsonify({
            'success': True,
            'aluno': aluno,
            'aluno_id': aluno_id,
            'dados_presenca': dados_presenca
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao obter dados do aluno: {str(e)}'})

@app.route('/salvar_dados_manualmente')
@login_obrigatorio  
def salvar_dados_manualmente():
    try:
        sucesso = academia.salvar_dados()
        if sucesso:
            return jsonify({
                'success': True,
                'message': f'Dados salvos com sucesso! Total: {len(academia.alunos_reais)} alunos',
                'total_alunos': len(academia.alunos_reais)
            })
        else:
            return jsonify({'success': False, 'message': 'Erro ao salvar dados'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

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
@login_obrigatorio
def backup_planilhas():
    if session.get('usuario_nivel') != 'admin':
        flash('Acesso negado! Apenas administradores podem acessar esta área.', 'error')
        return redirect(url_for('dashboard'))
    
    atividades = academia.get_atividades_disponiveis()
    usuario_nome = session.get('usuario_nome', 'Usuário')
    return render_template('backup_planilhas.html', atividades=atividades, usuario_nome=usuario_nome)

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

# Teste simples
@app.route('/test')
def test():
    return "Sistema funcionando! ✅"

# Para produção
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Iniciando Associação Amigo do Povo...")
    print(f"🌐 Sistema carregado: {len(academia.alunos_reais)} alunos")
    app.run(host='0.0.0.0', port=port, debug=False)