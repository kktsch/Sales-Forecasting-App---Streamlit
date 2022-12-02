import pandas as pd
import pickle
import plotly.graph_objects as go

import warnings
warnings.filterwarnings("ignore")


def Get_Data():
    url='https://drive.google.com/file/d/1v2KgBJ-JQbdQLEfBgF_IoyzNuWatrv9u/view?usp=share_link'
    url='https://drive.google.com/uc?id=' + url.split('/')[-2]
    df = pd.read_csv(url)
    return df


def PreProcess(data):

    data = data.drop_duplicates()
    df_obj = data.select_dtypes(['object'])
    data[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())

    data.CustomerNo = data.CustomerNo.astype(str)

    data_cancelled = data[data["TransactionNo"].str.contains("C")]
    data = data[~data["TransactionNo"].str.contains("C")]
    data = data.sort_values(by="Quantity", ascending=False).iloc[10:,:]

    data['Revenue'] = data.Price*data.Quantity
    data['Date'] = pd.to_datetime(data['Date'])
    data = data.sort_values("Date")
    data = data.set_index("Date",drop=True)

    df = data.resample("D").sum().Revenue.to_frame()
    df = df.reset_index()
    df.columns = ['Date', 'Value']
    return df

def Make_Rolling_Features(df):
    df_c = df.copy()
    lag = 30
    rolling_windows = [7,30]
    for window in rolling_windows:
        df_c['rolling_mean_'+str(window)] = df_c['Value'].rolling(window).mean().shift(1)
        df_c['rolling_std_'+str(window)] = df_c['Value'].rolling(window).std().shift(1)
        df_c['rolling_min_'+str(window)] = df_c['Value'].rolling(window).min().shift(1)
        df_c['rolling_max_'+str(window)] = df_c['Value'].rolling(window).max().shift(1)
        df_c['rolling_median_'+str(window)] = df_c['Value'].rolling(window).median().shift(1)
        df_c['rolling_quantile1st_'+str(window)] = df_c['Value'].rolling(window).quantile(0.25).shift(1)
        df_c['rolling_quantile3rd_'+str(window)] = df_c['Value'].rolling(window).quantile(0.75).shift(1)
        
    for i in range(lag):
        df_c['lag_'+str(i+1)] = df_c['Value'].shift(i+1)
    
    df_c['expanding_mean'] = df_c['Value'].expanding().mean().shift(1)
    df_c['expanding_std'] = df_c['Value'].expanding().std().shift(1)
    df_c['expanding_min'] = df_c['Value'].expanding().min().shift(1)
    df_c['expanding_var'] = df_c['Value'].expanding().var().shift(1)
    
    df_c['month'] = df_c['Date'].dt.month
    df_c['day_of_week'] = df_c['Date'].dt.dayofweek
    df_c['day_of_month'] = df_c['Date'].dt.day

    forecast_row = df_c.iloc[-1,:].drop(['Value','Date'])
    
    return forecast_row

def Get_Models():
    models = []
    with open("models.pckl", "rb") as f:
        while True:
            try:
                models.append(pickle.load(f))
            except EOFError:
                break

    return models

def Get_Prediction(forecast_row):
    models = Get_Models()

    preds = models[0].predict(forecast_row)
    lower_preds = models[1].predict(forecast_row)
    upper_preds = models[2].predict(forecast_row)

    return [preds, lower_preds, upper_preds]

def Make_Forecast(df):

    df_processed = PreProcess(df)
    forecast_row = Make_Rolling_Features(df_processed)

    predictions = Get_Prediction(forecast_row.to_frame().transpose())
    main_pred = predictions[0]
    lower_pred = predictions[1]
    upper_pred = predictions[2]

    forecast_dates = pd.date_range(start=df_processed.Date.tail(1).values[0], periods=31, freq="D")

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(name='Current data', x=df_processed.Date[-600:],y=df_processed.Value))
    fig1.add_trace(go.Scatter(name='Prediction', x=forecast_dates[1:],y=main_pred.ravel()))
    fig1.update_layout(xaxis_title="Date",yaxis_title="Sales",width=600, height=400, margin=dict(t=20,l=0,r=0))

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(name='Prediction', x=forecast_dates[1:],y=main_pred.ravel(),line_color='red'))
    fig2.add_trace(go.Scatter(name='Lower Boud', x=forecast_dates[1:],y=lower_pred.ravel(),
    line_color='rgba(0, 0, 255, 0.5)',showlegend=False))
    fig2.add_trace(go.Scatter(name='95% Confidence', x=forecast_dates[1:],y=upper_pred.ravel(),
    line_color='rgba(0, 0, 255, 0.5)', fill='tonexty',fillcolor='rgba(255, 0, 0, 0.1)'))
    fig2.update_layout(xaxis_title="Date",yaxis_title="Sales",width=500, height=400, margin=dict(t=20,l=0,r=0))

    return fig1, fig2



