import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

def identificar_debito_credito(valor):
    if valor >= 0:
        return 'D'
    else:
        return 'C'

def main():
    st.title("Identificar Valores Débito/Crédito")

    # Upload do arquivo Excel
    uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx", "xls"])

    if uploaded_file is not None:
        # Carregando os dados para um DataFrame
        df = pd.read_excel(uploaded_file, header=7)

        # Adicionando uma coluna para identificar débito/crédito
        df['Debito/Credito'] = df['Saldo-Exercício'].apply(identificar_debito_credito)

        # Exibindo o DataFrame modificado
        st.subheader("Planilha Razão Enviada")
        df_limpo = df.dropna(axis=1, how='all')
        st.write(df_limpo)

        # Exibindo os valores com 'C' no final
        # Exibindo os valores com 'C' no final, excluindo os valores nulos (None)
        st.subheader("Valores com 'C' (Crédito)")
        valores_com_c_df = df[(df['Debito/Credito'] == 'C')]
        valores_com_c_df_limpo = valores_com_c_df.dropna(axis=1, how='all')
        st.write(valores_com_c_df_limpo)

if __name__ == "__main__":
    main()