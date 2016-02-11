# Bares y Tapas

> Aplicación Bares y Tapas desarrollada en la asignatura de Desarrollo de Aplicaciones para Internet (DAI)

## Descripción 

La aplicación consiste en una adaptación del tutorial [How To Tango With Django 1.7](http://www.tangowithdjango.com/book17/). Disponemos de una lista de bares y tapas asociadas a dichos bares, que los usuarios registrados podrán ir incrementando. El sistema cuenta con las siguientes funcionalidades:

- Autentificación y registro de usuarios. Implementado con el plugin `django-registration-redux`.
- Contador de visitas de bares. Cada vez que un usuario solicita la página de un bar, su contador de visitas aumenta en 1.
- Sistema para añadir nuevas tapas. Mediante un formulario restringido a usuarios autentificados, éstos pueden añadir nuevas tapas a la lista de tapas de un bar en concreto.
- Mapa de dirección de cada bar. Gracias al plugin [`easy maps`](https://github.com/bashu/django-easy-maps), añadimos un mapa con la dirección de cada bar, a partir de su atributo `direccion`.
- Botones para cambiar tamaño de letra. Con [JQuery](http://jquery.com/) podemos cambiar el tamaño de la fuente de toda la página, habilitando tres botones para ello: `Letra grande`, `Letra más grande` y `Letra normal`.
- Gráfico comparativo de las visitas de cada bar. Haciendo uso de la librería [Highcharts](http://www.highcharts.com/).
- Botón `Me gusta` para cada tapa. Con estos botones incrementamos el número de votos de cada tapa haciendo una llamada _ajax_ al servidor.

## Puesta en producción

Para poner en producción la aplicación, necesitamos hacer algunos cambios:

- Deshabilitar el ambiente de depuración
- Cambiar el servidor web por el definitivo de producción.

### Deshabilitando ambiente de depuración

Creamos un nuevo fichero `production.py` que contendrá los _settings_ propios para producción. Esto es:

```
# DEBUG = True, pasa a:
DEBUG = False

# ALLOWED_HOSTS = [] pasa a:
ALLOWED_HOSTS = ['*']
```

### Servidor web

La aplicación funcionará con otro servidor web distinto del de desarrollo. Además, se encargará de servir los archivos (direcotio `static`). Django, como el resto de los framewors de python, necesitan de un servidor web con interface WSGI, los cuales hacen una llamada asíncrona a la aplicación con toda la indormación del ambiente.

Haremos uso de [`gunicorn`](http://gunicorn.org/), el cual es un servidor web wsgi muy sencillo de instalar y que usará nuestro fichero `.wsgi` ya incluido en Django.

```
# Lo instalamos con:
$ pip install gunicorn

# Si queremos ejecutarlo en el puerto 8000:
$ gunicorn mi_app.wsgi --bind: 0.0.0.0:8000
```

Para servir los archivos estáticos, balance de carga, restricciones de accesos, etc, podemos utilizar [`nginx`](http://nginx.org/). 

Lo primero, será copiar el directorio `static` al directorio donde nginx los sirva. Para ello, podemos ejecutar:

```
$ cp -r static/ /var/www/static
``` 

En el repositorio se adjunta la configuración elegida para ello:

```
server {
     listen 80 default_server;
     
     # servidor web para archivos en  /static
     location /static/ {
		alias /var/www/static/; 
	 }

     # proxy inverso, se pasa a la aplicación wsgi
     location / {
           proxy_pass http://127.0.0.1:8001;
           proxy_set_header X-Forwarded-Host $server_name;
           proxy_set_header X-Real-IP $remote_addr;
     }
```

Además, usaremos [`supervisor`](http://supervisord.org/) para vigilar que el proceso del servidor web esté siempre ejecutándose. Su configuración se adjunta también al repositorio.

```
# /etc/supervisor/conf.d/supervisor.conf

[program:gunicorn]
command=/usr/local/bin/gunicorn Bares.wsgi  --bind 0.0.0.0:8000
directory=/path/donde/este/manage.py
user=elquesea
autostart=true
autorestart=true
redirect_stderr=true
```

Ya que dispongo de una cuenta de forma temporal en Azure, realizaremos el despliegue allí. Los pasos seguidos para ello son:

- **Creación de la máquina virtual en Azure**: para la creación de la máquina, tendremos que descargar el cliente para linea de órdenes de Azure y realizar lo siguiente:

```
# Descargamos el cliente
$ sudo apt-get install nodejs-legacy
$ sudo apt-get install npm
$ sudo npm install -g azure-cli

# Iniciamos sesión
$ azure login

# Instalamos una imagen
$ azure vm create baresytapas b39f27a8b8c64d52b05eac6a62ebad85__Ubuntu-14_04_3-LTS-amd64-server-20160201-en-us-30GB <usuario> <clave> --location "East Asia" --ssh
```

A continuación, utilizaremos [Ansible](http://www.ansible.com/) para aprovisionar la máquina con todo lo necesario. Para ello, creamos un Playbook en formato `.yml`. Además, debemos almacenar como variable de entorno ANSIBLE_HOSTS, con el contenido de un fichero `ansible_hosts` con el alias de la máquina entre corchetes ([]) y, en otra línea, el dns o ip de la máquina. A continuación se muestra el contenido del `baresytapas.yml` utilizado.

```
---
- hosts: baresytapas
  remote_user: <usuario_maquina>
  become: yes
  become_method: sudo
  tasks:
  - name: Actualizar repositorios de paquetes
    apt: update_cache=yes

  - name: Instalar python y otros paquetes
    action: apt pkg={{ item }} state=present
    with_items:
      - python-setuptools
      - build-essential 
      - python-dev
      - git
      - nginx
      - supervisor

  - name: Instalar pip
    easy_install: name=pip
    
  - name: Instalar servidor wsgi Gunicorn
    pip: name=gunicorn 

  - - name: Obtener la aplicacion de Github
    become_user: <usuario>
    git: repo=https://github.com/mpvillafranca/barestapas.git  dest=/home/<usuario>/barestapas clone=yes force=yes
    
  - name: Instalar dependencias de la aplicacion
    become_user: <usuario>
    pip: requirements=/home/<usuario>/barestapas/requirements.txt
```

Para aplicar los cambios, ejecutamos:

```
$ ansible-playbook -u <usuario> baresytapas.yml
```

A continuación, con [Fabric] realizamos las últimas gestiones por medio de un fichero `fabfile.py`:

```python
from fabric.api import run

def runserver():
    run('cd barestapas/tango_with_django_project && python manage.py migrate --settings=tango_with_django_project.productionsettings')
    run('sudo mkdir -p /var/www')
    run('cd barestapas/tango_with_django_project && sudo cp -r static/ /var/www/static')
    run('cd barestapas && sudo cp production-webconfig/default /etc/nginx/sites-available/')
    run('cd barestapas && sudo cp production-webconfig/supervisor.conf /etc/supervisor/conf.d/')
    run('sudo service nginx restart')
    run('sudo service supervisor restart')
```

Con todo esto, finalmente, tendremos a la aplicación ejecutándose [aquí](http://baresytapas.cloudapp.net) con la configuración de Django correspondiente a produción.
