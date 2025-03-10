import requests
import pandas as pd
from io import StringIO

response = requests.get('https://docs.google.com/spreadsheets/d/1t3wSutzLqKCV6-ZZVaEEU3NZaRT_ZNhVyxHPAqK_oE8/export?format=csv')
assert response.status_code == 200, 'Wrong status code'

# Convert the response content to a pandas DataFrame
csv_data = StringIO(response.content.decode('utf-8'))
df = pd.read_csv(csv_data)

# Set pandas display options to show the entire DataFrame
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

print(df)