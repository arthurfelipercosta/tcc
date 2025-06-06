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
    
    // Adicionar eventos aos botões (mantido para garantir compatibilidade, podem ser movidos para dentro do if acima)
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

// Cria checkboxes para seleção dos campos
function criarSelecaoCampos() {
    const container = document.getElementById('botoes-centro');
    container.innerHTML = '';
    
    camposComparacao.forEach(campo => {
        const label = document.createElement('label');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = campo;
        checkbox.checked = true;
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(' ' + campo));
        container.appendChild(label);
    });
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

    // Filtra os veículos com base nos critérios (permite campos vazios)
    const resultadosFiltrados1 = dadosVeiculos.filter(veiculo => {
        const matchCategoria = categoria1 === '' || veiculo['Categoria'] === categoria1;
        const matchMarca = marca1 === '' || veiculo['Marca'] === marca1;
        const matchModelo = modelo1 === '' || veiculo['Modelo'] === modelo1;
        return matchCategoria && matchMarca && matchModelo;
    });

     const resultadosFiltrados2 = dadosVeiculos.filter(veiculo => {
        const matchCategoria = categoria2 === '' || veiculo['Categoria'] === categoria2;
        const matchMarca = marca2 === '' || veiculo['Marca'] === marca2;
        const matchModelo = modelo2 === '' || veiculo['Modelo'] === modelo2;
        return matchCategoria && matchMarca && matchModelo;
    });

    // Agrupa os resultados por Marca e Modelo
    const resultadosAgrupados1 = agruparPorMarcaModelo(resultadosFiltrados1);
    const resultadosAgrupados2 = agruparPorMarcaModelo(resultadosFiltrados2);

    // Exibe os resultados agrupados nas listas
    exibirListaResultados(resultadosAgrupados1, 'lista-carro-1');
    exibirListaResultados(resultadosAgrupados2, 'lista-carro-2');

    // Limpa a tabela comparativa ao realizar nova pesquisa
    montarTabelaComparativa([], null, null); 
}

// Nova função para agrupar veículos por Marca e Modelo
function agruparPorMarcaModelo(veiculos) {
    const agrupados = {};
    veiculos.forEach(veiculo => {
        const chave = `${veiculo['Marca']}|${veiculo['Modelo']}`;
        if (!agrupados[chave]) {
            agrupados[chave] = {
                marca: veiculo['Marca'],
                modelo: veiculo['Modelo'],
                versoes: []
            };
        }
        agrupados[chave].versoes.push(veiculo);
    });
    return Object.values(agrupados);
}

// Função para exibir os resultados agrupados em uma lista (scrollview)
function exibirListaResultados(resultadosAgrupados, idLista) {
    const listaContainer = document.querySelector(`#${idLista} .lista-scrollview`);
    listaContainer.innerHTML = ''; // Limpa a lista anterior

    if (resultadosAgrupados.length === 0) {
        listaContainer.innerHTML = '<p>Nenhum carro encontrado.</p>';
        return;
    }

    resultadosAgrupados.forEach(grupo => {
        const itemDiv = document.createElement('div');
        itemDiv.classList.add('lista-item');
        itemDiv.textContent = `${grupo.marca} ${grupo.modelo}`; // Exibe Marca e Modelo únicos
        itemDiv.dataset.marca = grupo.marca; // Armazena a marca
        itemDiv.dataset.modelo = grupo.modelo; // Armazena o modelo

        // Adiciona evento de clique para selecionar o grupo de carros (modelo)
        itemDiv.addEventListener('click', () => selecionarModeloParaVersao(grupo, idLista));

        listaContainer.appendChild(itemDiv);
    });
}

let carroSelecionado1 = null;
let carroSelecionado2 = null;

