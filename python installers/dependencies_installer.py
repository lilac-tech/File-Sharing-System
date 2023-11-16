import os

print(os.getcwd())

modules = ["django==4.1.7", "django_cleanup==7.0.0", "tqdm==4.65.0", "PyPDF2==3.0.1", "pdf2image==1.16.3"]

for module in modules:
    command = "pip install " + module
    os.system(command)

input("Press Enter to continue...")
