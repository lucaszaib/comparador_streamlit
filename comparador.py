import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
import os
import io



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

# Função para destacar as diferenças entre duas colunas
def highlight_diff_santander(row, color='yellow'):
    attr = 'background-color: {}'.format(color)
    estilo = [''] * len(row)
    if row['Saldo (R$)'] != row['Saldo-Exercício']:
        estilo[row.index.get_loc('Saldo (R$)')] = 'background-color: {}'.format(color)
        estilo[row.index.get_loc('Saldo-Exercício')] = 'background-color: {}'.format(color)
    return estilo

# Função para ler um arquivo de texto
def ler_texto(file):
    try:
        # Lê o conteúdo do arquivo de texto
        content = pd.read_csv(file, sep=';', quotechar='"')
        return content
    except Exception as e:
        st.error(f"Erro ao ler arquivo de texto: {e}")
        return None

def load_dataframe(uploaded_file, **kwargs):
    if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
        return pd.read_excel(uploaded_file, **kwargs)
    else:
        st.error("Formato de arquivo não suportado.")
        return None

def extract_data_from_lines(lines):
    data_rows = []
    for line in lines:
        if "SALDO DIA" in line:
            data = line.split()
            # Verificar se a linha contém informações suficientes
            if len(data) >= 5:
                # Extrair as informações e dividir em colunas
                data_row = {
                    'Data': data[0],
                    'NrDoc': data[1],
                    'Histórico': ' '.join(data[2:-2]),
                    'Valor': data[-2]
                }
                data_rows.append(data_row)

    return data_rows

def read_pdf_to_dataframe(uploaded_file):
    # Ler o conteúdo do arquivo PDF
    content = uploaded_file.getvalue()

    # Criar um objeto PdfReader
    pdf_reader = PdfReader(io.BytesIO(content))

    # Extrair o texto de todas as páginas do PDF
    all_lines = []
    for page in pdf_reader.pages:
        text = page.extract_text()
        lines = text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        all_lines.extend(lines)

    # Extrair dados das linhas que contêm "SALDO DIA"
    data_rows = extract_data_from_lines(all_lines)

    # Criar o DataFrame
    df = pd.DataFrame(data_rows)

    return df

