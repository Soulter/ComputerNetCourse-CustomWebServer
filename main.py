from conn import WebServer

app = WebServer(8080)

@app.get("/")
def index(request):
    return "Hello World"

@app.get("/hello")
def hello(request):
    return "Hello"

@app.get("/world")
def world(request):
    return "World"

app.start()