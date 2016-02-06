from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from rango.models import Bar, Tapa
from rango.forms import TapaForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


# Pagina inicio
def index(request):
    # Query the database for a list of ALL bares currently stored.
    # Order the bares by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    bares_list = Bar.objects.order_by('-n_visitas')[:5]
    context_dict = {'bares': bares_list}

    # Render the response and send it back!
    return render(request, 'rango/index.html', context_dict)

# Pagina bares
def bar(request, bar_name_slug):
    # Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {}

    try:
        # Can we find a bar name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        bar = Bar.objects.get(slug=bar_name_slug)
        context_dict['bar_name'] = bar.nombre

        # Retrieve all of the associated tapas.
        # Note that filter returns >= 1 model instance.
        tapas = Tapa.objects.filter(bar=bar)

        # Adds our results list to the template context under name tapas.
        context_dict['tapas'] = tapas
        # We also add the bar object from the database to the context dictionary.
        # We'll use this in the template to verify that the bar exists.
        context_dict['bar'] = bar
        # New: Aumentar visitas cada vez que se pida la pagina
        bar.n_visitas += 1
        bar.save()
    except Bar.DoesNotExist:
        # We get here if we didn't find the specified bar.
        # Don't do anything - the template displays the "no bar" message for us.
        pass

    # Go render the response and return it to the client.
    return render(request, 'rango/bar.html', context_dict)

# Pagina Acerca de
def about(request):
    # Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {}

    return render(request, 'rango/about.html', context_dict)

# Pagina add tapa
@login_required
def add_tapa(request, bar_name_slug):
    try:
        ba = Bar.objects.get(slug=bar_name_slug)
    except Category.DoesNotExist:
        ba = None

    if request.method == 'POST':
        form = TapaForm(request.POST)
        if form.is_valid():
            if ba:
                tapa = form.save(commit=False)
                tapa.bar = ba
                tapa.votos = 0
                tapa.save()
                # probably better to use a redirect here.
                return bar(request, bar_name_slug)
        else:
            print form.errors
    else:
        form = TapaForm()

    context_dict = {'form':form, 'bar': ba}

    return render(request, 'rango/add_tapa.html', context_dict)

def reclama_datos (request):
    bares = Bar.objects.order_by('-n_visitas')[:3]

    datos={'bares':[bares[0].nombre,bares[1].nombre,bares[2].nombre], 
           'visitas':[bares[0].n_visitas,
                      bares[1].n_visitas,
                      bares[2].n_visitas
           ]
          }

    return JsonResponse(datos, safe=False)

def like_tapa(request):
    context = RequestContext(request)
    tapa_id = None
    if request.method == 'GET':
        tapa_id = request.GET['tapa_id']
    votos = 0

    if tapa_id:
        tapa = Tapa.objects.get(id=int(tapa_id))
        if tapa:
            votos = tapa.votos + 1
            tapa.votos =  votos
            tapa.save()

    return HttpResponse(votos)
