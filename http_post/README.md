
## (recommend) use on venv

```
# cd (working directry)
python3 -m venv venv
source venv/bin/activate
# (deactivate)
```

## install

```
pip install requests
```
## exec

```
$ python http_post.py -f test.json -u http://httpbin.org/post
{
  "args": {}, 
  "data": "{\"name\": \"Jane Smith\", \"email\": \"janesmith@example.com\", \"job\": \"Data Scientist\"}", 
  "files": {}, 
  "form": {}, 
  "headers": {
    "Accept": "*/*", 
    "Accept-Encoding": "gzip, deflate", 
    "Content-Length": "81", 
    "Host": "httpbin.org", 
    "User-Agent": "python-requests/2.32.3", 
    "X-Amzn-Trace-Id": "Root=1-66d3a607-626a1cc315dbbf822e5f9771"
  }, 
  "json": {
    "email": "janesmith@example.com", 
    "job": "Data Scientist", 
    "name": "Jane Smith"
  }, 
  "origin": "99.0.85.0", 
  "url": "http://httpbin.org/post"
}
```
