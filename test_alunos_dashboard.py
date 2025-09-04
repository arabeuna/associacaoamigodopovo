#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, obter_alunos_usuario

with app.app_context():
    with app.test_request_context():
        from flask import session
        
        # Simular sessão de admin
        session['usuario_logado'] = 'admin'
        session['usuario_nivel'] = 'admin_master'
        
        print("🔍 Testando função obter_alunos_usuario()...")
        
        try:
            alunos = obter_alunos_usuario()
            print(f"✅ Total de alunos encontrados: {len(alunos)}")
            
            if len(alunos) > 0:
                print("\n📋 Primeiros 5 alunos:")
                for i, aluno in enumerate(alunos[:5]):
                    nome = aluno.get('nome', 'N/A')
                    atividade = aluno.get('atividade', 'N/A')
                    data_cadastro = aluno.get('data_cadastro', 'N/A')
                    print(f"{i+1}. {nome} - {atividade} - Cadastrado: {data_cadastro}")
            else:
                print("❌ Nenhum aluno encontrado!")
                
        except Exception as e:
            print(f"❌ Erro ao obter alunos: {e}")
            import traceback
            traceback.print_exc()