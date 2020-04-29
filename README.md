# Smartweather-App
If you do not have the virtual environment package installed, run:

```
pip install virtualenv (pip3 for Mac/Linux)
```

Create a my_env folder for all environments, cd to the my_env folder and run:
```
virtualenv djangoPy3Env      (you can give the environment any name)
```

Use the following commands to activate the virtual environment:
```
| Mac/Linux: | source djangoPy3Env/bin/activate
| Windows: | call djangoPy3Env\Scripts\activate
```

Once the virtual environment is activated, you should see (djangoPy3Env)$ on the command line.

You can easily deactivate the virtual environment by typing the following command:
```
deactivate
```
With the virtual environment activated, cd to the folder where you wish to clone this repo and follow these commands:

```
git clone https://github.ncsu.edu/pmayank/weather.git
cd weather
pip install -r requirements.txt   (This will install all the required packages inside your virtual environment.)
python manage.py runserver
```
In the browser, enter http://127.0.0.1:8000/ and check if the app is running.
