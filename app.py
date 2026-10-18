import streamlit as st
import google.generativeai as genai
import random
import os

# --- 1. PROTEÇÃO DE ACESSO (SÓ VOCÊ ACESSA) ---
SENHA_ACESSO = st.secrets.get("APP_PASSWORD", "minhasenha123")

st.set_page_config(page_title="Painel Privado - Tarô AI", page_icon="🔮", layout="wide")

def autenticar():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.title("🔒 Acesso Restrito")
        senha_digitada = st.text_input("Digite a senha de acesso ao painel:", type="password")
        if st.button("Entrar"):
            if senha_digitada == SENHA_ACESSO:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
        st.stop()

autenticar()

# --- 2. CONFIGURAÇÃO DA API DO GEMINI ---
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))

if not GEMINI_KEY:
    st.warning("⚠️ GEMINI_API_KEY não foi encontrada nos Secrets. Cole sua chave abaixo para testar:")
    GEMINI_KEY = st.text_input("Cole sua Gemini API Key aqui:", type="password")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="""
Você é um tarólogo experiente, acolhedor e profundo.
Sua missão é interpretar as cartas sorteadas pelo sistema para a pergunta do cliente.

Regras de Atendimento:
1. Respeite rigorosamente as cartas sorteadas no prompt.
2. Relacione a carta, sua orientação (Normal/Invertida) e a posição no jogo com a pergunta do cliente.
3. Mantenha um tom empático e ético, destacando sempre o livre-arbítrio.
"""
    )

# --- 3. BANCO DE DADOS COMPLETO (78 CARTAS DO TARÔ) ---
BARALHO_COMPLETO = [
    # Arcanos Maiores (22)
    "0 - O Louco", "I - O Mago", "II - A Sacerdotisa", "III - A Imperatriz", "IV - O Imperador",
    "V - O Hierofante", "VI - Os Enamorados", "VII - O Carro", "VIII - A Força", "IX - O Eremita",
    "X - A Roda da Fortuna", "XI - A Justiça", "XII - O Enforcado", "XIII - A Morte",
    "XIV - A Temperança", "XV - O Diabo", "XVI - A Torre", "XVII - A Estrela", "XVIII - A Lua",
    "XIX - O Sol", "XX - O Julgamento", "XXI - O Mundo",
    
    # Arcanos Menores - Paus (14)
    "Ás de Paus", "2 de Paus", "3 de Paus", "4 de Paus", "5 de Paus", "6 de Paus", "7 de Paus",
    "8 de Paus", "9 de Paus", "10 de Paus", "Pagem de Paus", "Cavaleiro de Paus", "Rainha de Paus", "Rei de Paus",

    # Arcanos Menores - Copas (14)
    "Ás de Copas", "2 de Copas", "3 de Copas", "4 de Copas", "5 de Copas", "6 de Copas", "7 de Copas",
    "8 de Copas", "9 de Copas", "10 de Copas", "Pagem de Copas", "Cavaleiro de Copas", "Rainha de Copas", "Rei de Copas",

    # Arcanos Menores - Espadas (14)
    "Ás de Espadas", "2 de Espadas", "3 de Espadas", "4 de Espadas", "5 de Espadas", "6 de Espadas", "7 de Espadas",
    "8 de Espadas", "9 de Espadas", "10 de Espadas", "Pagem de Espadas", "Cavaleiro de Espadas", "Rainha de Espadas", "Rei de Espadas",

    # Arcanos Menores - Ouros (14)
    "Ás de Ouros", "2 de Ouros", "3 de Ouros", "4 de Ouros", "5 de Ouros", "6 de Ouros", "7 de Ouros",
    "8 de Ouros", "9 de Ouros", "10 de Ouros", "Pagem de Ouros", "Cavaleiro de Ouros", "Rainha de Ouros", "Rei de Ouros"
]

# --- 4. INTERFACE PRINCIPAL ---
st.title("🔮 Painel Exclusivo de Sorteio e Leitura de Tarô")

col_esq, col_dir = st.columns([1, 1])

with col_esq:
    st.subheader("📝 Dados do Atendimento")
    nome_cliente = st.text_input("Nome do Cliente (opcional):", placeholder="Ex: Maria Silva")
    pergunta_cliente = st.text_area("Pergunta do Cliente:", placeholder="Ex: Qual o panorama da minha vida profissional nos próximos meses?")
    
    tipo_tiragem = st.selectbox(
        "Selecione o Tipo de Tiragem:",
        [
            "1 Carta (Energia Geral)",
            "3 Cartas (Passado / Presente / Futuro)",
            "2 Cartas (Desafio / Conselho)",
            "4 Cartas (Situação / Obstáculo / Conselho / Resultado)"
        ]
    )
    
    permitir_invertidas = st.checkbox("Incluir cartas invertidas?", value=True)
    btn_sortear = st.button("🔮 Sortear & Gerar Leitura", type="primary", use_container_width=True)

with col_dir:
    st.subheader("🃏 Cartas Sorteadas & Interpretação")

    if btn_sortear:
        if not pergunta_cliente or not GEMINI_KEY:
            st.error("Preencha a pergunta do cliente e certifique-se de que a API Key está configurada.")
        else:
            # Mapeia as posições do jogo
            if "1 Carta" in tipo_tiragem:
                posicoes = ["Energia Geral"]
            elif "3 Cartas" in tipo_tiragem:
                posicoes = ["Passado / Causa", "Presente / Momento Atual", "Futuro / Tendência"]
            elif "2 Cartas" in tipo_tiragem:
                posicoes = ["O Desafio", "O Conselho"]
            else:
                posicoes = ["A Situação", "O Obstáculo", "O Conselho", "O Resultado"]

            # Sorteio determinístico fora do LLM
            cartas_sorteadas = random.sample(BARALHO_COMPLETO, len(posicoes))
            orientacoes = [
                random.choice(["Invertida", "Normal"]) if permitir_invertidas else "Normal" 
                for _ in posicoes
            ]

            # Exibe as cartas sorteadas na tela
            grid_cols = st.columns(len(posicoes))
            detalhes_prompts = []

            for i, col in enumerate(grid_cols):
                carta = cartas_sorteadas[i]
                orientacao = orientacoes[i]
                posicao = posicoes[i]
                
                detalhes_prompts.append(f"- Posição '{posicao}': {carta} ({orientacao})")
                
                with col:
                    st.metric(label=posicao, value=carta, delta=orientacao)

            # Monta o prompt para envio ao Gemini
            prompt_envio = f"""
Cliente: {nome_cliente if nome_cliente else 'Cliente'}
Pergunta: "{pergunta_cliente}"

Cartas sorteadas no sistema:
""" + "\n".join(detalhes_prompts) + "\n\nFaça a leitura completa e detalhada."

            st.markdown("---")
            with st.spinner("O tarólogo está interpretando as cartas..."):
                resposta = model.generate_content(prompt_envio)
                st.markdown("### ✨ Leitura do Tarô")
                st.write(resposta.text)
