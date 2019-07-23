import requests

url = "http://www.variflight.com/flight/detail/productImg&s=Y0RGVUFnd1dWQlRKU3dZNVU1YzJEeThtWGozQ1lKbmY=&w=80&h=40&fontSize=16&fontColor=707070&background=dbe2ec"

querystring = {"AE71649A58c77":""}

headers = {
    'cookie': "salt=5d35192eb6797;",
    'User-Agent': "PostmanRuntime/7.15.0",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Host': "www.variflight.com",
    'accept-encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)