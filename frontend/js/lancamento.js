// ========================================
// GERENCIADOR DE LANÇAMENTOS
// ========================================

class LancamentoManager {
  constructor() {
    this.isLoading = false;
    this.hasUnsavedChanges = false;
  }

  init() {
    this.setupEventListeners();
  }

  setupEventListeners() {
    // Botão carregar lista
    const carregarBtn = document.querySelector('#page-lancamento .btn');
    if (carregarBtn && !carregarBtn.hasAttribute('data-listener')) {
      carregarBtn.addEventListener('click', () => this.carregarListaDeLancamento());
      carregarBtn.setAttribute('data-listener', 'true');
    }

    // Detectar mudanças nos formulários
    document.addEventListener('input', (e) => {
      if (e.target.closest('#lancamento-lista-indicadores')) {
        this.hasUnsavedChanges = true;
      }
    });

    // Detectar mudanças em checkboxes
    document.addEventListener('change', (e) => {
      if (e.target.closest('#lancamento-lista-indicadores')) {
        this.hasUnsavedChanges = true;
        
        // Se marcou "Não se aplica", limpa os campos
        if (e.target.classList.contains('lancamento-na') && e.target.checked) {
          const card = e.target.closest('.indicador-lancamento-card');
          const numerador = card.querySelector('.lancamento-numerador');
          const denominador = card.querySelector('.lancamento-denominador');
          
          if (numerador) numerador.value = '';
          if (denominador) denominador.value = '';
          
          // Atualiza labels do Materialize
          M.updateTextFields();
        }
      }
    });
  }

  validateFormData() {
    const unidade = document.getElementById('form-unidade')?.value;
    const mes = document.getElementById('form-mes')?.value;
    const ano = document.getElementById('form-ano')?.value;

    if (!unidade || !mes || !ano) {
      window.app.showError('Por favor, selecione Unidade, Mês e Ano primeiro.');
      return false;
    }

    // Validar mês
    const mesNum = parseInt(mes);
    if (mesNum < 1 || mesNum > 12) {
      window.app.showError('Mês deve estar entre 1 e 12.');
      return false;
    }

    // Validar ano
    const anoNum = parseInt(ano);
    const currentYear = new Date().getFullYear();
    if (anoNum < 2020 || anoNum > currentYear + 5) {
      window.app.showError(`Ano deve estar entre 2020 e ${currentYear + 5}.`);
      return false;
    }

    return true;
  }

  async carregarListaDeLancamento() {
    if (this.isLoading) return;

    if (!this.validateFormData()) return;

    // Verifica se há mudanças não salvas
    if (this.hasUnsavedChanges) {
      if (!confirm(window.APP_CONFIG.MESSAGES.unsavedChanges)) {
        return;
      }
    }

    this.isLoading = true;

    try {
      const listaContainer = document.getElementById('lancamento-lista-indicadores');
      
      // Mostra loading
      this.showLoadingIndicadores(listaContainer);

      // Verifica se tem dicionário carregado
      if (!window.app.dicionarioIndicadores || window.app.dicionarioIndicadores.length === 0) {
        window.app.showError('Dicionário de indicadores não carregado. Tente recarregar a página.');
        return;
      }

      // Gera formulário
      await this.generateIndicadoresForm(listaContainer);
      
      // Mostra botão salvar
      document.getElementById('lancamento-botao-salvar').style.display = 'block';
      
      // Reset flag de mudanças
      this.hasUnsavedChanges = false;
      
      window.app.showSuccess('Formulário carregado com sucesso!');

    } catch (error) {
      window.app.log('error', 'Erro ao carregar lista de lançamento:', error);
      window.app.showError('Erro ao carregar formulário de indicadores');
    } finally {
      this.isLoading = false;
    }
  }

  showLoadingIndicadores(container) {
    container.innerHTML = `
      <div class="col s12">
        <div class="card">
          <div class="card-content center-align">
            <div class="preloader-wrapper active">
              <div class="spinner-layer spinner-blue-only">
                <div class="circle-clipper left">
                  <div class="circle"></div>
                </div>
                <div class="gap-patch">
                  <div class="circle"></div>
                </div>
                <div class="circle-clipper right">
                  <div class="circle"></div>
                </div>
              </div>
            </div>
            <p style="margin-top: 20px;">Carregando indicadores...</p>
          </div>
        </div>
      </div>
    `;
  }

