# 🏋️ COMO USAR O SISTEMA - ACADEMIA AMIGO DO POVO

## 🚀 **INÍCIO RÁPIDO**

### **OPÇÃO 1: Instalação Automática (Recomendado)**
```bash
# Execute o script de instalação
.\instalar_postgresql.bat
```

### **OPÇÃO 2: Instalação Manual**
1. **Instale o PostgreSQL:**
   - Baixe em: https://www.postgresql.org/download/windows/
   - Use senha: `admin123`
   - Porta: `5432`

2. **Configure o sistema:**
   ```bash
   python configurar_postgresql.py
   ```

3. **Execute a migração:**
   ```bash
   python database_setup.py
   ```

4. **Inicie o sistema:**
   ```bash
   python app.py
   ```

## 🌐 **ACESSO AO SISTEMA**

- **URL:** http://127.0.0.1:5000
- **Usuário:** `admin`
- **Senha:** `admin123`

## 📊 **FUNCIONALIDADES PRINCIPAIS**

### **👥 Gestão de Alunos**
- ✅ **Cadastro completo** de alunos
- ✅ **Busca avançada** por nome, atividade, turma
- ✅ **Edição e exclusão** de registros
- ✅ **Fichas individuais** para impressão
- ✅ **Histórico de presenças**

### **📅 Sistema de Presença**
- ✅ **Registro de presenças** por turma
- ✅ **Frequência individual** por aluno
- ✅ **Relatórios de presença** por período
- ✅ **Estatísticas** de frequência

### **🎯 Gestão de Atividades**
- ✅ **Cadastro de atividades** (Musculação, Pilates, etc.)
- ✅ **Gestão de turmas** por atividade
- ✅ **Horários e dias** da semana
- ✅ **Capacidade máxima** por turma

### **👨‍🏫 Gestão de Professores**
- ✅ **Cadastro de professores**
- ✅ **Vinculação** a atividades/turmas
- ✅ **Controle de acesso** por nível
- ✅ **Relatórios** por professor

### **📈 Relatórios e Estatísticas**
- ✅ **Dashboard** com visão geral
- ✅ **Relatórios de presença** por período
- ✅ **Estatísticas** por atividade/turma
- ✅ **Exportação** de dados

## 🔧 **CONFIGURAÇÕES AVANÇADAS**

### **Banco de Dados PostgreSQL**
- **Host:** localhost
- **Porta:** 5432
- **Banco:** academia_amigo_povo
- **Usuário:** postgres
- **Senha:** admin123

### **Arquivos de Configuração**
- `.env` - Configurações do banco
- `config.env.example` - Exemplo de configuração

## 🆘 **SOLUÇÃO DE PROBLEMAS**

### **Erro: "Connection refused"**
```bash
# Verifique se o PostgreSQL está rodando
# Abra "Serviços" do Windows
# Procure por "postgresql-x64-15" e inicie
```

### **Erro: "Database does not exist"**
```bash
# Execute o script de configuração
python configurar_postgresql.py
```

### **Erro: "Module not found"**
```bash
# Instale as dependências
pip install -r requirements.txt
```

### **Dados se perdem ao reiniciar**
- ✅ **Problema resolvido** com PostgreSQL
- ✅ **Dados salvos permanentemente** no banco
- ✅ **Backup automático** configurado

## 📱 **FUNCIONALIDADES MOBILE**

- ✅ **Interface responsiva** para celular
- ✅ **PWA (Progressive Web App)** instalável
- ✅ **Funciona offline** para consultas
- ✅ **Sincronização** automática

## 🔐 **SEGURANÇA**

- ✅ **Login obrigatório** para acesso
- ✅ **Controle de permissões** por nível
- ✅ **Logs de atividades** registrados
- ✅ **Backup automático** dos dados

## 📞 **SUPORTE**

Se encontrar problemas:
1. Verifique se o PostgreSQL está rodando
2. Confirme as credenciais no arquivo `.env`
3. Execute: `python testar_banco.py`
4. Verifique os logs do sistema

---

## 🎯 **PRÓXIMOS PASSOS**

1. **Instale o PostgreSQL** usando o script automático
2. **Configure o banco** com `python configurar_postgresql.py`
3. **Execute a migração** com `python database_setup.py`
4. **Inicie o sistema** com `python app.py`
5. **Acesse** http://127.0.0.1:5000
6. **Faça login** com admin/admin123

**✅ Sistema pronto para uso profissional!**
