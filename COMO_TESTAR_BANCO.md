# 🧪 COMO TESTAR O BANCO POSTGRESQL

## 🚀 **TESTE RÁPIDO (Recomendado)**

### **Opção 1: Script Automático**
```bash
# Execute o script batch
.\testar_postgresql.bat
```

### **Opção 2: Comando Direto**
```bash
# Execute o script Python
python testar_postgresql.py
```

## 📋 **O QUE O TESTE VERIFICA**

### **✅ 1. Configurações**
- Arquivo `.env` carregado corretamente
- Credenciais do PostgreSQL válidas
- Conexão com o banco estabelecida

### **✅ 2. Estrutura do Banco**
- Tabelas criadas corretamente
- Estrutura das colunas adequada
- Relacionamentos funcionando

### **✅ 3. Dados**
- Contagem de registros por tabela
- Amostra dos dados existentes
- Integridade dos dados

### **✅ 4. Operações**
- Inserção de dados de teste
- Consultas avançadas
- Remoção de dados de teste

### **✅ 5. Performance**
- Consultas por atividade
- Estatísticas de presença
- Relatórios funcionando

## 🔧 **TESTE MANUAL PASSO A PASSO**

### **PASSO 1: Verificar PostgreSQL**
```bash
# Verificar se PostgreSQL está rodando
psql --version

# Conectar ao banco
psql -U postgres -d academia_amigo_povo
```

### **PASSO 2: Verificar Tabelas**
```sql
-- Listar todas as tabelas
\dt

-- Ver estrutura de uma tabela
\d alunos

-- Contar registros
SELECT COUNT(*) FROM alunos;
```

### **PASSO 3: Testar Consultas**
```sql
-- Alunos por atividade
SELECT a.nome, COUNT(al.id) 
FROM atividades a 
LEFT JOIN alunos al ON a.id = al.atividade_id 
GROUP BY a.nome;

-- Presenças recentes
SELECT COUNT(*) 
FROM presencas 
WHERE data_presenca >= CURRENT_DATE - INTERVAL '30 days';
```

### **PASSO 4: Testar Inserção**
```sql
-- Inserir aluno de teste
INSERT INTO alunos (id_unico, nome, telefone, ativo) 
VALUES ('TESTE_001', 'Aluno Teste', '11999999999', true);

-- Verificar inserção
SELECT * FROM alunos WHERE id_unico = 'TESTE_001';

-- Remover teste
DELETE FROM alunos WHERE id_unico = 'TESTE_001';
```

## 📊 **RESULTADOS ESPERADOS**

### **✅ Teste Bem-Sucedido**
```
========================================
    TESTE DO BANCO POSTGRESQL - ACADEMIA AMIGO DO POVO
========================================

✅ Configurações carregadas do arquivo .env

🔗 Conectando ao PostgreSQL...
   Host: localhost:5432
   Usuário: postgres
   Banco: academia_amigo_povo
✅ Conexão estabelecida!
   Versão: PostgreSQL 15.4

📋 Tabelas encontradas no banco:
   - atividades
   - alunos
   - presencas
   - turmas
   - usuarios

📊 ESTATÍSTICAS DO BANCO:
   - atividades: 10 registros
   - alunos: 439 registros
   - presencas: 1250 registros
   - turmas: 32 registros
   - usuarios: 8 registros

🧪 TESTANDO INSERÇÃO DE DADOS:
✅ Dados de teste inseridos com sucesso!
   - Alunos de teste: 1
   - Presenças de teste: 1

🔍 TESTANDO CONSULTAS AVANÇADAS:
   📊 Alunos por atividade:
     - Musculação: 150 alunos
     - Pilates: 89 alunos
     - Natação: 67 alunos

✅ Teste do PostgreSQL concluído com sucesso!
```

### **❌ Problemas Comuns**

#### **Erro: "Connection refused"**
```
❌ Erro na conexão: connection to server at "localhost" (::1), port 5432 failed
```
**Solução:**
1. Verifique se PostgreSQL está rodando
2. Abra "Serviços" do Windows
3. Procure por "postgresql-x64-15" e inicie

#### **Erro: "Database does not exist"**
```
❌ Erro na conexão: database "academia_amigo_povo" does not exist
```
**Solução:**
1. Execute: `python configurar_postgresql.py`
2. Ou crie manualmente: `CREATE DATABASE academia_amigo_povo;`

#### **Erro: "Authentication failed"**
```
❌ Erro na conexão: authentication failed for user "postgres"
```
**Solução:**
1. Verifique a senha no arquivo `.env`
2. Teste: `psql -U postgres -h localhost`

## 🛠️ **FERRAMENTAS DE TESTE**

### **1. Script Python (`testar_postgresql.py`)**
- Teste completo automatizado
- Verifica estrutura e dados
- Testa operações CRUD
- Executa consultas avançadas

### **2. pgAdmin (Interface Gráfica)**
- Visualização das tabelas
- Editor de consultas SQL
- Monitoramento de performance
- Backup e restauração

### **3. psql (Linha de Comando)**
- Conexão direta ao banco
- Execução de comandos SQL
- Scripts automatizados
- Debugging avançado

## 📈 **MÉTRICAS DE PERFORMANCE**

### **Consultas Rápidas (< 1 segundo)**
- Contagem de registros
- Busca por ID único
- Filtros simples

### **Consultas Médias (1-5 segundos)**
- JOINs entre tabelas
- Agregações por período
- Busca por texto

### **Consultas Complexas (5+ segundos)**
- Relatórios completos
- Múltiplos JOINs
- Análises estatísticas

## 🔄 **TESTE CONTÍNUO**

### **Monitoramento Automático**
```bash
# Teste diário (agendar no Windows)
schtasks /create /tn "TestePostgreSQL" /tr "testar_postgresql.bat" /sc daily /st 08:00
```

### **Logs de Teste**
- Resultados salvos em `logs_teste_banco.txt`
- Alertas por email em caso de falha
- Relatórios semanais de performance

---

## 🎯 **PRÓXIMOS PASSOS**

1. **Execute o teste:** `.\testar_postgresql.bat`
2. **Verifique os resultados** acima
3. **Corrija problemas** se houver
4. **Execute novamente** até tudo funcionar
5. **Configure monitoramento** contínuo

**✅ Banco PostgreSQL pronto para uso profissional!**

