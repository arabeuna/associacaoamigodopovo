#!/usr/bin/env python3
"""
Script para configurar o PostgreSQL da Academia Amigo do Povo
"""
import os
import subprocess
import psycopg2
from dotenv import load_dotenv

def verificar_postgresql_instalado():
    """Verifica se o PostgreSQL está instalado"""
    print("🔍 Verificando instalação do PostgreSQL...")
    
    # Verificar diferentes versões do PostgreSQL
    versoes = ['17', '16', '15', '14']
    
    for versao in versoes:
        # Verificar se o executável existe
        psql_path = f"C:\\Program Files\\PostgreSQL\\{versao}\\bin\\psql.exe"
        if os.path.exists(psql_path):
            print(f"✅ PostgreSQL {versao} encontrado em: {psql_path}")
            return True, versao
        
        # Verificar se está no PATH
        try:
            result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ PostgreSQL encontrado no PATH: {result.stdout.strip()}")
                return True, versao
        except:
            continue
    
    print("❌ PostgreSQL não encontrado no PATH")
    return False, None

def instalar_dependencias():
    """Instala dependências Python necessárias"""
    print("📦 Instalando dependências Python...")
    
    dependencias = [
        'psycopg2-binary',
        'python-dotenv',
        'flask',
        'flask-sqlalchemy'
    ]
    
    for dep in dependencias:
        try:
            subprocess.run(['pip', 'install', dep], check=True, capture_output=True)
            print(f"✅ {dep} instalado")
        except subprocess.CalledProcessError:
            print(f"❌ Erro ao instalar {dep}")
            return False
    
    return True

def testar_conexao_postgresql():
    """Testa conexão com PostgreSQL"""
    print("🔗 Testando conexão com PostgreSQL...")
    
    try:
        # Tentar conectar com senha padrão primeiro
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='postgres',
            database='postgres'
        )
        conn.close()
        print("✅ Conexão estabelecida com senha padrão 'postgres'")
        return True
    except:
        try:
            # Tentar conectar com senha admin123
            conn = psycopg2.connect(
                host='localhost',
                port=5432,
                user='postgres',
                password='admin123',
                database='postgres'
            )
            conn.close()
            print("✅ Conexão estabelecida com senha 'admin123'")
            return True
        except Exception as e:
            print(f"❌ Falha na conexão: {e}")
            return False

def criar_banco_dados():
    """Cria o banco de dados academia_amigo_povo"""
    print("🗄️ Criando banco de dados...")
    
    try:
        # Tentar conectar e criar banco
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='admin123',
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Criar banco se não existir
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='academia_amigo_povo'")
        if not cursor.fetchone():
            cursor.execute("CREATE DATABASE academia_amigo_povo")
            print("✅ Banco de dados criado com sucesso!")
        else:
            print("✅ Banco de dados já existe!")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao criar banco: {e}")
        return False

def criar_arquivo_env():
    """Cria o arquivo .env com as configurações"""
    print("📝 Criando arquivo .env...")
    
    env_content = """# Configurações do PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=admin123
DB_NAME=academia_amigo_povo

# URL do banco de dados
DATABASE_URL=postgresql://postgres:admin123@localhost:5432/academia_amigo_povo

# Configurações da aplicação
SECRET_KEY=associacao_amigo_do_povo_2024_secure_key
FLASK_ENV=development
DEBUG=True
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Arquivo .env criado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar arquivo .env: {e}")
        return False

def configurar_senha_postgres():
    """Configura a senha do usuário postgres"""
    print("🔐 Configurando senha do usuário postgres...")
    
    try:
        # Tentar conectar com senha padrão
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='postgres',
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Alterar senha
        cursor.execute("ALTER USER postgres PASSWORD 'admin123'")
        print("✅ Senha configurada com sucesso!")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ Não foi possível configurar a senha automaticamente: {e}")
        print("   Configure manualmente: ALTER USER postgres PASSWORD 'admin123';")
        return False

def main():
    print("=" * 60)
    print("    CONFIGURAÇÃO DO POSTGRESQL - ACADEMIA AMIGO DO POVO")
    print("=" * 60)
    
    print("\n🔍 Verificando instalação do PostgreSQL...")
    instalado, versao = verificar_postgresql_instalado()
    if not instalado:
        print("\n❌ PostgreSQL não está instalado!")
        print("📥 Baixe e instale o PostgreSQL 17 em: https://www.postgresql.org/download/windows/")
        print("📋 Use a senha: admin123 para o usuário postgres")
        return
    
    print(f"\n✅ PostgreSQL {versao} encontrado!")
    
    print("\n📦 Instalando dependências Python...")
    if not instalar_dependencias():
        print("❌ Falha ao instalar dependências!")
        return
    
    print("\n🔐 Configurando senha do PostgreSQL...")
    configurar_senha_postgres()
    
    print("\n🔗 Testando conexão com PostgreSQL...")
    if not testar_conexao_postgresql():
        print("❌ Falha na conexão com PostgreSQL!")
        print("💡 Verifique se o PostgreSQL está rodando")
        return
    
    print("\n🗄️ Criando banco de dados...")
    if not criar_banco_dados():
        print("❌ Falha ao criar banco de dados!")
        return
    
    print("\n📝 Criando arquivo .env...")
    if not criar_arquivo_env():
        print("❌ Falha ao criar arquivo .env!")
        return
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    
    print("\n🚀 Próximos passos:")
    print("1. Execute: python database_setup.py")
    print("2. Execute: python app.py")
    print("3. Acesse: http://127.0.0.1:5000")
    
    print("\n📋 Credenciais do sistema:")
    print("   Usuário: admin")
    print("   Senha: admin123")

if __name__ == "__main__":
    main()
