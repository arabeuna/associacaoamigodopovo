# 🏛️ Associação Amigo do Povo - Sistema de Gestão

Sistema completo de gestão para a Associação Amigo do Povo, desenvolvido em Flask com funcionalidades de controle de alunos, presença e backup de planilhas.

## 🚀 Funcionalidades

### 🔐 Sistema de Autenticação
- Login seguro com níveis de usuário (Admin/Usuário)
- Senhas criptografadas com SHA256
- Sessões seguras

### 👥 Gestão de Alunos
- Cadastro completo com endereço, telefone, atividade
- Controle por atividades (Natação, Informática, Fisioterapia, etc.)
- Status inteligente de frequência

### 📊 Sistema de Frequência
- **Geração automática** de planilhas Excel por atividade
- **Download** de planilhas modelo
- **Upload** de planilhas editadas
- **Histórico** de backups organizados

### 📈 Relatórios e Dashboard
- Dashboard com estatísticas em tempo real
- Relatórios mensais detalhados
- Interface responsiva e moderna

## 🛠️ Tecnologias

- **Backend**: Python/Flask
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Dados**: Pandas, OpenPyXL
- **Deploy**: Render.com
- **Segurança**: Sessions, Hash SHA256

## 📋 Atividades Suportadas

- 🏊 Natação
- 💻 Informática  
- 🏥 Fisioterapia
- 💃 Dança
- 🌊 Hidroginástica
- 🏃 Funcional
- 🥋 Karatê
- 🚒 Bombeiro mirim
- 🤸 Capoeira

## 🔑 Credenciais de Acesso

### Administrador
- **Usuário**: `admin`
- **Senha**: `admin123`
- **Permissões**: Acesso total + Backup de planilhas

### Usuário Padrão
- **Usuário**: `usuario`
- **Senha**: `usuario123`
- **Permissões**: Consulta e presença

## 🚀 Deploy

### Render.com (Recomendado)
1. Fork este repositório
2. Conecte sua conta GitHub no Render
3. Criar novo Web Service
4. Usar configurações do `render.yaml`

### Local
```bash
pip install -r requirements.txt
python app.py
```

## 📱 Acesso

- **Local**: http://localhost:5000
- **Produção**: [URL do Render após deploy]

## 👨‍💻 Desenvolvedor

**Arabuenã Peçanha Gomes**  
- GitHub: [@Arabuena](https://github.com/Arabuena)
- Análise e Desenvolvimento de Sistemas

## 📄 Licença

Este projeto foi desenvolvido especificamente para a Associação Amigo do Povo.

---

## 🎯 Como Usar o Sistema de Backup

### 1. Gerar Planilha
- Acesse como **admin**
- Vá em **"Backup Planilhas"**
- Selecione a **atividade**
- Escolha **mês/ano**
- Clique **"Gerar e Baixar"**

### 2. Editar Planilha
- Abra no **Excel**
- Preencha frequências:
  - **P** = Presente
  - **F** = Falta  
  - **J** = Justificado
  - **X** = Presente

### 3. Enviar de Volta
- Selecione a **mesma atividade**
- Faça **upload** do arquivo
- Sistema processa **automaticamente**

## 🔧 Estrutura do Projeto

```
associacaoamigodopovo/
├── app.py                     # Aplicação principal
├── requirements.txt           # Dependências
├── render.yaml               # Configuração Render
├── templates/                # Templates HTML
│   ├── base.html            # Template base
│   ├── splash.html          # Tela inicial
│   ├── login.html           # Login
│   ├── dashboard.html       # Dashboard
│   ├── alunos.html          # Lista de alunos
│   ├── presenca.html        # Controle presença
│   ├── relatorios.html      # Relatórios
│   └── backup_planilhas.html # Backup sistema
├── uploads/                  # Arquivos enviados
└── outros/                  # Dados originais
```

---

**Sistema desenvolvido com ❤️ para a Associação Amigo do Povo**