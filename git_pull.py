import os, subprocess

# TODO: Change hardcoded path
os.chdir(r"C:\Users\fhnaz\Desktop\AZ-scan")
print("Actualizando AZ-scan...")
subprocess.run(["git","pull"], shell=True)
input("Presionar Enter para terminar...")