#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models import SessionLocal, Aluno, Atividade

db = SessionLocal()
try:
    print("🔍 Verificando estrutura dos alunos...")
    
    # Pegar primeiro aluno
    aluno = db.query(Aluno).first()
    if aluno:
        print(f"Aluno: {aluno.nome}")
        print(f"atividade_id: {aluno.atividade_id}")
        print(f"turma_id: {aluno.turma_id}")
        
        # Verificar se existe atividade com esse ID
        if aluno.atividade_id:
            atividade = db.query(Atividade).filter(Atividade.id == aluno.atividade_id).first()
            if atividade:
                print(f"Atividade encontrada: {atividade.nome}")
            else:
                print("❌ Atividade não encontrada para esse ID")
        else:
            print("❌ Aluno sem atividade_id")
    
    # Verificar quantas atividades existem
    total_atividades = db.query(Atividade).count()
    print(f"\n📊 Total de atividades no banco: {total_atividades}")
    
    if total_atividades > 0:
        print("\n📋 Atividades disponíveis:")
        atividades = db.query(Atividade).all()
        for ativ in atividades:
            print(f"- ID: {ativ.id}, Nome: {ativ.nome}, Ativa: {ativ.ativa}")
    
    # Verificar quantos alunos têm atividade_id preenchido
    alunos_com_atividade = db.query(Aluno).filter(Aluno.atividade_id.isnot(None)).count()
    alunos_sem_atividade = db.query(Aluno).filter(Aluno.atividade_id.is_(None)).count()
    
    print(f"\n📊 Alunos com atividade_id: {alunos_com_atividade}")
    print(f"📊 Alunos sem atividade_id: {alunos_sem_atividade}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()