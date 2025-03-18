import streamlit as st
import pandas as pd
import numpy as np
import plotly  as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import calendar
from datetime import datetime
import pycountry
from wordcloud import WordCloud

# Настройка страницы
st.set_page_config(
    page_title="Панель мониторинга миграционных инцидентов",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Заголовок и описание
st.title("Панель мониторинга анализа миграционных инцидентов")
st.markdown("""
Эта панель мониторинга анализирует данные об инцидентах с мигрантами, предоставляя аналитическую информацию 
о закономерностях, тенденциях и статистике, связанной с этими происшествиями по всему миру.
""")

# Функция для загрузки данных
@st.cache_data
def загрузить_данные(файл=None):
    if файл is not None:
        try:
            # Проверка расширения файла
            if файл.name.endswith('.csv'):
                df = pd.read_csv(файл)
            else:
                df = pd.read_excel(файл)
            return df, None
        except Exception as e:
            return None, str(e)
    else:
        # Создание примера DataFrame со структурой, аналогичной реальным данным
        # (только для демонстрации, когда нет загрузки)
        data = {
            'LATITUDE': [31.650259, 31.59713, 31.94026, 31.506777, 59.1551, 32.45435],
            'LONGITUDE': [-110.366453, -111.73756, -113.01125, -109.315632, 28, -113.18402],
            'Incident Type': ['Кораблекрушение', 'Автомобильная авария', 'Обезвоживание', 'Насилие', 'Утопление', 'Переохлаждение'],
            'Region of Incident': ['Северная Америка', 'Северная Америка', 'Северная Америка', 'Северная Америка', 'Европа', 'Северная Америка'],
            'Incident Date': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05', '2023-05-12', '2023-06-08'],
            'Incident Year': [2023, 2023, 2023, 2023, 2023, 2023],
            'Month': ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь'],
            'Number of Dead': [12, 5, 3, 8, 15, 2],
            'Minimum Estimated Number of Missing': [3, 0, 2, 1, 5, 0],
            'Total Number of Dead and Missing': [15, 5, 5, 9, 20, 2],
            'Number of Survivors': [8, 12, 5, 3, 2, 4],
            'Number of Females': [6, 7, 2, 5, 8, 1],
            'Number of Males': [14, 10, 6, 7, 14, 5],
            'Number of Children': [3, 4, 1, 2, 7, 0],
            'Country of Origin': ['Гватемала', 'Мексика', 'Гондурас', 'Эль-Сальвадор', 'Сирия', 'Мексика'],
            'Region of Origin': ['Центральная Америка', 'Северная Америка', 'Центральная Америка', 'Центральная Америка', 'Ближний Восток', 'Северная Америка'],
            'Cause of Death': ['Утопление', 'Травма', 'Обезвоживание', 'Насилие', 'Утопление', 'Воздействие окружающей среды'],
            'Country of Incident': ['Соединенные Штаты', 'Соединенные Штаты', 'Соединенные Штаты', 'Соединенные Штаты', 'Финляндия', 'Соединенные Штаты'],
            'Migration Route': ['Мексика в США', 'Мексика в США', 'Центральная Америка в США', 'Центральная Америка в США', 'Ближний Восток в Европу', 'Мексика в США'],
            'Location of Incident': ['Пустыня', 'Шоссе', 'Пустыня', 'Граница', 'Море', 'Горы']
        }
        df = pd.DataFrame(data)
        return df, None

# Опция для загрузки файла
st.sidebar.header("📊 Данные")
uploaded_file = st.sidebar.file_uploader("Загрузить файл с данными", type=["xlsx", "xls", "csv"])

# Загрузка данных
if uploaded_file is not None:
    df, ошибка = загрузить_данные(uploaded_file)
    if ошибка:
        st.error(f"Ошибка при загрузке файла: {ошибка}")
        st.stop()
    else:
        st.sidebar.success("✅ Данные успешно загружены!")
else:
    df, _ = загрузить_данные()
    st.sidebar.warning("⚠️ Использование примера данных. Загрузите свой файл для реального анализа.")

# Конвертация Incident Date в datetime, если необходимо
if 'Incident Date' in df.columns:
    try:
        df['Incident Date'] = pd.to_datetime(df['Incident Date'])
    except:
        pass

# Проверка и заполнение пустых значений в числовых полях
числовые_колонки = [
    'Number of Dead', 'Minimum Estimated Number of Missing', 
    'Total Number of Dead and Missing', 'Number of Survivors',
    'Number of Females', 'Number of Males', 'Number of Children'
]

for col in числовые_колонки:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(0)

# Боковая панель для фильтров
st.sidebar.header("🔍 Фильтры")

# Фильтр по периоду
if 'Incident Year' in df.columns:
    доступные_годы = sorted(df['Incident Year'].unique())
    if len(доступные_годы) > 1:
        выбранный_год = st.sidebar.multiselect(
            "Год инцидента",
            options=доступные_годы,
            default=доступные_годы
        )
        if выбранный_год:
            df = df[df['Incident Year'].isin(выбранный_год)]

# Фильтр по региону
if 'Region of Incident' in df.columns:
    доступные_регионы = sorted(df['Region of Incident'].unique())
    if len(доступные_регионы) > 1:
        выбранный_регион = st.sidebar.multiselect(
            "Регион инцидента",
            options=доступные_регионы,
            default=доступные_регионы
        )
        if выбранный_регион:
            df = df[df['Region of Incident'].isin(выбранный_регион)]

# Фильтр по типу инцидента
if 'Incident Type' in df.columns:
    доступные_типы = sorted(df['Incident Type'].unique())
    if len(доступные_типы) > 1:
        выбранный_тип = st.sidebar.multiselect(
            "Тип инцидента",
            options=доступные_типы,
            default=доступные_типы
        )
        if выбранный_тип:
            df = df[df['Incident Type'].isin(выбранный_тип)]

# Проверка наличия данных после фильтрации
if len(df) == 0:
    st.warning("Нет доступных данных для выбранных фильтров.")
    st.stop()

# Разделение панели мониторинга на секции
tab1, tab2, tab3, tab4 = st.tabs(["📈 Общий обзор", "🗺️ Географический анализ", "👥 Демография", "📊 Детальный анализ"])

with tab1:
    st.header("Общий обзор инцидентов")
    
    # Основные KPI
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        общее_число_инцидентов = len(df)
        st.metric("Всего инцидентов", f"{общее_число_инцидентов:,}")
    
    with col2:
        if 'Total Number of Dead and Missing' in df.columns:
            общее_число_погибших_пропавших = int(df['Total Number of Dead and Missing'].sum())
            st.metric("Всего жертв", f"{общее_число_погибших_пропавших:,}")
    
    with col3:
        if 'Number of Survivors' in df.columns:
            общее_число_выживших = int(df['Number of Survivors'].sum())
            st.metric("Всего выживших", f"{общее_число_выживших:,}")
    
    with col4:
        if 'Number of Children' in df.columns:
            общее_число_детей = int(df['Number of Children'].sum())
            st.metric("Пострадавших детей", f"{общее_число_детей:,}")
    
    st.markdown("---")
    
    # Временная тенденция
    if 'Incident Date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Incident Date']):
        st.subheader("Тенденция инцидентов во времени")
        
        # Группировка по месяцам
        df_время = df.copy()
        df_время['Месяц'] = df_время['Incident Date'].dt.to_period('M')
        инциденты_по_месяцам = df_время.groupby('Месяц').size().reset_index(name='Инциденты')
        инциденты_по_месяцам['Месяц'] = инциденты_по_месяцам['Месяц'].astype(str)
        
        # Погибшие и пропавшие по месяцам
        if 'Total Number of Dead and Missing' in df.columns:
            жертвы_по_месяцам = df_время.groupby('Месяц')['Total Number of Dead and Missing'].sum().reset_index()
            жертвы_по_месяцам['Месяц'] = жертвы_по_месяцам['Месяц'].astype(str)
            
            # Комбинированный линейный график
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=инциденты_по_месяцам['Месяц'],
                y=инциденты_по_месяцам['Инциденты'],
                name='Количество инцидентов',
                line=dict(color='blue', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=жертвы_по_месяцам['Месяц'],
                y=жертвы_по_месяцам['Total Number of Dead and Missing'],
                name='Жертвы (погибшие и пропавшие)',
                line=dict(color='red', width=2),
                yaxis='y2'
            ))
            
            fig.update_layout(
                title='Динамика инцидентов и жертв во времени',
                xaxis=dict(title='Месяц'),
                yaxis=dict(title='Количество инцидентов', showgrid=False),
                yaxis2=dict(title='Количество жертв', overlaying='y', side='right', showgrid=False),
                legend=dict(x=0.01, y=0.99),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Сравнение по типам инцидентов
    if 'Incident Type' in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Инциденты по типу")
            
            инциденты_по_типу = df['Incident Type'].value_counts().reset_index()
            инциденты_по_типу.columns = ['Тип инцидента', 'Количество']
            
            fig = px.bar(
                инциденты_по_типу.sort_values('Количество', ascending=False).head(10),
                x='Тип инцидента',
                y='Количество',
                color='Количество',
                color_continuous_scale='Blues',
                title='Топ-10 типов инцидентов'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Жертвы по типу инцидента")
            
            if 'Total Number of Dead and Missing' in df.columns:
                жертвы_по_типу = df.groupby('Incident Type')['Total Number of Dead and Missing'].sum().reset_index()
                жертвы_по_типу.columns = ['Тип инцидента', 'Всего жертв']
                
                fig = px.pie(
                    жертвы_по_типу.sort_values('Всего жертв', ascending=False).head(10),
                    values='Всего жертв',
                    names='Тип инцидента',
                    title='Распределение жертв по типу инцидента',
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Географический анализ")
    
    # Тепловая карта инцидентов
    st.subheader("Тепловая карта инцидентов")
    
    # Проверка наличия действительных координат
    if 'LATITUDE' in df.columns and 'LONGITUDE' in df.columns:
        # Очистка недействительных координат
        df_map = df.copy()
        df_map = df_map.dropna(subset=['LATITUDE', 'LONGITUDE'])
        df_map = df_map[(df_map['LATITUDE'] >= -90) & (df_map['LATITUDE'] <= 90) & 
                       (df_map['LONGITUDE'] >= -180) & (df_map['LONGITUDE'] <= 180)]
        
        if len(df_map) > 0:
            # Добавление размера маркера, если есть данные о жертвах
            if 'Total Number of Dead and Missing' in df_map.columns:
                df_map['marker_size'] = df_map['Total Number of Dead and Missing'].fillna(1)
                df_map.loc[df_map['marker_size'] == 0, 'marker_size'] = 1
                df_map['marker_size'] = np.log1p(df_map['marker_size']) * 5
            else:
                df_map['marker_size'] = 5
            
            # Добавление текста для наведения
            hover_text = []
            for idx, row in df_map.iterrows():
                текст = f"Место: {row.get('Location of Incident', 'N/A')}<br>"
                if 'Incident Type' in df_map.columns:
                    текст += f"Тип: {row['Incident Type']}<br>"
                if 'Incident Date' in df_map.columns:
                    дата = row['Incident Date']
                    if pd.api.types.is_datetime64_any_dtype(дата):
                        текст += f"Дата: {дата.strftime('%d/%m/%Y')}<br>"
                    else:
                        текст += f"Дата: {дата}<br>"
                if 'Total Number of Dead and Missing' in df_map.columns:
                    текст += f"Жертвы: {int(row['Total Number of Dead and Missing'])}"
                hover_text.append(текст)
            
            # Создание карты плотности
            fig = go.Figure()
            
            # Добавление тепловой карты
            fig.add_densitymapbox(
                lat=df_map['LATITUDE'],
                lon=df_map['LONGITUDE'],
                z=df_map.get('Total Number of Dead and Missing', np.ones(len(df_map))),
                radius=20,
                colorscale='Reds',
                colorbar=dict(title='Интенсивность'),
                hoverinfo='none',
                opacity=0.7
            )
            
            # Добавление отдельных точек
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
            
            # Настройка макета карты
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
            st.warning("Нет действительных координат для отображения на карте.")
    else:
        st.warning("Столбцы широты и долготы не найдены в данных.")
    
    # Анализ по региону/стране
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Country of Incident' in df.columns:
            st.subheader("Инциденты по странам")
            
            страны_инциденты = df['Country of Incident'].value_counts().reset_index()
            страны_инциденты.columns = ['Страна', 'Инциденты']
            
            fig = px.choropleth(
                страны_инциденты,
                locations='Страна',
                locationmode='country names',
                color='Инциденты',
                color_continuous_scale='Blues',
                title='Количество инцидентов по странам',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'Migration Route' in df.columns:
            st.subheader("Наиболее распространенные миграционные маршруты")
            
            маршруты = df['Migration Route'].value_counts().reset_index()
            маршруты.columns = ['Маршрут', 'Частота']
            
            fig = px.bar(
                маршруты.sort_values('Частота', ascending=False).head(10),
                x='Маршрут',
                y='Частота',
                color='Частота',
                color_continuous_scale='Blues',
                title='Топ-10 миграционных маршрутов'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Демографический анализ")
    
    # Распределение по полу и возрасту
    if all(col in df.columns for col in ['Number of Males', 'Number of Females', 'Number of Children']):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Распределение по полу")
            
            общий_пол = {
                'Пол': ['Мужской', 'Женский'],
                'Всего': [df['Number of Males'].sum(), df['Number of Females'].sum()]
            }
            
            fig = px.pie(
                общий_пол,
                values='Всего',
                names='Пол',
                color_discrete_sequence=['#1f77b4', '#ff7f0e'],
                hole=0.4
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Присутствие детей")
            
            всего_детей = df['Number of Children'].sum()
            всего_взрослых = df['Number of Males'].sum() + df['Number of Females'].sum() - всего_детей
            
            данные_возраст = {
                'Категория': ['Взрослые', 'Дети'],
                'Всего': [всего_взрослых, всего_детей]
            }
            
            fig = px.bar(
                данные_возраст,
                x='Категория',
                y='Всего',
                color='Категория',
                color_discrete_sequence=['#1f77b4', '#ff7f0e'],
                text='Всего'
            )
            fig.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Анализ по стране/региону происхождения
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Country of Origin' in df.columns:
            st.subheader("Основные страны происхождения")
            
            страны_происхождения = df['Country of Origin'].value_counts().reset_index()
            страны_происхождения.columns = ['Страна происхождения', 'Количество']
            
            fig = px.bar(
                страны_происхождения.sort_values('Количество', ascending=False).head(10),
                x='Страна происхождения',
                y='Количество',
                color='Количество',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'Region of Origin' in df.columns:
            st.subheader("Регионы происхождения")
            
            регионы_происхождения = df['Region of Origin'].value_counts().reset_index()
            регионы_происхождения.columns = ['Регион происхождения', 'Количество']
            
            fig = px.pie(
                регионы_происхождения,
                values='Количество',
                names='Регион происхождения',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Уровень выживаемости
    if all(col in df.columns for col in ['Number of Survivors', 'Total Number of Dead and Missing']):
        st.markdown("---")
        st.subheader("Уровень выживаемости по типу инцидента")
        
        # Расчет уровня выживаемости по типу инцидента
        if 'Incident Type' in df.columns:
            уровень_выживаемости = df.groupby('Incident Type').agg({
                'Number of Survivors': 'sum',
                'Total Number of Dead and Missing': 'sum'
            }).reset_index()
            
            уровень_выживаемости['Всего'] = уровень_выживаемости['Number of Survivors'] + уровень_выживаемости['Total Number of Dead and Missing']
            уровень_выживаемости['Уровень выживаемости (%)'] = (уровень_выживаемости['Number of Survivors'] / уровень_выживаемости['Всего'] * 100).round(1)
            
            # Сортировка по уровню и фильтрация только типов с более чем 5 вовлеченными людьми
            уровень_выживаемости = уровень_выживаемости[уровень_выживаемости['Всего'] >= 5].sort_values('Уровень выживаемости (%)', ascending=False)
            
            fig = px.bar(
                уровень_выживаемости,
                x='Incident Type',
                y='Уровень выживаемости (%)',
                color='Уровень выживаемости (%)',
                color_continuous_scale='Blues',
                text='Уровень выживаемости (%)'
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(height=500, xaxis_title='Тип инцидента', yaxis_title='Уровень выживаемости (%)')
            st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("Детальный анализ")
    
    # Причины смерти
    if 'Cause of Death' in df.columns:
        st.subheader("Основные причины смерти")
        
        причины = df['Cause of Death'].value_counts().reset_index()
        причины.columns = ['Причина', 'Количество']
        
        # Создание облака слов
        try:
            wordcloud_data = dict(zip(причины['Причина'], причины['Количество']))
            
            # Генерация облака слов
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white',
                colormap='Blues',
                max_words=50
            ).generate_from_frequencies(wordcloud_data)
            
            # Отображение
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        except:
            # Запасной вариант, если облако слов не работает
            fig = px.pie(
                причины.head(10),
                values='Количество',
                names='Причина',
                title='Топ-10 причин смерти'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Сезонный анализ (по месяцам)
    if 'Month' in df.columns:
        st.markdown("---")
        st.subheader("Сезонная модель инцидентов")
        
        # Преобразование месяца в числовой порядок для правильной сортировки
        месяцы_порядок = {month: i for i, month in enumerate(calendar.month_name[1:], 1)}
        
        # Проверка, являются ли месяцы текстовыми
        if df['Month'].dtype == 'object':
            try:
                # Попытка сопоставить месяцы с числами
                df_месяц = df.copy()
                df_месяц['Month_Num'] = df_месяц['Month'].map(месяцы_порядок)
                
                # Группировка по месяцам
                инциденты_по_месяцам = df_месяц.groupby('Month').size().reset_index(name='Инциденты')
                
                # Добавление номера месяца для сортировки
                инциденты_по_месяцам['Month_Num'] = инциденты_по_месяцам['Month'].map(месяцы_порядок)
                
                # Сортировка по месяцу
                инциденты_по_месяцам = инциденты_по_месяцам.sort_values('Month_Num')
                
                # График
                fig = px.line(
                    инциденты_по_месяцам,
                    x='Month',
                    y='Инциденты',
                    markers=True,
                    title='Инциденты по месяцам'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.warning("Невозможно создать график сезонности из-за проблем с форматом месяцев.")
    
    # Корреляции между числовыми переменными
    st.markdown("---")
    st.subheader("Корреляции между переменными")
    
    # Выбор только числовых столбцов для корреляции
    числовые_столбцы = df.select_dtypes(include=['number']).columns.tolist()
    
    # Удаление широты и долготы, чтобы не искажать корреляцию
    числовые_столбцы = [col for col in числовые_столбцы if col.upper() not in ['LATITUDE', 'LONGITUDE']]
    
    if len(числовые_столбцы) >= 3:
        # Расчет корреляционной матрицы
        корреляция = df[числовые_столбцы].corr()
        
        # Создание тепловой карты
        fig = px.imshow(
            корреляция,
            text_auto='.2f',
            color_continuous_scale='RdBu_r',
            title='Корреляционная матрица числовых переменных'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Недостаточно числовых переменных для создания корреляционной матрицы.")
    
    # Исследование отдельных данных
    st.markdown("---")
    st.subheader("Исследование отдельных данных")
    
    # Позволить пользователю выбирать определенные записи
    n_записей = min(10, len(df))
    показать_записей = st.slider("Количество записей для отображения", 1, min(50, len(df)), n_записей)
    
    # Отображение данных
    st.dataframe(df.head(показать_записей))
    
    # Опция для скачивания отфильтрованных данных
    st.download_button(
        label="📥 Скачать отфильтрованные данные (CSV)",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="отфильтрованные_данные_инцидентов.csv",
        mime="text/csv"
    )

# Нижний колонтитул
st.markdown("---")
st.caption("Дашборд разработан для анализа данных о миграционных инцидентах. Данные чувствительны и представляют собой человеческие трагедии.")
st.caption("Источник: Данные, загруженные пользователем")
