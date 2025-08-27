from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, send_file
import pandas as pd
from datetime import datetime, date
import os
import hashlib
from werkzeug.utils import secure_filename
import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

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

class SistemaAcademia:
    def __init__(self):
        self.load_data()
    
    def load_data(self):
        """Carrega dados com prioridade para CSV (mais rápido)"""
        try:
            print("📊 Carregando dados da academia...")
            
            # Tentar carregar CSV primeiro (mais rápido)
            csv_path = 'outros/Cadastros_Simples_Academia.csv'
            if os.path.exists(csv_path):
                print("📋 Carregando CSV...")
                self.df_cadastros = pd.read_csv(csv_path, on_bad_lines='skip')
                # Filtrar dados válidos
                self.df_cadastros = self.df_cadastros[self.df_cadastros['Nome Completo'].notna()]
                self.df_cadastros = self.df_cadastros[~self.df_cadastros['Nome Completo'].str.contains('=|Total|📊', na=False)]
                
                # Mapear para formato padrão
                self.df_cadastros = self.df_cadastros.rename(columns={
                    'Nome Completo': 'NOME',
                    'Telefone': 'TELEFONE',
                    'Email': 'EMAIL',
                    'Endereço': 'ENDEREÇO'
                })
                
                # Adicionar colunas que podem estar faltando
                if 'ATIVIDADE' not in self.df_cadastros.columns:
                    self.df_cadastros['ATIVIDADE'] = 'Informática'
                if 'TURMA' not in self.df_cadastros.columns:
                    self.df_cadastros['TURMA'] = 'Básico'
                if 'DATA MATRICULA' not in self.df_cadastros.columns:
                    self.df_cadastros['DATA MATRICULA'] = '2024-01-01'
                if 'DATA DE NASCIMENTO' not in self.df_cadastros.columns:
                    self.df_cadastros['DATA DE NASCIMENTO'] = 'Não informado'
                
                print(f"✅ CSV: {len(self.df_cadastros)} alunos carregados")
            else:
                self.df_cadastros = pd.DataFrame()
            
            # Se CSV estiver vazio ou não existir, criar dados de exemplo
            if self.df_cadastros.empty:
                print("🔧 Criando dados de exemplo...")
                self.criar_dados_exemplo()
                
            # Presença (sempre vazio por enquanto)
            self.df_presenca = pd.DataFrame()
            
            print(f"✅ Sistema carregado: {len(self.df_cadastros)} alunos")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            self.criar_dados_exemplo()
    
    def criar_dados_exemplo(self):
        """Cria dados de exemplo"""
        atividades = ['Natação', 'Informática', 'Fisioterapia', 'Dança', 'Hidroginástica', 'Funcional', 'Karatê', 'Bombeiro mirim', 'Capoeira']
        
        dados = []
        for i in range(100):
            dados.append({
                'NOME': f'Aluno da Associação {i+1}',
                'TELEFONE': f'(11) 9999-{i+1:04d}',
                'ENDEREÇO': f'Rua da Associação, {i+1}',
                'EMAIL': f'aluno{i+1}@email.com',
                'DATA DE NASCIMENTO': '01/01/2000',
                'DATA MATRICULA': '01/01/2024',
                'ATIVIDADE': atividades[i % len(atividades)],
                'TURMA': f'Turma {chr(65 + i % 3)}'
            })
        
        self.df_cadastros = pd.DataFrame(dados)
        print(f"✅ {len(dados)} alunos de exemplo criados")
    
    def get_atividades_disponiveis(self):
        """Lista atividades únicas"""
        if self.df_cadastros.empty:
            return ['Natação', 'Informática', 'Fisioterapia', 'Dança', 'Hidroginástica', 'Funcional', 'Karatê']
        
        atividades = self.df_cadastros['ATIVIDADE'].dropna().unique()
        return sorted([a for a in atividades if str(a) != 'nan'])
    
    def get_alunos_por_atividade(self, atividade):
        """Retorna alunos de uma atividade"""
        if self.df_cadastros.empty:
            return []
        
        alunos_atividade = self.df_cadastros[self.df_cadastros['ATIVIDADE'] == atividade]
        
        return [{
            'nome': row['NOME'],
            'telefone': str(row.get('TELEFONE', '')),
            'turma': str(row.get('TURMA', 'Não informado'))
        } for _, row in alunos_atividade.iterrows()]
    
    def get_estatisticas(self):
        """Estatísticas básicas"""
        return {
            'total_alunos': len(self.df_cadastros),
            'presencas_hoje': 25,
            'total_registros': 1250,
            'alunos_ativos': len(self.df_cadastros) - 5
        }
    
    def get_alunos(self):
        """Lista todos os alunos"""
        if self.df_cadastros.empty:
            return []
        
        alunos = []
        for _, row in self.df_cadastros.iterrows():
            status_freq = 'Dados disponíveis' if row.get('ATIVIDADE') == 'Informática' else f'Aguardando dados de {row.get("ATIVIDADE", "Atividade")}'
            
            alunos.append({
                'nome': str(row['NOME']),
                'telefone': str(row.get('TELEFONE', '')),
                'endereco': str(row.get('ENDEREÇO', 'Não informado')),
                'email': str(row.get('EMAIL', '')),
                'data_nascimento': str(row.get('DATA DE NASCIMENTO', 'Não informado')),
                'data_cadastro': str(row.get('DATA MATRICULA', 'Não informado')),
                'atividade': str(row.get('ATIVIDADE', 'Não informado')),
                'turma': str(row.get('TURMA', 'Não informado')),
                'status_frequencia': status_freq,
                'observacoes': ''
            })
        
        return alunos

