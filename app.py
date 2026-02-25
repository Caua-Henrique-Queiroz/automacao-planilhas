import streamlit as st
import pandas as pd
from PIL import Image 

favicon = Image.open("image/icon.png")

# config. a página
st.set_page_config(
    page_title="Automação de Planilhas", 
    layout="wide",
    page_icon=favicon
)

col_logo, col_titulo = st.columns([1, 10])

# cabeçalho
with col_titulo: 
    st.title("Sistema de Tratamento de Dados")

with col_logo: 
    st.image(favicon, width=80)

st.markdown("---")

# upload
st.sidebar.header("Configurações") # cria a barra lateral 
arquivo_postado = st.sidebar.file_uploader(
    "Carregue sua planilha (XLSX ou XLS)",
    type=["xlsx", "xls"]
)

# tratamento de erro
if arquivo_postado is not None:
    try:
        nome_arquivo = arquivo_postado.name # verifica qual é tipo do arquivo

        if nome_arquivo.endswith('.xls'): 
            # o "engine" aqui funciona para que o pandas saiba que esta sendo lido com uma versão mais antiga
            df = pd.read_excel(arquivo_postado, engine='xlrd') 
            st.info(f"Processando arquivo (.xls): {nome_arquivo}")
        else:
            df = pd.read_excel(arquivo_postado) # por padrão o pandas lê os arquivos modernos assim
            st.success(f"Processando arquivo (.xlsx): {nome_arquivo}")

        st.subheader("Resumo da Planilha")
        c1, c2, c3 = st.columns(3)

        # qnt. de linhas e colunas
        c1.metric("Candidatos", len(df))
        c2.metric("Total de Colunas", len(df.columns))
        # o "split" transforma o nome em lista, o "[-1]" pega o último item da lista e por fim o "upper()" transforma em maiúsculo
        c3.metric("Extensão do Arquivo", nome_arquivo.split(".")[-1].upper())

        st.markdown("### Visualização dos Dados")
        # usado para ter uma melhor pesquisa com as info dentro dos cartôes
        st.dataframe(df, use_container_width=True)

    except PermissionError:
        st.error("Erro: Feche a planilha no Excel antes de carregar aqui!")
    except ImportError:
        st.error("Erro: Instale o pacote 'openpyxl' para ler arquivos .xlsx")
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado.")
        st.info(f"Detalhe técnico: {e}")
    
else:
    st.info("Aguardando o upload de uma planilha...")
    