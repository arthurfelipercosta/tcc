/**
 * script.js
 * Lógica principal do comparador de veículos.
 * Carrega dados de um CSV, popula filtros, permite seleção e comparação de veículos.
 * Desenvolvido para o projeto de busca e comparação de carros.
 */

// Array com todos os veículos carregados do CSV
let dadosVeiculos = [];
// Array com veículos filtrados (não usado diretamente, mas pode ser útil futuramente)
let dadosFiltrados = [];
// Lista de nomes das colunas do CSV
let colunas = [];

// Adiciona campos selecionáveis para comparação
/*
    Categoria que podem ser selecionadas
    Marca,
    Modelo,
    Versão,
    Motor,
    Tipo de Propulsão,
    Transmissão,
    Ar Condicionado,
    Direção Assistida,
    Combustível,
    Poluentes(NMOG+NOx [mg/km]),
    Poluentes(CO [mg/km]),
    Poluentes(CHO [mg/km]),
    Redução Relativa ao Limite,
    Gás Efeito Estufa (Etanol [CO2 fóssil] [g/km]),
    Gás Efeito Estufa (Gasolina ou Diesel [CO2 fóssil] [g/km]),
    Gás Efeito Estufa (VEHP [CO2 fóssil] [g/km]),
    Km - (Etanol[Cidade][km/l]),
    Km - (Etanol[Estrada][km/l]),
    Km - (Gasolina ou Diesel[Cidade][km/l]),
    Km - (Gasolina ou Diesel[Estrada][km/l]),
    Km - (Elétrico quando VE ou VEHP [Cidade][km/le]),
    Km - (Elétrico quando VE ou VEHP [Estrada][km/le]),
    Consumo Energético,
    Autonomia modo Elétrico,
    Classificação PBE (Comparação Relativa),
    Classificação PBE (Absoluta na Categoria),
    Selo CONPET de Eficiência Energética
*/
const camposComparacao = [
    'Categoria', 'Marca', 'Modelo', 'Versão', 'Motor', 'Tipo de Propulsão', 'Transmissão',
    'Ar Condicionado', 'Direção Assistida', 'Combustível', 'Poluentes(NMOG+NOx [mg/km])',
    'Poluentes(CO [mg/km])', 'Poluentes(CHO [mg/km])', 'Redução Relativa ao Limite',
    'Consumo Energético', 'Classificação PBE (Comparação Relativa)',
    'Classificação PBE (Absoluta na Categoria)', 'Selo CONPET de Eficiência Energética'

    // Adicione ou retirar campos conforme desejar
];

const legendasCampos = {
    'Tipo de Propulsão': 'Tipos de Propulsão:\nElétrico\nHíbrido Plug-In\nHíbrido convencional (HEV)\nCombustão (Gasolina, Etanol, Diesel, Flex)',
    'Transmissão': 'Transmissão:\nAs trasmissões são organizadas em ordem\nde tecnologia:\nMais modernas: Automáticas e/ou elétricas\nMais rústicas: Manuais e convencionais.',
    'Direção Assistida': 'Direção Assistida:\nE: Direção Elétrica ou eletroassistida\nE-H: Direção Eletro-hidráulica\nH: Direção Hidráulica',
    'Combustível': 'Combustível:\nA = Álcool (Etanol)\nD = Diesel\nE = Elétrico\nF = Flex\nG = Gasolina',
    'Poluentes(NMOG+NOx [mg/km])': 'Poluentes(NMOG+NOx [mg/km]):\nNMOG = Non-Methane Organic Gases(Gases Orgânicos Não-metânicos)\nNOx = Óxidos de Nitrogênio\n(Principalmente NO e NO₂)\n[mg/km = miligramas por quilômetro]',
    'Poluentes(CO [mg/km])': 'Poluentes (CO [mg/km]):\nCO = Monóxido de Carbono\n[mg/km = miligramas por quilômetro[',
    'Poluentes(CHO [mg/km])':'Poluentes (CHO [mg/km]):\nCHO = Hidrocarbonetos oxigenados\n(formaldeído e outros compostos orgânicos coláteis)\n[mg/km = miligramas por quilômetro]',
    'Redução Relativa ao Limite': 'Redução Relativa ao Limite:\nIndica o quanto abaixo do limite legal o veículo está.',
    'Consumo Energético': 'Consumo Energético:\nConsumo de energia total do veículo',
    'Classificação PBE (Comparação Relativa)': 'Comparação do veículo com outros modelos (independente da categoria)',
    'Classificação PBE (Absoluta na Categoria)': 'Comparação do veículo com outros modelos (dentro da sua categoria)',
    'Selo CONPET de Eficiência Energética': 'Selo emitido pela Petrobras/Minas e Energia que reconhece veículos com alto desempenho energético'
    // Adicione outras legendas conforme necessário
};