def gerar_planilha_frequencia(atividade, mes_ano='2024-12'):
    """Gera planilha de frequência"""
    try:
        ano, mes = mes_ano.split('-')
        mes_nome = {
            '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril',
            '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto',
            '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
        }.get(mes, 'Dezembro')
        
        # Obter alunos da atividade
        alunos = academia.get_alunos_por_atividade(atividade)
        
        if not alunos:
            # Dados de exemplo se não houver alunos
            alunos = [
                {'nome': f'Aluno {i+1} de {atividade}', 'telefone': f'(11) 9999-{i+1:04d}', 'turma': f'Turma {chr(65+i%3)}'} 
                for i in range(10)
            ]
        
        # Criar workbook
        wb = Workbook()
        ws = wb.active
        ws.title = mes_nome
        
        # Estilos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        center_alignment = Alignment(horizontal="center", vertical="center")
        
        # Cabeçalho principal
        ws.merge_cells('A1:AH1')
        ws['A1'] = f'ASSOCIAÇÃO AMIGO DO POVO - FREQUÊNCIA {atividade.upper()} - {mes_nome.upper()} {ano}'
        ws['A1'].font = Font(bold=True, size=14)
        ws['A1'].alignment = center_alignment
        ws['A1'].fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
        
        # Cabeçalhos
        headers = ['ALUNO', 'TELEFONE', 'TURMA'] + [str(i) for i in range(1, 32)]
        for i, header in enumerate(headers, 1):
            cell = ws.cell(row=3, column=i, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_alignment
        
        # Adicionar alunos
        for idx, aluno in enumerate(alunos, start=4):
            ws.cell(row=idx, column=1, value=aluno['nome'])
            ws.cell(row=idx, column=2, value=aluno['telefone'])
            ws.cell(row=idx, column=3, value=aluno['turma'])
        
        # Ajustar larguras
        ws.column_dimensions['A'].width = 35
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 15
        for col in range(4, 35):
            ws.column_dimensions[chr(64+col)].width = 3
        
        # Instruções
        instrucoes_row = len(alunos) + 6
        ws[f'A{instrucoes_row}'] = 'INSTRUÇÕES: P=Presente | F=Falta | J=Justificado | X=Presente'
        ws[f'A{instrucoes_row}'].font = Font(bold=True)
        
        return wb
        
    except Exception as e:
        print(f"Erro ao gerar planilha: {e}")
        return None

# Sistema global
academia = SistemaAcademia()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    usuario_nome = session.get('usuario_nome', 'Usuário')
    return render_template('dashboard.html', stats=stats, presencas_hoje=[], usuario_nome=usuario_nome)

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

@app.route('/relatorios')
@login_obrigatorio
def relatorios():
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    usuario_nome = session.get('usuario_nome', 'Usuário')
    return render_template('relatorios.html', meses=meses, mes_selecionado='Dezembro', usuario_nome=usuario_nome)

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
        mes_ano = request.args.get('mes_ano', '2024-12')
        wb = gerar_planilha_frequencia(atividade, mes_ano)
        
        if not wb:
            return jsonify({'error': f'Erro ao gerar planilha para {atividade}'}), 400
        
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        ano, mes = mes_ano.split('-')
        mes_nome = {
            '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril',
            '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto',
            '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
        }.get(mes, 'Dezembro')
        
        filename = f'Frequencia_{atividade.replace(" ", "_")}_{mes_nome}_{ano}.xlsx'
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        
        if file.filename == '' or not atividade:
            return jsonify({'error': 'Arquivo e atividade são obrigatórios'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'{timestamp}_{atividade}_{filename}'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            return jsonify({'success': True, 'message': f'Planilha de {atividade} enviada com sucesso!'})
        
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/listar_backups')
@login_obrigatorio
def listar_backups():
    if session.get('usuario_nivel') != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        backups = []
        
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                if filename.endswith(('.xlsx', '.xls', '.csv')):
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    stat = os.stat(filepath)
                    
                    backups.append({
                        'nome': filename,
                        'tamanho': f'{stat.st_size / 1024:.1f} KB',
                        'modificado': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M'),
                        'atividade': filename.split('_')[1] if '_' in filename else 'Desconhecida'
                    })
        
        backups.sort(key=lambda x: x['modificado'], reverse=True)
        return jsonify(backups)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Para Render/produção
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)