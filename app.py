import streamlit as st
import pandas as pd
import numpy as np
import plotly as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import calendar
from datetime import datetime
import pycountry
from wordcloud import WordCloud

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Incidentes Migratórios",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título e descrição
st.title("Dashboard de Análise de Incidentes Migratórios")
st.markdown("""
Este dashboard analisa dados sobre incidentes envolvendo imigrantes, fornecendo insights sobre padrões, 
tendências e estatísticas relacionadas a estas ocorrências ao redor do mundo.
""")

# Função para carregar dados
@st.cache_data
def carregar_dados(arquivo=None):
    if arquivo is not None:
        try:
            # Verificar extensão do arquivo
            if arquivo.name.endswith('.csv'):
                df = pd.read_csv(arquivo)
            else:
                df = pd.read_excel(arquivo)
            return df, None
        except Exception as e:
            return None, str(e)
    else:
        # Criar DataFrame de exemplo com estrutura similar aos dados reais
        # (apenas para demonstração quando não há upload)
        data = {
            'LATITUDE': [31.650259, 31.59713, 31.94026, 31.506777, 59.1551, 32.45435],
            'LONGITUDE': [-110.366453, -111.73756, -113.01125, -109.315632, 28, -113.18402],
            'Incident Type': ['Shipwreck', 'Vehicle Accident', 'Dehydration', 'Violence', 'Drowning', 'Hypothermia'],
            'Region of Incident': ['North America', 'North America', 'North America', 'North America', 'Europe', 'North America'],
            'Incident Date': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05', '2023-05-12', '2023-06-08'],
            'Incident Year': [2023, 2023, 2023, 2023, 2023, 2023],
            'Month': ['January', 'February', 'March', 'April', 'May', 'June'],
            'Number of Dead': [12, 5, 3, 8, 15, 2],
            'Minimum Estimated Number of Missing': [3, 0, 2, 1, 5, 0],
            'Total Number of Dead and Missing': [15, 5, 5, 9, 20, 2],
            'Number of Survivors': [8, 12, 5, 3, 2, 4],
            'Number of Females': [6, 7, 2, 5, 8, 1],
            'Number of Males': [14, 10, 6, 7, 14, 5],
            'Number of Children': [3, 4, 1, 2, 7, 0],
            'Country of Origin': ['Guatemala', 'Mexico', 'Honduras', 'El Salvador', 'Syria', 'Mexico'],
            'Region of Origin': ['Central America', 'North America', 'Central America', 'Central America', 'Middle East', 'North America'],
            'Cause of Death': ['Drowning', 'Trauma', 'Dehydration', 'Violence', 'Drowning', 'Exposure'],
            'Country of Incident': ['United States', 'United States', 'United States', 'United States', 'Finland', 'United States'],
            'Migration Route': ['Mexico to US', 'Mexico to US', 'Central America to US', 'Central America to US', 'Middle East to Europe', 'Mexico to US'],
            'Location of Incident': ['Desert', 'Highway', 'Desert', 'Border', 'Sea', 'Mountains']
        }
        df = pd.DataFrame(data)
        return df, None

# Opção para upload de arquivo
st.sidebar.header("📊 Dados")
uploaded_file = st.sidebar.file_uploader("Carregar arquivo de dados", type=["xlsx", "xls", "csv"])

# Carregar dados
if uploaded_file is not None:
    df, erro = carregar_dados(uploaded_file)
    if erro:
        st.error(f"Erro ao carregar o arquivo: {erro}")
        st.stop()
    else:
        st.sidebar.success("✅ Dados carregados com sucesso!")
else:
    df, _ = carregar_dados()
    st.sidebar.warning("⚠️ Usando dados de exemplo. Carregue seu arquivo para análise real.")

# Converter Incident Date para datetime, se necessário
if 'Incident Date' in df.columns:
    try:
        df['Incident Date'] = pd.to_datetime(df['Incident Date'])
    except:
        pass

# Verificar e preencher valores nulos nos campos numéricos
colunas_numericas = [
    'Number of Dead', 'Minimum Estimated Number of Missing', 
    'Total Number of Dead and Missing', 'Number of Survivors',
    'Number of Females', 'Number of Males', 'Number of Children'
]

