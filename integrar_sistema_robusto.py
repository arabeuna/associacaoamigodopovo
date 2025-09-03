#!/usr/bin/env python3
"""
Script para integrar o sistema robusto de banco de dados na aplicação Flask
Substitui as chamadas de cadastro existentes pelo sistema com tratamento de erro avançado
"""

import os
import sys
import re
from typing import List, Tuple

def backup_file(file_path: str) -> str:
    """Cria backup de um arquivo antes de modificá-lo"""
    backup_path = f"{file_path}.backup_robusto"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as original:
            content = original.read()
        
        with open(backup_path, 'w', encoding='utf-8') as backup:
            backup.write(content)
        
        print(f"✅ Backup criado: {backup_path}")
        return backup_path
    
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        raise

def update_app_py() -> bool:
    """Atualiza o app.py para usar o sistema robusto"""
    app_file = 'app.py'
    
    if not os.path.exists(app_file):
        print(f"❌ Arquivo {app_file} não encontrado")
        return False
    
    try:
        # Criar backup
        backup_file(app_file)
        
        # Ler conteúdo atual
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Lista de modificações a fazer
        modifications = [
            # Adicionar import do sistema robusto
            {
                'pattern': r'from database_integration import DatabaseIntegration',
                'replacement': '''from database_integration import DatabaseIntegration
from database_integration_robusto import db_integration_robusto''',
                'description': 'Adicionar import do sistema robusto'
            },
            
            # Substituir chamadas de salvamento de aluno
            {
                'pattern': r'self\.db_integration\.salvar_aluno_db\(([^)]+)\)',
                'replacement': r'db_integration_robusto.salvar_aluno_db_robusto(\1)',
                'description': 'Substituir chamadas de salvamento por versão robusta'
            },
            
            # Adicionar tratamento de resposta robusta
            {
                'pattern': r'(resultado = db_integration_robusto\.salvar_aluno_db_robusto\([^)]+\))\s*\n\s*if resultado:',
                'replacement': '''\1
            
            # Tratamento robusto de resposta
            if resultado.get('success'):
                if resultado.get('method') == 'fallback':
                    flash(f"⚠️ {resultado['message']}", 'warning')
                else:
                    flash('✅ Aluno cadastrado com sucesso!', 'success')
                return redirect(url_for('alunos'))
            else:
                flash(f"❌ {resultado['message']}", 'error')
                return render_template('novo_aluno.html', 
                                     atividades=self.atividades,
                                     turmas=self.turmas,
                                     dados_aluno=dados_aluno)
            
            if False:  # Desabilitar código antigo''',
                'description': 'Adicionar tratamento robusto de resposta'
            }
        ]
        
        # Aplicar modificações
        modified_content = content
        changes_made = 0
        
        for mod in modifications:
            if re.search(mod['pattern'], modified_content):
                modified_content = re.sub(mod['pattern'], mod['replacement'], modified_content)
                changes_made += 1
                print(f"✅ {mod['description']}")
            else:
                print(f"⚠️ Padrão não encontrado: {mod['description']}")
        
        # Se houve mudanças, salvar o arquivo
        if changes_made > 0:
            with open(app_file, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            print(f"✅ {app_file} atualizado com {changes_made} modificações")
            return True
        else:
            print(f"⚠️ Nenhuma modificação foi aplicada em {app_file}")
            return False
    
    except Exception as e:
        print(f"❌ Erro ao atualizar {app_file}: {e}")
        return False

def create_status_endpoint() -> bool:
    """Cria endpoint para monitorar status do sistema robusto"""
    endpoint_code = '''

@app.route('/sistema/status')
@login_required
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

@app.route('/sistema/processar-fallback', methods=['POST'])
@login_required
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
'''
    
    try:
        # Adicionar endpoints ao final do app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se os endpoints já existem
        if '/sistema/status' in content:
            print("⚠️ Endpoints de status já existem")
            return True
        
        # Adicionar antes da última linha (if __name__ == '__main__':)
        if "if __name__ == '__main__':" in content:
            content = content.replace(
                "if __name__ == '__main__':",
                endpoint_code + "\nif __name__ == '__main__':"
            )
        else:
            content += endpoint_code
        
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Endpoints de status adicionados")
        return True
    
    except Exception as e:
        print(f"❌ Erro ao adicionar endpoints: {e}")
        return False

def create_admin_template() -> bool:
    """Cria template para administração do sistema robusto"""
    template_content = '''{% extends "base.html" %}

{% block title %}Sistema - Status{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-12">
            <h2>🔧 Status do Sistema</h2>
            
            <div class="card mb-4">
                <div class="card-header">
                    <h5>📊 Status da Conexão</h5>
                </div>
                <div class="card-body">
                    <div id="status-info">
                        <p>Carregando status...</p>
                    </div>
                    <button class="btn btn-primary" onclick="atualizarStatus()">🔄 Atualizar Status</button>
                </div>
            </div>
            
            <div class="card mb-4">
                <div class="card-header">
                    <h5>💾 Registros Pendentes (Fallback)</h5>
                </div>
                <div class="card-body">
                    <div id="fallback-info">
                        <p>Verificando registros pendentes...</p>
                    </div>
                    <button class="btn btn-success" onclick="processarFallback()" id="btn-processar">⚡ Processar Pendentes</button>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h5>📝 Log de Atividades</h5>
                </div>
                <div class="card-body">
                    <div id="log-atividades" style="height: 300px; overflow-y: auto; background: #f8f9fa; padding: 10px; border-radius: 5px;">
                        <p>Aguardando atividades...</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
let logCount = 0;

function adicionarLog(mensagem, tipo = 'info') {
    const logDiv = document.getElementById('log-atividades');
    const timestamp = new Date().toLocaleTimeString();
    const cor = tipo === 'error' ? 'text-danger' : tipo === 'success' ? 'text-success' : 'text-info';
    
    logDiv.innerHTML += `<div class="${cor}"><small>[${timestamp}]</small> ${mensagem}</div>`;
    logDiv.scrollTop = logDiv.scrollHeight;
    
    logCount++;
    if (logCount > 100) {
        // Limpar logs antigos
        const lines = logDiv.innerHTML.split('</div>');
        logDiv.innerHTML = lines.slice(-50).join('</div>');
        logCount = 50;
    }
}

function atualizarStatus() {
    adicionarLog('🔄 Atualizando status do sistema...');
    
    fetch('/sistema/status')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const status = data.status;
                const statusHtml = `
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Conexão com Banco:</strong> 
                                <span class="badge ${status.database_connected ? 'bg-success' : 'bg-danger'}">
                                    ${status.database_connected ? '✅ Conectado' : '❌ Desconectado'}
                                </span>
                            </p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Registros Pendentes:</strong> 
                                <span class="badge ${status.fallback_records > 0 ? 'bg-warning' : 'bg-success'}">
                                    ${status.fallback_records} registros
                                </span>
                            </p>
                        </div>
                    </div>
                    <p><small><strong>Última verificação:</strong> ${new Date(status.last_check).toLocaleString()}</small></p>
                `;
                
                document.getElementById('status-info').innerHTML = statusHtml;
                
                const fallbackHtml = status.fallback_records > 0 ? 
                    `<div class="alert alert-warning">⚠️ Existem ${status.fallback_records} registros aguardando processamento.</div>` :
                    `<div class="alert alert-success">✅ Nenhum registro pendente.</div>`;
                
                document.getElementById('fallback-info').innerHTML = fallbackHtml;
                
                adicionarLog(`✅ Status atualizado: Banco ${status.database_connected ? 'conectado' : 'desconectado'}, ${status.fallback_records} pendentes`, 'success');
            } else {
                adicionarLog(`❌ Erro ao obter status: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            adicionarLog(`❌ Erro na requisição: ${error.message}`, 'error');
        });
}

function processarFallback() {
    const btn = document.getElementById('btn-processar');
    btn.disabled = true;
    btn.innerHTML = '⏳ Processando...';
    
    adicionarLog('⚡ Iniciando processamento de registros pendentes...');
    
    fetch('/sistema/processar-fallback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const resultado = data.resultado;
            adicionarLog(`✅ Processamento concluído: ${resultado.processed} processados, ${resultado.remaining} restantes`, 'success');
            
            if (resultado.errors && resultado.errors.length > 0) {
                resultado.errors.forEach(error => {
                    adicionarLog(`⚠️ ${error}`, 'error');
                });
            }
            
            // Atualizar status após processamento
            setTimeout(atualizarStatus, 1000);
        } else {
            adicionarLog(`❌ Erro no processamento: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        adicionarLog(`❌ Erro na requisição: ${error.message}`, 'error');
    })
    .finally(() => {
        btn.disabled = false;
        btn.innerHTML = '⚡ Processar Pendentes';
    });
}

// Atualizar status automaticamente a cada 30 segundos
setInterval(atualizarStatus, 30000);

// Carregar status inicial
document.addEventListener('DOMContentLoaded', atualizarStatus);
</script>
{% endblock %}
'''
    
    try:
        template_dir = 'templates'
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)
        
        template_path = os.path.join(template_dir, 'sistema_status.html')
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print(f"✅ Template criado: {template_path}")
        return True
    
    except Exception as e:
        print(f"❌ Erro ao criar template: {e}")
        return False

