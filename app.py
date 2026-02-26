import streamlit as st
import pandas as pd
import io 
from PIL import Image 

def preparar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Lista')
    return output.getvalue()

favicon = Image.open("image/icon.png")
logo_consul = Image.open("image/logo_consulpam.png")

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

try:
    st.sidebar.image(logo_consul, caption="Instituto Consulpam", use_container_width=True)
except:
    st.sidebar.write("Logo Consulpam")

st.sidebar.markdown("---")

# upload
st.sidebar.header("Configurações") # cria a barra lateral 
data_corte = st.sidebar.date_input("Data da Realização da Inscrição", value=pd.Timestamp.now())
arquivo_postado = st.sidebar.file_uploader(
    "Carregue sua planilha (XLSX ou XLS)",
    type=["xlsx", "xls"]
)

# tratamento de erro
if arquivo_postado is not None:
    try:
        # verifica qual é o tipo do arquivo
        nome_arquivo = arquivo_postado.name 

        if nome_arquivo.endswith('.xls'): 
            # o "engine" aqui funciona para que o pandas saiba que esta sendo lido com uma versão mais antiga
            df = pd.read_excel(arquivo_postado, engine='xlrd') 
            st.info(f"Processando arquivo (.xls): {nome_arquivo}")
        else:
            df = pd.read_excel(arquivo_postado) # por padrão o pandas lê os arquivos modernos assim
            st.success(f"Processando arquivo (.xlsx): {nome_arquivo}")

        if "NASCIMENTO" in df.columns:
            # Converte a coluna para o formato de data (Datetime)
            # errors='coerce' garante que datas inválidas virem 'NaT' (vazio) e não travem o código
            df["NASCIMENTO"] = pd.to_datetime(df["NASCIMENTO"], errors='coerce')
            
            # Data de hoje
            hoje = pd.Timestamp.now()
            
            # "(hoje - df["NASCIMENTO"])" - o resultado disto gera um objeto chamado 'Timedelta'
                # ele guarda o intervalo exato de tempo entre as duas datas (ex: "12450 days 08:30:15").
                
            # ".dt.days" - do 'Timedelta' extraimos o que importa: '.dt' é uma chave que permite entrar nas propriedades de data da coluna inteira. '.days' pega apenas o número total de dias vividos pelo candidato até hoje 
            
            # e por fim a "/ 365.25" transforma os dias em anos. o ".25" é por que a cada 4 anos temos um ano bissexto (366 dias). Isso permite que não descole alguns dias.
            idades_calculadas = (hoje - df["NASCIMENTO"]).dt.days / 365.25

            media_idade = idades_calculadas.mean()
        else:
            media_idade = 0
            st.warning("Coluna 'NACIMENTO' não encontrada para calcular a idade")
        
        # criando uma coluna que não existe no excel original 
        if "NASCIMENTO" in df.columns:
            # Convertendo a data de corte para o formato do Pandas para a conta bater 
            data_referencia = pd.Timestamp(data_corte)
            
            df["IDADE_CONCURSO"] = (data_referencia - pd.to_datetime(df["NASCIMENTO"])).dt.days / 365.25
            
            df_idosos = df[df["IDADE_CONCURSO"] >= 60]
        else:
            df_idosos = pd.DataFrame()
            
        st.subheader("Resumo da Planilha")
        c1, c2, c3 = st.columns(3)

        # qnt. de linhas e colunas
        c1.metric("Candidatos", len(df))
        c2.metric("Média de Idade", f"{media_idade:.1f} anos" if media_idade > 0 else "N/A")
        c3.metric("Idosos(+60)", len(df_idosos))
        
        st.markdown("### Visualização dos Candidatos")
        # usado para ter uma melhor pesquisa com as info dentro dos cartôes
        st.dataframe(df, use_container_width=True)
        
        tab_idosos, = st.tabs(["Idosos"])
            
        with tab_idosos:
            if not df_idosos.empty:
                st.write(f"Candidatos com 60 anos ou mais em {data_corte.strftime('%d/%m/%Y')}")

                ficheiro_idosos = preparar_excel(df_idosos)
                st.download_button(
                    label="Baixar lista (.xlsx)",
                    data=ficheiro_idosos,
                    file_name="candidatos_idosos.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                st.dataframe(df_idosos, use_container_width=True)
            
            else:
                st.info("Nenhum candidato idoso encontrado.")
        
        coluna_negro = "NEGRO"
        coluna_pcd = "DEFICIENTE"

        # aplicar filtros de forma case-insensitive e sem considerar NaN
        if coluna_negro in df.columns:
            # ".astype(str) - converte todos os valores de uma Series/coluna para strings"
            df_negros = df[df[coluna_negro].astype(str).str.contains("SIM", case=False, na=False)]
        else:
            # cria um data frame vazia
            df_negros = pd.DataFrame()
            st.warning("Atenção: Coluna 'NEGRO' não encontrada na planilha.")

        if coluna_pcd in df.columns:
            df_pcd = df[df[coluna_pcd].astype(str).str.contains("SIM", case=False, na=False)]
        else:
            df_pcd = pd.DataFrame()
            st.warning("Atenção: Coluna 'DEFICIENTE' não encontrada na planilha.")

        # corrigir verificação booleana usando 'and' (não o operador bitwise '&' aplicado incorretamente antes)
        if (coluna_negro in df.columns) and (coluna_pcd in df.columns):
            mask_negro = df[coluna_negro].astype(str).str.contains("SIM", case=False, na=False)
            mask_pcd = df[coluna_pcd].astype(str).str.contains("SIM", case=False, na=False)
            df_misto = df[mask_negro & mask_pcd]
        else:
            df_misto = pd.DataFrame()

        st.markdown("---")
        
        # onde vai aparecer as métricas
        st.subheader("Estatísticas de Cotas")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total", len(df))
        m2.metric("Negros", len(df_negros))
        m3.metric("PCD", len(df_pcd))
        m4.metric("Negros e PCD", len(df_misto))

        tab_geral, tab_negros, tab_pcd, tab_misto = st.tabs(["Todos", "Negros", "PCD", "Negros e PCD"])

        with tab_geral:
            st.dataframe(df, use_container_width=True)

        with tab_negros:
            if not df_negros.empty:
                st.dataframe(df_negros, use_container_width=True)
            else:
                st.warning("Nenhum candidato Negro encontrado.")

        with tab_pcd:
            if not df_pcd.empty:
                st.dataframe(df_pcd, use_container_width=True)
            else:
                st.warning("Nenhum candidato Pcd encontrado.")

        with tab_misto:
            if not df_misto.empty:
                st.dataframe(df_misto, use_container_width=True)
            else:
                st.warning("Nenhum candidato que seja Negro e PCD encontrado.")

    except PermissionError:
        st.error("Erro: Feche a planilha no Excel antes de carregar aqui!")
    except ImportError:
        st.error("Erro: Instale o pacote 'openpyxl' para ler arquivos .xlsx")
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado.")
        st.info(f"Detalhe técnico: {e}")
    
else:
    st.info("Aguardando o upload de uma planilha...")