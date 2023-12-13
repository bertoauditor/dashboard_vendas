import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time


@st.cache_data
def convert_csv(dataframe):
    return dataframe.to_csv(index=False).encode('latin1')


def message_sucess():
    sucesso = st.success('Download realizado com sucesso', icon='✅')
    time.sleep(5)
    sucesso.empty()


url = "https://labdados.com/produtos"
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(
    dados['Data da Compra'], format='%d/%m/%Y')
st.title('Dados Brutos')
with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(
        dados.columns), list(dados.columns))

st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do Produto'):
    produtos = st.multiselect(
        'Selecione o produto', dados['Produto'].unique(), dados['Produto'].unique())

with st.sidebar.expander('Preço do Produto'):
    preco = st.slider('Selecione o preço do produto',
                      min_value=0, max_value=5000, value=(0, 5000))

with st.sidebar.expander('Data da Compra'):
    data_compra = st.date_input('Selecione o período', min_value=dados['Data da Compra'].min(
    ), max_value=dados['Data da Compra'].max(), value=(dados['Data da Compra'].min(), dados['Data da Compra'].max()))

with st.sidebar.expander('Categoria do Produto'):
    categorias = st.multiselect('Selecione a categoria', dados['Categoria do Produto'].unique(
    ), dados['Categoria do Produto'].unique())

with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect(
        'Selecione o vendedor', dados['Vendedor'].unique(), dados['Vendedor'].unique())

with st.sidebar.expander('Local da Compra'):
    local_compra = st.multiselect('Selecione o local da compra', dados['Local da compra'].unique(
    ), dados['Local da compra'].unique())

with st.sidebar.expander('Tipo de pagamento'):
    tipo_pagamento = st.multiselect('Selecione o tipo de pagamento', dados['Tipo de pagamento'].unique(
    ), dados['Tipo de pagamento'].unique())

with st.sidebar.expander('Avaliação da compra'):
    aval_compra = st.multiselect('Selecione a avaliação da compra', dados['Avaliação da compra'].unique(
    ), dados['Avaliação da compra'].unique())

query = '''
Produto in @produtos and \
@preco[0]<=Preço<=@preco[1] and \
@data_compra[0]<=`Data da Compra`<=@data_compra[1] and \
`Categoria do Produto` in @categorias and \
Vendedor in @vendedores and \
`Local da compra` in @local_compra and \
`Tipo de pagamento` in @tipo_pagamento and \
`Avaliação da compra`in @aval_compra

'''
dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)

st.markdown(
    f'A tabela possui {dados_filtrados.shape[0]} linhas e {dados_filtrados.shape[1]} colunas')

st.markdown('Digite o nome do arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input(
        '', label_visibility='collapsed', value='dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer Download da tabela em CSV', file_name=nome_arquivo, data=convert_csv(
        dados_filtrados), mime='text/csv', on_click=message_sucess)
