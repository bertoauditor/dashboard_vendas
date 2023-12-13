import streamlit as st
import plotly.express as px
import pandas as pd
import requests

st.set_page_config(layout='wide')


def formata_numero(num, prefixo=''):
    for unidade in ['', 'mil']:
        if num < 1000:
            return (f'{prefixo} {num:.2f} {unidade}')
        num /= 1000
    return f'{prefixo} {num:.2f} milhões'


st.title('DASHBOARD DE VENDAS :shopping_trolley:')


url = "https://labdados.com/produtos"
regioes = ['Brasil', 'Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Selecione a região', regioes)
if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Todo o período', value=True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Selecione o ano', min_value=2020, max_value=2023)

query_string = {'regiao': regiao.lower(), 'ano': ano}

response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(
    dados['Data da Compra'], format='%d/%m/%Y')

vendedor = st.sidebar.multiselect(
    'Selecione os vendedores', list(dados['Vendedor'].unique()))
if vendedor:
    selecao = dados['Vendedor'].isin(vendedor)
    dados = dados[selecao]

# Tabelas de Receita
# Tabela da Receita por estado
receita_estados = dados.groupby('Local da compra')[
    ['Preço']].sum().sort_values('Preço', ascending=False)
df_temporario = dados[['Local da compra', 'lat', 'lon']].drop_duplicates()
receita_estados = receita_estados.merge(
    right=df_temporario, how='left', left_on='Local da compra', right_on='Local da compra')

# Tabela da Receita Mensal
receita_mensal = dados.set_index('Data da Compra').groupby(
    pd.Grouper(freq='M'))[['Preço']].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

# Tabela da Receita por Categorias
receita_categorias = dados.groupby(['Categoria do Produto'])[
    ['Preço']].sum().sort_values('Preço', ascending=False)


# Tabelas de Quantidade de Vendas


# Tabelas de Vendedores
vendedores = dados.groupby('Vendedor')[['Preço']].agg(['sum', 'count'])
vendedores.columns = ['soma', 'contagem']


# Graficos
# Grafico de Mapa Receita por estado
fig_mapa_receita_estados = px.scatter_geo(
    data_frame=receita_estados,
    lat='lat',
    lon='lon',
    scope='south america',
    size='Preço',
    template='seaborn',
    hover_name='Local da compra',
    hover_data={'lat': False, 'lon': False},
    title='Receita por estado')

# Grafico de Barra da Receita por estado
fig_receita_estados = px.bar(data_frame=receita_estados.head(),
                             x='Local da compra',
                             y='Preço',
                             text_auto=True,
                             template='seaborn',
                             title='Top Estados (Receita)'
                             )
fig_receita_estados.update_layout(yaxis_title='Receita')
fig_receita_estados.update_traces(textposition='outside')


# Grafico da Receita Mensal
fig_receita_mensal = px.line(data_frame=receita_mensal,
                             x='Mes',
                             y='Preço',
                             color='Ano',
                             line_dash='Ano',
                             markers=True,
                             template='seaborn',
                             range_y=(0, receita_mensal.max()),
                             title='Receita mensal')
fig_receita_mensal.update_layout(yaxis_title='Receita')

# Grafico da Receita por categorias
fig_receita_categorias = px.bar(data_frame=receita_categorias,
                                x=receita_categorias.index,
                                y='Preço',
                                template='seaborn',
                                title='Receita por Categoria de Produto',
                                text_auto=True)
fig_receita_categorias.update_traces(textposition='outside')
fig_receita_categorias.update_layout(yaxis_title='Receita')


# Visualização no streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])
with aba1:
    receita_total = formata_numero(dados['Preço'].sum())
    qtd_vendas = formata_numero(dados.shape[0])
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita Total', receita_total)
        st.plotly_chart(fig_mapa_receita_estados, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with coluna2:
        st.metric('Quantidade de Vendas', qtd_vendas)
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

with aba2:
    receita_total = formata_numero(dados['Preço'].sum())
    qtd_vendas = formata_numero(dados.shape[0])
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita Total', receita_total)

    with coluna2:
        st.metric('Quantidade de Vendas', qtd_vendas)

with aba3:
    receita_total = formata_numero(dados['Preço'].sum())
    qtd_vendas = formata_numero(dados.shape[0])
    qtd_vendedores = st.number_input(
        label='Número de vendedores?', min_value=1, max_value=15, value=5)

    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita Total', receita_total)
        fig_receita_vendedores = px.bar(data_frame=vendedores.sort_values('soma', ascending=False).head(qtd_vendedores),
                                        y=vendedores.sort_values('soma', ascending=False).head(
                                            qtd_vendedores).index,
                                        x='soma',
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (Soma das Vendas)',
                                        template='seaborn')
        fig_receita_vendedores.update_layout(xaxis_title='Soma das Vendas')
        st.plotly_chart(fig_receita_vendedores, use_container_width=True)

    with coluna2:
        st.metric('Quantidade de Vendas', qtd_vendas)
        fig_vendas_vendedores = px.bar(data_frame=vendedores.sort_values('contagem', ascending=False).head(qtd_vendedores),
                                       y=vendedores.sort_values('contagem', ascending=False).head(
                                           qtd_vendedores).index,
                                       x='contagem',
                                       text_auto=True,
                                       title=f'Top {qtd_vendedores} vendedores (Número de vendas)',
                                       template='seaborn')
        fig_vendas_vendedores.update_layout(xaxis_title='Número de Vendas')
        st.plotly_chart(fig_vendas_vendedores, use_container_width=True)
