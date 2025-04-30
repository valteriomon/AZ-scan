# import subprocess

# while True:
#     subprocess.run([
#         r"C:\Program Files\NAPS2\NAPS2.Console.exe",
#         '--output', "test.png",
#         '--noprofile',
#         '--driver', "wia",
#         '--device', "lide",
#         '--dpi', "600",
#     ], check=True, text=True)

#     input("Press Enter to scan the next page...")
import comtypes.client

wia = comtypes.client.CreateObject("WIA.CommonDialog")
device = wia.ShowSelectDevice()
item = device.Items[0]
image = wia.ShowTransfer(item)

image.SaveFile("scan_output.jpg")
print("Scan saved as scan_output.jpg")
