from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
from typing import Optional, List, Dict
import json
import re
from fuzzywuzzy import fuzz
import numpy as np
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="Car Comparison Bot API")

# Configure sua Meta API Key
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "EAFa6hEcZAzx8BPPdChZCkGr9zpRj2cwbhjhBmouEoIACH3WjYVZCdTpwyZBCbZBuEloF4XgiqrjKMqKXYibZBzGYHrYbEIbVuIOZAy5LKsjDQ8tGZBBxQyFkPN8VgL5HgH4doKIa6hpE0sYiUpM7siIvwnMnPziGoWEyEcki5Sl52nln570c4uhygIpfHw00uZCGrztrE5wScxofTHc65TwfQrJ2LtpxKW6CcEoZAejECOnsk5ZAAZDZD")

class WhatsAppMessage(BaseModel):
    message: str
    phone: str
    user_name: Optional[str] = None

class BotResponse(BaseModel):
    response: str
    message_type: str = "text"

class WebmotorsAPI:
    """Integração com a API do Webmotors para buscar preços"""
    
    @staticmethod
    def buscar_precos_webmotors(marca: str, modelo: str, limite: int = 10) -> tuple:
        """
        Busca preços de veículos no Webmotors por marca e modelo.
        """
        try:
            url = (
                "https://www.webmotors.com.br/api/search/car"
                "?displayPerPage=10"
                "&actualPage=1"
                "&showMenu=true"
                "&showCount=true"
                "&showBreadCrumb=true"
                "&order=1"
                f"&url=https://www.webmotors.com.br/carros/estoque/{marca.lower()}/{modelo.lower()}?marca={marca.lower()}&modelo={modelo.lower()}&autocomplete={modelo.lower()}&autocompleteTerm={marca.title()}%20{modelo.upper()}&tipoveiculo=carros&marca1={marca.upper()}&modelo1={modelo.upper()}&page=1"
                "&mediaZeroKm=true"
            )
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            r = requests.get(url, headers=headers, timeout=10)
            
            if r.status_code != 200:
                return 0, "Erro na consulta"
            
            data = r.json()
            precos = []
            
            for anuncio in data.get("SearchResults", [])[:limite]:
                price = anuncio.get("Prices", {}).get("Price")
                if price:
                    precos.append(float(price))
            
            if precos:
                media = sum(precos) / len(precos)
                return media, precos
            
            return 0, "Preços não encontrados"
            
        except Exception as e:
            print(f"Erro ao buscar preços: {e}")
            return 0, "Erro na consulta"