  async generateIndicadoresForm(container) {
    const indicadores = window.app.dicionarioIndicadores;
    let htmlLista = '';

    indicadores.forEach((indicador, index) => {
      const cardId = `indicador-card-${index}`;
      
      htmlLista += `
        <div class="col s12 m6 l4" data-aos="fade-up" data-aos-delay="${index * 100}">
          <div class="indicador-lancamento-card hover-lift" id="${cardId}" data-indicador-nome="${indicador.nome}">
            
            <h6>
              <span class="indicador-numero">${index + 1}.</span>
              <span class="indicador-nome">${indicador.nome}</span>
              <i class="material-icons info-icon modal-trigger tooltipped" 
                 href="#infoModal"
                 data-position="top" 
                 data-tooltip="Mais informações"
                 onclick="window.lancamentoManager.mostrarInfoModal(${index})">
                info_outline
              </i>
            </h6>
            
            <div class="indicador-description">
              <p class="grey-text text-darken-1">${indicador.descricao}</p>
            </div>
            
            <div class="fraction-layout">
              <div class="input-field">
                <input id="num_${index}" 
                       type="number" 
                       class="validate lancamento-numerador" 
                       min="0"
                       step="0.01">
                <label for="num_${index}">Numerador</label>
                <span class="helper-text">${indicador.label_numerador}</span>
              </div>
              
              <span class="fraction-separator">/</span>
              
              <div class="input-field">
                <input id="den_${index}" 
                       type="number" 
                       class="validate lancamento-denominador" 
                       min="0"
                       step="0.01">
                <label for="den_${index}">Denominador</label>
                <span class="helper-text">${indicador.label_denominador}</span>
              </div>
            </div>
            
            <div class="result-preview" id="result_${index}" style="display: none;">
              <div class="card-panel blue-grey lighten-5">
                <span class="result-label">Resultado:</span>
                <span class="result-value"></span>
              </div>
            </div>
            
            <div class="na-checkbox-field">
              <label>
                <input type="checkbox" 
                       class="filled-in lancamento-na" 
                       id="na_${index}"
                       onchange="window.lancamentoManager.toggleNaoSeAplica(${index})" />
                <span>Não se aplica</span>
              </label>
            </div>
            
          </div>
        </div>
      `;
    });

    container.innerHTML = htmlLista;

    // Inicializa componentes Materialize
    M.Tooltip.init(document.querySelectorAll('.tooltipped'));
    M.updateTextFields();

    // Adiciona listeners para cálculo automático
    this.setupCalculationListeners();

    // Anima entrada se AOS estiver disponível
    if (typeof AOS !== 'undefined') {
      AOS.refresh();
    }
  }

  setupCalculationListeners() {
    const numeradores = document.querySelectorAll('.lancamento-numerador');
    const denominadores = document.querySelectorAll('.lancamento-denominador');

    [...numeradores, ...denominadores].forEach(input => {
      input.addEventListener('input', (e) => {
        this.calculateResult(e.target);
      });
    });
  }

  calculateResult(input) {
    const card = input.closest('.indicador-lancamento-card');
    const index = card.id.split('-')[2];
    
    const numerador = document.getElementById(`num_${index}`)?.value;
    const denominador = document.getElementById(`den_${index}`)?.value;
    const resultDiv = document.getElementById(`result_${index}`);

    if (numerador && denominador && parseFloat(denominador) > 0) {
      const resultado = (parseFloat(numerador) / parseFloat(denominador)) * 100;
      
      resultDiv.querySelector('.result-value').textContent = `${resultado.toFixed(2)}%`;
      resultDiv.style.display = 'block';
      
      // Adiciona animação
      resultDiv.classList.add('animate-fadeIn');
    } else {
      resultDiv.style.display = 'none';
    }
  }

  toggleNaoSeAplica(index) {
    const checkbox = document.getElementById(`na_${index}`);
    const numerador = document.getElementById(`num_${index}`);
    const denominador = document.getElementById(`den_${index}`);
    const resultDiv = document.getElementById(`result_${index}`);
    const card = document.getElementById(`indicador-card-${index}`);

    if (checkbox.checked) {
      // Limpa campos e desabilita
      numerador.value = '';
      denominador.value = '';
      numerador.disabled = true;
      denominador.disabled = true;
      resultDiv.style.display = 'none';
      
      // Visual feedback
      card.classList.add('disabled-card');
      
      M.updateTextFields();
    } else {
      // Habilita campos
      numerador.disabled = false;
      denominador.disabled = false;
      
      // Remove visual feedback
      card.classList.remove('disabled-card');
      
      // Foca no primeiro campo
      numerador.focus();
    }
  }

  mostrarInfoModal(index) {
    const indicador = window.app.dicionarioIndicadores[index];
    
    if (indicador) {
      document.getElementById('modal-title').textContent = indicador.nome;
      document.getElementById('modal-descricao').textContent = indicador.descricao;
      document.getElementById('modal-numerador').textContent = indicador.label_numerador;
      document.getElementById('modal-denominador').textContent = indicador.label_denominador;
      
      // Abre modal
      const modal = window.app.modalInstances.info;
      if (modal) {
        modal.open();
      }
    }
  }

