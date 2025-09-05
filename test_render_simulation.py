#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para simular exatamente o ambiente de produção do Render
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente de produção
if os.path.exists('.env.production'):
    load_dotenv('.env.production')
    print("✅ Carregando variáveis de ambiente de produção (.env.production)")
else:
    print("❌ Arquivo .env.production não encontrado")
    sys.exit(1)

print("\n🚀 SIMULAÇÃO DO AMBIENTE RENDER:")
print("="*50)

try:
    # Importar o app Flask
    from app import app
    
    # Criar um cliente de teste
    with app.test_client() as client:
        with client.session_transaction() as sess:
            # Simular sessão de admin diretamente
            sess['usuario_logado'] = 'admin'
            sess['usuario_nome'] = 'Administrador Geral'
            sess['usuario_nivel'] = 'admin'
            print("✅ Sessão de admin configurada")
        
        print("\n🌐 Testando rota /alunos_adaptado...")
        
        # Acessar a rota alunos_adaptado
        response = client.get('/alunos_adaptado')
        
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Rota acessada com sucesso")
            
            # Analisar o conteúdo HTML
            html_content = response.get_data(as_text=True)
            print(f"📏 Tamanho do HTML: {len(html_content)} caracteres")
            
            # Verificar se há dados de alunos no HTML
            if "João Silva" in html_content:
                print("✅ Dados dos alunos estão presentes no HTML")
            elif "Nenhum aluno encontrado" in html_content:
                print("❌ PROBLEMA: HTML mostra 'Nenhum aluno encontrado'")
                print("🔍 Isso indica que a variável 'alunos' está vazia no template")
            else:
                print("⚠️  HTML não contém dados esperados")
                # Procurar por outros indicadores
                if "alunos" in html_content.lower():
                    print("🔍 Palavra 'alunos' encontrada no HTML")
            
            # Verificar contadores
            if "315 alunos" in html_content:
                print("✅ Contador de alunos está correto: 315")
            elif "0 alunos" in html_content:
                print("❌ PROBLEMA: Contador mostra 0 alunos")
            else:
                print("⚠️  Contador de alunos não encontrado ou diferente")
                # Procurar por qualquer número + alunos
                import re
                matches = re.findall(r'(\d+)\s*alunos?', html_content, re.IGNORECASE)
                if matches:
                    print(f"🔍 Contadores encontrados: {matches}")
            
            # Verificar se há tabela de alunos
            if '<table class="table table-hover mb-0" id="alunosTable">' in html_content:
                print("✅ Tabela de alunos está presente")
            else:
                print("❌ PROBLEMA: Tabela de alunos não encontrada")
            
            # Verificar se há linhas de dados na tabela
            if 'class="aluno-row"' in html_content:
                print("✅ Linhas de alunos estão presentes")
                
                # Contar quantas linhas
                count_rows = html_content.count('class="aluno-row"')
                print(f"📊 Número de linhas de alunos encontradas: {count_rows}")
            else:
                print("❌ PROBLEMA: Nenhuma linha de aluno encontrada")
            
            # Verificar estrutura do template
            if "{% for aluno in alunos %}" in html_content:
                print("⚠️  Template não foi processado (código Jinja visível)")
            elif "<tbody>" in html_content:
                print("✅ Template foi processado corretamente")
            
            # Salvar HTML para análise detalhada
            with open('render_simulation_output.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("💾 HTML salvo em render_simulation_output.html")
            
        elif response.status_code == 302:
            print("⚠️  Redirecionamento detectado (possivelmente para login)")
            print(f"🔍 Location: {response.headers.get('Location', 'N/A')}")
        else:
            print(f"❌ ERRO: Status {response.status_code}")
            print(f"🔍 Conteúdo: {response.get_data(as_text=True)[:500]}...")
        
        print("\n🧪 Testando rota /alunos (original)...")
        
        # Comparar com a rota original
        response_original = client.get('/alunos')
        print(f"📊 Status da rota original: {response_original.status_code}")
        
        if response_original.status_code == 200:
            html_original = response_original.get_data(as_text=True)
            print(f"📏 Tamanho do HTML original: {len(html_original)} caracteres")
            
            if "João Silva" in html_original:
                print("✅ Rota original também tem dados dos alunos")
            else:
                print("❌ Rota original também não tem dados")
        
        print("\n🎯 CONCLUSÃO DA SIMULAÇÃO:")
        if response.status_code == 200:
            if "João Silva" in html_content and 'class="aluno-row"' in html_content:
                print("✅ A aplicação está funcionando corretamente localmente")
                print("🔍 O problema deve estar específico do ambiente Render")
                print("💡 Possíveis causas:")
                print("   - Variáveis de ambiente diferentes no Render")
                print("   - Problemas de conectividade com MongoDB Atlas")
                print("   - Cache ou sessão no Render")
                print("   - Timeout na conexão com o banco")
            else:
                print("❌ O problema também ocorre localmente")
                print("🔍 Isso indica um problema na lógica da aplicação")
        else:
            print("❌ Falha na simulação - problema de autenticação ou rota")
    
except Exception as e:
    print(f"❌ ERRO DURANTE A SIMULAÇÃO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)