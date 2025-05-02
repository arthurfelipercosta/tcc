// Dados dos veículos (você precisará carregar o CSV)
let dadosVeiculos = [];
let dadosFiltrados = [];
let colunas = [];

// Inicializa a aplicação quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    // Carrega o CSV 
    fetch('dados_corrigidos.csv')
        .then(response => response.text())
        .then(data => {
            processarCSV(data);
            inicializarFiltros();
            montarTabelaVazia();
        })
        .catch(error => console.error('Erro ao carregar os dados:', error));
    
    // Adiciona eventos aos botões
    document.getElementById('btnPesquisar').addEventListener('click', pesquisar);
    document.getElementById('btnLimpar').addEventListener('click', limparFiltros);
    
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

// Inicializa os filtros com opções únicas
function inicializarFiltros() {
    const categorias = new Set();
    const marcas = new Set();
    
    dadosVeiculos.forEach(veiculo => {
        if (veiculo['Categoria']) categorias.add(veiculo['Categoria']);
        if (veiculo['Marca']) marcas.add(veiculo['Marca']);
    });
    
    // Preenche o select de categorias
    const selectCategorias = document.getElementById('categoria');
    categorias.forEach(categoria => {
        const option = document.createElement('option');
        option.value = categoria;
        option.textContent = categoria;
        selectCategorias.appendChild(option);
    });
    
    // Preenche o select de marcas
    const selectMarcas = document.getElementById('marca');
    marcas.forEach(marca => {
        const option = document.createElement('option');
        option.value = marca;
        option.textContent = marca;
        selectMarcas.appendChild(option);
    });
    
    // Inicializa os modelos baseados na marca selecionada
    atualizarModelos();
}

// Atualiza a lista de modelos baseada na marca selecionada
function atualizarModelos() {
    const marcaSelecionada = document.getElementById('marca').value;
    const categoriaSelecionada = document.getElementById('categoria').value;
    const modelos = new Set();
    
    dadosVeiculos.forEach(veiculo => {
        // Agora verifica se atende AMBOS os critérios (marca E categoria)
        const matchMarca = marcaSelecionada === '' || veiculo['Marca'] === marcaSelecionada;
        const matchCategoria = categoriaSelecionada === '' || veiculo['Categoria'] === categoriaSelecionada;
        
        // Só adiciona o modelo se ambas as condições forem atendidas
        if (matchMarca && matchCategoria) {
            if (veiculo['Modelo']) modelos.add(veiculo['Modelo']);
        }
    });
    
    // Preenche o select de modelos
    const selectModelos = document.getElementById('modelo');
    // Limpa as opções atuais
    selectModelos.innerHTML = '<option value="">Todos</option>';
    
    modelos.forEach(modelo => {
        const option = document.createElement('option');
        option.value = modelo;
        option.textContent = modelo;
        selectModelos.appendChild(option);
    });
}

// Configura a tabela com os cabeçalhos
function montarTabelaVazia() {
    const thead = document.querySelector('#tabelaResultados thead tr');
    
    // Limpa os cabeçalhos existentes
    thead.innerHTML = '';
    
    // Adiciona os cabeçalhos das colunas
    colunas.forEach(coluna => {
        const th = document.createElement('th');
        th.textContent = coluna;
        th.addEventListener('click', () => ordenarTabela(coluna));
        thead.appendChild(th);
    });
}

// Pesquisa veículos com os filtros selecionados
function pesquisar() {
    const categoria = document.getElementById('categoria').value;
    const marca = document.getElementById('marca').value;
    const modelo = document.getElementById('modelo').value;
    
    // Filtra os dados
    dadosFiltrados = dadosVeiculos.filter(veiculo => {
        return (categoria === '' || veiculo['Categoria'] === categoria) &&
               (marca === '' || veiculo['Marca'] === marca) &&
               (modelo === '' || veiculo['Modelo'] === modelo);
    });
    
    // Atualiza a tabela com os resultados
    atualizarTabela();
}

// Limpa todos os filtros
function limparFiltros() {
    document.getElementById('categoria').value = '';
    document.getElementById('marca').value = '';
    document.getElementById('modelo').value = '';
    
    // Restaura todos os dados
    dadosFiltrados = [...dadosVeiculos];
    atualizarTabela();
}

// Atualiza a tabela com os resultados filtrados
function atualizarTabela() {
    const tbody = document.querySelector('#tabelaResultados tbody');
    const totalResultados = document.getElementById('totalResultados');
    
    // Limpa a tabela
    tbody.innerHTML = '';
    
    // Atualiza o contador de resultados
    totalResultados.textContent = `${dadosFiltrados.length} veículos encontrados`;
    
    // Adiciona as linhas de resultados
    dadosFiltrados.forEach(veiculo => {
        const tr = document.createElement('tr');
        
        colunas.forEach(coluna => {
            const td = document.createElement('td');
            td.textContent = veiculo[coluna] || '';
            tr.appendChild(td);
        });
        
        tbody.appendChild(tr);
    });
}

// Último estado de ordenação
let ultimaColuna = null;
let ordemAscendente = true;

// Ordena a tabela por uma coluna
function ordenarTabela(coluna) {
    // Inverte a ordem se clicar na mesma coluna
    if (ultimaColuna === coluna) {
        ordemAscendente = !ordemAscendente;
    } else {
        ordemAscendente = true;
    }
    
    ultimaColuna = coluna;
    
    // Ordena os dados
    dadosFiltrados.sort((a, b) => {
        let valorA = a[coluna] || '';
        let valorB = b[coluna] || '';
        
        // Tenta converter para número se possível
        const numA = parseFloat(valorA);
        const numB = parseFloat(valorB);
        
        if (!isNaN(numA) && !isNaN(numB)) {
            return ordemAscendente ? numA - numB : numB - numA;
        }
        
        // Ordenação de texto
        return ordemAscendente 
            ? valorA.localeCompare(valorB, 'pt-BR') 
            : valorB.localeCompare(valorA, 'pt-BR');
    });
    
    // Atualiza os ícones de ordenação
    const headers = document.querySelectorAll('#tabelaResultados th');
    headers.forEach(th => {
        if (th.textContent === coluna) {
            th.classList.remove('ordem-asc', 'ordem-desc');
            th.classList.add(ordemAscendente ? 'ordem-asc' : 'ordem-desc');
        } else {
            th.classList.remove('ordem-asc', 'ordem-desc');
        }
    });
    
    // Atualiza a tabela
    atualizarTabela();
}