for col in colunas_numericas:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(0)

# Sidebar para filtros
st.sidebar.header("🔍 Filtros")

# Filtro de período
if 'Incident Year' in df.columns:
    anos_disponiveis = sorted(df['Incident Year'].unique())
    if len(anos_disponiveis) > 1:
        ano_selecionado = st.sidebar.multiselect(
            "Ano do Incidente",
            options=anos_disponiveis,
            default=anos_disponiveis
        )
        if ano_selecionado:
            df = df[df['Incident Year'].isin(ano_selecionado)]

# Filtro de região
if 'Region of Incident' in df.columns:
    regioes_disponiveis = sorted(df['Region of Incident'].unique())
    if len(regioes_disponiveis) > 1:
        regiao_selecionada = st.sidebar.multiselect(
            "Região do Incidente",
            options=regioes_disponiveis,
            default=regioes_disponiveis
        )
        if regiao_selecionada:
            df = df[df['Region of Incident'].isin(regiao_selecionada)]

# Filtro de tipo de incidente
if 'Incident Type' in df.columns:
    tipos_disponiveis = sorted(df['Incident Type'].unique())
    if len(tipos_disponiveis) > 1:
        tipo_selecionado = st.sidebar.multiselect(
            "Tipo de Incidente",
            options=tipos_disponiveis,
            default=tipos_disponiveis
        )
        if tipo_selecionado:
            df = df[df['Incident Type'].isin(tipo_selecionado)]

# Verificar se há dados após a filtragem
if len(df) == 0:
    st.warning("Não há dados disponíveis para os filtros selecionados.")
    st.stop()

# Dividir o dashboard em seções
tab1, tab2, tab3, tab4 = st.tabs(["📈 Visão Geral", "🗺️ Análise Geográfica", "👥 Demografia", "📊 Análise Detalhada"])