/**
 * Inicializa a aplicação ao carregar a página.
 * Carrega o CSV, processa os dados e inicializa os filtros e eventos.
 */
document.addEventListener('DOMContentLoaded', function () {
    // Carrega o CSV 
    fetch('dados_corrigidos_sem_duplicatas.csv')
        .then(response => response.text())
        .then(data => {
            processarCSV(data);
            inicializarFiltros();
            criarSelecaoCampos();
            adicionarEventosSelectsAutomatico();
            aplicarFiltrosAutomatico();
        })
        .catch(error => console.error('Erro ao carregar os dados:', error));

    // Adicionar eventos aos botões (Pesquisar será oculto via CSS, Limpar Filtros ainda funciona)
    document.getElementById('btnPesquisar').addEventListener('click', pesquisar);
    document.getElementById('btnLimpar').addEventListener('click', limparFiltros);

    // Atualiza modelos quando a marca muda (Esta função será chamada internamente pelo filtro automático agora)
    // document.getElementById('marca').addEventListener('change', atualizarModelos);
    // document.getElementById('categoria').addEventListener('change', atualizarModelos);
});

/**
 * Processa o conteúdo do CSV e preenche o array de veículos.
 * @param {string} csv - Conteúdo do arquivo CSV como string.
 */
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
        if (valores.length !== colunas.length) {
            console.warn('Linha com número diferente de colunas:', linhas[i]);
            console.warn('Esperado:', colunas.length, 'Obtido:', valores.length);
        }
        const veiculo = {};

        // Associa cada valor à sua coluna
        for (let j = 0; j < colunas.length; j++) {
            if (j < valores.length) {
                veiculo[colunas[j]] = valores[j].replace(/"/g, '').trim();
            }
        }

        dadosVeiculos.push(veiculo);
    }

    // Ordena os veículos por Marca e depois por Modelo
    dadosVeiculos.sort((a, b) => {
        if (a['Marca'] < b['Marca']) return -1;
        if (a['Marca'] > b['Marca']) return 1;
        // Se as marcas forem iguais, ordena por Modelo
        if (a['Modelo'] < b['Modelo']) return -1;
        if (a['Modelo'] > b['Modelo']) return 1;
        return 0;
    });

    console.log('Dados carregados:', dadosVeiculos.length, 'veículos');
}

/**
 * Cria os checkboxes para seleção dos campos de comparação.
 */
