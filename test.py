import streamlit as st 
import numpy as np  
import pandas as pd 
import time  
import plotly.express as px  
import datetime as dt
from datetime import timezone, timedelta,datetime
import os
import matplotlib.pyplot as plt 
import seaborn as sns 
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore", message="The default value of regex will change from True to False in a future version.")

ahoy_events=pd.read_csv(r'C:\Users\R\Desktop\Dataset\Raghib- User Engagement\ahoy_events.csv')
ahoy_visits=pd.read_csv(r'C:\Users\R\Desktop\Dataset\Raghib- User Engagement\ahoy_visits.csv')
geo_tables=pd.read_csv(r'C:\Users\R\Desktop\Dataset\Raghib- User Engagement\geo_tables.csv')
user_designations=pd.read_csv(r'C:\Users\R\Desktop\Dataset\Raghib- User Engagement\user_designations.csv')
users=pd.read_csv(r'C:\Users\R\Desktop\Dataset\Raghib- User Engagement\users.csv')

st.set_page_config(
    page_title = 'User Engagement Dashboard',
    page_icon = ':chart_with_upwards_trend:',
    layout = 'wide'
)
st.title(":chart_with_upwards_trend: User Engagement Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

total_sign_ins = users['sign_in_count'].sum()
average_sign_ins_per_user = users['sign_in_count'].mean()
median_sign_ins_per_user = users['sign_in_count'].median()
login_frequency_distribution = users['sign_in_count'].value_counts().sort_index()


st.header('User Sign-In Statistics')
col1, col2, col3 = st.columns(3)
col1.metric("Total Sign-Ins", total_sign_ins)
col2.metric("Average Sign-Ins Per User", f"{average_sign_ins_per_user:.2f}")
col3.metric("Median Sign-Ins Per User", median_sign_ins_per_user)

st.subheader('Login Frequency Distribution')
st.bar_chart(login_frequency_distribution)


col1, col2, col3 = st.columns(3)
with col1:
    device_usage = ahoy_visits['device_type'].value_counts().rename_axis('device').reset_index(name='count')
    fig_device = px.pie(device_usage, names='device', values='count', title='Device Usage Distribution')
    st.plotly_chart(fig_device, use_container_width=True)
with col2:
    browser_visits = ahoy_visits['browser'].value_counts()
    top_10_browsers = browser_visits.sort_values(ascending=False).head(10)
    
    # Plot for Browser Visits
    fig_browser = px.bar(top_10_browsers, x=top_10_browsers.index, y=top_10_browsers.values, labels={'y': 'Number of Visits', 'index': 'Browser'}, title='Top 10 Browsers by Number of Visits')
    fig_browser.update_layout(xaxis_title='Browser', yaxis_title='Number of Visits', xaxis_tickangle=-45)
    st.plotly_chart(fig_browser, use_container_width=True)
with col3:
    os_visits = ahoy_visits['os'].value_counts()
    top_10_os = os_visits.sort_values(ascending=False).head(10)
    
    # Plot for OS Visits
    fig_os = px.bar(top_10_os, x=top_10_os.index, y=top_10_os.values, labels={'y': 'Number of Visits', 'index': 'Operating System'}, title='Top 10 Operating Systems by Number of Visits')
    fig_os.update_layout(xaxis_title='Operating System', yaxis_title='Number of Visits', xaxis_tickangle=-45)
    st.plotly_chart(fig_os, use_container_width=True)

users['access_program_list'] = users['access_program'].str.replace('{', '').str.replace('}', '').str.replace('NULL', '').str.split(',')
users['access_program_list'] = users['access_program_list'].apply(lambda x: [i for i in x if i.strip() != ""])
feature_counts_direct = users.explode('access_program_list')['access_program_list'].value_counts()
fig = px.bar(feature_counts_direct, title='Feature Usage Frequency')
st.plotly_chart(fig)

users_with_roles = pd.merge(users, user_designations, how="left", left_on="role_id", right_on="id", suffixes=('', '_designation'))
users_with_roles.rename(columns={'name_en': 'role_name'}, inplace=True)

users_with_roles['current_sign_in_at'] = pd.to_datetime(users_with_roles['current_sign_in_at'])
users_with_roles['year_month'] = users_with_roles['current_sign_in_at'].dt.to_period('M').astype(str) 

monthly_sign_ins = users_with_roles.groupby('year_month').size().reset_index(name='count')

fig = px.line(monthly_sign_ins, x='year_month', y='count', markers=True,
              title='Monthly User Sign-Ins Over Time',
              labels={'year_month': 'Month', 'count': 'Number of Sign-Ins'})

fig.update_layout(xaxis_tickangle=-45, xaxis=dict(title='Month'),
                  yaxis=dict(title='Number of Sign-Ins'),
                  plot_bgcolor='white', xaxis_showgrid=False, yaxis_showgrid=True)
st.plotly_chart(fig, use_container_width=True)

users_with_roles['day_of_week'] = users_with_roles['current_sign_in_at'].dt.dayofweek
weekly_sign_ins = users_with_roles.groupby('day_of_week').size()
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weekly_sign_ins.index = days
weekly_sign_ins_df = weekly_sign_ins.reset_index()
weekly_sign_ins_df.columns = ['Day of the Week', 'Number of Sign-Ins']
fig = px.bar(weekly_sign_ins_df, x='Day of the Week', y='Number of Sign-Ins',
             title='Weekly Sign-Ins Pattern', color='Number of Sign-Ins',
             color_continuous_scale=px.colors.sequential.Blues)  
fig.update_layout(xaxis_tickangle=-45, plot_bgcolor='white',
                  xaxis=dict(title='Day of the Week'),
                  yaxis=dict(title='Number of Sign-Ins'),
                  coloraxis_showscale=False) 
st.plotly_chart(fig, use_container_width=True)
fig_monthly = px.line(monthly_sign_ins, x='year_month', y='count',
                      title='Seasonal Trends in Monthly User Sign-Ins',
                      markers=True, 
                      line_shape='linear') 

fig_monthly.update_traces(line=dict(color='green', width=2)) 
fig_monthly.update_layout(
    xaxis_title='Month',
    yaxis_title='Number of Sign-Ins',
    xaxis_tickangle=-45,
    plot_bgcolor='white', 
    xaxis=dict(showgrid=False), 
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightPink') 
)
st.plotly_chart(fig_monthly, use_container_width=True)

geo_engagement = users.groupby(['geography_type', 'geography_id']).agg(
    total_sign_ins=pd.NamedAgg(column='sign_in_count', aggfunc='sum'),
    unique_users=pd.NamedAgg(column='id', aggfunc='nunique')
).reset_index()
geo_engagement_sorted = geo_engagement.sort_values(by='total_sign_ins', ascending=False)
top_engagement = geo_engagement_sorted.head()
low_engagement = geo_engagement_sorted.tail()

district_mapping = geo_tables[['district_id', 'district_name']].drop_duplicates()
district_engagement = pd.merge(geo_engagement[geo_engagement['geography_type'] == 'District'],
                               district_mapping, left_on='geography_id', right_on='district_id', how='left')
district_engagement_sorted = district_engagement.sort_values(by='total_sign_ins', ascending=False)
top_districts_engagement = district_engagement_sorted.head()
low_districts_engagement = district_engagement_sorted.tail()

fig_top = px.bar(top_districts_engagement, x='district_name', y='total_sign_ins',
                 title="Top Engagement Districts",
                 labels={"total_sign_ins": "Total Sign-Ins", "district_name": "District Name"},
                 color='total_sign_ins', color_continuous_scale='Viridis')

fig_low = px.bar(low_districts_engagement, x='district_name', y='total_sign_ins',
                 title="Low Engagement Districts",
                 labels={"total_sign_ins": "Total Sign-Ins", "district_name": "District Name"},
                 color='total_sign_ins', color_continuous_scale='Viridis')

st.title('District Engagement Analysis')
st.write('This dashboard provides insights into user engagement across districts, showcasing both high and low engagement areas.')

col1, col2 = st.columns(2)
with col1:
    st.header('Top Engagement Districts')
    st.plotly_chart(fig_top)
with col2:
    st.header('Low Engagement Districts')
    st.plotly_chart(fig_low)
role_segmentation = user_designations['name_en'].value_counts()
role_segmentation_df = role_segmentation.reset_index()
role_segmentation_df.columns = ['Role', 'Count']
fig = px.bar(role_segmentation_df, x='Role', y='Count', title="Role Segmentation")
st.plotly_chart(fig)



ahoy_events['time'] = pd.to_datetime(ahoy_events['time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
ahoy_events['hour'] = ahoy_events['time'].dt.hour
ahoy_events['day_of_week'] = ahoy_events['time'].dt.dayofweek
events_by_hour = ahoy_events.groupby('hour').size().reset_index(name='counts')
events_by_day_of_week = ahoy_events.groupby('day_of_week').size().reset_index(name='counts')
fig = px.line(events_by_hour, x='hour', y='counts', markers=True, title='User Engagement by Hour of Day')
fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1), xaxis_title='Hour of Day', yaxis_title='Number of Events')
st.title('User Engagement Analysis')
st.plotly_chart(fig)


