import os, subprocess

print("Actualizando AZ-scan...")
subprocess.run(["git","pull"], shell=True)
input("Presionar Enter para terminar...")