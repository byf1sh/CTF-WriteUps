import requests
from bs4 import BeautifulSoup
import json

# Step 1: Kirim request ke URL
for i in range(600,700):
	url = f"http://targetlist.deadface.io:3001/pages?page={i}"
	response = requests.get(url)

	# Step 2: Parse HTML menggunakan BeautifulSoup
	soup = BeautifulSoup(response.content, "html.parser")

	# Step 3: Ambil data JSON dari tag <script> dengan id __NEXT_DATA__
	script_tag = soup.find("script", id="__NEXT_DATA__")
	if script_tag:
	    json_data = json.loads(script_tag.string)

	    # Step 4: Ambil bagian "targets" dari data JSON
	    targets = json_data['props']['pageProps'].get('targets', [])

	    if (targets):
		    print(f"{i} Targets:", targets)

	    # Print the targets
	else:
	    print("Script tag not found.")
