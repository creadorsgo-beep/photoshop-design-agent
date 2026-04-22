"""Find and dismiss any blocking Photoshop dialog."""
import win32gui, win32con, win32api, time

def find_ok_buttons():
    buttons = []
    def enum_all(hwnd, _):
        try:
            cls = win32gui.GetClassName(hwnd)
            title = win32gui.GetWindowText(hwnd)
            if cls == 'Button' and title in ('OK', 'Aceptar', 'Yes', 'Si', 'Si\xad'):
                parent = win32gui.GetParent(hwnd)
                parent_title = win32gui.GetWindowText(parent) if parent else ''
                buttons.append((hwnd, title, parent_title))
        except Exception:
            pass
        return True
    win32gui.EnumWindows(enum_all, None)
    # Also enumerate child windows
    def enum_child(hwnd, _):
        try:
            cls = win32gui.GetClassName(hwnd)
            title = win32gui.GetWindowText(hwnd)
            if cls == 'Button' and title in ('OK', 'Aceptar', 'Yes', 'Si', 'Si\xad'):
                buttons.append((hwnd, title, 'child'))
        except Exception:
            pass
        return True
    try:
        win32gui.EnumWindows(lambda h, _: win32gui.EnumChildWindows(h, enum_child, None) or True, None)
    except Exception:
        pass
    return buttons

# Press Enter/Space to dismiss any dialog
import win32com.client
shell = win32com.client.Dispatch("WScript.Shell")

# Find PS window and send Enter
def find_windows():
    wins = []
    def cb(hwnd, _):
        try:
            title = win32gui.GetWindowText(hwnd)
            if title:
                wins.append((hwnd, title))
        except:
            pass
        return True
    win32gui.EnumWindows(cb, None)
    return wins

wins = find_windows()
for hwnd, title in wins:
    try:
        enc = title.encode('ascii', 'replace').decode()
        print(f"  {hex(hwnd)} {enc[:60]}")
    except:
        pass

# Send Enter key to bring PS to focus and dismiss dialog
print("\nSending Enter key...")
shell.AppActivate("Photoshop")
time.sleep(0.5)
shell.SendKeys("{ENTER}", 0)
time.sleep(0.3)
shell.SendKeys("{ENTER}", 0)
time.sleep(0.3)
print("Done. Check if PS is responsive now.")
