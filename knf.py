import requests
from datetime import datetime, timedelta
import os
url = 'https://rss.knf.gov.pl/rss_pub/JSON'

form_data = {
    'request': '{"cmd":"get","search":[],"limit":10000,"offset":0,"method":"RssHTable","sort":[{"field":"POSITION_DATE","direction":"asc"}],"searchLogic":"AND","searchValue":""}'
}

headers = {
    'Content-Type': 'application/json',
}
data = []
try:
    response = requests.post(url, data=form_data)
    

    if response.status_code == 200:

        data = response.json()["records"]
    else:

        print(f"Error: {response.status_code}")
except requests.exceptions.RequestException as e:

    print(f"Error: {e}")
    
def array_has_string(arr, search_string):
    return any(isinstance(elem, str) and elem == search_string for elem in arr)

# isin = []
# records = []
# print(res[0])
# for e in res:
#     if (array_has_string(isin, e['ISIN'])):
#         continue
#     isin.append(e['ISIN'])
#     records.append(e)
# print(len(res))
# print(len(records))

for entry in data:
    entry['POSITION_DATE'] = datetime.strptime(entry['POSITION_DATE'], '%Y-%m-%d')
    entry['MODIFY_DATE'] = datetime.strptime(entry['MODIFY_DATE'], '%Y-%m-%d')
    issuer_name = entry['ISIN']
    issuer_name = issuer_name[2:]
    issuer_name = ''.join(char for char in issuer_name if not char.isdigit())
    if (entry['ISIN'] == 'LU2237380790'):
        entry['ISIN'] = 'ALE'
    elif (entry['ISIN'] == 'NL0015000AU7'):
        entry['ISIN'] = 'PCO'
    elif (entry['ISIN'] == 'CY1000031710'):
        entry['ISIN'] = 'ASB'
    elif (entry['ISIN'] == 'PLEURCH00011'):
        entry['ISIN'] = 'EUR'
    elif (entry['ISIN'] == 'PLENEA000013'):
        entry['ISIN'] = 'ENA'
    elif (entry['ISIN'] == 'PLOPTTC00011'):
        entry['ISIN'] = 'CDR'
    elif (entry['ISIN'] == 'PLTLKPL00017'):
        entry['ISIN'] = 'OPL'
    elif (entry['ISIN'] == 'PLPEKAO00016'):
        entry['ISIN'] = 'PEO'
    elif (entry['ISIN'] == 'PLENERG00022'):
        entry['ISIN'] = 'ENG'
    elif (entry['ISIN'] == 'PLBZ00000044'):
        entry['ISIN'] = 'SPL'
    elif (entry['ISIN'] == 'PLTAURN00011'):
        entry['ISIN'] = 'TPE'
    elif (entry['ISIN'] == 'PLKGHM000017'):
        entry['ISIN'] = 'KGH'
    elif (entry['ISIN'] == 'PLBIG0000016'):
        entry['ISIN'] = 'MIL'
    elif (entry['ISIN'] == 'PLALIOR00045'):
        entry['ISIN'] = 'ALR'
    elif (entry['ISIN'] == 'PLBRE0000012'):
        entry['ISIN'] = 'MBK'
    elif (entry['ISIN'] == 'PLSOFTB00016'):
        entry['ISIN'] = 'ACP'
    elif (entry['ISIN'] == 'PLLWBGD00016'):
        entry['ISIN'] = 'LWB'
    elif (entry['ISIN'] == 'PLBH00000012'):
        entry['ISIN'] = 'BHW'
    elif (entry['ISIN'] == 'PLTRKPL00014'):
        entry['ISIN'] = 'TRK'
    elif (entry['ISIN'] == 'PLRAFAK00018'):
        entry['ISIN'] = 'RFK'
    else:
        entry['ISIN'] = issuer_name

# Create a new array to store filtered data
filtered_data = []

# Create a dictionary to keep track of short positions by company for each stock
short_positions = {}
data = [entry for entry in data if entry['ISSUER_NAME'] not in ('CEDC', 'DWORY', 'LOTOS', 'NETIA', 'TVN', 'GETBK', 'SYNTHOS', 'GETINOBLE')]

# Iterate over the original data
for entry in data:
    issuer_name = entry['ISSUER_NAME']
    holder_name = entry['HOLDER_FULL_NAME']
    position_date = entry['POSITION_DATE']
    if (entry['NET_SHORT_POSITION_O']) == '&lt;0,5':
        continue
    # If the stock has not been shorted by this company in the past 365 days, include this entry
    if issuer_name not in short_positions.get(holder_name, {}) or (position_date - short_positions[holder_name][issuer_name]).days >= 400:
        filtered_data.append(entry)
        # Update the short positions dictionary
        short_positions.setdefault(holder_name, {})[issuer_name] = position_date

# Print the filtered data
# for entry in filtered_data:
#     print(entry['ISIN'])

# print(len(filtered_data))

def calculate_percentage_change(old_price, new_price):
    return ((new_price - old_price) / old_price) * 100

# Function to check if the short was successful
def is_short_successful(start_date, isin):
    # Define the path to the file
    file_path = os.path.join('records', f'{isin}.txt')
    # Check if the file exists
    if not os.path.exists(file_path):
        return False

    # Read the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Parse the data
    candles = []
    for line in lines[1:]:
        parts = line.strip().split(',')
        date = datetime.strptime(parts[2], '%Y%m%d')
        close_price = float(parts[7])
        candles.append((date, close_price))
    
    # Find the index of the start date
    for i, (date, _) in enumerate(candles):
        if date >= start_date:
            start_index = i
            break

    # Check the next 10 candles
    for i in range(start_index, start_index + 90):
        if i >= len(candles):
            return False
        _, start_price = candles[start_index]
        _, current_price = candles[i]
        percentage_change = calculate_percentage_change(start_price, current_price)
        if percentage_change <= -3:
            return True

    return False

# Calculate success rate
total_shorts = len(filtered_data)
successful_shorts = sum(1 for entry in filtered_data if is_short_successful(entry['POSITION_DATE'], entry['ISIN']))

# Calculate success rate
success_rate = (successful_shorts / total_shorts) * 100 if total_shorts > 0 else 0

print(f"Success Rate: {success_rate:.2f}%")


holder_shorts = {}

# Calculate success rate
for entry in filtered_data:
    holder_name = entry['HOLDER_FULL_NAME']
    start_date = entry['POSITION_DATE']
    isin = entry['ISIN']
    success = is_short_successful(start_date, isin)
    holder_shorts.setdefault(holder_name, {'total': 0, 'successful': 0})
    holder_shorts[holder_name]['total'] += 1
    if success:
        holder_shorts[holder_name]['successful'] += 1

# Sort holders by winrate
sorted_holders = sorted(holder_shorts.items(), key=lambda x: x[1]['successful'] / x[1]['total'] if x[1]['total'] > 0 else 0, reverse=True)
filtered_holders = [(holder, stats) for holder, stats in sorted_holders if stats['total'] >= 0 and (stats['successful'] / stats['total']) * 100 > 50]
# filtered_holders = sorted_holders
# Print winrate, amount of shorts, and rank for each holder
print("Winrate for each holder (Ranked by Winrate):")
for rank, (holder, stats) in enumerate(filtered_holders, start=1):
    winrate = (stats['successful'] / stats['total']) * 100 if stats['total'] > 0 else 0
    print(f"{rank}. {holder}: Winrate: {winrate:.2f}%, Amount of Shorts: {stats['total']}")