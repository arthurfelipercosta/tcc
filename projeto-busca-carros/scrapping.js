/**
 * scrapping.js
 * Responsável por buscar informações externas (preço médio, reclamações, etc)
 * via API backend (Flask).
 */

/**
 * Busca informações de preço médio e reclamações para um veículo.
 * @param {string} marca
 * @param {string} modelo
 * @returns {Promise<Object>} Objeto com preco_medio, precos, reclamacoes
 */

export async function buscarInfoCarro(marca, modelo) {
    const url = `http://127.0.0.1:5000/api/info_carro?marca=${encodeURIComponent(marca)}&modelo=${encodeURIComponent(modelo)}`;
    console.log("URL: ", url);
    const resp = await fetch(url);
    const data = await resp.json()
    // console.log("SCRAPPING para ", marca, modelo, ":", data, null, 2);
    return data;
}