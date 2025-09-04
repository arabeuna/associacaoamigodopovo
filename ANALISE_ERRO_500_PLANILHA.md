# Análise do Erro 500 no Endpoint /processar_planilha

## Problema Identificado
O endpoint `/processar_planilha` está retornando erro 500 (Internal Server Error) quando processa planilhas de cadastro, possivelmente devido a incompatibilidades entre os campos da planilha e o modelo de dados da aplicação.

## Análise do Modelo Aluno

### Campos Obrigatórios (nullable=False)
- `id` - Chave primária (auto-incremento)
- `id_unico` - String(50), único, indexado
- `nome` - String(200), indexado

### Campos Opcionais (nullable=True ou padrão)
- `telefone` - String(20)
- `endereco` - Text
- `email` - String(200)
- `data_nascimento` - Date
- `data_cadastro` - Date (padrão: hoje)
- `titulo_eleitor` - String(20)
- `atividade_id` - Integer (FK)
- `turma_id` - Integer (FK)
- `status_frequencia` - String(200)
- `observacoes` - Text
- `ativo` - Boolean (padrão: True)
- `data_criacao` - DateTime (padrão: agora)
- `criado_por` - String(50)

### Campos Mencionados pelo Usuário que NÃO Existem no Modelo
- `cpf` - **NÃO EXISTE** no modelo Aluno
- `rg` - **NÃO EXISTE** no modelo Aluno
- `id` - Existe, mas é auto-incremento (não deve ser fornecido)

## Análise do Processamento Atual

### Campos Mapeados no `/processar_planilha`
O endpoint mapeia apenas estes campos:
```python
colunas_mapeadas = {
    'nome': ['nome', 'Name', 'NOME', 'name'],
    'telefone': ['telefone', 'Telefone', 'TELEFONE', 'phone', 'celular'],
    'email': ['email', 'Email', 'EMAIL', 'e-mail'],
    'endereco': ['endereco', 'Endereco', 'ENDERECO', 'endereço', 'address'],
    'data_nascimento': ['data_nascimento', 'Data Nascimento', 'nascimento', 'birth_date'],
    'observacoes': ['observacoes', 'Observacoes', 'obs', 'observações']
}
```

### Campos NÃO Mapeados
- `cpf` - Campo comum em planilhas, mas não existe no modelo
- `rg` - Campo comum em planilhas, mas não existe no modelo
- `titulo_eleitor` - Existe no modelo, mas não está sendo mapeado
- `id` - Se presente na planilha, pode causar conflitos

## Possíveis Causas do Erro 500

### 1. Campos Extras na Planilha
- Planilha contém colunas `cpf`, `rg`, `id` que não são processadas
- Sistema pode estar tentando inserir dados em campos inexistentes

### 2. Conflito de ID
- Se a planilha contém coluna `id`, pode haver tentativa de inserir ID manualmente
- IDs duplicados ou inválidos podem causar erro de constraint

### 3. Dados Inválidos
- Formato de data incorreto
- Strings muito longas para os limites do banco
- Valores nulos em campos que deveriam ter dados

### 4. Problema de Encoding
- Caracteres especiais em nomes ou endereços
- Encoding incorreto do arquivo CSV/Excel

## Soluções Propostas

### 1. Expandir Mapeamento de Campos
```python
colunas_mapeadas = {
    'nome': ['nome', 'Name', 'NOME', 'name'],
    'telefone': ['telefone', 'Telefone', 'TELEFONE', 'phone', 'celular'],
    'email': ['email', 'Email', 'EMAIL', 'e-mail'],
    'endereco': ['endereco', 'Endereco', 'ENDERECO', 'endereço', 'address'],
    'data_nascimento': ['data_nascimento', 'Data Nascimento', 'nascimento', 'birth_date'],
    'titulo_eleitor': ['titulo_eleitor', 'Titulo Eleitor', 'TITULO_ELEITOR', 'titulo'],
    'observacoes': ['observacoes', 'Observacoes', 'obs', 'observações']
}
```

### 2. Ignorar Campos Não Mapeados
- Adicionar lógica para ignorar colunas como `cpf`, `rg`, `id`
- Log de aviso para campos não reconhecidos

### 3. Melhorar Tratamento de Erros
- Capturar exceções específicas (IntegrityError, DataError)
- Logs detalhados para debugging
- Retornar erros mais informativos

### 4. Validação de Dados
- Validar formato de datas antes da inserção
- Truncar strings longas automaticamente
- Validar formato de telefone e email

## Próximos Passos
1. Implementar mapeamento para `titulo_eleitor`
2. Adicionar lógica para ignorar campos não mapeados
3. Melhorar logs de erro para diagnóstico
4. Testar com planilha real que contém os campos problemáticos
5. Implementar validação robusta de dados

## Logs Recomendados para Debugging
```python
print(f"Colunas encontradas na planilha: {list(csv_data[0].keys())}")
print(f"Colunas mapeadas: {list(mapeamento_final.keys())}")
print(f"Colunas ignoradas: {set(csv_data[0].keys()) - set(mapeamento_final.values())}")
```