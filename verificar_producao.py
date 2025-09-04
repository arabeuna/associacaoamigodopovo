#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificação - Produção
Verifica se as configurações de produção estão funcionando corretamente
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from datetime import datetime

def verificar_variaveis_ambiente():
    """Verifica se todas as variáveis necessárias estão definidas"""
    print("🔍 VERIFICANDO VARIÁVEIS DE AMBIENTE")
    print("=" * 50)
    
    variaveis_obrigatorias = {
        'DATABASE_URL': 'URL completa do PostgreSQL',
        'DB_HOST': 'Hostname do PostgreSQL',
        'DB_PORT': 'Porta do PostgreSQL',
        'DB_USER': 'Usuário do banco',
        'DB_PASSWORD': 'Senha do banco',
        'DB_NAME': 'Nome do banco',
        'SECRET_KEY': 'Chave secreta da aplicação',
        'FLASK_ENV': 'Ambiente Flask',
        'FLASK_DEBUG': 'Debug Flask'
    }
    
    variaveis_ok = True
    
    for var, descricao in variaveis_obrigatorias.items():
        valor = os.environ.get(var)
        
        if not valor:
            print(f"❌ {var}: NÃO DEFINIDA ({descricao})")
            variaveis_ok = False
        elif valor.startswith('${') and valor.endswith('}'):
            print(f"⚠️  {var}: PLACEHOLDER NÃO SUBSTITUÍDO ({valor})")
            variaveis_ok = False
        else:
            if 'PASSWORD' in var or 'SECRET' in var:
                print(f"✅ {var}: {'*' * 8} ({descricao})")
            else:
                valor_exibir = valor[:30] + '...' if len(valor) > 30 else valor
                print(f"✅ {var}: {valor_exibir} ({descricao})")
    
    return variaveis_ok

def testar_conexao_banco():
    """Testa conexão com o banco de dados"""
    print("\n🔌 TESTANDO CONEXÃO COM BANCO DE DADOS")
    print("=" * 50)
    
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url or database_url.startswith('${'):
        print("❌ DATABASE_URL não está configurada corretamente")
        return False
    
    try:
        print(f"🔗 Conectando ao PostgreSQL...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Testar versão
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Conexão estabelecida com sucesso!")
        print(f"   PostgreSQL: {version.split(',')[0]}")
        
        # Verificar tabelas principais
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('alunos', 'atividades', 'turmas', 'usuarios', 'presencas')
            ORDER BY table_name;
        """)
        
        tabelas = cursor.fetchall()
        print(f"\n📋 Tabelas encontradas ({len(tabelas)}/5):")
        tabelas_esperadas = ['alunos', 'atividades', 'presencas', 'turmas', 'usuarios']
        
        for tabela in tabelas:
            print(f"   ✅ {tabela[0]}")
        
        tabelas_encontradas = [t[0] for t in tabelas]
        tabelas_faltantes = [t for t in tabelas_esperadas if t not in tabelas_encontradas]
        
        if tabelas_faltantes:
            print(f"\n⚠️  Tabelas faltantes: {', '.join(tabelas_faltantes)}")
        
        # Contar registros principais
        print(f"\n📊 Contagem de registros:")
        for tabela in tabelas_encontradas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela[0]};")
                count = cursor.fetchone()[0]
                print(f"   {tabela[0]}: {count} registros")
            except Exception as e:
                print(f"   {tabela[0]}: Erro ao contar - {e}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro de conexão: {e}")
        print("\n💡 Possíveis causas:")
        print("   - Credenciais incorretas")
        print("   - Servidor PostgreSQL indisponível")
        print("   - Firewall bloqueando conexão")
        print("   - URL de conexão malformada")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def verificar_configuracoes_flask():
    """Verifica configurações específicas do Flask"""
    print("\n⚙️ VERIFICANDO CONFIGURAÇÕES FLASK")
    print("=" * 50)
    
    flask_env = os.environ.get('FLASK_ENV')
    flask_debug = os.environ.get('FLASK_DEBUG')
    secret_key = os.environ.get('SECRET_KEY')
    
    config_ok = True
    
    # Verificar ambiente
    if flask_env == 'production':
        print(f"✅ FLASK_ENV: {flask_env} (correto para produção)")
    else:
        print(f"⚠️  FLASK_ENV: {flask_env} (deveria ser 'production')")
        config_ok = False
    
    # Verificar debug
    if flask_debug in ['False', 'false', '0', False]:
        print(f"✅ FLASK_DEBUG: {flask_debug} (correto para produção)")
    else:
        print(f"⚠️  FLASK_DEBUG: {flask_debug} (deveria ser 'False' em produção)")
        config_ok = False
    
    # Verificar chave secreta
    if secret_key and len(secret_key) >= 32:
        print(f"✅ SECRET_KEY: Definida e segura ({len(secret_key)} caracteres)")
    elif secret_key:
        print(f"⚠️  SECRET_KEY: Muito curta ({len(secret_key)} caracteres, recomendado: 32+)")
        config_ok = False
    else:
        print(f"❌ SECRET_KEY: Não definida")
        config_ok = False
    
    return config_ok

def gerar_relatorio_status():
    """Gera relatório final de status"""
    print("\n📋 RELATÓRIO FINAL")
    print("=" * 50)
    
    # Carregar configurações
    if os.path.exists('.env.production'):
        load_dotenv('.env.production', override=True)
        print("✅ Configurações de produção carregadas")
    else:
        load_dotenv()
        print("⚠️  Usando configurações padrão (.env)")
    
    # Executar verificações
    variaveis_ok = verificar_variaveis_ambiente()
    conexao_ok = testar_conexao_banco()
    flask_ok = verificar_configuracoes_flask()
    
    # Status geral
    print("\n🏁 STATUS GERAL")
    print("=" * 50)
    
    if variaveis_ok and conexao_ok and flask_ok:
        print("✅ PRODUÇÃO CONFIGURADA CORRETAMENTE!")
        print("   Todas as verificações passaram")
        print("   Sistema pronto para uso em produção")
        return True
    else:
        print("❌ PROBLEMAS ENCONTRADOS:")
        if not variaveis_ok:
            print("   - Variáveis de ambiente não configuradas")
        if not conexao_ok:
            print("   - Falha na conexão com banco de dados")
        if not flask_ok:
            print("   - Configurações Flask inadequadas para produção")
        
        print("\n💡 Consulte SOLUCAO_ERRO_POSTGRESQL_PRODUCAO.md para correções")
        return False

def main():
    """Função principal"""
    print(f"🔍 VERIFICAÇÃO DE PRODUÇÃO - ACADEMIA AMIGO DO POVO")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        sucesso = gerar_relatorio_status()
        return sucesso
    except Exception as e:
        print(f"❌ Erro durante verificação: {e}")
        return False

if __name__ == "__main__":
    try:
        sucesso = main()
        print("\n" + "=" * 60)
        if sucesso:
            print("🎉 VERIFICAÇÃO CONCLUÍDA COM SUCESSO!")
            sys.exit(0)
        else:
            print("⚠️  VERIFICAÇÃO CONCLUÍDA COM PROBLEMAS")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Verificação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        sys.exit(1)