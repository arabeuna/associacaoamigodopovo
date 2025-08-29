/**
 * FormManager - Implementação de padrão similar ao useMemo para formulários
 * Gerencia estado dos formulários com cache e limpeza baseada em callbacks de sucesso
 */

class FormManager {
    constructor() {
        this.formCache = new Map();
        this.formStates = new Map();
        this.pendingSubmissions = new Set();
    }

    /**
     * useMemo para formulários - cache de dados do formulário
     * @param {string} formId - ID do formulário
     * @param {Function} getFormData - Função para obter dados do formulário
     * @param {Array} dependencies - Dependências para invalidar cache
     * @returns {Object} Dados do formulário em cache
     */
    useFormMemo(formId, getFormData, dependencies = []) {
        const cacheKey = `${formId}_${dependencies.join('_')}`;
        
        // Verificar se já existe cache válido
        if (this.formCache.has(cacheKey)) {
            const cached = this.formCache.get(cacheKey);
            if (Date.now() - cached.timestamp < 300000) { // 5 minutos
                return cached.data;
            }
        }

        // Gerar novos dados
        const formData = getFormData();
        this.formCache.set(cacheKey, {
            data: formData,
            timestamp: Date.now()
        });

        return formData;
    }

    /**
     * Inicializar formulário com cache
     * @param {string} formId - ID do formulário
     * @param {Object} options - Opções de configuração
     */
    initForm(formId, options = {}) {
        const defaultOptions = {
            autoSave: true,
            cacheTimeout: 300000, // 5 minutos
            clearOnSuccess: true,
            validateBeforeSubmit: true,
            ...options
        };

        this.formStates.set(formId, {
            ...defaultOptions,
            isSubmitting: false,
            lastSaved: null,
            originalData: null
        });

        // Configurar auto-save se habilitado
        if (defaultOptions.autoSave) {
            this.setupAutoSave(formId);
        }

        // Configurar validação
        if (defaultOptions.validateBeforeSubmit) {
            this.setupValidation(formId);
        }

        console.log(`FormManager: Formulário ${formId} inicializado`);
    }

