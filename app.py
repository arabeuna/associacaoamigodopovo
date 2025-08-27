from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from datetime import datetime
import os
import hashlib

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
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class SistemaAcademia:
    def __init__(self):
        self.alunos_exemplo = self.criar_dados_exemplo()
    
    def criar_dados_exemplo(self):
        """Cria dados de exemplo da Associação Amigo do Povo"""
        atividades = ['Natação', 'Informática', 'Fisioterapia', 'Dança', 'Hidroginástica', 'Funcional', 'Karatê', 'Bombeiro mirim', 'Capoeira']
        
        alunos = []
        for i in range(100):
            alunos.append({
                'nome': f'Aluno da Associação {i+1}',
                'telefone': f'(11) 9999-{i+1:04d}',
                'endereco': f'Rua da Associação, {i+1}',
                'email': f'aluno{i+1}@email.com',
                'data_nascimento': '01/01/2000',
                'data_cadastro': '01/01/2024',
                'atividade': atividades[i % len(atividades)],
                'turma': f'Turma {chr(65 + i % 3)}',
                'status_frequencia': 'Dados disponíveis' if atividades[i % len(atividades)] == 'Informática' else f'Aguardando dados de {atividades[i % len(atividades)]}',
                'observacoes': ''
            })
        
        print(f"✅ {len(alunos)} alunos de exemplo criados")
        return alunos
    
    def get_atividades_disponiveis(self):
        """Lista atividades únicas"""
        atividades = set(aluno['atividade'] for aluno in self.alunos_exemplo)
        return sorted(list(atividades))
    
    def get_alunos_por_atividade(self, atividade):
        """Retorna alunos de uma atividade"""
        return [aluno for aluno in self.alunos_exemplo if aluno['atividade'] == atividade]
    
    def get_estatisticas(self):
        """Estatísticas básicas"""
        return {
            'total_alunos': len(self.alunos_exemplo),
            'presencas_hoje': 25,
            'total_registros': 1250,
            'alunos_ativos': len(self.alunos_exemplo) - 5
        }
    
    def get_alunos(self):
        """Lista todos os alunos"""
        return self.alunos_exemplo

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

@app.route('/novo_aluno')
@login_obrigatorio
def novo_aluno():
    usuario_nome = session.get('usuario_nome', 'Usuário')
    return render_template('novo_aluno.html', usuario_nome=usuario_nome)

@app.route('/marcar_presenca', methods=['POST'])
@login_obrigatorio
def marcar_presenca():
    nome_aluno = request.form.get('nome_aluno')
    return jsonify({'success': True, 'message': f'Presença marcada para {nome_aluno}!'})

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
    nome = request.form.get('nome')
    return jsonify({'success': True, 'message': f'Aluno {nome} será cadastrado'})

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
    
    # Retornar mensagem informativa (sem Excel por enquanto)
    return jsonify({
        'success': True, 
        'message': f'Funcionalidade de planilha para {atividade} será implementada após deploy completo!'
    })

@app.route('/upload_planilha', methods=['POST'])
@login_obrigatorio
def upload_planilha():
    if session.get('usuario_nivel') != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
    
    return jsonify({
        'success': True, 
        'message': 'Upload de planilhas será implementado após deploy completo!'
    })

@app.route('/listar_backups')
@login_obrigatorio
def listar_backups():
    if session.get('usuario_nivel') != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Retornar lista vazia por enquanto
    return jsonify([])

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
    print(f"🌐 Sistema carregado: {len(academia.alunos_exemplo)} alunos")
    app.run(host='0.0.0.0', port=port, debug=True)  # Debug temporário para ver erro