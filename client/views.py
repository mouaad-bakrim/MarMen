from django.shortcuts import render, redirect
from .forms import ClientForm

def ajouter_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client:ajouter_client')  # à adapter selon ta route de retour
    else:
        form = ClientForm()
    return render(request, 'add_client.html', {'form': form})
