import pickle
import streamlit as st
import pandas as pd

with open('ufc_ml.pkl', 'rb') as file:
    model = pickle.load(file)

data = pd.read_csv('../backend/data/ufc-master.csv')
imp_columns = ['RedOdds', 'BlueOdds', 'RedExpectedValue', 'BlueExpectedValue', 'BlueCurrentLoseStreak', 'BlueCurrentWinStreak', 'BlueLosses', 'BlueWinsByDecisionMajority', 'BlueWinsByDecisionSplit', 'BlueWinsByDecisionUnanimous', 'BlueWinsByKO', 'BlueWinsBySubmission', 'BlueWins','BlueHeightCms','BlueReachCms', 'BlueWeightLbs', 'RedCurrentLoseStreak', 'RedCurrentWinStreak', 'RedLosses', 'RedWinsByDecisionMajority', 'RedWinsByDecisionSplit', 'RedWinsByDecisionUnanimous', 'RedWinsByKO', 'RedWinsBySubmission', 'RedWins','RedHeightCms','RedReachCms', 'RedWeightLbs']
all_fighters = sorted(set(data['RedFighter']).union(set(data['BlueFighter'])))

st.title("🥋 UFC (MMA) Match Outcome Predictor")

with st.form("Predictor"):
    fighter1 =  st.selectbox("Select first fighter: ", all_fighters)
    fighter2 =  st.selectbox("Select second fighter: ", all_fighters)
    button = st.form_submit_button("Predict the outcome")

if button:
   weightclass1 = data[(data['BlueFighter'] == fighter1)| (data['RedFighter'] == fighter1)]['WeightClass'].iloc[0]
   weightclass2 = data[(data['BlueFighter'] == fighter2)| (data['RedFighter'] == fighter2)]['WeightClass'].iloc[0] 
   if weightclass1 != weightclass2:
       st.warning("⚠️ please select fighters from the same weight class. ")
       st.info(f"{fighter1} is in the weight class: {weightclass1}\n\n"
        f"{fighter2} is in the weight class: {weightclass2}")
   elif fighter1 == fighter2:
       st.warning("⚠️ please select Two different fighters.")
   else: 
       red_f, blue_f = sorted([fighter1, fighter2])
       all_red_fights = data[(data['RedFighter'] == red_f) | (data['BlueFighter'] == red_f)].copy()
       all_blue_fights = data[(data['RedFighter'] == blue_f)| (data['BlueFighter'] == blue_f)].copy()
       if all_red_fights.empty  or all_blue_fights.empty:
           st.error("⚠️ Cannot predict due to low data!.")
       else:
           for col in all_red_fights.columns:
               if col.startswith('Blue'):
                   all_red_fights.rename(columns = {col: 'Temp' + col.replace('Blue', '')}, inplace = True)
               elif col.startswith('Red'):
                    all_red_fights.rename(columns={col: 'Red' + col.replace('Red', '')}, inplace=True)
           for col in all_blue_fights.columns:
               if col.startswith('Red'):
                   all_blue_fights.rename(columns = {col: 'Temp' + col.replace('Red', '')}, inplace = True)
               elif col.startswith('Red'):
                    all_blue_fights.rename(columns={col: 'Blue' + col.replace('Blue', '')}, inplace=True)
           red_avg_stats = all_red_fights.filter(regex = '^Red|^Temp').mean(numeric_only = True)
           blue_avg_stats = all_blue_fights.filter(regex='^Blue|^Temp').mean(numeric_only=True)

           input_row ={}
           for col in imp_columns:
                if col.startswith('Red'):
                    stat = col.replace('Red', '')
                    input_row[col] = red_avg_stats.get('Temp_' + stat, red_avg_stats.get(col, 0))
            
                if col.startswith('Blue'):
                    stat = col.replace('Blue', '')
                    input_row[col] = blue_avg_stats.get('Temp_' + stat, blue_avg_stats.get(col, 0))
           inp = pd.DataFrame([input_row])
           predc = model.predict(inp)[0]
           prob = model.predict_proba(inp)[0]

           if predc == 1:
               pred_winner = red_f
           else:
               pred_winner = blue_f
           st.success(f"🏆 Predicted Winner: {pred_winner}")
           st.info(f"Win Probabilities of fighters: \n\n"
                    f" {red_f}: {prob[1]*100:.2f}%\n"
                    f" {blue_f}: {prob[0]*100:.2f}%")