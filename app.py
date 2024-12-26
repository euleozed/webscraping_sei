import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards
from datetime import datetime

# Configurações da página
st.set_page_config(page_title='Timeline', layout='wide', page_icon='⏳', initial_sidebar_state='expanded')

# Carregar arquivos
df = pd.read_csv(r'./data/processed/df_andamento.csv',
                 dtype={'Usuário': str,
                        'Protocolo': str},
                 parse_dates=['Data/Hora'])
df_objeto = pd.read_excel(r'./data/database/objetos.xlsx',
                          sheet_name='objetos')
df_objeto = df_objeto.rename(columns={'numero_processo': 'Processo'})

# Título
st.markdown("<h1 style='text-align: center;'>LINHA DO TEMPO DE PROCESSOS EM ANDAMENTO ⏳</h1>", unsafe_allow_html=True)
# ---------------------------------------------------------------------------------

# APRESENTAR A DATA DE ATUALIZAÇÃO
today = datetime.now().strftime("%d/%m/%Y")
st.text(f"Data da Última Atualização: {today}")

# Definir colunas
c1, c2, c3 = st.columns(3)
qtd_processos = df['Processo'].nunique()
df_termos = df[df['Documento'] == 'Termo de Referência'].groupby('Protocolo')['Documento'].size().reset_index()
qtd_termos = df_termos['Protocolo'].count()

df_qtd_documentos_gecomp = df[(df['Unidade'] == 'SESAU-GECOMP') &
    (~df['Documento'].str.contains('remetido', case=False, na=False))].groupby('Protocolo')['Documento'].size().reset_index()
qtd_documentos_gecomp = df_qtd_documentos_gecomp['Protocolo'].count()

c1.metric("Quantidade de Processos na Base de Dados:", value=qtd_processos)
c2.metric("Quantidade de Termos de Referência Elaborados:", qtd_termos)
c3.metric("Quantidade de Documentos Elaborados pela GECOMP:", value=qtd_documentos_gecomp)
style_metric_cards(background_color= 'rainbow')

# st.markdown("<h3 style='text-align: center;'>LINHA DO TEMPO DE PROCESSOS EM ANDAMENTO</h3>", unsafe_allow_html=True)
st.divider()

# Convertendo 'Data/Hora' para datetime
df['Data/Hora'] = pd.to_datetime(df['Data/Hora'], errors='coerce')

# Ordenando o DataFrame pelo número do processo e pela data
df = df.sort_values(by=['Processo', 'Data/Hora'])

# Criando a coluna para a quantidade de dias entre o documento 2 e o documento 1
df['Dias entre Documentos'] = df.groupby('Processo', sort=False)['Data/Hora'].diff().dt.days

# Preenchendo valores NaN com 0
# df['Dias entre Documentos'] = df['Dias entre Documentos'].fillna(0)

# Criando a coluna para a quantidade de dias acumulados entre o primeiro documento e o documento atual
df['Dias Acumulados'] = df.groupby('Processo')['Data/Hora'].transform(lambda x: (x - x.min()).dt.days)

# Removendo linhas duplicadas
df = df.drop_duplicates(keep='last')

# Mesclar df e df_objeto com base na coluna 'Processo'
df_combinado = pd.merge(df, df_objeto, on='Processo', how='inner')

# Criar lista combinando número do processo e o texto do objeto
opcoes = (df_combinado['Processo'].astype(str) + ' - ' + df_combinado['objeto'].astype(str)).unique()

# Inicializando df_selected como um DataFrame vazio
df_selected = pd.DataFrame()

# Entrada de texto para palavra-chave
palavra_chave = st.text_input("Digite uma palavra-chave para buscar o processo:")

# Filtrar opções com base na palavra-chave
opcoes_filtradas = [opcao for opcao in opcoes if palavra_chave.lower() in opcao.lower()] if palavra_chave else opcoes

# Criando o selectbox para escolher o processo entre as opções filtradas
processo_selecionado = st.selectbox('Selecione o processo:', options=opcoes_filtradas)

# # Função para filtrar opções com base na palavra-chave
# def filtrar_opcoes(palavra_chave, opcoes):
#     return [opcao for opcao in opcoes if palavra_chave.lower() in opcao.lower()]

# # Criando o selectbox para escolher o processo
# processo_selecionado = st.selectbox('Selecione o processo:', options=opcoes.unique())

