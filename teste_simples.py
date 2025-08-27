#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("🚀 Iniciando teste simples...")

try:
    from flask import Flask
    print("✅ Flask importado")
    
    app = Flask(__name__)
    print("✅ App Flask criado")
    
    @app.route('/')
    def home():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Associação Amigo do Povo - FUNCIONANDO!</title>
        </head>
        <body>
            <h1>🎉 SISTEMA FUNCIONANDO!</h1>
            <p>✅ Associação Amigo do Povo</p>
            <p>🔐 Login: admin/admin123</p>
            <p>📱 Sistema completo carregado!</p>
        </body>
        </html>
        '''
    
    print("🌐 Iniciando servidor na porta 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
