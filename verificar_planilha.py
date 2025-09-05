import csv

with open('uploads/planilha_teste_404_alunos_20250905_084725.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    
print(f'Total de linhas: {len(rows)}')
print('Primeiras 3 linhas:')
for i, row in enumerate(rows[:3]):
    print(f'{i+1}: {row["Nome"]} - {row["Atividade"]}')
    
print('\nÚltimas 3 linhas:')
for i, row in enumerate(rows[-3:]):
    print(f'{len(rows)-2+i}: {row["Nome"]} - {row["Atividade"]}')