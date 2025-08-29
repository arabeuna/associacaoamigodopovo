# 🚀 Instalação Rápida - Sistema PostgreSQL

Guia rápido para configurar o sistema de banco de dados PostgreSQL para a Academia Amigo do Povo.

## ⚡ Instalação em 5 Passos

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar PostgreSQL
```bash
# No Windows (se usando XAMPP/WAMP)
# Ou instalar PostgreSQL: https://www.postgresql.org/download/windows/

# No Linux
sudo apt-get install postgresql postgresql-contrib

# No macOS
brew install postgresql
```

### 3. Criar Banco de Dados
```bash
# Conectar ao PostgreSQL
sudo -u postgres psql

# Criar usuário e banco
CREATE USER academia_user WITH PASSWORD 'sua_senha';
CREATE DATABASE academia_amigo_povo OWNER academia_user;
GRANT ALL PRIVILEGES ON DATABASE academia_amigo_povo TO academia_user;
\q
```

### 4. Configurar Variáveis de Ambiente
```bash
# Copiar arquivo de exemplo
cp config.env.example .env

# Editar .env com suas configurações
# DB_USER=academia_user
# DB_PASSWORD=sua_senha
```

### 5. Executar Inicialização
```bash
python init_db.py
```

## ✅ Verificar Instalação

```bash
python test_db.py
```

Se todos os testes passarem, o sistema está pronto!

## 🎯 Próximos Passos

1. **Executar o sistema:**
   ```bash
   python app.py
   ```

2. **Acessar no navegador:**
   ```
   http://localhost:5000
   ```

3. **Fazer login com:**
   - Usuário: `admin_master`
   - Senha: `master123`

## 🔧 Solução de Problemas

### Erro de Conexão
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Testar conexão
psql -h localhost -U academia_user -d academia_amigo_povo
```

### Erro de Dependência
```bash
# Reinstalar dependências
pip install --upgrade -r requirements.txt
```

### Erro de Permissão
```sql
-- No PostgreSQL
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO academia_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO academia_user;
```

## 📞 Suporte

Se encontrar problemas:
1. Verificar logs de erro
2. Consultar `README_POSTGRESQL.md`
3. Executar `python test_db.py` para diagnóstico

---

**Tempo estimado de instalação**: 10-15 minutos  
**Versão**: 1.0  
**Data**: Dezembro 2024
