from app import app


# the fact that these route functions are above the method declaration make them correspond to the "index" method's function.
@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"