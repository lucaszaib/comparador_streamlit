import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Comparador",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

def encontrar_ultima_data(df):
    saldo_indices = df.index[df['HISTÓRICO'] == 'SALDO DO DIA ===== >']

    datas_saldo = []
    for saldo_index in saldo_indices:
        last_filled_index = None
        for index, row in df.iloc[:saldo_index].iterrows():
            if not pd.isna(row['DATA']):
                last_filled_index = index

        if last_filled_index is not None:
            data_saldo = df.at[last_filled_index, 'DATA']
            datas_saldo.append(data_saldo)
        else:
            datas_saldo.append(None)

    return datas_saldo

def formatar_valor(valor):
    # Remove a letra 'C'
    valor_sem_c = valor.replace('C', '')
    # Substitui a vírgula por um ponto e divide a string em duas partes
    parte_inteira, parte_centavos = valor_sem_c.replace(',', '.').split('.')
    # Adiciona um ponto às centenas
    parte_inteira_formatada = "{:,.0f}".format(float(parte_inteira))
    # Junta a parte inteira formatada com a parte dos centavos e retorna
    return parte_inteira_formatada + '.' + parte_centavos

def formatar_moeda(valor):
    return '{:,.2f}'.format(valor).replace('.', ',')


# Função para destacar as diferenças entre duas colunas
def highlight_diff(row, color='yellow'):
    attr = 'background-color: {}'.format(color)
    estilo = [''] * len(row)
    if row['Valor_Saldo_df1'] != row['Valor_Saldo_df2']:
        estilo[row.index.get_loc('Valor_Saldo_df1')] = 'background-color: {}'.format(color)
        estilo[row.index.get_loc('Valor_Saldo_df2')] = 'background-color: {}'.format(color)
    return estilo




def main():
    st.title("Comparador de Extratos BANCOS x RAZÃO")
    

    # Upload dos arquivos
    uploaded_file1 = st.file_uploader("SELECIONE EXTRATO DO BANCO", type=["xlsx", "xls"])
    uploaded_file2 = st.file_uploader("SELECIONE EXTRATO RAZÃO SISTEMA DOMÍNIO", type=["xlsx", "xls"])

    if uploaded_file1 is not None and uploaded_file2 is not None:
        df1 = load_dataframe(uploaded_file1, header=2)  # Define o cabeçalho na linha 3
        df2 = load_dataframe(uploaded_file2)

        st.subheader("Conteúdo do arquivo 1")
        df1_cleaned = df1.dropna(axis=1, how='all')  # Remove colunas que são todas None
        st.write(df1_cleaned)

        st.subheader("Conteúdo do arquivo 2")
        df2_cleaned = df2.dropna(axis=1, how='all')  # Remove colunas que são todas None
        st.write(df2_cleaned)

        if df1_cleaned is not None and df2 is not None:
            if 'VALOR' in df1_cleaned.columns and 'Saldo-Exercício' in df2.columns and 'Data' in df2.columns:
                # Remove os valores de texto da coluna 'Data' em df2 e converte para datetime
                df2['Data'] = pd.to_datetime(df2['Data'], errors='coerce')

                # Remove as linhas com valores nulos na coluna 'Data'
                df2 = df2.dropna(subset=['Data'])

                datas_saldos_df1 = encontrar_ultima_data(df1_cleaned)

                df2_last_of_day = df2.groupby(df2['Data'].dt.date).tail(1)

                df_comparacao = pd.DataFrame({
                    'Data Saldo Banco': datas_saldos_df1,
                    'Valor_Saldo_df1': df1_cleaned.loc[df1_cleaned['HISTÓRICO'] == 'SALDO DO DIA ===== >', 'VALOR'].str.replace('.', '').str.replace(',', '.').str.rstrip('C').astype(float).values,
                    'Data': df2_last_of_day['Data'].dt.strftime('%d/%m/%Y'),
                    'Valor_Saldo_df2': df2_last_of_day['Saldo-Exercício'].values
                })
                

                # Aplicar a função aos dados e estilizar o DataFrame
                df_comparacao_styled = df_comparacao.style.apply(highlight_diff, axis=1)

                df_comparacao_styled = df_comparacao_styled.format({
                    'Valor_Saldo_df1': formatar_moeda,
                    'Valor_Saldo_df2': formatar_moeda
                })
                df_comparacao_styled.set_table_styles([{'selector': 'table', 'props': [('height', '1600px')]}])
                st.subheader("Comparação Extrato Banco e Razão Relatório :")
                st.write(df_comparacao_styled, unsafe_allow_html=True)

            else:
                st.write("As colunas 'VALOR' e/ou 'Saldo-Exercício' e/ou 'Data' não foram encontradas nos arquivos.")

def load_dataframe(uploaded_file, **kwargs):
    if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
        return pd.read_excel(uploaded_file, **kwargs)
    else:
        st.error("Formato de arquivo não suportado.")
        return None

if __name__ == "__main__":
    main()