class CarDatabase:
    def __init__(self, csv_file: str = "dados_corrigidos_sem_duplicatas.csv"):
        self.df = None
        self.load_database(csv_file)
    
    def load_database(self, csv_file: str):
        """Carrega a base de dados do CSV"""
        try:
            encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    self.df = pd.read_csv(csv_file, encoding=encoding, sep=';')
                    print(f"✅ Base de dados carregada! ({encoding})")
                    print(f"📊 Total de carros: {len(self.df)}")
                    print(f"📋 Colunas: {list(self.df.columns)}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if self.df is None:
                raise Exception("Não foi possível carregar o arquivo CSV")
            
            self.clean_data()
            
        except FileNotFoundError:
            print("❌ Arquivo CSV não encontrado.")
            self.create_fallback_database()
        except Exception as e:
            print(f"❌ Erro ao carregar CSV: {e}")
            self.create_fallback_database()
    
    def clean_data(self):
        """Limpa e padroniza os dados"""
        # Limpar espaços em branco
        string_columns = self.df.select_dtypes(include=['object']).columns
        for col in string_columns:
            self.df[col] = self.df[col].astype(str).str.strip()
        
        print("✅ Dados limpos e organizados")
    
    def create_fallback_database(self):
        """Base de fallback se o CSV não carregar"""
        fallback_data = {
            'Marca': ['TOYOTA', 'HONDA', 'HYUNDAI', 'CHEVROLET', 'VOLKSWAGEN'],
            'Modelo': ['COROLLA', 'CIVIC', 'HB20', 'ONIX', 'GOLF'],
            'Versão': ['XEI', 'TOURING', 'COMFORT', 'LT', 'COMFORTLINE']
        }
        self.df = pd.DataFrame(fallback_data)
        print("⚠️ Usando base de fallback")
    
    def get_marcas(self) -> List[str]:
        """Retorna lista única de marcas"""
        if self.df is None:
            return []
        return sorted(self.df['Marca'].unique().tolist())
    
    def get_modelos_por_marca(self, marca: str) -> List[str]:
        """Retorna modelos disponíveis para uma marca"""
        if self.df is None:
            return []
        
        marca_upper = marca.upper()
        modelos = self.df[self.df['Marca'].str.upper() == marca_upper]['Modelo'].unique()
        return sorted(modelos.tolist())
    
    def get_versoes_por_marca_modelo(self, marca: str, modelo: str) -> List[Dict]:
        """Retorna versões disponíveis para uma marca e modelo"""
        if self.df is None:
            return []
        
        marca_upper = marca.upper()
        modelo_upper = modelo.upper()
        
        versoes = self.df[
            (self.df['Marca'].str.upper() == marca_upper) & 
            (self.df['Modelo'].str.upper() == modelo_upper)
        ]
        
        versoes_list = []
        for idx, row in versoes.iterrows():
            versao_info = {
                'versao': row.get('*Versão', row.get('Versão', 'N/A')),
                'motor': row.get('*Motor', row.get('Motor', 'N/A')),
                'combustivel': row.get('Combustível', 'N/A'),
                'consumo_cidade_gasolina': row.get('Km - (Gasolina ou Diesel[Cidade][km/l])', 'N/A'),
                'consumo_estrada_gasolina': row.get('Km - (Gasolina ou Diesel[Estrada][km/l])', 'N/A'),
                'consumo_cidade_etanol': row.get('Km - (Etanol[Cidade][km/l])', 'N/A'),
                'consumo_estrada_etanol': row.get('Km - (Etanol[Estrada][km/l])', 'N/A'),
                'selo_conpet': row.get('Selo CONPET de Eficiência Energética', 'N/A'),
                'classificacao_pbe': row.get('*Classificação PBE (Absoluta na Categoria)', 'N/A'),
                'dados_completos': row.to_dict()
            }
            versoes_list.append(versao_info)
        
        return versoes_list
    
    def buscar_marca_modelo(self, query: str) -> List[Dict]:
        """Busca marca e modelo usando fuzzy matching"""
        if self.df is None:
            return []
        
        query = query.lower().strip()
        results = []
        
        # Buscar por marca + modelo
        for idx, row in self.df.iterrows():
            marca = str(row['Marca']).lower()
            modelo = str(row['Modelo']).lower()
            combined = f"{marca} {modelo}"
            
            score = fuzz.partial_ratio(query, combined)
            if score > 70:
                results.append({
                    'marca': row['Marca'],
                    'modelo': row['Modelo'],
                    'score': score,
                    'match': combined
                })
        
        # Remover duplicatas e ordenar por score
        unique_results = {}
        for result in results:
            key = f"{result['marca']}_{result['modelo']}"
            if key not in unique_results or result['score'] > unique_results[key]['score']:
                unique_results[key] = result
        
        return sorted(unique_results.values(), key=lambda x: x['score'], reverse=True)[:5]

class CarComparisonBot:
    def __init__(self):
        self.conversation_context = {}
        self.car_db = CarDatabase()
        self.webmotors = WebmotorsAPI()
    
    def get_user_context(self, phone: str) -> dict:
        """Recupera o contexto da conversa do usuário"""
        if phone not in self.conversation_context:
            self.conversation_context[phone] = {
                "stage": "inicio",  # inicio -> carro1_marca -> carro1_modelo -> carro1_versao -> carro2_marca -> etc
                "carro1": {
                    "marca": None,
                    "modelo": None,
                    "versao": None,
                    "versoes_disponiveis": []
                },
                "carro2": {
                    "marca": None,
                    "modelo": None,
                    "versao": None,
                    "versoes_disponiveis": []
                },
                "conversation_history": []
            }
        return self.conversation_context[phone]
    
    def update_context(self, phone: str, message: str, response: str):
        """Atualiza o contexto da conversa"""
        context = self.get_user_context(phone)
        context["conversation_history"].append({
            "user": message,
            "bot": response
        })
        
        # Manter apenas últimas 10 interações
        if len(context["conversation_history"]) > 10:
            context["conversation_history"] = context["conversation_history"][-10:]
    
    def generate_response(self, message: str, phone: str) -> str:
        """Gera resposta baseada no stage da conversa"""
        context = self.get_user_context(phone)
        stage = context["stage"]
        message_lower = message.lower().strip()
        
        # Comandos especiais
        if message_lower in ['recomecar', 'restart', 'novo']:
            self.reset_context(phone)
            context = self.get_user_context(phone)
            stage = "inicio"
        
        # Roteamento baseado no stage
        if stage == "inicio":
            return self.handle_inicio(message, context)
        elif stage == "carro1_marca":
            return self.handle_carro1_marca(message, context)
        elif stage == "carro1_modelo":
            return self.handle_carro1_modelo(message, context)
        elif stage == "carro1_versao":
            return self.handle_carro1_versao(message, context)
        elif stage == "carro2_marca":
            return self.handle_carro2_marca(message, context)
        elif stage == "carro2_modelo":
            return self.handle_carro2_modelo(message, context)
        elif stage == "carro2_versao":
            return self.handle_carro2_versao(message, context)
        elif stage == "comparacao":
            return self.handle_comparacao_final(message, context)
        
        return "Algo deu errado. Digite 'recomecar' para começar novamente."
    
    def handle_inicio(self, message: str, context: dict) -> str:
        """Início da conversa"""
        context["stage"] = "carro1_marca"
        
        return """🚗 **Olá! Sou seu comparador de carros!**

Vou te ajudar a comparar 2 carros com dados técnicos detalhados e preços atualizados do Webmotors.

**Como funciona:**
1️⃣ Você escolhe o primeiro carro (marca, modelo e versão)
2️⃣ Depois o segundo carro  
3️⃣ Eu mostro uma comparação completa!

**Primeiro carro - Qual a marca?**
Ex: Toyota, Honda, Hyundai, Chevrolet, etc."""

    def handle_carro1_marca(self, message: str, context: dict) -> str:
        """Usuário escolhendo marca do primeiro carro"""
        marcas_disponiveis = self.car_db.get_marcas()
        message_clean = message.strip()
        
        # Buscar marca por similaridade
        best_match = None
        best_score = 0
        
        for marca in marcas_disponiveis:
            score = fuzz.ratio(message_clean.upper(), marca.upper())
            if score > best_score and score > 70:
                best_score = score
                best_match = marca
        
        if best_match:
            context["carro1"]["marca"] = best_match
            context["stage"] = "carro1_modelo"
            
            modelos = self.car_db.get_modelos_por_marca(best_match)
            modelos_text = ", ".join(modelos[:10])  # Primeiros 10
            
            if len(modelos) > 10:
                modelos_text += f"... (e mais {len(modelos) - 10})"
            
            return f"""✅ **Marca selecionada: {best_match}**

**Agora escolha o modelo:**
{modelos_text}

Digite o nome do modelo que você quer:"""
        else:
            # Mostrar marcas disponíveis
            marcas_text = ", ".join(marcas_disponiveis[:15])
            return f"""❌ Não encontrei essa marca.

**Marcas disponíveis:**
{marcas_text}

Digite uma das marcas acima:"""

    def handle_carro1_modelo(self, message: str, context: dict) -> str:
        """Usuário escolhendo modelo do primeiro carro"""
        marca = context["carro1"]["marca"]
        modelos_disponiveis = self.car_db.get_modelos_por_marca(marca)
        message_clean = message.strip()
        
        # Buscar modelo por similaridade
        best_match = None
        best_score = 0
        
        for modelo in modelos_disponiveis:
            score = fuzz.ratio(message_clean.upper(), modelo.upper())
            if score > best_score and score > 70:
                best_score = score
                best_match = modelo
        
        if best_match:
            context["carro1"]["modelo"] = best_match
            
            # Buscar versões disponíveis
            versoes = self.car_db.get_versoes_por_marca_modelo(marca, best_match)
            context["carro1"]["versoes_disponiveis"] = versoes
            
            if len(versoes) == 1:
                # Só tem uma versão, selecionar automaticamente
                context["carro1"]["versao"] = versoes[0]
                context["stage"] = "carro2_marca"
                
                return f"""✅ **Primeiro carro:** {marca} {best_match} - {versoes[0]['versao']}

**Agora vamos ao segundo carro!**

**Qual a marca do segundo carro?**
Ex: Toyota, Honda, Hyundai, etc."""
                
            else:
                context["stage"] = "carro1_versao"
                
                versoes_text = ""
                for i, versao in enumerate(versoes[:8], 1):  # Máximo 8
                    motor = versao['motor']
                    combustivel = versao['combustivel']
                    versoes_text += f"{i}. {versao['versao']} ({motor} - {combustivel})\n"
                
                return f"""✅ **Modelo selecionado:** {marca} {best_match}

**Escolha a versão (digite o número ou nome):**

{versoes_text}

Digite o número ou nome da versão:"""
        else:
            modelos_text = ", ".join(modelos_disponiveis[:10])
            return f"""❌ Modelo não encontrado para {marca}.

**Modelos disponíveis:**
{modelos_text}

Digite um dos modelos acima:"""

    def handle_carro1_versao(self, message: str, context: dict) -> str:
        """Usuário escolhendo versão do primeiro carro"""
        versoes = context["carro1"]["versoes_disponiveis"]
        message_clean = message.strip()
        
        # Tentar por número
        if message_clean.isdigit():
            idx = int(message_clean) - 1
            if 0 <= idx < len(versoes):
                context["carro1"]["versao"] = versoes[idx]
                context["stage"] = "carro2_marca"
                
                marca = context["carro1"]["marca"]
                modelo = context["carro1"]["modelo"]
                versao = versoes[idx]["versao"]
                
                return f"""✅ **Primeiro carro selecionado:**
🚗 {marca} {modelo} - {versao}

**Agora vamos ao segundo carro!**

**Qual a marca do segundo carro?**"""
        
        # Tentar por nome da versão
        best_match = None
        best_score = 0
        
        for versao in versoes:
            score = fuzz.ratio(message_clean.upper(), versao['versao'].upper())
            if score > best_score and score > 70:
                best_score = score
                best_match = versao
        
        if best_match:
            context["carro1"]["versao"] = best_match
            context["stage"] = "carro2_marca"
            
            marca = context["carro1"]["marca"]
            modelo = context["carro1"]["modelo"]
            
            return f"""✅ **Primeiro carro selecionado:**
🚗 {marca} {modelo} - {best_match['versao']}

**Agora vamos ao segundo carro!**

**Qual a marca do segundo carro?**"""
        
        # Não encontrou
        versoes_text = ""
        for i, versao in enumerate(versoes[:8], 1):
            versoes_text += f"{i}. {versao['versao']}\n"
        
        return f"""❌ Versão não encontrada.

**Versões disponíveis:**
{versoes_text}

Digite o número ou nome da versão:"""

    def handle_carro2_marca(self, message: str, context: dict) -> str:
        """Usuário escolhendo marca do segundo carro"""
        # Mesmo processo do primeiro carro
        marcas_disponiveis = self.car_db.get_marcas()
        message_clean = message.strip()
        
        best_match = None
        best_score = 0
        
        for marca in marcas_disponiveis:
            score = fuzz.ratio(message_clean.upper(), marca.upper())
            if score > best_score and score > 70:
                best_score = score
                best_match = marca
        
        if best_match:
            context["carro2"]["marca"] = best_match
            context["stage"] = "carro2_modelo"
            
            modelos = self.car_db.get_modelos_por_marca(best_match)
            modelos_text = ", ".join(modelos[:10])
            
            return f"""✅ **Segunda marca selecionada: {best_match}**

**Escolha o modelo:**
{modelos_text}

Digite o nome do modelo:"""
        else:
            marcas_text = ", ".join(marcas_disponiveis[:15])
            return f"""❌ Marca não encontrada.

**Marcas disponíveis:**
{marcas_text}

Digite uma das marcas:"""

    def handle_carro2_modelo(self, message: str, context: dict) -> str:
        """Usuário escolhendo modelo do segundo carro"""
        marca = context["carro2"]["marca"]
        modelos_disponiveis = self.car_db.get_modelos_por_marca(marca)
        message_clean = message.strip()
        
        best_match = None
        best_score = 0
        
        for modelo in modelos_disponiveis:
            score = fuzz.ratio(message_clean.upper(), modelo.upper())
            if score > best_score and score > 70:
                best_score = score
                best_match = modelo
        
        if best_match:
            context["carro2"]["modelo"] = best_match
            versoes = self.car_db.get_versoes_por_marca_modelo(marca, best_match)
            context["carro2"]["versoes_disponiveis"] = versoes
            
            if len(versoes) == 1:
                context["carro2"]["versao"] = versoes[0]
                context["stage"] = "comparacao"
                
                return self.gerar_comparacao_final(context)
            else:
                context["stage"] = "carro2_versao"
                
                versoes_text = ""
                for i, versao in enumerate(versoes[:8], 1):
                    versoes_text += f"{i}. {versao['versao']} ({versao['motor']} - {versao['combustivel']})\n"
                
                return f"""✅ **Segundo modelo: {marca} {best_match}**

**Escolha a versão:**

{versoes_text}

Digite o número ou nome da versão:"""
        else:
            modelos_text = ", ".join(modelos_disponiveis[:10])
            return f"""❌ Modelo não encontrado.

**Modelos disponíveis:**
{modelos_text}"""

    def handle_carro2_versao(self, message: str, context: dict) -> str:
        """Usuário escolhendo versão do segundo carro"""
        versoes = context["carro2"]["versoes_disponiveis"]
        message_clean = message.strip()
        
        # Por número
        if message_clean.isdigit():
            idx = int(message_clean) - 1
            if 0 <= idx < len(versoes):
                context["carro2"]["versao"] = versoes[idx]
                context["stage"] = "comparacao"
                return self.gerar_comparacao_final(context)
        
        # Por nome
        best_match = None
        best_score = 0
        
        for versao in versoes:
            score = fuzz.ratio(message_clean.upper(), versao['versao'].upper())
            if score > best_score and score > 70:
                best_score = score
                best_match = versao
        
        if best_match:
            context["carro2"]["versao"] = best_match
            context["stage"] = "comparacao"
            return self.gerar_comparacao_final(context)
        
        return "❌ Versão não encontrada. Tente novamente."

    def gerar_comparacao_final(self, context: dict) -> str:
        """Gera a comparação final entre os dois carros"""
        carro1 = context["carro1"]
        carro2 = context["carro2"]
        
        # Informações básicas
        nome1 = f"{carro1['marca']} {carro1['modelo']} {carro1['versao']['versao']}"
        nome2 = f"{carro2['marca']} {carro2['modelo']} {carro2['versao']['versao']}"
        
        comparacao = f"""🏁 **COMPARAÇÃO FINAL**

**CARRO 1:** {nome1}
**CARRO 2:** {nome2}

---

"""
        
        # Comparar especificações técnicas
        specs = [
            ("🔧 **Motor**", "motor"),
            ("⛽ **Combustível**", "combustivel"),
            ("🏙️ **Consumo Cidade (Gasolina)**", "consumo_cidade_gasolina"),
            ("🛣️ **Consumo Estrada (Gasolina)**", "consumo_estrada_gasolina"),
            ("🏙️ **Consumo Cidade (Etanol)**", "consumo_cidade_etanol"),
            ("🛣️ **Consumo Estrada (Etanol)**", "consumo_estrada_etanol"),
            ("🏆 **Classificação PBE**", "classificacao_pbe"),
            ("✅ **Selo CONPET**", "selo_conpet")
        ]
        
        for label, key in specs:
            val1 = carro1['versao'].get(key, 'N/A')
            val2 = carro2['versao'].get(key, 'N/A')
            
            if val1 != 'N/A' or val2 != 'N/A':
                comparacao += f"{label}\n"
                comparacao += f"• {carro1['modelo']}: {val1}\n"
                comparacao += f"• {carro2['modelo']}: {val2}\n\n"
        
        # Buscar preços no Webmotors
        comparacao += "💰 **PREÇOS (Webmotors):**\n"
        
        try:
            preco1, _ = self.webmotors.buscar_precos_webmotors(carro1['marca'], carro1['modelo'])
            preco2, _ = self.webmotors.buscar_precos_webmotors(carro2['marca'], carro2['modelo'])
            
            if preco1 > 0:
                comparacao += f"• {carro1['modelo']}: R$ {preco1:,.0f} (média)\n".replace(',', '.')
            else:
                comparacao += f"• {carro1['modelo']}: Preço não encontrado\n"
            
            if preco2 > 0:
                comparacao += f"• {carro2['modelo']}: R$ {preco2:,.0f} (média)\n".replace(',', '.')
            else:
                comparacao += f"• {carro2['modelo']}: Preço não encontrado\n"
            
            if preco1 > 0 and preco2 > 0:
                diferenca = abs(preco1 - preco2)
                mais_barato = carro1['modelo'] if preco1 < preco2 else carro2['modelo']
                comparacao += f"\n💡 **{mais_barato}** é R$ {diferenca:,.0f} mais barato\n".replace(',', '.')
            
        except Exception as e:
            comparacao += "• Erro ao consultar preços online\n"
        
        comparacao += "\n---\n\n"
        comparacao += "🔄 Digite 'recomecar' para comparar outros carros\n"
        comparacao += "📊 Digite 'detalhes' para mais informações técnicas"
        
        return comparacao

    def handle_comparacao_final(self, message: str, context: dict) -> str:
        """Pós-comparação - comandos adicionais"""
        message_lower = message.lower().strip()
        
        if message_lower == 'detalhes':
            return self.gerar_detalhes_tecnicos(context)
        elif message_lower in ['recomecar', 'novo']:
            self.reset_context(context)
            return self.handle_inicio("", context)
        else:
            return """Comandos disponíveis:
🔄 'recomecar' - Nova comparação
📊 'detalhes' - Mais informações técnicas"""

    def gerar_detalhes_tecnicos(self, context: dict) -> str:
        """Gera detalhes técnicos completos"""
        carro1 = context["carro1"]["versao"]["dados_completos"]
        carro2 = context["carro2"]["versao"]["dados_completos"]
        
        detalhes = "📊 **DETALHES TÉCNICOS COMPLETOS**\n\n"
        
        # Pegar todas as colunas disponíveis
        for col in carro1.keys():
            if col not in ['Marca', 'Modelo']:
                val1 = carro1.get(col, 'N/A')
                val2 = carro2.get(col, 'N/A')
                
                if val1 != 'N/A' or val2 != 'N/A':
                    detalhes += f"**{col}:**\n"
                    detalhes += f"• {context['carro1']['modelo']}: {val1}\n"
                    detalhes += f"• {context['carro2']['modelo']}: {val2}\n\n"
        
        return detalhes[:4000]  # Limite para WhatsApp
    
    def reset_context(self, phone: str):
        """Reseta o contexto do usuário"""
        if phone in self.conversation_context:
            del self.conversation_context[phone]

# Instância global do bot
car_bot = CarComparisonBot()

@app.post("/process-message", response_model=BotResponse)
async def process_whatsapp_message(request: WhatsAppMessage):
    """Endpoint principal que processa mensagens do WhatsApp"""
    try:
        response = car_bot.generate_response(request.message, request.phone)
        car_bot.update_context(request.phone, request.message, response)
        
        return BotResponse(
            response=response,
            message_type="text"
        )
        
    except Exception as e:
        print(f"Erro: {e}")
        return BotResponse(
            response="Desculpe, tive um problema técnico. Digite 'recomecar' para tentar novamente! 🔧",
            message_type="text