def main():
    """Função principal de integração"""
    print("🔧 INTEGRAÇÃO DO SISTEMA ROBUSTO")
    print("=" * 50)
    
    try:
        # Verificar se estamos no diretório correto
        if not os.path.exists('app.py'):
            print("❌ app.py não encontrado. Execute este script no diretório do projeto.")
            return False
        
        success_count = 0
        
        # 1. Atualizar app.py
        print("\n1. Atualizando app.py...")
        if update_app_py():
            success_count += 1
        
        # 2. Criar endpoints de status
        print("\n2. Adicionando endpoints de status...")
        if create_status_endpoint():
            success_count += 1
        
        # 3. Criar template de administração
        print("\n3. Criando template de administração...")
        if create_admin_template():
            success_count += 1
        
        print("\n" + "=" * 50)
        if success_count == 3:
            print("🎉 Integração concluída com sucesso!")
            print("\n📋 Próximos passos:")
            print("1. Reinicie a aplicação Flask")
            print("2. Acesse /sistema/status para monitorar o sistema")
            print("3. Teste o cadastro de alunos")
            print("4. Em caso de erro de conexão, os dados serão salvos em fallback")
            return True
        else:
            print(f"⚠️ Integração parcial: {success_count}/3 etapas concluídas")
            return False
    
    except Exception as e:
        print(f"❌ Erro durante integração: {e}")
        return False

if __name__ == "__main__":
    main()