// Nova função chamada ao selecionar um MODELO da lista
function selecionarModeloParaVersao(grupo, idLista) {
     // Remove a classe 'selecionado' dos itens anteriores na mesma lista
    const listaAnterior = document.querySelector(`#${idLista} .lista-scrollview`);
    listaAnterior.querySelectorAll('.lista-item').forEach(item => {
        item.classList.remove('selecionado');
    });

    // Adiciona a classe 'selecionado' ao item clicado
    const itemClicado = listaAnterior.querySelector(`[data-marca="${grupo.marca}"][data-modelo="${grupo.modelo}"]`);
     if (itemClicado) {
        itemClicado.classList.add('selecionado');
    }

    // --- LÓGICA PARA EXIBIR AS VERSÕES/TRANSMISSÕES --- 
    console.log(`Modelo selecionado para ${idLista}: `, grupo);

    // Exibe a área de seleção de versões
    const versoesSelecaoArea = document.querySelector(`#${idLista} .versoes-selecao`);
    versoesSelecaoArea.style.display = 'block';

    // Preenche a área de versões com as opções disponíveis
    const versoesScrollview = versoesSelecaoArea.querySelector('.versoes-scrollview');
    versoesScrollview.innerHTML = ''; // Limpa a lista anterior

    if (grupo.versoes.length === 0) {
        versoesScrollview.innerHTML = '<p>Nenhuma versão disponível.</p>';
    } else {
        grupo.versoes.forEach(veiculo => {
            const versaoItemDiv = document.createElement('div');
            versaoItemDiv.classList.add('versao-item');
            // Exibe a combinação de Versão e Transmissão (ou outros campos relevantes)
            versaoItemDiv.textContent = `${veiculo['Versão'] || '-'} / ${veiculo['Transmissão'] || '-'}`; 
            // Adiciona evento de clique para selecionar a versão específica
            versaoItemDiv.addEventListener('click', () => selecionarVersaoParaComparacao(veiculo, idLista, versaoItemDiv));
            versoesScrollview.appendChild(versaoItemDiv);
        });
    }

    // Limpamos a seleção de carro específica até que uma versão seja escolhida
     if (idLista === 'lista-carro-1') {
        carroSelecionado1 = null;
    } else {
        carroSelecionado2 = null;
    }

    // Atualiza a tabela comparativa (provavelmente ficará vazia até uma versão ser selecionada)
    const camposSelecionados = Array.from(document.querySelectorAll('#botoes-centro input[type=checkbox]:checked')).map(cb => cb.value);
    montarTabelaComparativa(camposSelecionados, carroSelecionado1, carroSelecionado2);
}

// Função chamada DEPOIS que a versão/transmissão for selecionada
function selecionarVersaoParaComparacao(veiculo, idLista, itemClicado) {
    // Remove a classe 'selecionado-versao' dos itens anteriores na mesma lista de versões
    const versoesScrollview = document.querySelector(`#${idLista} .versoes-selecao .versoes-scrollview`);
    versoesScrollview.querySelectorAll('.versao-item').forEach(item => {
        item.classList.remove('selecionado-versao');
    });

    // Adiciona a classe 'selecionado-versao' ao item de versão clicado
    if (itemClicado) {
        itemClicado.classList.add('selecionado-versao');
    }

    // Armazena o carro específico selecionado
     if (idLista === 'lista-carro-1') {
        carroSelecionado1 = veiculo;
    } else {
        carroSelecionado2 = veiculo;
    }

    // Atualiza a tabela comparativa com o carro específico selecionado
    const camposSelecionados = Array.from(document.querySelectorAll('#botoes-centro input[type=checkbox]:checked')).map(cb => cb.value);
    montarTabelaComparativa(camposSelecionados, carroSelecionado1, carroSelecionado2);
}

function montarTabelaComparativa(campos, v1, v2) {
    const thead = document.querySelector('#tabelaResultados thead');
    const tbody = document.querySelector('#tabelaResultados tbody');
    thead.innerHTML = '';
    tbody.innerHTML = '';

    // Cabeçalhos
    const trHead = document.createElement('tr');
    // Cabeçalhos agora são: Carro 1 | Campo | Carro 2
    trHead.innerHTML = `<th>${v1 ? (v1['Marca'] + ' ' + v1['Modelo']) : 'Carro 1'}</th><th>Campo</th><th>${v2 ? (v2['Marca'] + ' ' + v2['Modelo']) : 'Carro 2'}</th>`;
    thead.appendChild(trHead);

    // Linhas
    campos.forEach(campo => {
        const tr = document.createElement('tr');
        // Dados agora são: Valor Carro 1 | Nome do Campo | Valor Carro 2
        tr.innerHTML = `<td>${v1 ? (v1[campo] || '-') : '-'}</td><td>${campo}</td><td>${v2 ? (v2[campo] || '-') : '-'}</td>`;
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
