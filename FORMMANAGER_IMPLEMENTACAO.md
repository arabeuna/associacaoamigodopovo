# FormManager - Implementação com useMemo Pattern

## 📋 Visão Geral

O **FormManager** é uma implementação JavaScript que simula o comportamento do `useMemo` do React para gerenciamento de formulários em aplicações Flask/Jinja2. Ele fornece cache automático de dados, validação em tempo real, auto-save e limpeza baseada em callbacks de sucesso.

## 🎯 Funcionalidades Principais

### 1. **Cache Inteligente (useMemo Pattern)**
- Cache automático de dados do formulário
- Invalidação baseada em dependências
- Timeout configurável (padrão: 5 minutos)

### 2. **Auto-save**
- Salva dados automaticamente a cada 2 segundos
- Preserva dados em caso de perda de conexão
- Cache local para recuperação

### 3. **Validação em Tempo Real**
- Validação automática de campos
- Feedback visual imediato
- Suporte a padrões personalizados

### 4. **Limpeza Inteligente**
- Limpa formulário apenas após sucesso
- Preserva dados em caso de erro
- Restauração de dados do cache

## 🚀 Como Usar

### 1. Incluir o FormManager

```html
<script src="{{ url_for('static', filename='js/formManager.js') }}"></script>
```

### 2. Inicializar um Formulário

```javascript
// Inicializar FormManager com useMemo pattern
formManager.initForm('formCadastro', {
    autoSave: true,           // Auto-save habilitado
    clearOnSuccess: true,     // Limpar após sucesso
    validateBeforeSubmit: true, // Validar antes de enviar
    cacheTimeout: 300000      // 5 minutos de cache
});
```

### 3. Submeter Formulário

```javascript
// Envio tradicional
$('#formCadastro').on('submit', function(e) {
    e.preventDefault();
    
    // Usar FormManager para submeter com cache e callback
    formManager.submitForm('formCadastro', {
        url: '/cadastrar_aluno'
    }).then(response => {
        if (response.success) {
            // Formulário será limpo automaticamente
            console.log('Sucesso!');
        }
    }).catch(error => {
        console.error('Erro:', error);
    });
});
```

## 📁 Estrutura de Arquivos

```
static/
└── js/
    └── formManager.js          # Biblioteca principal

templates/
├── novo_aluno.html            # Formulário de cadastro atualizado
├── gerenciar_atividades.html  # Formulário de atividades atualizado
├── gerenciar_turmas.html      # Formulário de turmas atualizado
├── gerenciar_colaboradores.html # Formulário de colaboradores atualizado
└── form_manager_demo.html     # Página de demonstração

app.py                         # Rotas Flask atualizadas
```

## 🔧 API do FormManager

### Métodos Principais

#### `initForm(formId, options)`
Inicializa um formulário com as opções especificadas.

```javascript
formManager.initForm('formId', {
    autoSave: true,           // Boolean
    clearOnSuccess: true,     // Boolean
    validateBeforeSubmit: true, // Boolean
    cacheTimeout: 300000      // Number (ms)
});
```

#### `submitForm(formId, options)`
Submete um formulário com cache e callback.

```javascript
formManager.submitForm('formId', {
    url: '/endpoint',         // String
    method: 'POST',           // String
    headers: {}               // Object
}).then(response => {
    // Sucesso
}).catch(error => {
    // Erro
});
```

#### `useFormMemo(formId, getFormData, dependencies)`
Implementa o padrão useMemo para cache de dados.

```javascript
const formData = formManager.useFormMemo(
    'formId',
    () => formManager.getFormData('formId'),
    ['dependency1', 'dependency2']
);
```

#### `restoreFormData(formId)`
Restaura dados do cache.

```javascript
formManager.restoreFormData('formId');
```

#### `clearForm(formId)`
Limpa formulário e cache.

```javascript
formManager.clearForm('formId');
```

#### `getCacheStats()`
Retorna estatísticas do cache.

```javascript
const stats = formManager.getCacheStats();
// { totalCached: 5, pendingSubmissions: 0, activeForms: 3 }
```

## 📊 Exemplo de Implementação Completa

### Template HTML

```html
<form id="formCadastro">
    <div class="mb-3">
        <label for="nome" class="form-label">Nome *</label>
        <input type="text" class="form-control" id="nome" name="nome" required minlength="3">
        <div class="invalid-feedback">Nome deve ter pelo menos 3 caracteres</div>
    </div>
    
    <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input type="email" class="form-control" id="email" name="email" pattern="[^\s@]+@[^\s@]+\.[^\s@]+">
        <div class="invalid-feedback">Email inválido</div>
    </div>
    
    <button type="submit" class="btn btn-primary">Enviar</button>
    <button type="button" class="btn btn-outline-info" id="restaurarDados">Restaurar</button>
</form>
```

