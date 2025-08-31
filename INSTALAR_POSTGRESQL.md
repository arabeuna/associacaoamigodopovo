# 📥 INSTALAÇÃO DO POSTGRESQL - WINDOWS

## 🎯 **OBJETIVO**
Instalar o PostgreSQL 15 ou 16 no Windows para usar com o sistema Academia Amigo do Povo.

## 📋 **PRÉ-REQUISITOS**
- Windows 10/11
- Acesso de administrador
- Conexão com internet

## 🚀 **PASSO A PASSO**

### **PASSO 1: Download do PostgreSQL**

1. **Acesse o site oficial:**
   ```
   https://www.postgresql.org/download/windows/
   ```

2. **Clique em "Download the installer"**
   - Escolha PostgreSQL 15.4 ou 16.1
   - Baixe o arquivo .exe (exemplo: postgresql-15.4-1-windows-x64.exe)

### **PASSO 2: Instalação**

1. **Execute o instalador como administrador**
   - Clique com botão direito no arquivo .exe
   - Selecione "Executar como administrador"

2. **Configurações de instalação:**
   ```
   ✅ PostgreSQL Server
   ✅ pgAdmin 4 (interface gráfica)
   ✅ Command Line Tools
   ✅ Stack Builder
   ```

3. **Diretório de instalação:**
   ```
   C:\Program Files\PostgreSQL\15\
   ```

4. **Senha do usuário postgres:**
   ```
   admin123
   ```
   ⚠️ **IMPORTANTE:** Use exatamente esta senha!

5. **Porta:**
   ```
   5432
   ```

6. **Locale:**
   ```
   Default locale
   ```

### **PASSO 3: Verificação da Instalação**

Após a instalação, execute:

```powershell
# Verificar se o PostgreSQL está rodando
Get-Service -Name "*postgresql*"

# Testar conexão
psql -U postgres -h localhost
# Digite a senha: admin123
```

### **PASSO 4: Configurar o Sistema**

Execute o script de configuração:

```powershell
# Usar o caminho completo do Python
& "C:\Users\joaoj\AppData\Local\Programs\Python\Python313\python.exe" configurar_postgresql.py
```

## 🔧 **CONFIGURAÇÃO AUTOMÁTICA**

### **Opção 1: Script Batch**
```batch
# Execute o arquivo
.\instalar_postgresql.bat
```

### **Opção 2: Manual**
1. Instale o PostgreSQL seguindo os passos acima
2. Execute: `python configurar_postgresql.py`
3. Execute: `python database_setup.py`
4. Execute: `python app.py`

## ✅ **VERIFICAÇÃO FINAL**

Após a instalação, teste:

```powershell
# Teste completo do banco
& "C:\Users\joaoj\AppData\Local\Programs\Python\Python313\python.exe" testar_postgresql.py
```

## 🛠️ **RESOLUÇÃO DE PROBLEMAS**

### **Erro: "Service not found"**
- Verifique se a instalação foi concluída
- Reinicie o computador
- Execute como administrador

### **Erro: "Port already in use"**
- Verifique se outro PostgreSQL está rodando
- Mude a porta para 5433

### **Erro: "Access denied"**
- Execute como administrador
- Verifique permissões de pasta

## 📊 **ESTRUTURA FINAL**

Após instalação bem-sucedida:

```
✅ PostgreSQL Server (porta 5432)
✅ pgAdmin 4 (interface web)
✅ Banco academia_amigo_povo
✅ Usuário postgres (senha: admin123)
✅ Tabelas criadas
✅ Dados migrados
```

## 🎯 **PRÓXIMOS PASSOS**

1. **Instale o PostgreSQL** seguindo este guia
2. **Execute:** `python configurar_postgresql.py`
3. **Execute:** `python database_setup.py`
4. **Execute:** `python app.py`
5. **Teste:** `python testar_postgresql.py`

---

**✅ PostgreSQL pronto para uso profissional!**
