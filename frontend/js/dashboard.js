// ========================================
// GERENCIADOR DO DASHBOARD
// ========================================

class DashboardManager {
  constructor() {
    this.currentDashboardData = [];
    this.isLoading = false;
  }

  init() {
    this.setupEventListeners();
    this.setDefaultFilters();
  }

  setupEventListeners() {
    // Botão de filtrar
    const filterBtn = document.querySelector('#page-dashboard .btn');
    if (filterBtn && !filterBtn.hasAttribute('data-listener')) {
      filterBtn.addEventListener('click', () => this.carregarDashboard());
      filterBtn.setAttribute('data-listener', 'true');
    }

    // Enter nos campos de filtro
    const anoInput = document.getElementById('filtro-ano');
    if (anoInput && !anoInput.hasAttribute('data-listener')) {
      anoInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') this.carregarDashboard();
      });
      anoInput.setAttribute('data-listener', 'true');
    }
  }

  setDefaultFilters() {
    // Define ano atual
    const anoInput = document.getElementById('filtro-ano');
    if (anoInput && !anoInput.value) {
      anoInput.value = new Date().getFullYear();
    }

    // Define mês atual
    const mesSelect = document.getElementById('filtro-mes');
    if (mesSelect && !mesSelect.value) {
      mesSelect.value = new Date().getMonth() + 1;
      M.FormSelect.init(mesSelect);
    }
  }

  async carregarDashboard() {
    if (this.isLoading) return;

    this.isLoading = true;
    
    try {
      // Coleta filtros
      const filters = this.getFilters();
      
      // Atualiza header da unidade
      this.updateDashboardHeader(filters);
      
      // Mostra loading
      this.showLoading();
      
      // Busca dados
      const lancamentos = await this.fetchLancamentos(filters);
      
      // Renderiza resultados
      this.renderDashboardResults(lancamentos);
      
      window.app.showSuccess('Dashboard atualizado com sucesso!');
      
    } catch (error) {
      window.app.log('error', 'Erro ao carregar dashboard:', error);
      window.app.showError('Erro ao carregar dados do dashboard');
      this.showError();
    } finally {
      this.isLoading = false;
    }
  }

  getFilters() {
    return {
      unidade: document.getElementById('filtro-unidade')?.value || '',
      ano: document.getElementById('filtro-ano')?.value || '',
      mes: document.getElementById('filtro-mes')?.value || ''
    };
  }

  updateDashboardHeader(filters) {
    const headerDiv = document.getElementById('dashboard-header');
    
    if (filters.unidade && window.app.listaUnidades) {
      const unidade = window.app.listaUnidades.find(u => u.id === filters.unidade);
      
      if (unidade) {
        const foto = unidade.foto_url || 'https://via.placeholder.com/80?text=Hospital';
        const mesLabel = window.APP_CONFIG.ConfigUtils.getMonthLabel(filters.mes);
        const periodo = filters.mes ? `${mesLabel}/${filters.ano}` : filters.ano;
        
        headerDiv.innerHTML = `
          <div class="card">
            <div class="card-content">
              <div class="header-content">
                <img src="${foto}" alt="Foto da Unidade" class="hover-scale">
                <div>
                  <h5><strong>${unidade.nome}</strong></h5>
                  <h6 class="grey-text">Período: ${periodo}</h6>
                  <p class="grey-text">Resultados dos indicadores hospitalares</p>
                </div>
              </div>
            </div>
          </div>
        `;
        
        headerDiv.style.display = 'block';
        
        // Anima entrada
        headerDiv.classList.add('animate-fadeInUp');
      }
    } else {
      headerDiv.style.display = 'none';
    }
  }

  showLoading() {
    const resultsDiv = document.getElementById('dashboard-results');
    resultsDiv.innerHTML = `
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

  showError() {
    const resultsDiv = document.getElementById('dashboard-results');
    resultsDiv.innerHTML = `
      <div class="col s12">
        <div class="card">
          <div class="card-content center-align">
            <i class="material-icons large red-text">error_outline</i>
            <h5 class="red-text">Erro ao carregar dados</h5>
            <p class="grey-text">Verifique sua conexão e tente novamente</p>
            <button class="btn waves-effect waves-light" onclick="window.dashboardManager.carregarDashboard()">
              <i class="material-icons left">refresh</i>Tentar Novamente
            </button>
          </div>
        </div>
      </div>
    `;
  }

  async fetchLancamentos(filters) {
    try {
      const params = new URLSearchParams();
      
      if (filters.unidade) params.append('unidade', filters.unidade);
      if (filters.ano) params.append('ano', filters.ano);
      if (filters.mes) params.append('mes', filters.mes);
      
      return await window.app.makeApiCall(`/lancamentos?${params.toString()}`);
      
    } catch (error) {
      // Fallback para dados de exemplo em desenvolvimento
      return this.getMockData(filters);
    }
  }

  getMockData(filters) {
    // Dados de exemplo para desenvolvimento
    return [
      {
        Indicador_Nome: 'Taxa de Mortalidade',
        ID_Unidade: filters.unidade || 'Hospital Central',
        Mes: filters.mes || '10',
        Ano: filters.ano || '2025',
        Valor_Numerador: 2,
        Valor_Denominador: 100,
        resultado: '2.00',
        meta: '<5%',
        status: 'green',
        descricao: 'Percentual de óbitos em relação ao total de internações',
        num_label: 'Número de óbitos',
        den_label: 'Total de internações'
      },
      {
        Indicador_Nome: 'Taxa de Infecção Hospitalar',
        ID_Unidade: filters.unidade || 'Hospital Central',
        Mes: filters.mes || '10',
        Ano: filters.ano || '2025',
        Valor_Numerador: 8,
        Valor_Denominador: 200,
        resultado: '4.00',
        meta: '<3%',
        status: 'yellow',
        descricao: 'Percentual de infecções hospitalares',
        num_label: 'Casos de infecção',
        den_label: 'Total de pacientes'
      }
    ];
  }

  renderDashboardResults(lancamentos) {
    const resultsDiv = document.getElementById('dashboard-results');
    this.currentDashboardData = lancamentos;
    
    if (lancamentos.error) {
      resultsDiv.innerHTML = `
        <div class="col s12">
          <div class="card">
            <div class="card-content center-align">
              <i class="material-icons large red-text">error</i>
              <h5 class="red-text">Erro</h5>
              <p>${lancamentos.error}</p>
            </div>
          </div>
        </div>
      `;
      return;
    }
    
    if (lancamentos.length === 0) {
      resultsDiv.innerHTML = `
        <div class="col s12">
          <div class="card">
            <div class="card-content center-align">
              <i class="material-icons large grey-text">inbox</i>
              <h5 class="grey-text">Nenhum dado encontrado</h5>
              <p class="grey-text">Não há lançamentos para os filtros selecionados</p>
              <a href="#" onclick="navegarPara('lancamento')" class="btn gradient-btn">
                <i class="material-icons left">add</i>Fazer Lançamento
              </a>
            </div>
          </div>
        </div>
      `;
      return;
    }
    
    let tableHtml = `
      <div class="col s12">
        <div class="card">
          <div class="card-content">
            <span class="card-title">
              <i class="material-icons left">analytics</i>
              Resultados dos Indicadores
              <span class="badge new blue" data-badge-caption="indicadores">${lancamentos.length}</span>
            </span>
            
            <div class="responsive-table-wrapper">
              <table class="responsive-table striped highlight">
                <thead>
                  <tr>
                    <th><i class="material-icons tiny">lens</i> Status</th>
                    <th><i class="material-icons tiny">assignment</i> Indicador</th>
                    <th><i class="material-icons tiny">trending_up</i> Resultado</th>
                    <th><i class="material-icons tiny">flag</i> Meta</th>
                    <th><i class="material-icons tiny">business</i> Unidade</th>
                    <th><i class="material-icons tiny">calculate</i> Valores (N/D)</th>
                    <th><i class="material-icons tiny">info</i> Detalhes</th>
                  </tr>
                </thead>
                <tbody>
    `;
    
    lancamentos.forEach((lanc, index) => {
      const resultadoNum = parseFloat(lanc.resultado);
      const resultadoFormatado = !isNaN(resultadoNum) ? `${lanc.resultado}%` : 'N/A';
      
      // Determina a cor do resultado baseado no status
      let resultClass = 'table-result';
      if (lanc.status === 'green') resultClass += ' green-text';
      else if (lanc.status === 'red') resultClass += ' red-text';
      else if (lanc.status === 'yellow') resultClass += ' orange-text';
      
      tableHtml += `
        <tr class="hover-lift">
          <td>
            <span class="status-dot status-${lanc.status}" 
                  title="${this.getStatusLabel(lanc.status)}"></span>
          </td>
          <td>
            <strong>${lanc.Indicador_Nome}</strong>
          </td>
          <td>
            <span class="${resultClass}">${resultadoFormatado}</span>
          </td>
          <td>
            <span class="meta-badge">${lanc.meta}</span>
          </td>
          <td>
            ${lanc.ID_Unidade}
          </td>
          <td>
            <code>${lanc.Valor_Numerador} / ${lanc.Valor_Denominador}</code>
          </td>
          <td>
            <button class="btn-floating btn-small waves-effect waves-light gradient-btn tooltipped" 
                    data-position="top" 
                    data-tooltip="Ver detalhes"
                    onclick="window.dashboardManager.mostrarDetalhes(${index})">
              <i class="material-icons">info_outline</i>
            </button>
          </td>
        </tr>
      `;
    });
    
    tableHtml += `
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    `;
    
    resultsDiv.innerHTML = tableHtml;
    
    // Inicializa tooltips
    M.Tooltip.init(document.querySelectorAll('.tooltipped'));
    
    // Anima entrada
    resultsDiv.classList.add('animate-fadeInUp');
  }

  getStatusLabel(status) {
    const labels = {
      green: 'Adequado - Meta atingida',
      yellow: 'Atenção - Próximo ao limite',
      red: 'Crítico - Meta não atingida',
      gray: 'Sem dados suficientes'
    };
    return labels[status] || 'Status desconhecido';
  }

  mostrarDetalhes(index) {
    const lanc = this.currentDashboardData[index];
    
    if (lanc) {
      // Popula modal
      document.getElementById('dashboard-modal-title').textContent = lanc.Indicador_Nome;
      document.getElementById('dashboard-modal-descricao').textContent = lanc.descricao;
      document.getElementById('dashboard-modal-numerador').textContent = lanc.num_label;
      document.getElementById('dashboard-modal-denominador').textContent = lanc.den_label;
      
      // Abre modal
      const modal = window.app.modalInstances.dashboard;
      if (modal) {
        modal.open();
      }
    }
  }

  exportarDados() {
    if (this.currentDashboardData.length === 0) {
      window.app.showError('Não há dados para exportar');
      return;
    }

    // Implementar exportação para CSV/Excel
    const csv = this.convertToCSV(this.currentDashboardData);
    this.downloadCSV(csv, 'indicadores_dashboard.csv');
  }

  convertToCSV(data) {
    const headers = ['Indicador', 'Resultado', 'Meta', 'Unidade', 'Numerador', 'Denominador'];
    const rows = data.map(item => [
      item.Indicador_Nome,
      item.resultado,
      item.meta,
      item.ID_Unidade,
      item.Valor_Numerador,
      item.Valor_Denominador
    ]);

    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }

  downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', filename);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
}

// Expor globalmente
window.dashboardManager = new DashboardManager();

// Auto-inicializar quando a aplicação estiver pronta
document.addEventListener('DOMContentLoaded', () => {
  if (window.app) {
    window.dashboardManager.init();
  }
});