# Verificando se um processo foi selecionado
if processo_selecionado:
    # Separar o número do processo selecionado
    processo_escolhido = processo_selecionado.split(' - ')[0]

    # Filtrando o DataFrame com base no processo selecionado
    df_selected = df_combinado[df_combinado['Processo'] == processo_escolhido]

    # Definindo o novo registro
    data_hoje = datetime.now()
    novo_registro = {
        'Processo': processo_escolhido,
        'Data/Hora': data_hoje,
        'Documento': "Dias desde a última movimentação",
        'Unidade': '',
        'Dias entre Documentos': 0,
        'Dias Acumulados': 0
    }
    

    # Adicionando o novo registro ao DataFrame
    df_selected = pd.concat([df_selected, pd.DataFrame([novo_registro])], ignore_index=True)

    # Converter a coluna 'Data' para datetime
    df_selected['Data/Hora'] = pd.to_datetime(df_selected['Data/Hora'])

    # Recalculando as colunas 'Dias entre Documentos' e 'Dias Acumulados'
    df_selected['Dias entre Documentos'] = df_selected.groupby('Processo')['Data/Hora'].diff().dt.days + 1
    df_selected['Dias Acumulados'] = df_selected.groupby('Processo')['Data/Hora'].transform(lambda x: (x - x.min()).dt.days)

    # Ajustando os valores nulos de 'Dias entre Documentos'
    df_selected['Dias entre Documentos'] = df_selected['Dias entre Documentos'].fillna(0)

    # Criar uma coluna de rótulo com 'Documento' e 'Dias entre Documentos'
    df_selected['Rotulo'] = df_selected['Documento'] + ': ' + df_selected['Dias entre Documentos'].astype(int).astype(str) + 'd' + ' - ' + df_selected['Protocolo']

    # Converter a data para formato legível
    df_selected['Data Documento'] = df_selected['Data/Hora'].dt.strftime('%d/%m/%y')

    
    # TABELA DE MOVIMENTAÇÕES
    st.markdown(f"<h5 style='text-align: center;'>Tabela de Movimentações do Processo: {processo_escolhido}</h5>", unsafe_allow_html=True)
    df_table = df_selected[['Data/Hora', 'Unidade', 'Nome', 'Protocolo', 'Documento', 'Data Documento', 'Dias entre Documentos', 'Dias Acumulados']].sort_values(by='Data/Hora', ascending=False)
    
    # Drop duplicadas
    # Mantém a última duplicata e remove as anteriores
    df_table = df_table.drop_duplicates(keep='last')
    st.dataframe(df_table, hide_index=True, width=1750, height=450)
    st.divider()

    # MÉTRICAS
    # Definir as variáveis
    df_termos = df_selected[df_selected['Documento'] == 'Termo de Referência'].groupby('Protocolo')['Documento'].size().reset_index()
    qtd_termos = df_termos['Protocolo'].count()
    qtd_setores = df_selected['Unidade'].nunique()
    
    df_qtd_documentos_gecomp = df_selected[(df_selected['Unidade'] == 'SESAU-GECOMP') &
    (~df_selected['Documento'].str.contains('remetido', case=False, na=False))].groupby('Protocolo')['Documento'].size().reset_index()
    qtd_documentos_gecomp = df_qtd_documentos_gecomp['Protocolo'].count()

    # Definir as colunas
    c1, c2 = st.columns(2)
    c1.metric("Quantidade de Termos de Referência no Processo:", qtd_termos)
    c1.metric("Quantidade de Setores Envolvidos:", qtd_setores)
    c1.metric("Quantidade de Documentos Produzidos pela GECOMP:", qtd_documentos_gecomp)


    # GRÁFICO DE RADAR POR UNIDADE    
    # tempo máximo em cada setor
    df_tempo_maximo = df_selected.groupby('Unidade').agg(Dias=("Dias entre Documentos", "max")).nlargest(10, 'Dias').sort_values(by="Dias").reset_index()
    
    # Figura
    fig_tempo_maximo = px.line_polar(df_tempo_maximo, r='Dias', theta='Unidade', line_close=True, text='Dias')
    
    fig_tempo_maximo.update_layout(
    polar=dict(
        bgcolor="rgba(0,0,0,0)",  # Cor de fundo azul claro
        radialaxis=dict(
            visible=False,
        ),
    ),
    showlegend=False
)
    c2.markdown(f"<h5 style='text-align: center;'>Tempo Máximo de Resposta Por Setor</h5>", unsafe_allow_html=True)
    c2.plotly_chart(fig_tempo_maximo)
    
    # TEMPO ACUMULADO EM CADA SETOR
    # Definir dataframe apenas com top 10 valores
    df_fig = df_selected.nlargest(10, 'Dias entre Documentos').sort_values(by='Data/Hora')

    st.markdown(f"<h5 style='text-align: center;'>Linha do Tempo do Processo: {processo_escolhido}</h5>", unsafe_allow_html=True)
    # Criar o gráfico
    fig = px.area(df_fig,
                  x='Data Documento',
                  y='Dias entre Documentos',
                  markers=True,
                  text='Rotulo')

    # Atualizar a posição dos rótulos
    fig.update_traces(textposition="top center", line_shape='spline')

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)
    st.divider()

    

    # Tabela de tempo de servidor GECOMP
    st.markdown(f"<h5 style='text-align: center;'>Análise Temporal dos Servidores GECOMP</h5>", unsafe_allow_html=True)
    st.text("A barra da cor laranja indica o maior período (dias) para a produção de um documento.")
    st.text("A barra da cor verde claro indica os dias acumulados de cada servido envolvido no processo. ")
    st.text("A barra da cor azul indica a quantidade de aparições do servidor no processso.")
    df_tempo_servidor = df_selected.groupby('Nome').agg(Dias_Maximo=("Dias entre Documentos", "max"),
                                                        Dias_Acumulados=("Dias entre Documentos", "sum"),
                                                        Aparicao=("Protocolo", "count")).sort_values(by="Dias_Maximo", ascending=True).reset_index()
    
    # Transformar o DataFrame para o formato longo, necessário para barras agrupadas
    df_long = df_tempo_servidor.melt(id_vars="Nome", 
                                    value_vars=["Dias_Maximo", "Dias_Acumulados", "Aparicao"],
                                    var_name="Métrica", value_name="Valor")
    # Definindo cores personalizadas para cada métrica
    color_map = {
        "Dias_Maximo": "orange",
        "Dias_Acumulados": "#DAF7A6",
        "Aparicao": "blue"
    }
    # Criar gráfico de barras horizontais agrupadas
    fig_tempo_servidor = px.bar(df_long, 
                x="Valor", 
                y="Nome", 
                text_auto=True,
                height=750,
                color="Métrica", 
                orientation="h", 
                # title="Dias Máximo, Dias Acumulados e Aparições por Servidor",
                color_discrete_map=color_map,
                labels={"Nome": "Servidores", "Valor": "Valores"})
    
    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig_tempo_servidor)
    st.divider()

