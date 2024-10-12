import requests

url = "https://api.paymongo.com/v1/links"

payload = { "data": { "attributes": {
            "amount": 129900,
            "description": "Standard Room",
            "remarks": "Thankyou For Booking!"
        } } }
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Basic c2tfdGVzdF9uUnVobmFFMk1uZFYyNzhrbXJzaExGdEY6"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)