// Funcoes para gerenciar atividades

function excluirAtividade(nome) {
    if (confirm('Tem certeza que deseja excluir a atividade "' + nome + '"?')) {
        fetch('/excluir_atividade/' + encodeURIComponent(nome), {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Atividade excluida com sucesso!');
                location.reload();
            } else {
                alert('Erro ao excluir atividade: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao excluir atividade. Tente novamente.');
        });
    }
}

function ativarAtividade(nome) {
    fetch('/ativar_atividade/' + encodeURIComponent(nome), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Atividade ativada com sucesso!');
            location.reload();
        } else {
            alert('Erro ao ativar atividade: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao ativar atividade. Tente novamente.');
    });
}

// Desativar atividade
function desativarAtividade(nome) {
    if (confirm('Deseja desativar a atividade "' + nome + '"?')) {
        fetch('/desativar_atividade/' + encodeURIComponent(nome), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(function(data) {
            if (data.success) {
                alert('Atividade "' + nome + '" desativada com sucesso!');
                location.reload();
            } else {
                alert('Erro ao desativar atividade: ' + data.message);
            }
        })
        .catch(function(error) {
            console.error('Erro:', error);
            alert('Erro ao desativar atividade. Tente novamente.');
        });
    }
}

// Gerenciar turmas da atividade
function gerenciarTurmas(nome) {
    // Redirecionar para gerenciar turmas com filtro da atividade
    window.location.href = '/gerenciar_turmas?atividade=' + encodeURIComponent(nome);
}

// Editar atividade
function editarAtividade(nome) {
    // Buscar dados da atividade via fetch
    fetch('/api/atividade/' + encodeURIComponent(nome))
        .then(response => response.json())
        .then(atividade => {
            if (atividade) {
                document.getElementById('edit_nome_antigo').value = nome;
                document.getElementById('edit_nome_atividade').value = nome;
                document.getElementById('edit_descricao_atividade').value = atividade.descricao || '';
                
                // Definir professor se existir
                var professorSelect = document.getElementById('edit_professor');
                if (atividade.professores_vinculados && atividade.professores_vinculados.length > 0) {
                    professorSelect.value = atividade.professores_vinculados[0];
                } else {
                    professorSelect.value = '';
                }
                
                // Definir status
                var statusSelect = document.getElementById('edit_status');
                statusSelect.value = atividade.ativa ? 'true' : 'false';
            }
            
            var modal = new bootstrap.Modal(document.getElementById('modalEditarAtividade'));
            modal.show();
        })
        .catch(error => {
            console.error('Erro ao buscar atividade:', error);
            alert('Erro ao carregar dados da atividade.');
        });
}

// Ver detalhes da atividade
function verDetalhesAtividade(nome) {
    // Buscar dados da atividade via fetch
    fetch('/api/atividade/' + encodeURIComponent(nome))
        .then(response => response.json())
        .then(atividade => {
            if (!atividade) {
                alert('Atividade nao encontrada.');
                return;
            }
            
            // Criar modal com detalhes da atividade
            var modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Detalhes da Atividade</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Informacoes Basicas</h6>
                                    <p><strong>Nome:</strong> ${atividade.nome}</p>
                                    <p><strong>Descricao:</strong> ${atividade.descricao || 'Nao informado'}</p>
                                    <p><strong>Status:</strong> <span class="badge bg-${atividade.ativa ? 'success' : 'danger'}">${atividade.ativa ? 'Ativa' : 'Inativa'}</span></p>
                                    <p><strong>Data de Criacao:</strong> ${atividade.data_criacao || 'Nao informado'}</p>
                                    <p><strong>Criado por:</strong> ${atividade.criado_por || 'Nao informado'}</p>
                                </div>
                                <div class="col-md-6">
                                    <h6>Estatisticas</h6>
                                    <p><strong>Total de Alunos:</strong> <span class="badge bg-info">${atividade.total_alunos || 0}</span></p>
                                    ${atividade.professores_vinculados && atividade.professores_vinculados.length > 0 ? 
                                        '<h6>Professores Vinculados</h6>' +
                                        '<div class="mb-3">' +
                                            atividade.professores_vinculados.map(prof => `<span class="badge bg-secondary me-1 mb-1">${prof}</span>`).join('') +
                                        '</div>'
                                     : '<p><strong>Professores:</strong> <span class="text-muted">Nenhum professor vinculado</span></p>'}
                                    ${atividade.turmas && atividade.turmas.length > 0 ? 
                                        '<h6>Turmas</h6>' +
                                        '<div class="mb-3">' +
                                            atividade.turmas.map(turma => `<span class="badge bg-primary me-1 mb-1">${turma}</span>`).join('') +
                                        '</div>'
                                     : ''}
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                            <div class="btn-group">
                                ${atividade.ativa ? 
                                    `<button type="button" class="btn btn-warning" onclick="desativarAtividade('${atividade.nome}')" data-bs-dismiss="modal">
                                        <i class="fas fa-pause"></i> Desativar
                                    </button>` :
                                    `<button type="button" class="btn btn-success" onclick="ativarAtividade('${atividade.nome}')" data-bs-dismiss="modal">
                                        <i class="fas fa-play"></i> Ativar
                                    </button>`
                                }
                                <button type="button" class="btn btn-danger" onclick="excluirAtividade('${atividade.nome}')" data-bs-dismiss="modal">
                                    <i class="fas fa-trash"></i> Excluir
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            var bsModal = new bootstrap.Modal(modal);
            bsModal.show();
            
            // Remove modal do DOM quando fechado
            modal.addEventListener('hidden.bs.modal', function() {
                document.body.removeChild(modal);
            });
        })
        .catch(error => {
            console.error('Erro ao buscar atividade:', error);
            alert('Erro ao carregar detalhes da atividade.');
        });
}

// Funcionalidades do Modal de Sincronização
document.addEventListener('DOMContentLoaded', function() {
    const syncCriterio = document.getElementById('sync_criterio');
    const syncAtividadeOrigem = document.getElementById('sync_atividade_origem');
    const syncAtividadeOrigemContainer = document.getElementById('sync_atividade_origem_container');
    const syncAlunosContainer = document.getElementById('sync_alunos_container');
    const syncFiltrosContainer = document.getElementById('sync_filtros_container');
    const syncListaAlunos = document.getElementById('sync_lista_alunos');
    const formSincronizar = document.getElementById('formSincronizarAtividades');

    // Controlar exibição de campos baseado no critério
    if (syncCriterio) {
        syncCriterio.addEventListener('change', function() {
            const criterio = this.value;
            
            // Resetar containers
            syncAtividadeOrigemContainer.style.display = 'none';
            syncAlunosContainer.style.display = 'none';
            syncFiltrosContainer.style.display = 'none';
            
            if (criterio === 'todos') {
                syncAtividadeOrigemContainer.style.display = 'block';
            } else if (criterio === 'selecionados') {
                syncAtividadeOrigemContainer.style.display = 'block';
                syncAlunosContainer.style.display = 'block';
            } else if (criterio === 'filtro') {
                syncFiltrosContainer.style.display = 'block';
            }
        });
    }

    // Carregar alunos quando atividade de origem for selecionada
    if (syncAtividadeOrigem) {
        syncAtividadeOrigem.addEventListener('change', function() {
            const atividade = this.value;
            if (atividade && syncCriterio.value === 'selecionados') {
                carregarAlunosAtividade(atividade);
            }
        });
    }

    // Submissão do formulário
    if (formSincronizar) {
        formSincronizar.addEventListener('submit', function(e) {
            e.preventDefault();
            sincronizarAtividades();
        });
    }
});

function carregarAlunosAtividade(atividade) {
    const syncListaAlunos = document.getElementById('sync_lista_alunos');
    
    syncListaAlunos.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Carregando alunos...</div>';
    
    fetch(`/listar_alunos_atividade/${encodeURIComponent(atividade)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.alunos.length > 0) {
                let html = '';
                data.alunos.forEach(aluno => {
                    html += `
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" value="${aluno.id}" id="aluno_${aluno.id}">
                            <label class="form-check-label" for="aluno_${aluno.id}">
                                <strong>${aluno.nome}</strong><br>
                                <small class="text-muted">
                                    ${aluno.telefone || 'Sem telefone'} | ${aluno.email || 'Sem email'}
                                    ${aluno.turma ? ` | Turma: ${aluno.turma}` : ''}
                                </small>
                            </label>
                        </div>
                    `;
                });
                
                // Adicionar botão para selecionar todos
                html = `
                    <div class="mb-3">
                        <button type="button" class="btn btn-sm btn-outline-primary" onclick="selecionarTodosAlunos(true)">
                            <i class="fas fa-check-square"></i> Selecionar Todos
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-secondary ms-2" onclick="selecionarTodosAlunos(false)">
                            <i class="fas fa-square"></i> Desmarcar Todos
                        </button>
                    </div>
                    <hr>
                ` + html;
                
                syncListaAlunos.innerHTML = html;
            } else {
                syncListaAlunos.innerHTML = '<p class="text-muted">Nenhum aluno encontrado nesta atividade.</p>';
            }
        })
        .catch(error => {
            console.error('Erro ao carregar alunos:', error);
            syncListaAlunos.innerHTML = '<p class="text-danger">Erro ao carregar alunos. Tente novamente.</p>';
        });
}

function selecionarTodosAlunos(selecionar) {
    const checkboxes = document.querySelectorAll('#sync_lista_alunos input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = selecionar;
    });
}

function sincronizarAtividades() {
    const form = document.getElementById('formSincronizarAtividades');
    const formData = new FormData(form);
    
    const data = {
        criterio: formData.get('criterio'),
        atividade_destino: formData.get('atividade_destino'),
        atividade_origem: formData.get('atividade_origem') || null
    };
    
    // Adicionar dados específicos baseado no critério
    if (data.criterio === 'selecionados') {
        const alunosSelecionados = [];
        const checkboxes = document.querySelectorAll('#sync_lista_alunos input[type="checkbox"]:checked');
        checkboxes.forEach(checkbox => {
            alunosSelecionados.push(checkbox.value);
        });
        
        if (alunosSelecionados.length === 0) {
            alert('Selecione pelo menos um aluno para migrar.');
            return;
        }
        
        data.alunos_selecionados = alunosSelecionados;
    } else if (data.criterio === 'filtro') {
        data.filtros = {
            turma: document.getElementById('sync_filtro_turma').value || null,
            status: document.getElementById('sync_filtro_status').value || null,
            atividade_atual: document.getElementById('sync_filtro_atividade_atual').value || null
        };
    }
    
    // Validações
    if (!data.criterio || !data.atividade_destino) {
        alert('Preencha todos os campos obrigatórios.');
        return;
    }
    
    if ((data.criterio === 'todos' || data.criterio === 'selecionados') && !data.atividade_origem) {
        alert('Selecione a atividade de origem.');
        return;
    }
    
    // Confirmar ação
    let mensagem = `Confirma a migração `;
    if (data.criterio === 'todos') {
        mensagem += `de todos os alunos da atividade "${data.atividade_origem}" para "${data.atividade_destino}"?`;
    } else if (data.criterio === 'selecionados') {
        mensagem += `de ${data.alunos_selecionados.length} aluno(s) selecionado(s) para "${data.atividade_destino}"?`;
    } else {
        mensagem += `dos alunos filtrados para "${data.atividade_destino}"?`;
    }
    
    if (!confirm(mensagem)) {
        return;
    }
    
    // Desabilitar botão e mostrar loading
    const btnSubmit = form.querySelector('button[type="submit"]');
    const originalText = btnSubmit.innerHTML;
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Sincronizando...';
    
    fetch('/sincronizar_atividades', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert(`Sincronização concluída!\n\nMigrados: ${result.migrados}\nErros: ${result.erros}`);
            
            // Fechar modal e recarregar página
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalSincronizarAtividades'));
            modal.hide();
            location.reload();
        } else {
            alert('Erro na sincronização: ' + result.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao sincronizar atividades. Tente novamente.');
    })
    .finally(() => {
        // Restaurar botão
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = originalText;
    });
}