else:
    st.write("Por favor, selecione um processo.")



# ÁREA DE PROCESSOS ATRASADOS
# Para encontrar o registro mais recente de cada processo
df_atrasados = df_combinado.loc[df_combinado.groupby('Processo')['Data/Hora'].idxmax()]

# Selecionar apenas as colunas necessárias
df_atrasados = df_atrasados[['Processo', 'objeto', 'Data/Hora', 'Documento', 'Unidade', 'Nome']].reset_index(drop=True)
df_atrasados = df_atrasados.rename(columns={'Data/Hora': 'Data da Última Movimentação'})

# Converter a coluna 'Data da Última Movimentação' para datetime
df_atrasados['Data da Última Movimentação'] = pd.to_datetime(df_atrasados['Data da Última Movimentação'], format='%Y-%m-%d')

# Obter a data de hoje
data_hoje = datetime.now()

# Calcular a diferença de dias entre 'Data da Última Movimentação' e a data de hoje
df_atrasados['Dias desde a Última Movimentação'] = (data_hoje - df_atrasados['Data da Última Movimentação']).dt.days

# Formatar a data no formato dd-mm-aaaa
df_atrasados['Data da Última Movimentação'] = df_atrasados['Data da Última Movimentação'].dt.strftime('%d-%m-%Y')

# Ordenar pela coluna 'Dias desde a Última Movimentação' em ordem decrescente
df_atrasados = df_atrasados.sort_values(by='Dias desde a Última Movimentação', ascending=False)

# Criar filtros para os diferentes grupos de processos
mais_300_dias = df_atrasados[(df_atrasados['Dias desde a Última Movimentação'] >= 300)].shape[0]
mais_200_dias = df_atrasados[(df_atrasados['Dias desde a Última Movimentação'] >= 200) & (df_atrasados['Dias desde a Última Movimentação'] < 300)].shape[0]
mais_100_dias = df_atrasados[(df_atrasados['Dias desde a Última Movimentação'] >= 100)  & (df_atrasados['Dias desde a Última Movimentação'] < 200)].shape[0]
mais_50_dias = df_atrasados[(df_atrasados['Dias desde a Última Movimentação'] >= 50)  & (df_atrasados['Dias desde a Última Movimentação'] < 100)].shape[0]

st.markdown(f"<h3 style='text-align: center;'>Métrica de Processos Desde a Última Movimentação 🕰️</h3>", unsafe_allow_html=True)


# Exibir os metric cards
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Processos com +300:", value=mais_300_dias)
col2.metric(label="Processos com +200:", value=mais_200_dias)
col3.metric(label="Processos com +100:", value=mais_100_dias)
col4.metric(label="Processos com +50:", value=mais_50_dias)
style_metric_cards(background_color= 'rainbow')

st.markdown(f"<h5 style='text-align: center;'>Tabela do Processos</h5>", unsafe_allow_html=True)

# Filtro de dias usando st.slider
min_dias = df_atrasados['Dias desde a Última Movimentação'].min()
max_dias = df_atrasados['Dias desde a Última Movimentação'].max()

duracao = st.slider('Selecione o intervalo de dias:',
                    min_value=df_atrasados['Dias desde a Última Movimentação'].min(),
                    max_value=df_atrasados['Dias desde a Última Movimentação'].max(),
                    value=(min_dias, max_dias)
                    )

# Filtrar o DataFrame com base no intervalo selecionado

df_filtrado = df_atrasados[(df_atrasados['Dias desde a Última Movimentação'] >= duracao[0]) & 
                            (df_atrasados['Dias desde a Última Movimentação'] <= duracao[1])]


# Quantidade de processos atrasados
qtd_df_atrasados = df_filtrado['Processo'].count()
st.text(f"Quantidade de Processos: {qtd_df_atrasados}")

st.dataframe(df_filtrado, hide_index=True,
              width=1750,
            # height=750
              )
