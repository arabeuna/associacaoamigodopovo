# 🔐 Credenciais do Sistema - Academia Amigo do Povo

## 📋 Visão Geral do Sistema de Controle de Acesso

O sistema foi implementado com três níveis hierárquicos de acesso:

### 👑 **ADMIN MASTER** - Controle Total
- **Função**: Controle total do sistema e gerenciamento de colaboradores
- **Permissões**:
  - ✅ Todas as funcionalidades do sistema
  - ✅ Criar, editar e excluir colaboradores
  - ✅ Definir níveis de acesso para outros usuários
  - ✅ Atribuir atividades para professores/usuários
  - ✅ Gerenciar todos os alunos
  - ✅ Acessar todas as funcionalidades administrativas

### 🛡️ **ADMINISTRADOR** - Gestão Geral
- **Função**: Gerenciar sistema exceto colaboradores
- **Permissões**:
  - ✅ Cadastrar, editar e excluir alunos
  - ✅ Ver todos os alunos
  - ✅ Gerar relatórios
  - ✅ Fazer backup de planilhas
  - ✅ Marcar presença de qualquer aluno
  - ❌ Não pode gerenciar colaboradores

### 👨‍🏫 **USUÁRIO/PROFESSOR** - Acesso Restrito
- **Função**: Gerenciar apenas seus próprios alunos
- **Permissões**:
  - ✅ Ver apenas alunos da sua atividade responsável
  - ✅ Marcar presença apenas dos seus alunos
  - ✅ Gerenciar frequência dos seus alunos
  - ❌ Não pode cadastrar novos alunos
  - ❌ Não pode ver alunos de outras atividades
  - ❌ Não pode acessar funcionalidades administrativas

---

## 🔑 Credenciais de Acesso

### 👑 Admin Master (3 contas disponíveis)

**1. Admin Master Principal**
- **Username**: `admin_master`
- **Senha**: `master123`
- **Nome**: Admin Master

**2. Admin Master 2**
- **Username**: `admin_master2`
- **Senha**: `master456`
- **Nome**: Admin Master 2

**3. Admin Master 3**
- **Username**: `admin_master3`
- **Senha**: `master789`
- **Nome**: Admin Master 3

### 🛡️ Administrador

**Administrador Geral**
- **Username**: `admin`
- **Senha**: `admin123`
- **Nome**: Administrador Geral

### 👨‍🏫 Professores/Usuários

**1. Professor de Natação**
- **Username**: `prof_natacao`
- **Senha**: `natacao123`
- **Nome**: Professor de Natação
- **Atividade Responsável**: Natação

**2. Professor de Informática**
- **Username**: `prof_informatica`
- **Senha**: `info123`
- **Nome**: Professor de Informática
- **Atividade Responsável**: Informática

---

## 🚀 Como Usar o Sistema

### 1. Login no Sistema
1. Acesse a página de login
2. Use uma das credenciais acima
3. O sistema redirecionará baseado no seu nível de acesso

### 2. Admin Master - Gerenciamento de Colaboradores
1. Faça login como Admin Master
2. Acesse "Gerenciar Colaboradores" no menu
3. Crie novos colaboradores definindo:
   - Username e senha
   - Nível de acesso (Admin ou Usuário)
   - Atividade responsável (para usuários)
4. Edite ou desative colaboradores conforme necessário

### 3. Administrador - Gestão Geral
1. Faça login como Administrador
2. Acesse todas as funcionalidades exceto gerenciamento de colaboradores
3. Cadastre novos alunos, gere relatórios, faça backups

### 4. Professor/Usuário - Gestão de Alunos
1. Faça login como Professor
2. Veja apenas alunos da sua atividade
3. Marque presença apenas dos seus alunos atribuídos
4. Gerencie frequência restrita aos seus alunos

---

## 🔄 Fluxo de Trabalho Recomendado

### Cenário: Cadastrar um novo professor de Dança

1. **Admin Master acessa o sistema**
   - Login: `admin_master` / `master123`

