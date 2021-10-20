from django.http import HttpRequest, HttpResponse
import base64
import json

COOKIE_KEY = "carrinho"

def get_carrinho_dict(req:HttpRequest) -> list:
    carrinho = []
    carrinhoBase64 = req.COOKIES.get(COOKIE_KEY)
    if not carrinhoBase64 is None:
        carrinho = json.loads(base64.b64decode(carrinhoBase64))
    return carrinho

def save_carrinho_dict(resp:HttpResponse, carrinho:list):
    resp.set_cookie(COOKIE_KEY, base64.b64encode(json.dumps(carrinho).encode('ascii')).decode('ascii'))