#!/usr/bin/env python3
"""
Script de inicialização da Academia Amigo do Povo
"""

import subprocess
import sys
import os
import webbrowser
import time

def instalar_dependencias():
    """Instala as dependências necessárias"""
    print("🔧 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        return False

def verificar_arquivos():
    """Verifica se os arquivos necessários existem"""
    arquivos_necessarios = [
        "app.py",
        "outros/Cadastros_Simples_Academia.csv",
        "outros/Presenca_Simples_Academia.csv",
        "templates/base.html",
        "templates/dashboard.html",
        "templates/alunos.html",
        "templates/presenca.html"
    ]
    
    for arquivo in arquivos_necessarios:
        if not os.path.exists(arquivo):
            print(f"❌ Arquivo não encontrado: {arquivo}")
            return False
    
    print("✅ Todos os arquivos necessários estão presentes!")
    return True

def iniciar_aplicacao():
    """Inicia a aplicação Flask"""
    print("\n🚀 Iniciando a Academia Amigo do Povo...")
    print("📱 Acesse: http://localhost:5000")
    print("⏹️ Para parar, pressione Ctrl+C")
    print("-" * 50)
    
    # Aguardar um pouco e abrir o navegador
    def abrir_navegador():
        time.sleep(2)
        webbrowser.open("http://localhost:5000")
    
    import threading
    thread_navegador = threading.Thread(target=abrir_navegador)
    thread_navegador.daemon = True
    thread_navegador.start()
    
    # Executar a aplicação
    try:
        os.system("python app.py")
    except KeyboardInterrupt:
        print("\n👋 Sistema encerrado pelo usuário")

def main():
    print("=" * 50)
    print("   ACADEMIA AMIGO DO POVO - SISTEMA SIMPLES")
    print("=" * 50)
    print()
    
    # Verificar arquivos
    if not verificar_arquivos():
        print("❌ Arquivos necessários não encontrados!")
        input("Pressione Enter para sair...")
        return
    
    # Instalar dependências
    if not instalar_dependencias():
        print("❌ Falha na instalação das dependências!")
        input("Pressione Enter para sair...")
        return
    
    # Iniciar aplicação
    iniciar_aplicacao()

if __name__ == "__main__":
    main()