function criarSelecaoCampos() {
    const container = document.getElementById('botoes-centro');
    container.innerHTML = '';

    camposComparacao.forEach(campo => {
        const label = document.createElement('label');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = campo;
        checkbox.checked = true;                                    // Trocar para false para ficar desativado no início
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

// Função para agrupar veículos por Marca e Modelo
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

// Função chamada ao selecionar um MODELO da lista
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
    trHead.innerHTML = `<th>${v1 ? (v1['Marca'] + ' ' + v1['Modelo']) : 'Carro 1'}</th><th>Campo</th><th>${v2 ? (v2['Marca'] + ' ' + v2['Modelo']) : 'Carro 2'}</th>`;
    thead.appendChild(trHead);

    // Variáveis para pontuação
    let pontos1 = 0;
    let pontos2 = 0;

    // Função de comparação para cada campo
    function compararCampo(campo, valor1, valor2) {
        // Critério para comparar tipo de propulsão entre os automóveis
        if (campo === 'Tipo de Propulsão') {
            // Elétrico, Combustão, Híbrido, Plug-in
            const ordemPropulsao = ['Elétrico', 'Combustão', 'Híbrido', 'Plug-in'];
            const auto1 = ordemPropulsao.indexOf(valor1.trim());
            const auto2 = ordemPropulsao.indexOf(valor2.trim());
            if (auto1 !== -1 && auto2 !== -1) {
                if (auto1 < auto2) return 1;        // auto1 é melhor
                else if (auto1 > auto2) return -1;  // auto2 é melhor
                return 0;                           // empate
            }
        }
        // Critério para comparar tipo de transmissões entre os automóveis
        if (campo === 'Transmissão') {
            // 🥇 1º	    eCVT, DHT-2, DHT, DCT-8, DCT-7, DCT, A-10, A-9, A-8
            // 🥈 2º	    A-7, A-6, CVT-7, CVT, A-5, A-4
            // 🥉 3º	    M-6, M-5
            // 🚩 Último	A, N.A., --
            const ordemTransmissao = [
                'eCVT', 'DHT-2', 'DHT', 'DCT-8', 'DCT-7', 'DCT-6', 'DCT', 'A-10', 'A-9', 'A-8',
                'A-7', 'A-6', 'CVT-7', 'CVT', 'A-5', 'A-4', 'A-1',
                'M-6', 'M-5',
                'A', 'N.A.', '--'
            ];
            const auto1 = ordemTransmissao.indexOf(valor1.trim());
            const auto2 = ordemTransmissao.indexOf(valor2.trim());
            if (auto1 !== -1 && auto2 !== -1) {
                if (auto1 < auto2) return 1;        // auto1 é melhor
                else if (auto1 > auto2) return -1;  // auto2 é melhor
                return 0;                           // empate
            }
        }
        // Critério para comparar o tipo de ar-condicionado entre os automóveis
        if (campo === 'Ar condicionado') {
            const ordemDirecao = ['S', 'N'];
            const auto1 = ordemDirecao.indexOf(valor1.trim());
            const auto2 = ordemDirecao.indexOf(valor2.trim());
            if (auto1 !== -1 && auto2 !== -1) {
                if (auto1 < auto2) return 1;        // auto1 é melhor
                else if (auto1 > auto2) return -1;  // auto2 é melhor
                return 0;                           // empate
            }
        }
        // Critério para comparar o tipo de direção assistida entre os automóveis
        if (campo === 'Direção Assistida') {
            const ordemDirecao = ['E', 'E-H', 'H'];
            const auto1 = ordemDirecao.indexOf(valor1.trim());
            const auto2 = ordemDirecao.indexOf(valor2.trim());
            if (auto1 !== -1 && auto2 !== -1) {
                if (auto1 < auto2) return 1;        // auto1 é melhor
                else if (auto1 > auto2) return -1;  // auto2 é melhor
                return 0;                           // empate
            }
        }
        // Critério para comparar o tipo de combustível entre os automóveis
        // Em relação ao nível de poluição
        if (campo === 'Combustível') {
            const ordemCombustivel = ['E', 'A', 'F', 'G', 'D'];
            // A - Álcool (Etanol)
            // D - Diesel
            // E - Elétrico
            // F - Flex
            // G - Gasolina
            const auto1 = ordemCombustivel.indexOf(valor1.trim());
            const auto2 = ordemCombustivel.indexOf(valor2.trim());
            if (auto1 !== -1 && auto2 !== -1) {
                if (auto1 < auto2) return 1;        // auto1 é melhor
                else if (auto1 > auto2) return -1;  // auto2 é melhor
                return 0;                           // empate
            }
        }
        // Critérios para comparar os poluentes emitidos entre os automóveis
        // Em relação ao nível de (NMOG+NOx [mg/km])
        if (campo === 'Poluentes(NMOG+NOx [mg/km])') {
            // Converte para números, removendo caracteres não numéricos
            const valor1Num = parseFloat(valor1.toString().replace(/[^\d.,]/g, '').replace(',', '.'));
            const valor2Num = parseFloat(valor2.toString().replace(/[^\d.,]/g, '').replace(',', '.'));

            if (isNaN(valor1Num)) { valor1Num = 1000; }
            if (isNaN(valor2Num)) { valor2Num = 1000; }
            // Verifica se os valores são números válidos
            if (!isNaN(valor1Num) && !isNaN(valor2Num)) {
                if (valor1Num < valor2Num) return 1;        // auto1 é melhor (menos poluente)
                else if (valor1Num > valor2Num) return -1;  // auto2 é melhor (menos poluente)
                return 0;                                   // empate
            }
        }
        // Em relação ao nível de (CO [mg/km])
        if (campo === 'Poluentes(CO [mg/km])') {
            // Converte para números, removendo caracteres não numéricos
            const valor1Num = parseFloat(valor1.toString().replace(/[^\d.,]/g, '').replace(',', '.'));
            const valor2Num = parseFloat(valor2.toString().replace(/[^\d.,]/g, '').replace(',', '.'));

            if (isNaN(valor1Num)) { valor1Num = 1000; }
            if (isNaN(valor2Num)) { valor2Num = 1000; }
            // Verifica se os valores são números válidos
            if (!isNaN(valor1Num) && !isNaN(valor2Num)) {
                if (valor1Num < valor2Num) return 1;        // auto1 é melhor (menos poluente)
                else if (valor1Num > valor2Num) return -1;  // auto2 é melhor (menos poluente)
                return 0;                                   // empate
            }
        }
        // Em relação ao nível de (CHO [mg/km])
        if (campo === 'Poluentes(CHO [mg/km])') {
            // Converte para números, removendo caracteres não numéricos
            const valor1Num = parseFloat(valor1.toString().replace(/[^\d.,]/g, '').replace(',', '.'));
            const valor2Num = parseFloat(valor2.toString().replace(/[^\d.,]/g, '').replace(',', '.'));

            if (isNaN(valor1Num)) { valor1Num = 1000; }
            if (isNaN(valor2Num)) { valor2Num = 1000; }
            // Verifica se os valores são números válidos
            if (!isNaN(valor1Num) && !isNaN(valor2Num)) {
                if (valor1Num < valor2Num) return 1;        // auto1 é melhor (menos poluente)
                else if (valor1Num > valor2Num) return -1;  // auto2 é melhor (menos poluente)
                return 0;                                   // empate
            }
        }

        // Critério para comparar Classificação PBE relativa e absoluta entre os carros selecionados
        if (campo === 'Classificação PBE (Comparação Relativa)' ||
            campo === 'Classificação PBE (Absoluta na Categoria)') {
            // Ordem: A > B > C > D > E
            const ordemPBE = ['A', 'B', 'C', 'D', 'E'];
            const v1 = ordemPBE.indexOf(valor1.trim().toUpperCase());
            const v2 = ordemPBE.indexOf(valor2.trim().toUpperCase());
            if (v1 !== -1 && v2 !== -1) {
                if (v1 < v2) return 1;        // valor1 é melhor
                else if (v1 > v2) return -1;  // valor2 é melhor
                return 0;                     // empate
            }
        }

        // Critério para comparar consumo energético entre os carros selecionados
        if (campo === 'Consumo Energético') {
            // Converte para números, removendo caracteres não numéricos
            const valor1Num = parseFloat(valor1.toString().replace(/[^\d.,]/g, '').replace(',', '.'));
            const valor2Num = parseFloat(valor2.toString().replace(/[^\d.,]/g, '').replace(',', '.'));

            if (isNaN(valor1Num)) { valor1Num = 1000; }
            if (isNaN(valor2Num)) { valor2Num = 1000; }
            // Verifica se os valores são números válidos
            if (!isNaN(valor1Num) && !isNaN(valor2Num)) {
                if (valor1Num < valor2Num) return 1;        // auto1 é melhor (menos consumo)
                else if (valor1Num > valor2Num) return -1;  // auto2 é melhor (menos consumo)
                return 0;                                   // empate
            }
        }

        if (campo === 'Selo CONPET de Eficiência Energética') {
            const ordemCONPET = ['SIM', 'NÃO'];
            const v1 = ordemCONPET.indexOf(valor1.trim().toUpperCase());
            const v2 = ordemCONPET.indexOf(valor2.trim().toUpperCase());

            if (v1 !== -1 && v2 !== -1) {
                if (v1 < v2) return 1;        // valor1 é melhor
                else if (v1 > v2) return -1;  // valor2 é melhor
                return 0;                     // empate
            }
        }
        // Adicionar outros critérios aqui!
        return 0;
    }

    campos.forEach(campo => {
        const tr = document.createElement('tr');
        const valor1 = v1 ? (v1[campo] || '-') : '-';
        const valor2 = v2 ? (v2[campo] || '-') : '-';
        let classe1 = '', classe2 = '';
        let simbolo1 = '', simbolo2 = '';
        const resultado = compararCampo(campo, valor1, valor2);

        if (resultado === 1) {
            simbolo1 = '<span style="color:green;font-weight:bold;">🟢</span> ';
            simbolo2 = '<span style="color:red;font-weight:bold;"> ❌</span> ';
            pontos1++;
        } else if (resultado === -1) {
            simbolo1 = '<span style="color:red;font-weight:bold;">❌</span> ';
            simbolo2 = '<span style="color:green;font-weight:bold;"> 🟢</span> ';
            pontos2++;
        } else if (resultado === 0 && valor1 !== '-' && valor2 !== '-') {
            simbolo1 = '<span style="color:red;font-weight:bold;">🟨</span> ';
            simbolo2 = '<span style="color:green;font-weight:bold;"> 🟨</span> ';
        }

        // Comparar resultados
        if (resultado === 1) {
            classe1 = 'ganhador';
            classe2 = 'perdedor';
        } else if (resultado === -1) {
            classe1 = 'perdedor';
            classe2 = 'ganhador';
        } else if (resultado === 0 && valor1 !== '-' && valor2 !== '-') {
            classe1 = 'empate';
            classe2 = 'empate';
        }

        tr.innerHTML = `<td class="${classe1}">${simbolo1}${valor1}</td><td>${campo}</td><td class="${classe2}">${valor2}${simbolo2}</td>`;
        tbody.appendChild(tr);
    });

    //  Linha final com a pontuação
    const trPontuacao = document.createElement('tr');
    trPontuacao.innerHTML = `<td style="text-align:center; font-weight:bold;">${pontos1} pts</td>
                             <td style="text-align:center; font-weight:bold;">Pontuação</td>
                             <td style="text-align:center; font-weight:bold;">${pontos2} pts</td>`;
    tbody.appendChild(trPontuacao);

    // Adiciona tooltip nas células da coluna do meio
    document.querySelectorAll('#tabelaResultados tbody tr td:nth-child(2)').forEach((td, idx) => {
        const campo = campos[idx];
        const legenda = legendasCampos[campo];
        if (legenda) {
            td.style.cursor = 'help';
            td.addEventListener('mouseenter', function(e) {
                const tooltip = document.getElementById('tooltip');
                tooltip.textContent = legenda;
                tooltip.style.display = 'block';
                tooltip.style.left = (e.pageX + 10) + 'px';
                tooltip.style.top = (e.pageY + 10) + 'px';
            });
            td.addEventListener('mousemove', function(e) {
                const tooltip = document.getElementById('tooltip');
                tooltip.style.left = (e.pageX + 10) + 'px';
                tooltip.style.top = (e.pageY + 10) + 'px';
            });
            td.addEventListener('mouseleave', function() {
                const tooltip = document.getElementById('tooltip');
                tooltip.style.display = 'none';
            });
        }
    });
}

// Limpa todos os filtros
function limparFiltros() {
    ['categoria', 'marca', 'modelo', 'categoria2', 'marca2', 'modelo2'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    aplicarFiltrosAutomatico();
}

// Eventos dinâmicos para selects - AGORA COM FILTRO AUTOMÁTICO
function adicionarEventosSelectsAutomatico() {
    // Eventos para Carro 1
    document.getElementById('categoria').addEventListener('change', aplicarFiltrosAutomatico);
    document.getElementById('marca').addEventListener('change', aplicarFiltrosAutomatico);
    document.getElementById('modelo').addEventListener('change', aplicarFiltrosAutomatico);

    // Eventos para Carro 2
    document.getElementById('categoria2').addEventListener('change', aplicarFiltrosAutomatico);
    document.getElementById('marca2').addEventListener('change', aplicarFiltrosAutomatico);
    document.getElementById('modelo2').addEventListener('change', aplicarFiltrosAutomatico);
}

// Nova função para aplicar filtros automaticamente e atualizar listas
function aplicarFiltrosAutomatico() {
    // Atualizar as opções dos selects (Marca e Modelo) para Carro 1
    atualizarModelos('marca', 'categoria', 'modelo');
    // Atualizar as opções dos selects (Marca e Modelo) para Carro 2
    // Precisamos re-filtrar os modelos2 com base na categoria2 e marca2 atuais
    // A função atualizarModelos já faz isso, só precisamos chamá-la para os selects do Carro 2
    atualizarModelos('marca2', 'categoria2', 'modelo2');


    // Agora, aplicar os filtros atuais para atualizar as listas de carros
    // A função pesquisar já lê os valores dos selects e atualiza as listas
    pesquisar();
}
