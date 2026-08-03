import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import pickle
data = pd.read_csv("ufc-master.csv")

data['Winner'] = data['Winner'].map({'Red': 1, 'Blue': 0})
imp_columns = ['RedOdds', 'BlueOdds', 'RedExpectedValue', 'BlueExpectedValue', 'BlueCurrentLoseStreak', 'BlueCurrentWinStreak', 'BlueLosses', 'BlueWinsByDecisionMajority', 'BlueWinsByDecisionSplit', 'BlueWinsByDecisionUnanimous', 'BlueWinsByKO', 'BlueWinsBySubmission', 'BlueWins','BlueHeightCms','BlueReachCms', 'BlueWeightLbs', 'RedCurrentLoseStreak', 'RedCurrentWinStreak', 'RedLosses', 'RedWinsByDecisionMajority', 'RedWinsByDecisionSplit', 'RedWinsByDecisionUnanimous', 'RedWinsByKO', 'RedWinsBySubmission', 'RedWins','RedHeightCms','RedReachCms', 'RedWeightLbs']
y = data['Winner']
X = data[imp_columns]
my_imputer = SimpleImputer(strategy = 'mean')
X_imp = my_imputer.fit_transform(X)
train_X, val_X, train_y, val_y = train_test_split(X_imp, y, random_state=1)
model = LogisticRegression(random_state = 1)
model.fit(train_X, train_y)
predictions = model.predict(val_X)

print(predictions[:10])
from sklearn.metrics import mean_absolute_error
mean = mean_absolute_error(predictions, val_y)
print(mean)
accuracy = accuracy_score(predictions,val_y)
print(accuracy)

from sklearn.metrics import f1_score

f1 = f1_score(val_y, predictions)
print("F1 Score:", f1)
from sklearn.metrics import precision_score
precision = precision_score(val_y, predictions)
print("Precision:", precision)

from sklearn.metrics import classification_report
print(classification_report(val_y, predictions))

with open('ufc_ml.pkl', 'wb') as file:
    pickle.dump(model, file)

with open('ufc_ml.pkl', 'rb') as file:
    loaded_model = pickle.load(file)