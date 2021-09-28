from django.shortcuts import render,redirect
from apps.common.models import Usuario

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('painel')
    else:
        return redirect('login')

def painel(request):
    return render(request, 'painel.html')