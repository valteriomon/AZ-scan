import subprocess

while True:
    subprocess.run([
        r"C:\Program Files\NAPS2\NAPS2.Console.exe",
        '--output', "test.png",
        '--noprofile',
        '--driver', "twain",
        '--device', "twain",
        '--dpi', "600",
    ], check=True, text=True)

    input("Press Enter to scan the next page...")
