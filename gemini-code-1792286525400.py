import streamlit as st
import google.generativeai as genai
import random
import os

# --- 1. PROTEÇÃO DE ACESSO (APENAS VOCÊ ACESSA) ---
# Altere 'SUA_SENHA_AQUI' para a senha de sua preferência
SENHA_ACESSO = os.environ.get("APP_PASSWORD", "minhasenha123")

st.set_page_config(page_title="Painel Privado - Tarô AI", page_icon="🔮")

def autenticar():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.title("🔒 Acesso Restrito")
        senha_digitada = st.text_input("Digite a senha de acesso:", type="password")
        if st.button("Entrar"):
            if senha_digitada == SENHA_ACESSO:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
        st.stop()

autenticar()

# --- 2. CONFIGURAÇÃO DA API DO GEMINI ---
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_KEY:
    st.warning("⚠️ Adicione sua GEMINI_API_KEY nas variáveis de ambiente ou no painel do Streamlit Cloud.")
    GEMINI_KEY = st.text_input("Ou insira sua Gemini API Key aqui:", type="password")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="Você é um tarólogo experiente e acolhedor. Interprete as cartas sorteadas considerando o contexto e a pergunta do cliente."
    )

# --- 3. BANCO DE DADOS DAS CARTAS ---
BARALHO = [
    "O Louco", "O Mago", "A Sacerdotisa", "A Imperatriz", "O Imperador",
    "O Hierofante", "Os Enamorados", "O Carro", "A Força", "O Eremita",
    "A Roda da Fortuna", "A Justiça", "O Enforcado", "A Morte",
    "A Temperança", "O Diabo", "A Torre", "A Estrela", "A Lua",
    "O Sol", "O Julgamento", "O Mundo"
]

# --- 4. INTERFACE DO USUÁRIO / CLIENTE ---
st.title("🔮 Painel de Atendimento - Tarô")

st.subheader("1. Dados do Atendimento")
cliente_nome = st.text_input("Nome do Cliente:")
pergunta_cliente = st.text_area("Pergunta ou Situação do Cliente:")

tipo_tiragem = st.selectbox(
    "Tipo de Tiragem:",
    ["1 Carta (Energia Geral)", "3 Cartas (Passado / Presente / Futuro)", "2 Cartas (Desafio / Conselho)"]
)

# --- 5. LÓGICA DE SORTEIO E LEITURA ---
if st.button("🔮 Sortear Cartas & Gerar Leitura", type="primary"):
    if not pergunta_cliente or not GEMINI_KEY:
        st.error("Por favor, preencha a pergunta e certifique-se de que a API Key está configurada.")
    else:
        # Define posições conforme a escolha
        if "1 Carta" in tipo_tiragem:
            posicoes = ["Energia Geral"]
        elif "3 Cartas" in tipo_tiragem:
            posicoes = ["Passado / Origem", "Presente / Momento Atual", "Futuro / Conselho"]
        else:
            posicoes = ["O Desafio", "O Conselho"]

        # Sorteio determinístico no backend
        cartas_sorteadas = random.sample(BARALHO, len(posicoes))
        orientacoes = [random.choice(["Normal", "Invertida"]) for _ in posicoes]

        st.markdown("---")
        st.subheader("📋 Cartas Sorteadas (Sorteio Interno)")

        # Exibe as cartas na tela em colunas
        cols = st.columns(len(posicoes))
        resultado_detalhado = []

        for idx, col in enumerate(cols):
            nome_carta = cartas_sorteadas[idx]
            orientacao = orientacoes[idx]
            posicao = posicoes[idx]
            
            resultado_detalhado.append(f"- **{posicao}**: {nome_carta} ({orientacao})")
            
            with col:
                st.metric(label=posicao, value=nome_carta, delta=orientacao)

        # Monta a solicitação para a IA
        prompt_ia = f"""
Cliente: {cliente_nome if cliente_nome else 'Anônimo'}
Pergunta: "{pergunta_cliente}"

Cartas sorteadas deterministicamente pelo sistema:
""" + "\n".join(resultado_detalhado) + "\n\nFaça a interpretação integrada para o cliente."

        st.markdown("---")
        st.subheader("✨ Leitura Gerada pela IA")

        with st.spinner("Gerando a interpretação do tarô..."):
            resposta = model.generate_content(prompt_ia)
            st.write(resposta.text)