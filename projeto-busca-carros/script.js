// Dados dos veículos (você precisará carregar o CSV)
let dadosVeiculos = [];
let dadosFiltrados = [];
let colunas = [];

// Adiciona campos selecionáveis para comparação
const camposComparacao = [
    'Categoria', 'Marca', 'Modelo', 'Versão', 'Motor', 'Tipo de Propulsão', 'Transmissão', 'Ar Condicionado', 'Direção Assistida', 'Combustível'
    // Adicione mais campos conforme desejar
];

// Inicializa a aplicação quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    // Carrega o CSV 
    fetch('dados_corrigidos.csv')
        .then(response => response.text())
        .then(data => {
            processarCSV(data);
            inicializarFiltros();
            criarSelecaoCampos();
            adicionarEventosSelects();
            pesquisar();
        })
        .catch(error => console.error('Erro ao carregar os dados:', error));
    
    // Botões já têm listeners adicionados acima, apenas movê-los
    // Adicionar eventos aos botões (mantido para garantir compatibilidade, podem ser movidos para dentro do if acima)
    document.getElementById('btnPesquisar').addEventListener('click', pesquisar);
    document.getElementById('btnLimpar').addEventListener('click', limparFiltros);
    
    // Mover botões para o container central
    const botoesContainer = document.getElementById('botoes-centro');
    const btnPesquisar = document.getElementById('btnPesquisar');
    const btnLimpar = document.getElementById('btnLimpar');
    if (botoesContainer && btnPesquisar && btnLimpar) {
        botoesContainer.appendChild(btnPesquisar);
        botoesContainer.appendChild(btnLimpar);
    }

    // Atualiza modelos quando a marca muda
    document.getElementById('marca').addEventListener('change', atualizarModelos);
    document.getElementById('categoria').addEventListener('change', atualizarModelos);
});

