import requests

def get_user_location():
    try:
        print("Sending request...")

        response = requests.get("http://ip-api.com/json/")

        print("Status Code:", response.status_code)

        data = response.json()

        print("Response Data:", data)

        return data["city"]

    except Exception as e:
        print("Error:", e)
        return None

print(get_user_location())