import streamlit as st
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import calendar
from datetime import datetime
import pycountry
from wordcloud import WordCloud

# Page configuration
st.set_page_config(
    page_title="Migration Incidents Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("Migration Incidents Analysis Dashboard")
st.markdown("""
This dashboard analyzes data on incidents involving immigrants, providing insights on patterns, 
trends and statistics related to these occurrences around the world.
""")

# Function to load data
@st.cache_data
def load_data(file=None):
    if file is not None:
        try:
            # Check file extension
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            return df, None
        except Exception as e:
            return None, str(e)
    else:
        # Create example DataFrame with structure similar to real data
        # (only for demonstration when there's no upload)
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

# Option for file upload
st.sidebar.header("📊 Data")
uploaded_file = st.sidebar.file_uploader("Upload data file", type=["xlsx", "xls", "csv"])

# Load data
if uploaded_file is not None:
    df, error = load_data(uploaded_file)
    if error:
        st.error(f"Error loading file: {error}")
        st.stop()
    else:
        st.sidebar.success("✅ Data loaded successfully!")
else:
    df, _ = load_data()
    st.sidebar.warning("⚠️ Using example data. Upload your file for real analysis.")

# Convert Incident Date to datetime, if necessary
if 'Incident Date' in df.columns:
    try:
        df['Incident Date'] = pd.to_datetime(df['Incident Date'])
    except:
        pass

# Check and fill null values in numeric fields
numeric_columns = [
    'Number of Dead', 'Minimum Estimated Number of Missing', 
    'Total Number of Dead and Missing', 'Number of Survivors',
    'Number of Females', 'Number of Males', 'Number of Children'
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(0)

# Sidebar for filters
st.sidebar.header("🔍 Filters")

# Period filter
if 'Incident Year' in df.columns:
    available_years = sorted(df['Incident Year'].unique())
    if len(available_years) > 1:
        selected_year = st.sidebar.multiselect(
            "Incident Year",
            options=available_years,
            default=available_years
        )
        if selected_year:
            df = df[df['Incident Year'].isin(selected_year)]

# Region filter
if 'Region of Incident' in df.columns:
    available_regions = sorted(df['Region of Incident'].unique())
    if len(available_regions) > 1:
        selected_region = st.sidebar.multiselect(
            "Incident Region",
            options=available_regions,
            default=available_regions
        )
        if selected_region:
            df = df[df['Region of Incident'].isin(selected_region)]

# Incident type filter
if 'Incident Type' in df.columns:
    available_types = sorted(df['Incident Type'].unique())
    if len(available_types) > 1:
        selected_type = st.sidebar.multiselect(
            "Incident Type",
            options=available_types,
            default=available_types
        )
        if selected_type:
            df = df[df['Incident Type'].isin(selected_type)]

# Check if there's data after filtering
if len(df) == 0:
    st.warning("No data available for the selected filters.")
    st.stop()

# Divide the dashboard into sections
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🗺️ Geographic Analysis", "👥 Demographics", "📊 Detailed Analysis"])

with tab1:
    st.header("Incidents Overview")
    
    # Main KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_incidents = len(df)
        st.metric("Total Incidents", f"{total_incidents:,}")
    
    with col2:
        if 'Total Number of Dead and Missing' in df.columns:
            total_dead_missing = int(df['Total Number of Dead and Missing'].sum())
            st.metric("Total Victims", f"{total_dead_missing:,}")
    
    with col3:
        if 'Number of Survivors' in df.columns:
            total_survivors = int(df['Number of Survivors'].sum())
            st.metric("Total Survivors", f"{total_survivors:,}")
    
    with col4:
        if 'Number of Children' in df.columns:
            total_children = int(df['Number of Children'].sum())
            st.metric("Children Affected", f"{total_children:,}")
    
    st.markdown("---")
    
    # Time trend
    if 'Incident Date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Incident Date']):
        st.subheader("Incident Trend Over Time")
        
        # Grouping by month
        df_time = df.copy()
        df_time['Month'] = df_time['Incident Date'].dt.to_period('M')
        incidents_by_month = df_time.groupby('Month').size().reset_index(name='Incidents')
        incidents_by_month['Month'] = incidents_by_month['Month'].astype(str)
        
        # Dead and missing by month
        if 'Total Number of Dead and Missing' in df.columns:
            victims_by_month = df_time.groupby('Month')['Total Number of Dead and Missing'].sum().reset_index()
            victims_by_month['Month'] = victims_by_month['Month'].astype(str)
            
            # Combined line chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=incidents_by_month['Month'],
                y=incidents_by_month['Incidents'],
                name='Number of Incidents',
                line=dict(color='blue', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=victims_by_month['Month'],
                y=victims_by_month['Total Number of Dead and Missing'],
                name='Victims (dead and missing)',
                line=dict(color='red', width=2),
                yaxis='y2'
            ))
            
            fig.update_layout(
                title='Evolution of Incidents and Victims Over Time',
                xaxis=dict(title='Month'),
                yaxis=dict(title='Number of Incidents', showgrid=False),
                yaxis2=dict(title='Number of Victims', overlaying='y', side='right', showgrid=False),
                legend=dict(x=0.01, y=0.99),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Comparison by incident type
    if 'Incident Type' in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Incidents by Type")
            
            incidents_by_type = df['Incident Type'].value_counts().reset_index()
            incidents_by_type.columns = ['Incident Type', 'Count']
            
            fig = px.bar(
                incidents_by_type.sort_values('Count', ascending=False).head(10),
                x='Incident Type',
                y='Count',
                color='Count',
                color_continuous_scale='Blues',
                title='Top 10 Incident Types'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Victims by Incident Type")
            
            if 'Total Number of Dead and Missing' in df.columns:
                victims_by_type = df.groupby('Incident Type')['Total Number of Dead and Missing'].sum().reset_index()
                victims_by_type.columns = ['Incident Type', 'Total Victims']
                
                fig = px.pie(
                    victims_by_type.sort_values('Total Victims', ascending=False).head(10),
                    values='Total Victims',
                    names='Incident Type',
                    title='Distribution of Victims by Incident Type',
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Geographic Analysis")
    
    # Heat map of incidents
    st.subheader("Incidents Heat Map")
    
    # Check if there are valid coordinates
    if 'LATITUDE' in df.columns and 'LONGITUDE' in df.columns:
        # Clean invalid coordinates
        df_map = df.copy()
        df_map = df_map.dropna(subset=['LATITUDE', 'LONGITUDE'])
        df_map = df_map[(df_map['LATITUDE'] >= -90) & (df_map['LATITUDE'] <= 90) & 
                       (df_map['LONGITUDE'] >= -180) & (df_map['LONGITUDE'] <= 180)]
        
        if len(df_map) > 0:
            # Add a size column if there's victim data
            if 'Total Number of Dead and Missing' in df_map.columns:
                df_map['marker_size'] = df_map['Total Number of Dead and Missing'].fillna(1)
                df_map.loc[df_map['marker_size'] == 0, 'marker_size'] = 1
                df_map['marker_size'] = np.log1p(df_map['marker_size']) * 5
            else:
                df_map['marker_size'] = 5
            
            # Add text for hover
            hover_text = []
            for idx, row in df_map.iterrows():
                text = f"Location: {row.get('Location of Incident', 'N/A')}<br>"
                if 'Incident Type' in df_map.columns:
                    text += f"Type: {row['Incident Type']}<br>"
                if 'Incident Date' in df_map.columns:
                    date = row['Incident Date']
                    if pd.api.types.is_datetime64_any_dtype(date):
                        text += f"Date: {date.strftime('%m/%d/%Y')}<br>"
                    else:
                        text += f"Date: {date}<br>"
                if 'Total Number of Dead and Missing' in df_map.columns:
                    text += f"Victims: {int(row['Total Number of Dead and Missing'])}"
                hover_text.append(text)
            
            # Create density map
            fig = go.Figure()
            
            # Add heat map
            fig.add_densitymapbox(
                lat=df_map['LATITUDE'],
                lon=df_map['LONGITUDE'],
                z=df_map.get('Total Number of Dead and Missing', np.ones(len(df_map))),
                radius=20,
                colorscale='Reds',
                colorbar=dict(title='Intensity'),
                hoverinfo='none',
                opacity=0.7
            )
            
            # Add individual points
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
            
            # Configure map layout
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
            st.warning("There are no valid coordinates to display on the map.")
    else:
        st.warning("Latitude and longitude columns were not found in the data.")
    
    # Analysis by region/country
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Country of Incident' in df.columns:
            st.subheader("Incidents by Country")
            
            incident_countries = df['Country of Incident'].value_counts().reset_index()
            incident_countries.columns = ['Country', 'Incidents']
            
            fig = px.choropleth(
                incident_countries,
                locations='Country',
                locationmode='country names',
                color='Incidents',
                color_continuous_scale='Blues',
                title='Number of Incidents by Country',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'Migration Route' in df.columns:
            st.subheader("Most Common Migration Routes")
            
            routes = df['Migration Route'].value_counts().reset_index()
            routes.columns = ['Route', 'Frequency']
            
            fig = px.bar(
                routes.sort_values('Frequency', ascending=False).head(10),
                x='Route',
                y='Frequency',
                color='Frequency',
                color_continuous_scale='Blues',
                title='Top 10 Migration Routes'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Demographic Analysis")
    
    # Distribution by gender and age
    if all(col in df.columns for col in ['Number of Males', 'Number of Females', 'Number of Children']):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Gender Distribution")
            
            total_gender = {
                'Gender': ['Male', 'Female'],
                'Total': [df['Number of Males'].sum(), df['Number of Females'].sum()]
            }
            
            fig = px.pie(
                total_gender,
                values='Total',
                names='Gender',
                color_discrete_sequence=['#1f77b4', '#ff7f0e'],
                hole=0.4
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Presence of Children")
            
            total_children = df['Number of Children'].sum()
            total_adults = df['Number of Males'].sum() + df['Number of Females'].sum() - total_children
            
            age_data = {
                'Category': ['Adults', 'Children'],
                'Total': [total_adults, total_children]
            }
            
            fig = px.bar(
                age_data,
                x='Category',
                y='Total',
                color='Category',
                color_discrete_sequence=['#1f77b4', '#ff7f0e'],
                text='Total'
            )
            fig.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Analysis by country/region of origin
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Country of Origin' in df.columns:
            st.subheader("Main Countries of Origin")
            
            origin_countries = df['Country of Origin'].value_counts().reset_index()
            origin_countries.columns = ['Country of Origin', 'Count']
            
            fig = px.bar(
                origin_countries.sort_values('Count', ascending=False).head(10),
                x='Country of Origin',
                y='Count',
                color='Count',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'Region of Origin' in df.columns:
            st.subheader("Regions of Origin")
            
            origin_regions = df['Region of Origin'].value_counts().reset_index()
            origin_regions.columns = ['Region of Origin', 'Count']
            
            fig = px.pie(
                origin_regions,
                values='Count',
                names='Region of Origin',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Survival rate
    if all(col in df.columns for col in ['Number of Survivors', 'Total Number of Dead and Missing']):
        st.markdown("---")
        st.subheader("Survival Rate by Incident Type")
        
        # Calculate survival rate by incident type
        if 'Incident Type' in df.columns:
            survival_rate = df.groupby('Incident Type').agg({
                'Number of Survivors': 'sum',
                'Total Number of Dead and Missing': 'sum'
            }).reset_index()
            
            survival_rate['Total'] = survival_rate['Number of Survivors'] + survival_rate['Total Number of Dead and Missing']
            survival_rate['Survival Rate (%)'] = (survival_rate['Number of Survivors'] / survival_rate['Total'] * 100).round(1)
            
            # Sort by rate and filter only types with more than 5 people involved
            survival_rate = survival_rate[survival_rate['Total'] >= 5].sort_values('Survival Rate (%)', ascending=False)
            
            fig = px.bar(
                survival_rate,
                x='Incident Type',
                y='Survival Rate (%)',
                color='Survival Rate (%)',
                color_continuous_scale='Blues',
                text='Survival Rate (%)'
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(height=500, xaxis_title='Incident Type', yaxis_title='Survival Rate (%)')
            st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("Detailed Analysis")
    
    # Causes of death
    if 'Cause of Death' in df.columns:
        st.subheader("Main Causes of Death")
        
        causes = df['Cause of Death'].value_counts().reset_index()
        causes.columns = ['Cause', 'Count']
        
        # Create word cloud
        try:
            wordcloud_data = dict(zip(causes['Cause'], causes['Count']))
            
            # Generate word cloud
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white',
                colormap='Blues',
                max_words=50
            ).generate_from_frequencies(wordcloud_data)
            
            # Display
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        except:
            # Fallback if wordcloud fails
            fig = px.pie(
                causes.head(10),
                values='Count',
                names='Cause',
                title='Top 10 Causes of Death'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Seasonal analysis (by month)
    if 'Month' in df.columns:
        st.markdown("---")
        st.subheader("Seasonal Pattern of Incidents")
        
        # Convert month to numerical order for correct sorting
        months_order = {month: i for i, month in enumerate(calendar.month_name[1:], 1)}
        
        # Check if months are as text
        if df['Month'].dtype == 'object':
            try:
                # Try to map months to numbers
                df_month = df.copy()
                df_month['Month_Num'] = df_month['Month'].map(months_order)
                
                # Group by month
                incidents_by_month = df_month.groupby('Month').size().reset_index(name='Incidents')
                
                # Add month number for sorting
                incidents_by_month['Month_Num'] = incidents_by_month['Month'].map(months_order)
                
                # Sort by month
                incidents_by_month = incidents_by_month.sort_values('Month_Num')
                
                # Chart
                fig = px.line(
                    incidents_by_month,
                    x='Month',
                    y='Incidents',
                    markers=True,
                    title='Incidents by Month'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.warning("Could not create the seasonality chart due to issues with the month format.")
    
    # Correlations between numerical variables
    st.markdown("---")
    st.subheader("Variable Correlations")
    
    # Select only numerical columns for correlation
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # Remove latitude and longitude to not distort the correlation
    num_cols = [col for col in num_cols if col.upper() not in ['LATITUDE', 'LONGITUDE']]
    
    if len(num_cols) >= 3:
        # Calculate correlation matrix
        corr = df[num_cols].corr()
        
        # Create heatmap
        fig = px.imshow(
            corr,
            text_auto='.2f',
            color_continuous_scale='RdBu_r',
            title='Correlation Matrix of Numerical Variables'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("There are not enough numerical variables to create a correlation matrix.")
    
    # Individual data exploration
    st.markdown("---")
    st.subheader("Individual Data Exploration")
    
    # Allow user to select specific records
    n_records = min(10, len(df))
    show_records = st.slider("Number of records to show", 1, min(50, len(df)), n_records)
    
    # Display data
    st.dataframe(df.head(show_records))
    
    # Option to download filtered data
    st.download_button(
        label="📥 Download filtered data (CSV)",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="filtered_incident_data.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.caption("Dashboard developed for migration incident data analysis. The data is sensitive and represents human tragedies.")
st.caption("Source: User uploaded data")
