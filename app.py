from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Microservices Architecture</title>
        <style>
            body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
            .container { background: white; padding: 50px; border-radius: 20px; text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
            h1 { color: #333; margin-bottom: 20px; }
            p { color: #666; font-size: 18px; margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏗️ Microservices Architecture</h1>
            <p>Professional microservices architecture implementation</p>
            <p>Scalable, distributed system design</p>
            <p>Docker containers, API Gateway, Service Discovery</p>
        </div>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

