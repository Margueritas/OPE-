from django.http import HttpRequest
import json

def get_carrinho_dict(req:HttpRequest):
    ses = req.session
    carrinhoDict = ses['carrinho']
    if carrinhoDict is None:
        print('carrinho none.')
        carrinhoDict = {}
        ses['carrinho'] = json.dumps(carrinhoDict)
    else:
        print('carrinho not none')
    ses.save()
    return carrinhoDict