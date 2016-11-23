# asdadsadsadsads - Choice Master

### Para instalar los requerimientos:

1. Creamos un entorno virtual para evitar conflictos.

```sh
sudo apt-get install virtualenv
virtualenv venv

```
2. Activamos el entorno virtual.

```sh
source ./venv/bin/activate
```

3. Instalamos los requerimientos de *requirements.txt*.

```sh
pip install -r requirements.txt
```

### Para hacer funcionar el login por Github o Google, en una terminal ejecutamos:

```sh
python manage.py loaddata choicemaster/fixtures/socialapps.json
```

### Como modificar y compilar el *CSS*:

- Para modificar el **CSS**, en realidad, debemos editar los archivos de terminación: **.scss**
- Estos son más poderosos que los **.css** de siempre.
- Se llaman **Sass (Syntactically Awesome Stylesheets)**.
- Luego de modificarlos debemos compilarlos, tarea que requiere que tengamos **Ruby Gems** instalado:

1. Bajamos **Ruby Gems** y lo descomprimimos.

```sh
cd 
wget "https://rubygems.org/rubygems/rubygems-2.6.7.tgz"
tar -xf rubygems-2.6.7.tgz
```

2. Instalamos **Ruby** y luego **Gems**.

```sh
sudo apt-get install ruby
cd rubygems-2.6.7
sudo ruby setup.rb
```

3. Cuando finalizan ambas instalaciones es momento de instalar **sass**.

```sh
sudo gems install sass
```

4. Finalmente nos dirigmos al directorio principal del proyecto y compilamos.

```sh
cd choice_master
sh build_sass.sh
```

