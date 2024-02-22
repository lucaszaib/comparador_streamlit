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

    # Seletor para escolher entre 'Balancete' e 'Razão'
    tipo_analise = st.selectbox("Escolha o tipo de análise:", ['Balancete', 'Razão'])

    # Upload do arquivo Excel
    uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx", "xls"])

    if uploaded_file is not None:
        # Carregando as 10 primeiras linhas para identificar o cabeçalho
        df_head = pd.read_excel(uploaded_file, nrows=10)

        if tipo_analise == 'Razão':
            # Procurando dinamicamente a linha que contém o valor na coluna "Data" RAZÃO
            for index, row in df_head.iterrows():
                if 'Data' in row.values:
                    header_row = index + 1
                    break
            else:
                header_row = None
        else:
            # Procurando dinamicamente a linha que contém o valor na coluna "Data" RAZÃO
            
            header_row = 0
            

        # Se a linha do cabeçalho foi encontrada, carregue o DataFrame com o header na linha correta
        if header_row is not None:
            df = pd.read_excel(uploaded_file, header=header_row)
            
            # Verifica o tipo de análise selecionada
            if tipo_analise == 'Balancete':
                # Análise feita na coluna 'Saldo Atual'
                df['Debito/Credito'] = df['Saldo Atual'].apply(identificar_debito_credito)
            elif tipo_analise == 'Razão':
                # Análise feita na coluna 'Saldo-Exercício'
                df['Debito/Credito'] = df['Saldo-Exercício'].apply(identificar_debito_credito)

            # Exibindo o DataFrame modificado
            st.subheader("Planilha Enviada")
            df_limpo = df.dropna(axis=1, how='all')
            st.write(df_limpo)

            # Exibindo os valores com 'C' no final
            st.subheader("Valores com 'C' (Crédito)")
            valores_com_c_df = df[(df['Debito/Credito'] == 'C')]
            valores_com_c_df_limpo = valores_com_c_df.dropna(axis=1, how='all')
            st.write(valores_com_c_df_limpo)
        else:
            # Se não encontrar, você pode tratar isso de acordo com sua lógica, como levantar um erro ou assumir uma linha padrão.
            st.error("Não foi possível encontrar a linha do cabeçalho com o valor 'Data'")

if __name__ == "__main__":
    main()
