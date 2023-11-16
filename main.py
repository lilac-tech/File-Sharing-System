import os

os.getcwd()
os.chdir('D:\python\python_django\pythonProject')
os.chdir('./python installers')
print(os.getcwd())
os.system("python dependencies_installer.py")
os.chdir('..')
os.chdir('./file_sharing_system')
print(os.getcwd())

os.system("python manage.py migrate --run-syncdb")
os.system("python manage.py makemigrations")

if not os.path.exists('db.sqlite3'):
    os.system("python manage.py createsuperuser")

print("\n\n\n", os.system('ipconfig'), "\n\n\n")
os.system("python manage.py runserver 0.0.0.0:8000")
