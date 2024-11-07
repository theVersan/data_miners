#- Instrução para rodar:
#1. rodar o arquivo training.py com "python training.py"
#2. rodar o arquivo interface-grafica.py "streamlit run interface-grafica.py"

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV

# Carrega a tabela Matches

dfMatches = pd.read_csv('../pre-processamento/dfMatches.csv')

# Selecão das variáveis importantes

## Definir X
X = dfMatches[['home_team_name',
               'away_team_name',
               'total_goal_count',
               'away_team_first_goal',
               'home_team_first_goal',
               'away_team_goal_count_half_time',
               'away_team_shots_on_target',
               'home_ppg',
               'team_a_xg',
               'home_team_goal_count_half_time',
               'Pre-Match PPG (Home)',
               'away_ppg']]

# Seleção das colunas alvo

y_gols_casa = dfMatches['home_team_goal_count']
y_gols_fora = dfMatches['away_team_goal_count']

# Treinamento do modelo

# Divisão dos dados em 80% treino e 20% teste
X_train, X_test, y_train_casa, y_test_casa = train_test_split(X, y_gols_casa, test_size=0.2, random_state=42)
_, _, y_train_fora, y_test_fora = train_test_split(X, y_gols_fora, test_size=0.2, random_state=42)

# Treinamento dos modelos
model_casa = RandomForestRegressor(n_estimators=100, random_state=42)
model_fora = RandomForestRegressor(n_estimators=100, random_state=42)

# Normalização dos dados

## Normalizando os dados
scaler = StandardScaler()
K_train_scaled = scaler.fit_transform(X_train)
K_test_scaled = scaler.transform(X_test)

## Treinamento dos modelos com dados normalizados
model_casa.fit(K_train_scaled, y_train_casa)
model_fora.fit(K_train_scaled, y_train_fora)

# Tuning de hiperparâmetros

## Definindo o modelo
rf_model = RandomForestRegressor(random_state=42)

## Definindo a grade de hiperparâmetros

param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'bootstrap': [True, False]
}

## Inicializando o GridSearchCV para a equipe da casa
grid_search_casa = GridSearchCV(estimator=rf_model, param_grid=param_grid, cv=5, n_jobs=-1, verbose=2, scoring='neg_mean_squared_error')
grid_search_fora = GridSearchCV(estimator=rf_model, param_grid=param_grid, cv=5, n_jobs=-1, verbose=2, scoring='neg_mean_squared_error')

## Treinamento dos modelos com GridSearchCV
grid_search_casa.fit(K_train_scaled, y_train_casa)
grid_search_fora.fit(K_train_scaled, y_train_fora)

## Melhores hiperparâmetros encontrados para o time da casa e o visitante
best_params_casa = grid_search_casa.best_params_
best_params_fora = grid_search_fora.best_params_

print(f"Melhores hiperparâmetros para o time da casa: {best_params_casa}")
print(f"Melhores hiperparâmetros para o time visitante: {best_params_fora}")

## Utilizando os melhores modelos
best_model_casa = grid_search_casa.best_estimator_
best_model_fora = grid_search_fora.best_estimator_

# Previsão do placar

def prever_placar(time1, time2, dfTeams, best_model_casa, best_model_fora, scaler):
    ## Verificar se os times existem no conjunto de dados
    if time1 > dfMatches['home_team_name'].max() or time2 > dfMatches['away_team_name'].max():
        print("Um dos times não existe.")
        return
    
    ## Selecionar as características do time da casa e visitante
    time1_features = dfMatches[dfMatches['home_team_name'] == time1].iloc[0]
    time2_features = dfMatches[dfMatches['away_team_name'] == time2].iloc[0]

    ## Criar o DataFrame de entrada para o jogo
    novo_jogo = pd.DataFrame([{
        'home_team_name': time1,
        'away_team_name': time2,
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

    ## Garantir que as colunas estejam alinhadas com o conjunto de treinamento
    novo_jogo = novo_jogo.reindex(columns=X.columns, fill_value=0)

    ## Normalizar o novo jogo com o scaler já ajustado
    novo_jogo_scaled = scaler.transform(novo_jogo)

    ## Fazer previsões para o time da casa e visitante
    gols_casa_predito = best_model_casa.predict(novo_jogo_scaled)[0]
    gols_fora_predito = best_model_fora.predict(novo_jogo_scaled)[0]

    print(f'Previsão de Gols Casa: {gols_casa_predito:.3f}')
    print(f'Previsão de Gols Fora: {gols_fora_predito:.3f}')

    ## Arredondar para obter o placar final
    placar_casa = round(gols_casa_predito)
    placar_fora = round(gols_fora_predito)

    print(f'Placar Previsto: {placar_casa} x {placar_fora}')

## Exemplo de uso
time1 = 1 # ID do time da casa
time2 = 16 # ID do time visitante
prever_placar(time1, time2, dfMatches, best_model_casa, best_model_fora, scaler)


# After defining X and before training
feature_columns = X.columns.tolist()

# Save the columns to a file
import joblib
joblib.dump(feature_columns, 'feature_columns.pkl')

# Save models and scaler as before
joblib.dump(best_model_casa, 'best_model_casa.pkl')
joblib.dump(best_model_fora, 'best_model_fora.pkl')
joblib.dump(scaler, 'scaler.pkl')

print("Models, scaler, e colunas de features foram salvas com sucesso.")
