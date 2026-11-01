import streamlit as st
import pandas as pd
import mysql.connector

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Agrosense - Painel de Pragas",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 Agrosense: Monitoramento Inteligente de Pragas")
st.markdown("Painel operacional para acompanhamento de surtos (*Helicoverpa zea*) integrado ao MySQL.")
st.markdown("---")


# ==========================================
# CONEXÃO E CARREGAMENTO DE DADOS DO MYSQL
# ==========================================
@st.cache_data(ttl=30)
def carregar_dados_agrosense():
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="sua_senha",
            database="agrosense"
        )

        # Buscar a última leitura da estação
        query_estacao = "SELECT data_leitura, latitude, longitude FROM leituras_estacao ORDER BY id DESC LIMIT 1"
        df_estacao = pd.read_sql(query_estacao, conexao)

        # Buscar o histórico de alertas registados
        query_alertas = "SELECT id, nivel_risco, status, data_alerta FROM alertas_pragas ORDER BY id DESC LIMIT 10"
        df_alertas = pd.read_sql(query_alertas, conexao)

        conexao.close()
        return df_estacao, df_alertas
    except Exception as e:
        st.error(f"Erro ao conectar com o MySQL: {e}")
        return None, None


df_estacao, df_alertas = carregar_dados_agrosense()

# ==========================================
# LAYOUT DO PAINEL (DASHBOARD)
# ==========================================
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("📍 Estado Atual da Estação")

    if df_estacao is not None and not df_estacao.empty:
        lat = df_estacao['latitude'].values[0]
        long = df_estacao['longitude'].values[0]
        data_leitura = df_estacao['data_leitura'].values[0]

        st.metric(label="Latitude", value=f"{lat:.4f}")
        st.metric(label="Longitude", value=f"{long:.4f}")
        st.info(f"📅 **Última Leitura:** {data_leitura}")

        st.dataframe(df_estacao, use_container_width=True)
    else:
        st.warning("⚠️ Nenhuma leitura encontrada na tabela `leituras_estacao` do MySQL.")

with col2:
    st.subheader("🚨 Histórico de Alertas de Risco")

    if df_alertas is not None and not df_alertas.empty:
        ultimo_risco = df_alertas['nivel_risco'].values[0]

        if ultimo_risco >= 50.0:
            st.error(f"⚠️ **ATENÇÃO:** Nível de risco crítico detetado: **{ultimo_risco:.2f}**")
        else:
            st.success(f"✅ **ESTABILIZADO:** Nível de risco sob controlo: **{ultimo_risco:.2f}**")

        st.dataframe(df_alertas, use_container_width=True)
    else:
        st.info("Nenhum alerta de praga registado até o momento.")

# ==========================================
# BOTÃO DE ATUALIZAÇÃO MANUAL
# ==========================================
st.markdown("---")
if st.button("🔄 Atualizar Painel"):
    st.rerun()