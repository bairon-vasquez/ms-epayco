from dataclasses import dataclass

from flask import Flask, request, jsonify
from dotenv import load_dotenv

import epaycosdk.epayco as epayco
import requests
import json
import os

load_dotenv()

apiKey = os.getenv("PUBLIC_KEY")
privateKey = os.getenv("PRIVATE_KEY")
lenguage = "ES"
test = True
options={"apiKey":apiKey,"privateKey":privateKey,"test":test,"lenguage":lenguage}

objepayco=epayco.Epayco(options)

def generate_token(data):
    credit_info = {
        "card[number]": data['number'],
        "card[exp_year]": data['exp_year'],
        "card[exp_month]": data['exp_month'],
        "card[cvc]": data['cvc'],
        "hasCvv": True  # // hasCvv: validar codigo de seguridad en la transacción
    }
    return objepayco.token.create(credit_info)

def create_customer(data, token_card):
    customer_info = {
        "token_card": token_card,
        "name": data['name'],
        "last_name": data['last_name'],
        "email": data['email'],
        "phone": data['phone'],
        "default": True
    }

    return objepayco.customer.create(customer_info)

app = Flask(__name__)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/customer/<string:customerId>', methods=['GET'])
def get_customer(customerId):
    return objepayco.customer.get(customerId)

@app.route('/charge', methods=['POST'])
def charge():
    data = request.get_json()
    token_card = generate_token(data['card'])
    customer_id = create_customer(data['customer'], token_card['data']['id'])['data']['customerId']

    customer = objepayco.customer.get(customer_id)

    payment_info = {
        "token_card": token_card['id'],
        "customer_id": customer['data']['id_customer'],
        "doc_type": "CC",
        "doc_number": data['customer']['doc_number'],
        "name": customer['data']['name'],
        "last_name": data['customer']['last_name'],
        "email": customer['data']['email'],
        "bill": data['bill'],
        "description": data['description'],
        "value": "116000",
        "tax": "16000",
        "tax_base": "100000",
        "currency": "COP",
        "dues": data['dues'],
        "ip": "190.000.000.000",  # This is the client's IP, it is required
        "url_response": "https://tudominio.com/respuesta.php",
        "url_confirmation": "https://tudominio.com/confirmacion.php",
        "method_confirmation": "GET",
        "use_default_card_customer": True,
    }

    return objepayco.charge.create(payment_info)

if __name__ == '__main__':
    app.run()