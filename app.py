from functions import *
import streamlit as st
import plotly.graph_objects as go

import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Sales Prediction Tool")

tabs = ["Forecasting","Insights","About"]

page = st.sidebar.radio("MENU",tabs)

if page == "Forecasting":
    st.markdown("<h1 style='text-align:center;'>Sales Forecasting</h1>", unsafe_allow_html=True)
    st.write("""This tool generates a 30-day sales forecast for the current data.""")
    st.markdown("<h2 style='text-align:center;'></h2>", unsafe_allow_html=True)
    button = st.button("Get Prediction")

    if button == True:
        with st.empty():
            with st.spinner("Loading the data..."):
                df = Get_Data()
            with st.spinner("Forecasting..."):
                fig1, fig2 = Make_Forecast(df)
        st.markdown("<h2 style='text-align:center;'></h2>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'>Results</h2>", unsafe_allow_html=True)
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("<h1 style='text-align:center;'></h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'>Predictions</h2>", unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)


elif page == "Insights":
    st.markdown("<h1 style='text-align:center;'>Data Insights</h1>", unsafe_allow_html=True)
    
    with st.spinner("Loading the data. Please wait..."):
        df = Get_Data()
        df_processed = PreProcess(df)
        expanding_mean = df_processed.Value.expanding().mean()

        st.markdown("<h2 style='text-align:center;'></h2>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'>Data</h2>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_processed.Date,y=df_processed.Value,))
        fig.update_layout(xaxis_title="Date",yaxis_title="Sales", margin=dict(t=20,l=0,r=0),
        width=200, height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<h2 style='text-align:center;'>Trend</h2>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(name='Sales', x=df_processed.Date,y=df_processed.Value,showlegend=False))
        fig.add_trace(go.Scatter(name='Trend', x=df_processed.Date,y=expanding_mean, line=dict(width=3),showlegend=False))
        fig.update_layout(xaxis_title="Date",yaxis_title="Sales", margin=dict(t=20,l=0,r=0),
        width=200, height=400)
        st.plotly_chart(fig, use_container_width=True)

        df_processed['Day'] = df_processed.Date.dt.day_name()
        daily_average = df_processed.groupby('Day').mean()

        st.markdown("<h2 style='text-align:center;'>Daily Averages</h2>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=daily_average.index,y=daily_average.Value))
        fig.update_layout(xaxis_title="Date",yaxis_title="Sales", margin=dict(t=20,l=0,r=0),
        width=500, height=400)
        st.plotly_chart(fig, use_container_width=True)

        df_processed['Month'] = df_processed.Date.dt.month_name()
        monthly_average = df_processed.groupby('Month').mean()

        st.markdown("<h2 style='text-align:center;'>Monthly Averages</h2>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly_average.index,y=monthly_average.Value))
        fig.update_layout(xaxis_title="Date",yaxis_title="Sales", margin=dict(t=20,l=0,r=0),
        width=500, height=400)
        st.plotly_chart(fig, use_container_width=True)

elif page == "About":
    st.write("This tool is built for X Ltd.")
    st.write("v.0.1")
    st.write("""[Haldun Köktaş](https://www.linkedin.com/in/haldunkoktas/)""")
