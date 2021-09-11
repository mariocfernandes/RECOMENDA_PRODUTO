import pandas as pd
import streamlit as st
import openpyxl
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix

st.title('GRUPO GF')
st.header('Recomendador de Produtos T&F')

# carrega arquivos

arquivo1 = 'compras_clientes_tf.xlsx'
colunas1 = ['Codigo_Cliente','Cliente Varejo','Produto','Qtde','Desc Produto']



@st.cache
def get_data():
    return pd.read_excel(arquivo1, dtype={'Codigo_Cliente':object},  usecols = colunas1,engine='openpyxl')[colunas1]

total= get_data()
df = get_data()

df = df.groupby(['Codigo_Cliente','Produto'])['Qtde'].sum()
df = df.reset_index()

cliente_pivot = df.pivot_table(index = 'Codigo_Cliente', columns = 'Produto', values = 'Qtde')

cliente_pivot.fillna(0,inplace = True)

cliente_sparse = csr_matrix(cliente_pivot)

model = NearestNeighbors(algorithm = 'brute',n_jobs= -1)
model.fit(cliente_sparse)

# Fazendo as Predicoes


    
#cod_cliente = st.sidebar.text_input('Digite o Codigo do Cliente : ')

lista_nomes  = total['Cliente Varejo'].unique().tolist()

escolha_nome = st.sidebar.selectbox("Nome do Cliente",lista_nomes)

df_filtro = total['Cliente Varejo']  == escolha_nome

cod_cliente = total[df_filtro].iloc[0,0]
st.sidebar.text(cod_cliente)
  
    
    
if cliente_pivot[cliente_pivot.index == cod_cliente].shape[0] > 0:
    
    distances, suggestions = model.kneighbors(cliente_pivot[cliente_pivot.index == cod_cliente].values.reshape(1,-1))
    
    
    objetivo = total[total.Codigo_Cliente == cod_cliente]
    nome_cliente = objetivo.iloc[0,1]
    #st.sidebar.text(nome_cliente)
    
    
    
    ind = suggestions.reshape(-1)
    
    
    clientes_similares = []
    for i in range(1,5):
       clientes_similares.append(cliente_pivot.index[ind[i]])        
    
    df_similar = pd.DataFrame(columns = objetivo.columns.to_list())
    
    for i in clientes_similares:
        similar = total[total.Codigo_Cliente == i]
        t = similar.merge(objetivo, how = 'left', on = 'Produto', indicator = True)
        t = t[t._merge == 'left_only']
        df_similar = pd.concat([df_similar,t])  
    
    
    df_similar = df_similar[['Produto','Desc Produto_x']]
    st.table(df_similar)
    
