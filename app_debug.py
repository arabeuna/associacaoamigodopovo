from flask import Flask, jsonify
import os

app = Flask(__name__)
app.secret_key = 'test'

@app.route('/')
def index():
    return "🎉 ASSOCIAÇÃO AMIGO DO POVO FUNCIONANDO!"

@app.route('/test')
def test():
    return jsonify({
        'status': 'OK',
        'message': 'Sistema funcionando!',
        'python_version': 'Working',
        'templates_dir': 'templates' in os.listdir('.'),
        'files': os.listdir('.')
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Debug app iniciando...")
    app.run(host='0.0.0.0', port=port, debug=True)
