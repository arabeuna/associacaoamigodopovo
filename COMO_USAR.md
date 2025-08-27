# 🏋️ Como Usar o Sistema da Academia Amigo do Povo

## 🚀 Inicialização Rápida

### Opção 1: Script Automático (Recomendado)
```bash
python iniciar.py
```

### Opção 2: Windows (Arquivo .bat)
```bash
iniciar.bat
```

### Opção 3: Manual
```bash
pip install -r requirements.txt
python app.py
```

## 📱 Acessando o Sistema

Após iniciar, abra seu navegador e acesse:
**http://localhost:5000**

## 🎯 Funcionalidades Principais

### 📊 Dashboard (Página Inicial)
- **Estatísticas em tempo real**
  - Total de alunos cadastrados
  - Presenças de hoje
  - Total de registros
  - Alunos ativos

- **Presenças do dia**
  - Lista de quem já chegou hoje
  - Horário de cada check-in
  - Observações especiais

- **Ações rápidas**
  - Botão para marcar presença
  - Link para ver alunos
  - Recarregar dados do sistema

### 👥 Alunos
- **Lista completa** de todos os alunos
- **Informações de contato**
  - Telefone (clicável para ligar)
  - Email (clicável para enviar email)
  - Data de cadastro
  - Status (ativo/ex-aluno)

- **Contatos rápidos**
  - Cards com iniciais dos nomes
  - Botões diretos para ligar/enviar email

### ✅ Presença
- **Duas formas de marcar presença:**
  1. **Lista suspensa**: Escolha o nome e clique em "Marcar Presença"
  2. **Botões rápidos**: Clique direto no botão "Check-in" do aluno

- **Recursos especiais:**
  - Relógio em tempo real
  - Confirmação visual de cada presença
  - Data e hora automáticas
  - Feedback imediato

## 📋 Dados do Sistema

### 📂 Planilhas Utilizadas
- `outros/Cadastros_Simples_Academia.csv` - Dados dos alunos
- `outros/Presenca_Simples_Academia.csv` - Registros de presença
- `outros/Dashboard_Simples_Academia.csv` - Configurações do dashboard

### 🔄 Como os Dados Funcionam
- **Leitura automática** das planilhas ao iniciar
- **Salvamento automático** das novas presenças
- **Botão "Recarregar"** para atualizar dados

## 🎨 Interface do Sistema

### 🌈 Design Moderno
- **Cores suaves** e profissionais
- **Ícones intuitivos** para cada função
- **Layout responsivo** (funciona em celular/tablet)
- **Animações sutis** para melhor experiência

### 📱 Navegação Simples
- **Menu superior** sempre visível
- **Botões grandes** e fáceis de clicar
- **Feedback visual** para todas as ações
- **Textos claros** e objetivos

## 💡 Dicas de Uso

### ⚡ Para Marcar Presença Rapidamente
1. Vá na aba "Presença"
2. Use os cartões de "Presença Rápida"
3. Clique no botão "Check-in" do aluno
4. Veja a confirmação instantânea

### 📞 Para Contatar Alunos
1. Vá na aba "Alunos"
2. Clique no telefone para ligar diretamente
3. Clique no email para enviar mensagem
4. Use os "Contatos Rápidos" na parte inferior

### 📊 Para Acompanhar Movimento
1. Use sempre o "Dashboard" como tela inicial
2. Veja quantos alunos vieram hoje
3. Compare com dias anteriores
4. Monitore alunos mais ativos

## 🔧 Personalização

### 📝 Modificar Dados
- Edite os arquivos CSV na pasta `outros/`
- Use Excel, Google Sheets ou qualquer editor CSV
- Clique "Recarregar Dados" após modificações

### 🎨 Alterar Aparência
- Cores e estilos estão em `templates/base.html`
- Modifique as seções `<style>` para personalizar
- Reinicie o sistema para ver mudanças

## ⚠️ Solucionando Problemas

### 🚫 Sistema não inicia
```bash
pip install --upgrade flask pandas
python app.py
```

### 📂 Dados não aparecem
1. Verifique se os arquivos CSV estão na pasta `outros/`
2. Clique em "Recarregar Dados" no dashboard
3. Reinicie o sistema

### 🌐 Não abre no navegador
- Acesse manualmente: http://localhost:5000
- Verifique se nenhum antivírus está bloqueando
- Tente usar outro navegador

## 📱 Uso em Dispositivos

### 💻 Computador/Notebook
- **Recomendado**: Use Chrome, Firefox ou Edge
- **Tela ideal**: Funciona em qualquer resolução
- **Teclado**: Use Tab para navegar entre campos

### 📱 Celular/Tablet
- **Acesse**: http://localhost:5000 (mesmo endereço)
- **Touch**: Botões otimizados para toque
- **Zoom**: Interface se adapta automaticamente

## 🎯 Filosofia do Sistema

Este sistema foi criado para ser:
- **SIMPLES**: Sem complicações desnecessárias
- **RÁPIDO**: Marcar presença em 2 cliques
- **VISUAL**: Interface bonita e moderna
- **PRÁTICO**: Focado no dia-a-dia da academia

## 🚀 Pronto para Usar!

O sistema está 100% funcional. Basta iniciar e começar a usar imediatamente!

**Qualquer dúvida, consulte este manual ou experimente as funcionalidades - elas são bem intuitivas! 😊**
