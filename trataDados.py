import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Tratamento de Dados",
    layout="wide"

)

def ler_arquivo_excel(caminho_arquivo):
    try:
        # Verifica se o objeto UploadedFile não está vazio
        if arquivo is not None:
            # Obtém o nome do arquivo
            nome_arquivo = arquivo.name
            
            # Verifica a extensão do arquivo
            if nome_arquivo.endswith('.xls') or nome_arquivo.endswith('.xlsx'):
                # Lê o arquivo Excel e retorna um DataFrame do Pandas
                df = pd.read_excel(arquivo)
                return df
            else:
                st.error("O arquivo selecionado não é um arquivo Excel (.xls ou .xlsx).")
        else:
            st.error("Nenhum arquivo selecionado.")
    except Exception as e:
        st.error(f"Ocorreu um erro ao ler o arquivo: {str(e)}")

def remover_colunas_em_branco(df):
    # Remove colunas em branco (com todos os valores NaN)
    df_sem_nan = df.dropna(axis=1, how='all')
    return df_sem_nan

def definir_header(df, linha_header):
    try:
        # Obtém a linha de cabeçalho
        novo_header = df.iloc[linha_header]

        # Preenche valores vazios com uma string padrão
        

        # Remove a linha do cabeçalho do DataFrame
        df_sem_header = df.iloc[linha_header + 1:].reset_index(drop=True).dropna(axis=1, how='all')
        
        
        # Define a linha de cabeçalho ajustada como o novo cabeçalho do DataFrame
        df_sem_header.columns = novo_header
        if len(df_sem_header.columns) == len(df_sem_header.iloc[novo_header]):
            df_sem_header.columns = df_sem_header.iloc[novo_header]

        return df_sem_header
    except Exception as e:
        st.error(f"Ocorreu um erro ao definir o cabeçalho: {str(e)}")

def exportar_para_excel(df):
    """
    Função para exportar um DataFrame para um arquivo Excel.

    Parâmetros:
        df (pd.DataFrame): O DataFrame a ser exportado.
    """
    try:
        # Exportar o DataFrame para um arquivo Excel
        df.to_excel("dados_modificados.xlsx", index=False)
        st.success("DataFrame exportado com sucesso para 'dados_modificados.xlsx'.")
    except Exception as e:
        st.error(f"Ocorreu um erro ao exportar os dados para Excel: {str(e)}")


# Exemplo de uso
if __name__ == '__main__':
    st.title("Leitor de Arquivo Excel")
    
    # Interface para selecionar o arquivo
    arquivo = st.file_uploader("Selecione um arquivo Excel (.xls ou .xlsx)", type=['xls', 'xlsx'])
    
    if arquivo is not None:
        # Lê o arquivo Excel
        df = ler_arquivo_excel(arquivo)
        
        # Mostra os dados do arquivo Excel
        if df is not None:
            st.write("Dados do arquivo Excel:")
            st.write(df)
        
        

        # Caixa de seleção para escolher a linha do cabeçalho
        linha_header = st.selectbox("Selecione a linha que contém o cabeçalho:", options=range(len(df)), index=0)

        # Botão para definir o cabeçalho e exportar o DataFrame
        if st.button("Definir Cabeçalho e Exportar"):
            df = definir_header(df, linha_header)
            st.write("DataFrame Após Definir Cabeçalho:")
            st.write(df)
            #exportar_para_excel(df)

        # Botão para remover colunas em branco
        if st.button("Remover Colunas em Branco"):
            df = remover_colunas_em_branco(df)
            st.write("DataFrame Após Remoção de Colunas em Branco:")
            st.write(df)