import requests , json

url = "https://goldpricez.com/api/rates/currency/inr/measure/gram"
headers = {
    "x-api-key": "b9448a9d3772d35f6c908954e8cc4789b9448a9d"
}
data = requests.get(url=url, headers=headers)

print(data.json())