// Processa o CSV para um array de objetos
function processarCSV(csv) {
    const linhas = csv.split('\n');
    colunas = linhas[0].split(';').map(col => col.trim());
    
    // Remove aspas e espaços extras das colunas
    colunas = colunas.map(col => col.replace(/"/g, '').trim());
    
    // Remove colunas sem nome ou com "Unnamed"
    colunas = colunas.filter(col => col && !col.includes('Unnamed:'));
    
    // Processa as linhas de dados
    for (let i = 1; i < linhas.length; i++) {
        if (linhas[i].trim() === '') continue;
        
        const valores = linhas[i].split(';');
        const veiculo = {};
        
        // Associa cada valor à sua coluna
        for (let j = 0; j < colunas.length; j++) {
            if (j < valores.length) {
                veiculo[colunas[j]] = valores[j].replace(/"/g, '').trim();
            }
        }
        
        dadosVeiculos.push(veiculo);
    }
    
    console.log('Dados carregados:', dadosVeiculos.length, 'veículos');
}

// Cria checkboxes para seleção dos campos
function criarSelecaoCampos() {
    const container = document.createElement('div');
    container.id = 'selecao-campos';
    container.style.margin = '20px 0';
    camposComparacao.forEach(campo => {
        const label = document.createElement('label');
        label.style.marginRight = '15px';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = campo;
        checkbox.checked = true;
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(' ' + campo));
        container.appendChild(label);
    });
    const resultadosDiv = document.querySelector('.resultados');
    resultadosDiv.parentNode.insertBefore(container, resultadosDiv);
}

// Inicializa os filtros com opções únicas
function inicializarFiltros() {
    const categorias = new Set();
    const marcas = new Set();
    
    dadosVeiculos.forEach(veiculo => {
        if (veiculo['Categoria']) categorias.add(veiculo['Categoria']);
        if (veiculo['Marca']) marcas.add(veiculo['Marca']);
    });
    
    // Carro 1
    const selectCategorias = document.getElementById('categoria');
    categorias.forEach(categoria => {
        const option = document.createElement('option');
        option.value = categoria;
        option.textContent = categoria;
        selectCategorias.appendChild(option);
    });
    
    const selectMarcas = document.getElementById('marca');
    marcas.forEach(marca => {
        const option = document.createElement('option');
        option.value = marca;
        option.textContent = marca;
        selectMarcas.appendChild(option);
    });
    
    atualizarModelos('marca', 'categoria', 'modelo');
    
    // Carro 2
    const selectCategorias2 = document.getElementById('categoria2');
    categorias.forEach(categoria => {
        const option = document.createElement('option');
        option.value = categoria;
        option.textContent = categoria;
        selectCategorias2.appendChild(option);
    });
    
    const selectMarcas2 = document.getElementById('marca2');
    marcas.forEach(marca => {
        const option = document.createElement('option');
        option.value = marca;
        option.textContent = marca;
        selectMarcas2.appendChild(option);
    });
    
    atualizarModelos('marca2', 'categoria2', 'modelo2');
}

// Atualiza modelos para selects dinâmicos
function atualizarModelos(idMarca, idCategoria, idModelo) {
    const marcaSelecionada = document.getElementById(idMarca).value;
    const categoriaSelecionada = document.getElementById(idCategoria).value;
    const modelos = new Set();
    
    dadosVeiculos.forEach(veiculo => {
        const matchMarca = marcaSelecionada === '' || veiculo['Marca'] === marcaSelecionada;
        const matchCategoria = categoriaSelecionada === '' || veiculo['Categoria'] === categoriaSelecionada;
        
        if (matchMarca && matchCategoria) {
            if (veiculo['Modelo']) modelos.add(veiculo['Modelo']);
        }
    });
    
    const selectModelos = document.getElementById(idModelo);
    selectModelos.innerHTML = '<option value="">Todos</option>';
    
    modelos.forEach(modelo => {
        const option = document.createElement('option');
        option.value = modelo;
        option.textContent = modelo;
        selectModelos.appendChild(option);
    });
}

// Pesquisa e monta tabela comparativa
function pesquisar() {
    // Carro 1
    const categoria1 = document.getElementById('categoria').value;
    const marca1 = document.getElementById('marca').value;
    const modelo1 = document.getElementById('modelo').value;
    // Carro 2
    const categoria2 = document.getElementById('categoria2').value;
    const marca2 = document.getElementById('marca2').value;
    const modelo2 = document.getElementById('modelo2').value;
    // Seleção de campos
    const camposSelecionados = Array.from(document.querySelectorAll('#selecao-campos input[type=checkbox]:checked')).map(cb => cb.value);
    // Busca os veículos
    const veiculo1 = dadosVeiculos.find(v => (categoria1 === '' || v['Categoria'] === categoria1) && (marca1 === '' || v['Marca'] === marca1) && (modelo1 === '' || v['Modelo'] === modelo1));
    const veiculo2 = dadosVeiculos.find(v => (categoria2 === '' || v['Categoria'] === categoria2) && (marca2 === '' || v['Marca'] === marca2) && (modelo2 === '' || v['Modelo'] === modelo2));
    // Monta a tabela comparativa
    montarTabelaComparativa(camposSelecionados, veiculo1, veiculo2);
}

function montarTabelaComparativa(campos, v1, v2) {
    const thead = document.querySelector('#tabelaResultados thead');
    const tbody = document.querySelector('#tabelaResultados tbody');
    thead.innerHTML = '';
    tbody.innerHTML = '';
    // Cabeçalhos
    const trHead = document.createElement('tr');
    trHead.innerHTML = `<th>Campo</th><th>${v1 ? (v1['Marca'] + ' ' + v1['Modelo']) : '-'}</th><th>${v2 ? (v2['Marca'] + ' ' + v2['Modelo']) : '-'}</th>`;
    thead.appendChild(trHead);
    // Linhas
    campos.forEach(campo => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${campo}</td><td>${v1 ? (v1[campo] || '-') : '-'}</td><td>${v2 ? (v2[campo] || '-') : '-'}</td>`;
        tbody.appendChild(tr);
    });
}

// Limpa todos os filtros
function limparFiltros() {
    ['categoria','marca','modelo','categoria2','marca2','modelo2'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    pesquisar();
}

// Eventos dinâmicos para selects
function adicionarEventosSelects() {
    [['marca','categoria','modelo'],['marca2','categoria2','modelo2']].forEach(([idMarca, idCategoria, idModelo]) => {
        document.getElementById(idMarca).addEventListener('change', () => atualizarModelos(idMarca, idCategoria, idModelo));
        document.getElementById(idCategoria).addEventListener('change', () => atualizarModelos(idMarca, idCategoria, idModelo));
    });
}