with tab1:
    st.header("Visão Geral dos Incidentes")
    
    # KPIs principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_incidentes = len(df)
        st.metric("Total de Incidentes", f"{total_incidentes:,}")
    
    with col2:
        if 'Total Number of Dead and Missing' in df.columns:
            total_mortos_desaparecidos = int(df['Total Number of Dead and Missing'].sum())
            st.metric("Total de Vítimas", f"{total_mortos_desaparecidos:,}")
    
    with col3:
        if 'Number of Survivors' in df.columns:
            total_sobreviventes = int(df['Number of Survivors'].sum())
            st.metric("Total de Sobreviventes", f"{total_sobreviventes:,}")
    
    with col4:
        if 'Number of Children' in df.columns:
            total_criancas = int(df['Number of Children'].sum())
            st.metric("Crianças Afetadas", f"{total_criancas:,}")
    
    st.markdown("---")
    
    # Tendência temporal
    if 'Incident Date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Incident Date']):
        st.subheader("Tendência de Incidentes ao Longo do Tempo")
        
        # Agrupamento por mês
        df_tempo = df.copy()
        df_tempo['Mês'] = df_tempo['Incident Date'].dt.to_period('M')
        incidentes_por_mes = df_tempo.groupby('Mês').size().reset_index(name='Incidentes')
        incidentes_por_mes['Mês'] = incidentes_por_mes['Mês'].astype(str)
        
        # Mortos e desaparecidos por mês
        if 'Total Number of Dead and Missing' in df.columns:
            vitimas_por_mes = df_tempo.groupby('Mês')['Total Number of Dead and Missing'].sum().reset_index()
            vitimas_por_mes['Mês'] = vitimas_por_mes['Mês'].astype(str)
            
            # Gráfico de linha combinado
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=incidentes_por_mes['Mês'],
                y=incidentes_por_mes['Incidentes'],
                name='Número de Incidentes',
                line=dict(color='blue', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=vitimas_por_mes['Mês'],
                y=vitimas_por_mes['Total Number of Dead and Missing'],
                name='Vítimas (mortos e desaparecidos)',
                line=dict(color='red', width=2),
                yaxis='y2'
            ))
            
            fig.update_layout(
                title='Evolução de Incidentes e Vítimas ao Longo do Tempo',
                xaxis=dict(title='Mês'),
                yaxis=dict(title='Número de Incidentes', showgrid=False),
                yaxis2=dict(title='Número de Vítimas', overlaying='y', side='right', showgrid=False),
                legend=dict(x=0.01, y=0.99),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Comparação por tipo de incidente
    if 'Incident Type' in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Incidentes por Tipo")
            
            incidentes_por_tipo = df['Incident Type'].value_counts().reset_index()
            incidentes_por_tipo.columns = ['Tipo de Incidente', 'Contagem']
            
            fig = px.bar(
                incidentes_por_tipo.sort_values('Contagem', ascending=False).head(10),
                x='Tipo de Incidente',
                y='Contagem',
                color='Contagem',
                color_continuous_scale='Blues',
                title='Top 10 Tipos de Incidentes'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Vítimas por Tipo de Incidente")
            
            if 'Total Number of Dead and Missing' in df.columns:
                vitimas_por_tipo = df.groupby('Incident Type')['Total Number of Dead and Missing'].sum().reset_index()
                vitimas_por_tipo.columns = ['Tipo de Incidente', 'Total de Vítimas']
                
                fig = px.pie(
                    vitimas_por_tipo.sort_values('Total de Vítimas', ascending=False).head(10),
                    values='Total de Vítimas',
                    names='Tipo de Incidente',
                    title='Distribuição de Vítimas por Tipo de Incidente',
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Análise Geográfica")
    
    # Mapa de calor dos incidentes
    st.subheader("Mapa de Calor de Incidentes")
    
    # Verificar se há coordenadas válidas
    if 'LATITUDE' in df.columns and 'LONGITUDE' in df.columns:
        # Limpar coordenadas inválidas
        df_map = df.copy()
        df_map = df_map.dropna(subset=['LATITUDE', 'LONGITUDE'])
        df_map = df_map[(df_map['LATITUDE'] >= -90) & (df_map['LATITUDE'] <= 90) & 
                       (df_map['LONGITUDE'] >= -180) & (df_map['LONGITUDE'] <= 180)]
        
        if len(df_map) > 0:
            # Adicionar uma coluna de tamanho se houver dados de vítimas
            if 'Total Number of Dead and Missing' in df_map.columns:
                df_map['marker_size'] = df_map['Total Number of Dead and Missing'].fillna(1)
                df_map.loc[df_map['marker_size'] == 0, 'marker_size'] = 1
                df_map['marker_size'] = np.log1p(df_map['marker_size']) * 5
            else:
                df_map['marker_size'] = 5
            
            # Adicionar texto para hover
            hover_text = []
            for idx, row in df_map.iterrows():
                texto = f"Local: {row.get('Location of Incident', 'N/A')}<br>"
                if 'Incident Type' in df_map.columns:
                    texto += f"Tipo: {row['Incident Type']}<br>"
                if 'Incident Date' in df_map.columns:
                    data = row['Incident Date']
                    if pd.api.types.is_datetime64_any_dtype(data):
                        texto += f"Data: {data.strftime('%d/%m/%Y')}<br>"
                    else:
                        texto += f"Data: {data}<br>"
                if 'Total Number of Dead and Missing' in df_map.columns:
                    texto += f"Vítimas: {int(row['Total Number of Dead and Missing'])}"
                hover_text.append(texto)
            
            # Criar mapa de densidade
            fig = go.Figure()
            
            # Adicionar mapa de calor
            fig.add_densitymapbox(
                lat=df_map['LATITUDE'],
                lon=df_map['LONGITUDE'],
                z=df_map.get('Total Number of Dead and Missing', np.ones(len(df_map))),
                radius=20,
                colorscale='Reds',
                colorbar=dict(title='Intensidade'),
                hoverinfo='none',
                opacity=0.7
            )
            
            # Adicionar pontos individuais
            fig.add_scattermapbox(
                lat=df_map['LATITUDE'],
                lon=df_map['LONGITUDE'],
                mode='markers',
                marker=dict(
                    size=df_map['marker_size'],
                    color='rgb(220, 20, 60)',
                    opacity=0.7
                ),
                text=hover_text,
                hoverinfo='text'
            )
            
            # Configurar layout do mapa
            fig.update_layout(
                mapbox_style="carto-positron",
                mapbox=dict(
                    center=dict(lat=df_map['LATITUDE'].mean(), lon=df_map['LONGITUDE'].mean()),
                    zoom=2
                ),
                margin=dict(r=0, t=0, l=0, b=0),
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Não há coordenadas válidas para exibir no mapa.")
    else:
        st.warning("As colunas de latitude e longitude não foram encontradas nos dados.")
    
    # Análise por região/país
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Country of Incident' in df.columns:
            st.subheader("Incidentes por País")
            
            paises_incidentes = df['Country of Incident'].value_counts().reset_index()
            paises_incidentes.columns = ['País', 'Incidentes']
            
            fig = px.choropleth(
                paises_incidentes,
                locations='País',
                locationmode='country names',
                color='Incidentes',
                color_continuous_scale='Blues',
                title='Número de Incidentes por País',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'Migration Route' in df.columns:
            st.subheader("Rotas Migratórias Mais Comuns")
            
            rotas = df['Migration Route'].value_counts().reset_index()
            rotas.columns = ['Rota', 'Frequência']
            
            fig = px.bar(
                rotas.sort_values('Frequência', ascending=False).head(10),
                x='Rota',
                y='Frequência',
                color='Frequência',
                color_continuous_scale='Blues',
                title='Top 10 Rotas Migratórias'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Análise Demográfica")
    
    # Distribuição por gênero e idade
    if all(col in df.columns for col in ['Number of Males', 'Number of Females', 'Number of Children']):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Distribuição por Gênero")
            
            total_genero = {
                'Gênero': ['Masculino', 'Feminino'],
                'Total': [df['Number of Males'].sum(), df['Number of Females'].sum()]
            }
            
            fig = px.pie(
                total_genero,
                values='Total',
                names='Gênero',
                color_discrete_sequence=['#1f77b4', '#ff7f0e'],
                hole=0.4
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Presença de Crianças")
            
            total_criancas = df['Number of Children'].sum()
            total_adultos = df['Number of Males'].sum() + df['Number of Females'].sum() - total_criancas
            
            dados_idade = {
                'Categoria': ['Adultos', 'Crianças'],
                'Total': [total_adultos, total_criancas]
            }
            
            fig = px.bar(
                dados_idade,
                x='Categoria',
                y='Total',
                color='Categoria',
                color_discrete_sequence=['#1f77b4', '#ff7f0e'],
                text='Total'
            )
            fig.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Análise por país/região de origem
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Country of Origin' in df.columns:
            st.subheader("Principais Países de Origem")
            
            paises_origem = df['Country of Origin'].value_counts().reset_index()
            paises_origem.columns = ['País de Origem', 'Contagem']
            
            fig = px.bar(
                paises_origem.sort_values('Contagem', ascending=False).head(10),
                x='País de Origem',
                y='Contagem',
                color='Contagem',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'Region of Origin' in df.columns:
            st.subheader("Regiões de Origem")
            
            regioes_origem = df['Region of Origin'].value_counts().reset_index()
            regioes_origem.columns = ['Região de Origem', 'Contagem']
            
            fig = px.pie(
                regioes_origem,
                values='Contagem',
                names='Região de Origem',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Taxa de sobrevivência
    if all(col in df.columns for col in ['Number of Survivors', 'Total Number of Dead and Missing']):
        st.markdown("---")
        st.subheader("Taxa de Sobrevivência por Tipo de Incidente")
        
        # Calcular taxa de sobrevivência por tipo de incidente
        if 'Incident Type' in df.columns:
            taxa_sobrev = df.groupby('Incident Type').agg({
                'Number of Survivors': 'sum',
                'Total Number of Dead and Missing': 'sum'
            }).reset_index()
            
            taxa_sobrev['Total'] = taxa_sobrev['Number of Survivors'] + taxa_sobrev['Total Number of Dead and Missing']
            taxa_sobrev['Taxa de Sobrevivência (%)'] = (taxa_sobrev['Number of Survivors'] / taxa_sobrev['Total'] * 100).round(1)
            
            # Ordenar por taxa e filtrar apenas os tipos com mais de 5 pessoas envolvidas
            taxa_sobrev = taxa_sobrev[taxa_sobrev['Total'] >= 5].sort_values('Taxa de Sobrevivência (%)', ascending=False)
            
            fig = px.bar(
                taxa_sobrev,
                x='Incident Type',
                y='Taxa de Sobrevivência (%)',
                color='Taxa de Sobrevivência (%)',
                color_continuous_scale='Blues',
                text='Taxa de Sobrevivência (%)'
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(height=500, xaxis_title='Tipo de Incidente', yaxis_title='Taxa de Sobrevivência (%)')
            st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("Análise Detalhada")
    
    # Causas de morte
    if 'Cause of Death' in df.columns:
        st.subheader("Principais Causas de Morte")
        
        causas = df['Cause of Death'].value_counts().reset_index()
        causas.columns = ['Causa', 'Contagem']
        
        # Criar nuvem de palavras
        try:
            wordcloud_data = dict(zip(causas['Causa'], causas['Contagem']))
            
            # Gerar nuvem de palavras
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white',
                colormap='Blues',
                max_words=50
            ).generate_from_frequencies(wordcloud_data)
            
            # Exibir
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        except:
            # Fallback se wordcloud falhar
            fig = px.pie(
                causas.head(10),
                values='Contagem',
                names='Causa',
                title='Top 10 Causas de Morte'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Análise sazonal (por mês)
    if 'Month' in df.columns:
        st.markdown("---")
        st.subheader("Padrão Sazonal de Incidentes")
        
        # Converter mês para ordem numérica para ordenação correta
        meses_ordem = {month: i for i, month in enumerate(calendar.month_name[1:], 1)}
        
        # Verificar se os meses estão como texto
        if df['Month'].dtype == 'object':
            try:
                # Tentar mapear os meses para números
                df_mes = df.copy()
                df_mes['Month_Num'] = df_mes['Month'].map(meses_ordem)
                
                # Agrupar por mês
                incidentes_por_mes = df_mes.groupby('Month').size().reset_index(name='Incidentes')
                
                # Adicionar número do mês para ordenação
                incidentes_por_mes['Month_Num'] = incidentes_por_mes['Month'].map(meses_ordem)
                
                # Ordenar por mês
                incidentes_por_mes = incidentes_por_mes.sort_values('Month_Num')
                
                # Gráfico
                fig = px.line(
                    incidentes_por_mes,
                    x='Month',
                    y='Incidentes',
                    markers=True,
                    title='Incidentes por Mês'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.warning("Não foi possível criar o gráfico de sazonalidade devido a problemas com o formato dos meses.")
    
    # Correlações entre variáveis numéricas
    st.markdown("---")
    st.subheader("Correlações Entre Variáveis")
    
    # Selecionar apenas colunas numéricas para correlação
    colunas_num = df.select_dtypes(include=['number']).columns.tolist()
    
    # Remover latitude e longitude para não distorcer a correlação
    colunas_num = [col for col in colunas_num if col.upper() not in ['LATITUDE', 'LONGITUDE']]
    
    if len(colunas_num) >= 3:
        # Calcular matriz de correlação
        corr = df[colunas_num].corr()
        
        # Criar heatmap
        fig = px.imshow(
            corr,
            text_auto='.2f',
            color_continuous_scale='RdBu_r',
            title='Matriz de Correlação das Variáveis Numéricas'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Não há variáveis numéricas suficientes para criar uma matriz de correlação.")
    
    # Exploração de dados individuais
    st.markdown("---")
    st.subheader("Exploração de Dados Individuais")
    
    # Permitir ao usuário selecionar registros específicos
    n_registros = min(10, len(df))
    mostrar_registros = st.slider("Número de registros para mostrar", 1, min(50, len(df)), n_registros)
    
    # Exibir dados
    st.dataframe(df.head(mostrar_registros))
    
    # Opção para download dos dados filtrados
    st.download_button(
        label="📥 Baixar dados filtrados (CSV)",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="dados_incidentes_filtrados.csv",
        mime="text/csv"
    )

# Rodapé
st.markdown("---")
st.caption("Dashboard desenvolvido para análise de dados de incidentes migratórios. Os dados são sensíveis e representam tragédias humanas.")
st.caption("Fonte: Dados de upload do usuário")
