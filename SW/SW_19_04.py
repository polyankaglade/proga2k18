import requests

endpoint = "api.vk.com/method"
method = "wall.get"
access_token = "6e4d0ec06e4d0ec06e4d0ec0a46e271b4a66e4d6e4d0ec032f4cd3c48768e41b63718b7"
params = "domain=ohlobistin&count=10"

url = "https://{endpoint}/{method}?{params}&v=5.52&access_token={token}".format(endpoint=endpoint, method=method, token=access_token, params=params)

print(url)
