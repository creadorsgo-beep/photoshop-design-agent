import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_HEADER  = "#0f1117"
BG_MAIN    = "#13151f"
BG_CARD    = "#1a1d2e"
ACCENT     = "#4f8ef7"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Design Agent")
        self.geometry("1340x860")
        self.minsize(960, 640)
        self.configure(fg_color=BG_MAIN)
        self._frame = None
        self.show_main()

    def _switch(self, frame_cls, **kwargs):
        if self._frame:
            self._frame.destroy()
        self._frame = frame_cls(self, **kwargs)
        self._frame.pack(fill="both", expand=True)

    def show_main(self):
        from gui.main_screen import MainScreen
        self._switch(MainScreen, on_select=self.show_client)

    def show_client(self, client_name):
        from gui.client_screen import ClientScreen
        self._switch(ClientScreen, client_name=client_name, on_back=self.show_main)