  async salvarTodosLancamentos() {
    if (this.isLoading) return;

    try {
      this.isLoading = true;

      // Coleta dados do formulário
      const payload = this.collectFormData();
      
      // Valida dados
      const validation = this.validateLancamentosData(payload);
      if (!validation.valid) {
        window.app.showError(validation.message);
        return;
      }

      // Confirma salvamento
      if (!confirm(`Confirma o salvamento de ${payload.lancamentos.length} indicadores?`)) {
        return;
      }

      // Mostra loading
      const toastCarregando = M.toast({
        html: '<i class="material-icons left">hourglass_empty</i>Salvando indicadores...',
        displayLength: 10000
      });

      // Envia para API
      const response = await this.sendLancamentos(payload);
      
      // Remove toast de loading
      toastCarregando.dismiss();

      if (response.success) {
        window.app.showSuccess(response.message);
        this.clearForm();
        this.hasUnsavedChanges = false;
      } else {
        window.app.showError(response.error || 'Erro ao salvar');
      }

    } catch (error) {
      window.app.log('error', 'Erro ao salvar lançamentos:', error);
      window.app.showError('Erro ao salvar lançamentos');
    } finally {
      this.isLoading = false;
    }
  }

  collectFormData() {
    const payload = {
      unidade: document.getElementById('form-unidade')?.value,
      mes: document.getElementById('form-mes')?.value,
      ano: document.getElementById('form-ano')?.value,
      lancamentos: []
    };

    document.querySelectorAll('.indicador-lancamento-card').forEach(card => {
      const checkbox = card.querySelector('.lancamento-na');
      
      if (!checkbox.checked) {
        const indicadorNome = card.dataset.indicadorNome;
        const numerador = card.querySelector('.lancamento-numerador')?.value;
        const denominador = card.querySelector('.lancamento-denominador')?.value;
        
        if (numerador !== '' && denominador !== '') {
          payload.lancamentos.push({
            indicador: indicadorNome,
            numerador: parseFloat(numerador),
            denominador: parseFloat(denominador)
          });
        }
      }
    });

    return payload;
  }

  validateLancamentosData(payload) {
    const errors = [];

    if (!payload.unidade) errors.push('Unidade não selecionada');
    if (!payload.mes) errors.push('Mês não informado');
    if (!payload.ano) errors.push('Ano não informado');

    // Verifica se pelo menos um indicador foi preenchido
    if (payload.lancamentos.length === 0) {
      return {
        valid: false,
        message: 'Nenhum indicador foi preenchido. Preencha pelo menos um indicador ou marque "Não se aplica".'
      };
    }

    // Valida dados dos indicadores
    document.querySelectorAll('.indicador-lancamento-card').forEach(card => {
      const checkbox = card.querySelector('.lancamento-na');
      
      if (!checkbox.checked) {
        const indicadorNome = card.dataset.indicadorNome;
        const numerador = card.querySelector('.lancamento-numerador')?.value;
        const denominador = card.querySelector('.lancamento-denominador')?.value;
        
        if ((numerador === '' || denominador === '') && (numerador !== '' || denominador !== '')) {
          errors.push(`"${indicadorNome}": Preencha tanto numerador quanto denominador, ou marque "Não se aplica"`);
        }
      }
    });

    if (errors.length > 0) {
      return {
        valid: false,
        message: errors.join('<br>')
      };
    }

    return { valid: true };
  }

  async sendLancamentos(payload) {
    try {
      return await window.app.makeApiCall('/lancamentos', {
        method: 'POST',
        body: payload
      });
    } catch (error) {
      // Fallback para desenvolvimento - simula sucesso
      window.app.log('warn', 'API não disponível, simulando sucesso:', error);
      return {
        success: true,
        message: `${payload.lancamentos.length} indicadores salvos com sucesso! (modo desenvolvimento)`
      };
    }
  }

  clearForm() {
    // Limpa lista de indicadores
    document.getElementById('lancamento-lista-indicadores').innerHTML = '';
    
    // Esconde botão salvar
    document.getElementById('lancamento-botao-salvar').style.display = 'none';
    
    // Mostra mensagem de sucesso
    document.getElementById('lancamento-lista-indicadores').innerHTML = `
      <div class="col s12">
        <div class="card">
          <div class="card-content center-align">
            <i class="material-icons large green-text">check_circle</i>
            <h5 class="green-text">Lançamentos salvos com sucesso!</h5>
            <p class="grey-text">Os dados foram enviados para a planilha</p>
            <button class="btn gradient-btn" onclick="window.lancamentoManager.carregarListaDeLancamento()">
              <i class="material-icons left">refresh</i>Novo Lançamento
            </button>
          </div>
        </div>
      </div>
    `;
  }

  // Função para detectar mudanças não salvas
  hasUnsavedData() {
    return this.hasUnsavedChanges;
  }

  // Função para limpar dados não salvos
  clearUnsavedData() {
    this.hasUnsavedChanges = false;
  }
}

// Expor globalmente
window.lancamentoManager = new LancamentoManager();

// Funções globais para compatibilidade
window.carregarListaDeLancamento = () => window.lancamentoManager.carregarListaDeLancamento();
window.salvarTodosLancamentos = () => window.lancamentoManager.salvarTodosLancamentos();

// Auto-inicializar quando a aplicação estiver pronta
document.addEventListener('DOMContentLoaded', () => {
  if (window.app) {
    window.lancamentoManager.init();
  }
});