2. **Cria novo colaborador**
   - Menu → "Gerenciar Colaboradores"
   - Clica em "Novo Colaborador"
   - Preenche dados:
     - Username: `prof_danca`
     - Nome: `Professor de Dança`
     - Senha: `danca123`
     - Nível: `Usuário/Professor`
     - Atividade: `Dança`

3. **Professor pode fazer login**
   - Login: `prof_danca` / `danca123`
   - Verá apenas alunos de Dança
   - Pode marcar presença apenas desses alunos

### Cenário: Professor marcando presença

1. **Professor faz login** (`prof_natacao` / `natacao123`)
2. **Acessa "Presença"**
   - Vê apenas alunos de Natação na lista
   - Seleciona aluno e marca presença
   - Sistema valida se o aluno pertence à sua atividade

3. **Tentativa de acesso negado**
   - Se tentar marcar presença de aluno de outra atividade
   - Sistema retorna erro: "Você só pode marcar presença dos alunos da sua atividade responsável"

---

## 🛡️ Segurança Implementada

### Validações de Acesso
- ✅ Middleware de autenticação em todas as rotas
- ✅ Decorators específicos para cada nível (`@apenas_admin_master`, `@apenas_admin_ou_master`)
- ✅ Validação de permissões em tempo real
- ✅ Filtragem de dados baseada no nível de acesso

### Controle de Dados
- ✅ Usuários veem apenas dados permitidos
- ✅ Professores não podem acessar alunos de outras atividades
- ✅ Senhas armazenadas com hash SHA256
- ✅ Sessões seguras com chaves secretas

### Interface Adaptativa
- ✅ Menus diferentes baseados no nível de acesso
- ✅ Botões de ação mostrados apenas para usuários autorizados
- ✅ Alertas informativos sobre o nível de acesso atual

---

## 📱 Interface por Nível de Acesso

### Admin Master vê:
- Dashboard completo
- Gerenciar Colaboradores
- Todas as funcionalidades administrativas
- Backup de planilhas
- Relatórios completos

### Administrador vê:
- Dashboard completo
- Gestão de alunos (todos)
- Backup de planilhas
- Relatórios completos
- ❌ Sem "Gerenciar Colaboradores"

### Professor/Usuário vê:
- Dashboard básico
- "Meus Alunos" (apenas da sua atividade)
- Marcar presença (apenas seus alunos)
- ❌ Sem funcionalidades administrativas
- ❌ Sem cadastro de novos alunos

---

## 🔧 Configurações Técnicas

### Estrutura de Permissões
```python
PERMISSOES = {
    'admin_master': ['gerenciar_colaboradores', 'todas_funcoes'],
    'admin': ['cadastrar_alunos', 'editar_alunos', 'excluir_alunos', 
              'ver_todos_alunos', 'gerar_relatorios', 'backup_planilhas'],
    'usuario': ['consultar_meus_alunos', 'gerenciar_frequencia_meus_alunos']
}
```

### Arquivo de Usuários
- Dados salvos em: `usuarios_sistema.json`
- Senhas criptografadas com SHA256
- Carregamento automático na inicialização

---

## 🎯 Próximos Passos

### Funcionalidades Futuras
1. **Sistema de notificações** para professores
2. **Relatórios específicos** por atividade para usuários
3. **Dashboard personalizado** para cada nível
4. **Logs de auditoria** para ações administrativas
5. **Sistema de recuperação de senha**

### Melhorias de Segurança
1. **Autenticação de dois fatores**
2. **Política de senhas mais robusta**
3. **Timeout de sessão automático**
4. **Logs de acesso detalhados**

---

> **⚠️ IMPORTANTE**: Esta documentação contém credenciais de demonstração. Em produção, todas as senhas devem ser alteradas e o acesso deve ser restrito adequadamente.

**Sistema desenvolvido para Academia Amigo do Povo**  
*Versão 2.0 - Sistema de Controle de Acesso Implementado*
