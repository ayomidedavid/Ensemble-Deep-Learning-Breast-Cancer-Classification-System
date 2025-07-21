import requests

# Replace with the actual URL of your login route
LOGIN_URL = 'http://localhost:5000/login'  # Adjust the port if necessary

def test_login(email, password):
    response = requests.post(LOGIN_URL, data={'email': email, 'password': password})
    print(response.text)

if __name__ == "__main__":
    test_login('batman@gmail.com', '12345678')  # Replace with the actual password
