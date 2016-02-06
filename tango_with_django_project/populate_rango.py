import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')

import django
django.setup()

from rango.models import Bar,Tapa

def populate():
    pepe_bar = add_bar("Casa Pepe", "Alegria, 69")

    add_tapa(bar=pepe_bar,
        nombre="Carne en salsa")

    add_tapa(bar=pepe_bar,
        nombre="Hamburguesa")

    add_tapa(bar=pepe_bar,
        nombre="Croquetas")

    juan_bar = add_bar("Bar de Juan", "Tristeza, 13")

    add_tapa(bar=juan_bar,
        nombre="Albondigas")

    django_bar = add_bar("Bar Django", "Euforia, 100")
    
    add_tapa(bar=django_bar,
        nombre="Canelones")

    for b in Bar.objects.all():
        for t in Tapa.objects.filter(bar=b):
            print "- {0} - {1}".format(str(b), str(t))

def add_bar(nombre, direccion, n_visitas=0):
    b = Bar.objects.get_or_create(nombre=nombre, direccion=direccion, n_visitas=n_visitas)[0]
    return b

def add_tapa(bar, nombre, votos=0):
    t = Tapa.objects.get_or_create(bar=bar, nombre=nombre)[0]
    t.votos=votos
    t.save()
    return t

# Start execution here!
if __name__ == '__main__':
    print "Starting Rango population script..."
    populate()
    