def main():
    st.title("Comparador de Extratos BANCOS x RAZÃO")
    
    opcoes_bancos = ['Selecione um Banco', 'SICOOB', 'Santander', 'Banrisul', 'Caixa Econômica', 'Bradesco']

    banco_selecionado = st.selectbox("Selecione o Banco", opcoes_bancos)

    if banco_selecionado == 'SICOOB':
        uploaded_sicoob = st.file_uploader("Selecione Extrato SICOOB", type=["xlsx", "xls"])
        # Upload Domínio Extrato Razão
        uploaded_file2 = st.file_uploader("SELECIONE EXTRATO RAZÃO SISTEMA DOMÍNIO", type=["xlsx", "xls"])

        if uploaded_sicoob is not None:

            # Verifica a extensão do arquivo
            _, file_extension = os.path.splitext(uploaded_sicoob.name)
            
            # Caso a extensão seja .xlsx ou .xls, lê o arquivo como Excel
            if file_extension in ['.xlsx', '.xls']:

                if uploaded_sicoob is not None and uploaded_file2 is not None:
                    df1 = load_dataframe(uploaded_sicoob, header=2)  # Define o cabeçalho na linha 3
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
            
            # Caso a extensão seja .txt, lê o arquivo como texto
            elif file_extension == '.txt':
                texto = ler_texto(uploaded_sicoob)
                if texto is not None:
                    st.write("Conteúdo do arquivo de texto:")
                    df = pd.DataFrame(texto)
                    df['Data_Mov'] = pd.to_datetime(df['Data_Mov'], format='%Y%m%d')
                    df['Data_Mov'] = df['Data_Mov'].dt.strftime('%d/%m/%Y')
                    st.write(df)
            


    elif banco_selecionado == 'Santander':
        uploaded_santander = st.file_uploader("Selecione Extrato SANTANDER", type=["xlsx", "xls"])
        # Upload Domínio Extrato Razão
        uploaded_file2 = st.file_uploader("SELECIONE EXTRATO RAZÃO SISTEMA DOMÍNIO", type=["xlsx", "xls"])

        if uploaded_santander is not None:
            # Verifica a extensão do arquivo
            _, file_extension = os.path.splitext(uploaded_santander.name)
            
            # Caso a extensão seja .xlsx ou .xls, lê o arquivo como Excel
            if file_extension in ['.xlsx', '.xls']:
                    
                if uploaded_santander is not None and uploaded_file2 is not None:
                    df1 = load_dataframe(uploaded_santander, header=2)  # Define o cabeçalho na linha 3
                    df2 = load_dataframe(uploaded_file2, header=6)

                    st.subheader("Conteúdo do arquivo 1")
                    df1_cleaned = df1.dropna(axis=1, how='all')  # Remove colunas que são todas None
                    st.write(df1_cleaned)

                    st.subheader("Conteúdo do arquivo 2")
                    df2_cleaned = df2.dropna(axis=1, how='all')  # Remove colunas que são todas None
                    df2_cleaned['Data'] = pd.to_datetime(df2_cleaned['Data'], errors='coerce').dt.strftime('%d/%m/%Y')
                    st.write(df2_cleaned)

                    if df1_cleaned is not None and df2_cleaned is not None:
                        if 'Saldo (R$)' in df1_cleaned.columns and 'Saldo-Exercício' in df2_cleaned.columns and 'Data' in df2_cleaned.columns:
                            # Remove os valores de texto da coluna 'Data' em df2 e converte para datetime
                            df2['Data'] = pd.to_datetime(df2['Data'], errors='coerce')

                            df1 = df1_cleaned.sort_values(by='Data', ascending=False).groupby('Data').first().reset_index() # DF1 DATAS AGRUPADAS
                            df1 = df1[['Data', 'Saldo (R$)']]
                            df2 = df2.groupby(df2['Data'].dt.date).tail(1).sort_values(by='Data')  # DF2 DATAS AGRUPADAS
                            df2 = df2[['Data', 'Saldo-Exercício']]
                            df2['Data'] = df2['Data'].dt.strftime('%d/%m/%Y')

                            
                            
                            # Limitando o número de linhas em cada DataFrame para o mesmo tamanho
                            min_len = min(len(df1), len(df2))
                            df1 = df1.reset_index()
                            df2 = df2.reset_index()
                            
                            df1 = df1.head(min_len)
                            df2 = df2.head(min_len)

                            # Mesclar os DataFrames com base nas datas
                            merged_df = pd.merge(df1, df2, how='outer', on='Data')

                            df_comparacao_styled = merged_df.style.apply(highlight_diff_santander, axis=1)

                            df_comparacao_styled = df_comparacao_styled.format({
                                'Saldo (R$)': formatar_moeda, 
                                'Saldo-Exercício': formatar_moeda
                            })
                            df_comparacao_styled.set_table_styles([{'selector': 'table', 'props': [('height', '1600px')]}])
                            st.subheader("Comparação Extrato Banco e Razão Relatório :")
                            st.write(df_comparacao_styled, unsafe_allow_html=True)

    elif banco_selecionado == 'Banrisul':
        uploaded_banrisul = st.file_uploader("Selecione Extrato BANRISUL", type=["xlsx", "xls"])
        # Upload Domínio Extrato Razão
        uploaded_file2 = st.file_uploader("SELECIONE EXTRATO RAZÃO SISTEMA DOMÍNIO", type=["xlsx", "xls"])

    elif banco_selecionado == 'Caixa Econômica':
        uploaded_cef = st.file_uploader("Selecione Extrato CAIXA ECONÔMICA", type=["pdf"])
       
        # Upload Domínio Extrato Razão
        uploaded_file2 = st.file_uploader("SELECIONE EXTRATO RAZÃO SISTEMA DOMÍNIO", type=["xlsx", "xls"])
        

        if uploaded_cef is not None:
            df = read_pdf_to_dataframe(uploaded_cef)
            st.write(df)

    elif banco_selecionado == 'Bradesco':
        uploaded_cef = st.file_uploader("Selecione Extrato BRADESCO", type=["xlsx", "xls"])
        # Upload Domínio Extrato Razão
        uploaded_file2 = st.file_uploader("SELECIONE EXTRATO RAZÃO SISTEMA DOMÍNIO", type=["xlsx", "xls"])
    else:
        st.write("Você nao selelecionou")
    

    


if __name__ == "__main__":
    main()