    /**
     * Configurar auto-save para formulário
     * @param {string} formId - ID do formulário
     */
    setupAutoSave(formId) {
        const form = document.getElementById(formId);
        if (!form) return;

        let saveTimeout;
        const saveDelay = 2000; // 2 segundos

        form.addEventListener('input', () => {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                this.autoSaveForm(formId);
            }, saveDelay);
        });
    }

    /**
     * Auto-save do formulário
     * @param {string} formId - ID do formulário
     */
    autoSaveForm(formId) {
        const formData = this.getFormData(formId);
        const state = this.formStates.get(formId);
        
        if (state && !state.isSubmitting) {
            // Salvar no cache local
            this.formCache.set(`${formId}_autosave`, {
                data: formData,
                timestamp: Date.now()
            });
            
            state.lastSaved = new Date();
            console.log(`FormManager: Auto-save realizado para ${formId}`);
        }
    }

    /**
     * Configurar validação do formulário
     * @param {string} formId - ID do formulário
     */
    setupValidation(formId) {
        const form = document.getElementById(formId);
        if (!form) return;

        // Adicionar classes de validação
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
        });
    }

    /**
     * Validar campo individual
     * @param {HTMLElement} field - Campo a ser validado
     */
    validateField(field) {
        const value = field.value.trim();
        const isRequired = field.hasAttribute('required');
        const minLength = field.getAttribute('minlength');
        const pattern = field.getAttribute('pattern');

        let isValid = true;
        let errorMessage = '';

        // Validação de campo obrigatório
        if (isRequired && !value) {
            isValid = false;
            errorMessage = 'Este campo é obrigatório';
        }

        // Validação de comprimento mínimo
        if (minLength && value.length < parseInt(minLength)) {
            isValid = false;
            errorMessage = `Mínimo de ${minLength} caracteres`;
        }

        // Validação de padrão
        if (pattern && value && !new RegExp(pattern).test(value)) {
            isValid = false;
            errorMessage = 'Formato inválido';
        }

        // Aplicar classes de validação
        field.classList.remove('is-valid', 'is-invalid');
        field.classList.add(isValid ? 'is-valid' : 'is-invalid');

        // Mostrar/ocultar mensagem de erro
        const errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.textContent = errorMessage;
        }

        return isValid;
    }

    /**
     * Obter dados do formulário
     * @param {string} formId - ID do formulário
     * @returns {Object} Dados do formulário
     */
    getFormData(formId) {
        const form = document.getElementById(formId);
        if (!form) return {};

        const formData = new FormData(form);
        const data = {};

        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        return data;
    }

    /**
     * Validar formulário completo
     * @param {string} formId - ID do formulário
     * @returns {boolean} Se o formulário é válido
     */
    validateForm(formId) {
        const form = document.getElementById(formId);
        if (!form) return false;

        const fields = form.querySelectorAll('input, select, textarea');
        let isValid = true;

        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    /**
     * Submeter formulário com cache e callback
     * @param {string} formId - ID do formulário
     * @param {Object} options - Opções de submissão
     * @returns {Promise} Promise da submissão
     */
    async submitForm(formId, options = {}) {
        const state = this.formStates.get(formId);
        if (!state) {
            throw new Error(`Formulário ${formId} não inicializado`);
        }

        if (state.isSubmitting) {
            throw new Error('Formulário já está sendo submetido');
        }

        // Validar formulário se necessário
        if (state.validateBeforeSubmit && !this.validateForm(formId)) {
            throw new Error('Formulário contém erros de validação');
        }

        state.isSubmitting = true;
        this.pendingSubmissions.add(formId);

        try {
            const formData = this.getFormData(formId);
            
            // Salvar dados originais antes da submissão
            state.originalData = { ...formData };

            // Fazer requisição
            const response = await this.makeRequest(formId, formData, options);

            // Se sucesso e clearOnSuccess habilitado, limpar formulário
            if (response.success && state.clearOnSuccess) {
                this.clearForm(formId);
                console.log(`FormManager: Formulário ${formId} limpo após sucesso`);
            }

            // Limpar cache de auto-save
            this.formCache.delete(`${formId}_autosave`);

            return response;

        } catch (error) {
            console.error(`FormManager: Erro na submissão do formulário ${formId}:`, error);
            throw error;
        } finally {
            state.isSubmitting = false;
            this.pendingSubmissions.delete(formId);
        }
    }

    /**
     * Fazer requisição HTTP
     * @param {string} formId - ID do formulário
     * @param {Object} formData - Dados do formulário
     * @param {Object} options - Opções da requisição
     * @returns {Promise} Promise da resposta
     */
    async makeRequest(formId, formData, options = {}) {
        const defaultOptions = {
            method: 'POST',
            url: `/${formId.replace('form', '').toLowerCase()}`,
            headers: {},
            ...options
        };

        const requestData = new FormData();
        for (let [key, value] of Object.entries(formData)) {
            requestData.append(key, value);
        }

        return new Promise((resolve, reject) => {
            $.ajax({
                url: defaultOptions.url,
                method: defaultOptions.method,
                data: requestData,
                processData: false,
                contentType: false,
                headers: defaultOptions.headers,
                success: function(response) {
                    resolve(response);
                },
                error: function(xhr, status, error) {
                    reject(new Error(`Erro na requisição: ${error}`));
                }
            });
        });
    }

    /**
     * Limpar formulário
     * @param {string} formId - ID do formulário
     */
    clearForm(formId) {
        const form = document.getElementById(formId);
        if (!form) return;

        // Resetar formulário
        form.reset();

        // Limpar classes de validação
        const fields = form.querySelectorAll('input, select, textarea');
        fields.forEach(field => {
            field.classList.remove('is-valid', 'is-invalid');
        });

        // Limpar mensagens de erro
        const errorMessages = form.querySelectorAll('.invalid-feedback');
        errorMessages.forEach(msg => {
            msg.textContent = '';
        });

        // Limpar cache relacionado
        this.clearFormCache(formId);

        console.log(`FormManager: Formulário ${formId} limpo`);
    }

    /**
     * Limpar cache do formulário
     * @param {string} formId - ID do formulário
     */
    clearFormCache(formId) {
        for (let [key] of this.formCache) {
            if (key.startsWith(formId)) {
                this.formCache.delete(key);
            }
        }
    }

    /**
     * Restaurar dados do formulário
     * @param {string} formId - ID do formulário
     */
    restoreFormData(formId) {
        const state = this.formStates.get(formId);
        if (!state || !state.originalData) return;

        const form = document.getElementById(formId);
        if (!form) return;

        // Restaurar dados originais
        for (let [key, value] of Object.entries(state.originalData)) {
            const field = form.querySelector(`[name="${key}"]`);
            if (field) {
                field.value = value;
            }
        }

        console.log(`FormManager: Dados restaurados para ${formId}`);
    }

    /**
     * Verificar se formulário foi modificado
     * @param {string} formId - ID do formulário
     * @returns {boolean} Se foi modificado
     */
    isFormModified(formId) {
        const currentData = this.getFormData(formId);
        const state = this.formStates.get(formId);
        
        if (!state || !state.originalData) return false;

        return JSON.stringify(currentData) !== JSON.stringify(state.originalData);
    }

    /**
     * Obter estatísticas do cache
     * @returns {Object} Estatísticas
     */
    getCacheStats() {
        return {
            totalCached: this.formCache.size,
            pendingSubmissions: this.pendingSubmissions.size,
            activeForms: this.formStates.size
        };
    }
}

// Instância global do FormManager
window.formManager = new FormManager();

// Exemplo de uso:
/*
// Inicializar formulário
formManager.initForm('formCadastro', {
    autoSave: true,
    clearOnSuccess: true,
    validateBeforeSubmit: true
});

// Submeter formulário
formManager.submitForm('formCadastro', {
    url: '/cadastrar_aluno'
}).then(response => {
    if (response.success) {
        console.log('Formulário enviado com sucesso!');
    }
}).catch(error => {
    console.error('Erro ao enviar formulário:', error);
});
*/