### JavaScript

```javascript
$(document).ready(function() {
    // Inicializar FormManager
    formManager.initForm('formCadastro', {
        autoSave: true,
        clearOnSuccess: true,
        validateBeforeSubmit: true
    });

    // Envio do formulário
    $('#formCadastro').on('submit', function(e) {
        e.preventDefault();
        
        formManager.submitForm('formCadastro', {
            url: '/cadastrar_aluno'
        }).then(response => {
            if (response.success) {
                $('#feedback').html(
                    '<div class="alert alert-success">Sucesso!</div>'
                );
                // Formulário limpo automaticamente
            }
        }).catch(error => {
            $('#feedback').html(
                '<div class="alert alert-danger">Erro: ' + error.message + '</div>'
            );
        });
    });

    // Restaurar dados
    $('#restaurarDados').on('click', function() {
        formManager.restoreFormData('formCadastro');
    });
});
```

## 🎨 Página de Demonstração

Acesse `/form_manager_demo` para ver o FormManager em ação com:

- Formulário interativo
- Painel de controle em tempo real
- Log de atividades
- Estatísticas do cache
- Botões de teste

## 🔄 Migração de Formulários Existentes

### Antes (Código Tradicional)

```javascript
$('#formCadastro').on('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    $.ajax({
        url: '/cadastrar_aluno',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                $('#formCadastro')[0].reset(); // Limpa sempre
            }
        }
    });
});
```

### Depois (Com FormManager)

```javascript
// Inicializar
formManager.initForm('formCadastro', {
    autoSave: true,
    clearOnSuccess: true
});

// Submeter
$('#formCadastro').on('submit', function(e) {
    e.preventDefault();
    
    formManager.submitForm('formCadastro', {
        url: '/cadastrar_aluno'
    }).then(response => {
        if (response.success) {
            // Limpa automaticamente apenas após sucesso
        }
    });
});
```

## 🎯 Benefícios

### 1. **Experiência do Usuário**
- Dados preservados em caso de erro
- Auto-save automático
- Validação em tempo real
- Feedback visual imediato

### 2. **Desenvolvimento**
- Código mais limpo e organizado
- Reutilização de lógica
- Padrão consistente
- Fácil manutenção

### 3. **Performance**
- Cache inteligente
- Redução de requisições desnecessárias
- Validação otimizada

## 🔧 Configurações Avançadas

### Timeout de Cache

```javascript
formManager.initForm('formId', {
    cacheTimeout: 600000 // 10 minutos
});
```

### Validação Personalizada

```javascript
// Adicionar validação customizada
$('#campo').on('blur', function() {
    const isValid = formManager.validateField(this);
    if (!isValid) {
        // Lógica adicional
    }
});
```

### Auto-save Personalizado

```javascript
formManager.initForm('formId', {
    autoSave: true,
    // Auto-save será executado a cada 2 segundos
});
```

## 🐛 Debug e Monitoramento

### Console Logs

```javascript
// Ver estatísticas
console.log('FormManager Stats:', formManager.getCacheStats());

// Verificar estado do formulário
const state = formManager.formStates.get('formId');
console.log('Form State:', state);
```

### Log de Atividades

A página de demonstração inclui um log em tempo real que mostra:
- Inicialização do FormManager
- Auto-saves realizados
- Submissões de formulário
- Erros e sucessos
- Restaurações de cache

## 📈 Métricas e Estatísticas

O FormManager coleta automaticamente:

- **Total de itens em cache**
- **Submissões pendentes**
- **Formulários ativos**
- **Último auto-save**
- **Tempo de cache**

## 🔮 Próximos Passos

### Melhorias Planejadas

1. **Persistência Local**
   - Salvar cache no localStorage
   - Recuperação após refresh

2. **Sincronização**
   - Sincronizar dados entre abas
   - Detectar conflitos

3. **Analytics**
   - Métricas de uso
   - Relatórios de performance

4. **Plugins**
   - Validação avançada
   - Máscaras automáticas
   - Upload de arquivos

## 📚 Referências

- [React useMemo Hook](https://react.dev/reference/react/useMemo)
- [FormData API](https://developer.mozilla.org/en-US/docs/Web/API/FormData)
- [Bootstrap Validation](https://getbootstrap.com/docs/5.3/forms/validation/)

---

**Desenvolvido para Academia Amigo do Povo**  
*Implementação de padrão useMemo para formulários Flask/Jinja2*
