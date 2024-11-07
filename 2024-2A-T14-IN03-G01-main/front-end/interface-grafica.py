#- Instrução para rodar:
#1. rodar o arquivo training.py com "python training.py"
#2. rodar o arquivo interface-grafica.py "streamlit run interface-grafica.py"

import streamlit as st
import pandas as pd
import joblib

# Loada os modelos pré-treinados, scaler e colunas de features
best_model_casa = joblib.load('best_model_casa.pkl')
best_model_fora = joblib.load('best_model_fora.pkl')
scaler = joblib.load('scaler.pkl')
feature_columns = joblib.load('feature_columns.pkl')  

# Loada o dataset
dfMatches = pd.read_csv('../pre-processamento/dfMatches.csv')

# Loada os nomes dos times e IDs do CSV
team_data = pd.DataFrame({
    'team_name': ["Vitória", "Flamengo", "Cruzeiro", "Botafogo", "Grêmio", "Fluminense", "São Paulo", "Palmeiras", "Atlético Mineiro", "Atlético PR", "Corinthians", "Vasco da Gama", "Bahia", "Atlético GO", "Internacional", "Bragantino", "Criciúma", "Juventude", "Cuiabá", "Fortaleza"],
    'index': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
})

team_name_to_id = dict(zip(team_data['team_name'], team_data['index']))

# Define o app Streamlit
st.title('Predição do Placar da Partida')

# Pega os nomes dos times do dataset
team_names = team_data['team_name'].tolist()

# Cria dropdowns para seleção de time por nome
home_team_name = st.selectbox('Selecione o time da casa', team_names)
away_team_name = st.selectbox('Selecione o time de fora', team_names)

# Mapeia os nomes dos times selecionados para seus IDs correspondentes
home_team_id = team_name_to_id[home_team_name]
away_team_id = team_name_to_id[away_team_name]

# Função para prever o placar
def prever_placar(time1_id, time2_id, time1_name, time2_name, dfMatches, best_model_casa, best_model_fora, scaler, feature_columns):
    # Garante que os times selecionados existem no dataset
    if time1_id not in dfMatches['home_team_name'].values or time2_id not in dfMatches['away_team_name'].values:
        st.write("Algum dos times selecionados não existe.")
        return

    # Extrai as features dos times selecionados
    time1_features = dfMatches[dfMatches['home_team_name'] == time1_id].iloc[0]
    time2_features = dfMatches[dfMatches['away_team_name'] == time2_id].iloc[0]

    # Create a new match dataframe with the necessary features
    novo_jogo = pd.DataFrame([{
        'home_team_name': time1_id,
        'away_team_name': time2_id,
        'total_goal_count': time1_features['total_goal_count'],
        'away_team_first_goal': time2_features['away_team_first_goal'],
        'home_team_first_goal': time1_features['home_team_first_goal'],
        'away_team_goal_count_half_time': time2_features['away_team_goal_count_half_time'],
        'away_team_shots_on_target': time2_features['away_team_shots_on_target'],
        'home_ppg': time1_features['home_ppg'],
        'team_a_xg': time1_features['team_a_xg'],
        'home_team_goal_count_half_time': time1_features['home_team_goal_count_half_time'],
        'Pre-Match PPG (Home)': time1_features['Pre-Match PPG (Home)'],
        'away_ppg': time2_features['away_ppg']
    }])

    # Alinha as colunas com os dados de treinamento
    novo_jogo = novo_jogo.reindex(columns=feature_columns, fill_value=0)

    # Normaliza os novos dados da partida usando o scaler pré-ajustado
    novo_jogo_scaled = scaler.transform(novo_jogo)

    # Faz predições usando os modelos pré-treinados
    gols_casa_predito = best_model_casa.predict(novo_jogo_scaled)[0]
    gols_fora_predito = best_model_fora.predict(novo_jogo_scaled)[0]

    # Arredonda os gols previstos pra obter o placar final
    placar_casa = round(gols_casa_predito)
    placar_fora = round(gols_fora_predito)

    st.write(f'{time1_name} {placar_casa} x {placar_fora} {time2_name}')

# Botão para acionar a predição
if st.button('Predizer Placar'):
    prever_placar(home_team_id, away_team_id, home_team_name, away_team_name, dfMatches, best_model_casa, best_model_fora, scaler, feature_columns)