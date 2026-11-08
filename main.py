import customtkinter as tk
import json, os, pygame, sys

class TouchKeypadFrame(tk.CTkFrame):
    def __init__(self, parent, target_entry, **kwargs):
        super().__init__(parent, **kwargs)
        self.target_entry = target_entry
        self.configure(fg_color="#CCCCCC", corner_radius=12)
        
        # 3x5 Grid Layout Layout Matrix
        layout = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['#', '0', '⌫'],
            ['Clear']
        ]
        
        for r in range(5): self.grid_rowconfigure(r, weight=1)
        for c in range(3): self.grid_columnconfigure(c, weight=1)
            
        for r, row in enumerate(layout):
            for c, key in enumerate(row):
                span = 3 if key == 'Clear' else 1
                b_color = "#404040" if key in ['Clear', '⌫'] else "#F5F5F5"

                btn = tk.CTkButton(
                    self, text=key, font=("Arial", 18, "bold"),
                    fg_color=b_color, hover_color="#B3B3B3", text_color="#1C1C24",
                    corner_radius=6, command=lambda k=key: self.key_press(k)
                )
                btn.grid(row=r, column=c, columnspan=span, padx=4, pady=4, sticky="nsew")

    def key_press(self, key):
        if key == 'Clear':
            self.target_entry.delete(0, tk.END)
        elif key == '⌫':
            txt = self.target_entry.get()
            if txt: self.target_entry.delete(len(txt) - 1, tk.END)
        else:
            self.target_entry.insert(tk.END, key)


class Application(tk.CTk):


    def __init__(self):
        super().__init__()
        
        self.withdraw()
        self.title("Alarm Application")
        self.geometry("500x800")
        self.configure(fg_color=("#F8FAFC", "#1E293B"))
        
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        self.settings = self.check_settings()
        self.CORRECT_PIN = self.settings["Pin_Code"]
        
        self.is_armed = self.settings["activated"]
        
        theme = self.settings["theme"]
        self.is_playing = self.settings["sound_active"]
        self.panic_clicks = 0
        
        if theme == "dark":
            tk.set_appearance_mode("dark")
        else:
            tk.set_appearance_mode("light")
        
        
        self.count_down = False
        

        self.header_label = tk.CTkButton(
            self, 
            text="Wertz Home Security", 
            font=("Arial", 11, "bold"),
            text_color="#2C3E50",
            fg_color="transparent",
            hover=False,
            command=self.secret_settings
        )
        self.header_label.pack(pady=(25, 5))

                
        self.status_frame = tk.CTkFrame(
            self,
            height=110,                        
            fg_color="#1A1A1A",  
            corner_radius=16,               
            border_width=1,                  
            border_color=("#E2E8F0", "#334155")
        )
        self.status_frame.pack(pady=20, fill="x", padx=40)
        self.status_frame.pack_propagate(False)

        # Main Title Status
        self.status_label = tk.CTkLabel(
            self.status_frame, 
            text="SYSTEM READY", 
            font=("Arial", 26, "bold"),        
            text_color=("#DCFCE7", "#22C55E")  
        )
        
        self.status_label.pack(pady=(22, 4))   

        
        self.details_label = tk.CTkLabel(
            self.status_frame, 
            text="All entry zones secured",    
            font=("Arial", 13),                
            text_color=("#64748B", "#94A3B8")
        )
        self.details_label.pack(pady=(0, 22))
        
        self.split_container = tk.CTkFrame(self, fg_color="transparent")
        self.split_container.pack(pady=10, fill="both", expand=True, padx=20)

       
        self.left_panel = tk.CTkFrame(self.split_container, fg_color="transparent", width=600)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))
        self.left_panel.pack_propagate(False) 

        
        self.right_panel = tk.CTkFrame(self.split_container, fg_color="transparent")
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))


        
        self.code = tk.CTkEntry(
            self.right_panel, 
            placeholder_text="Enter Code", 
            show='*', 
            width=425,
            font=("Arial", 36),               
            corner_radius=10,                 
            border_width=2,                    
            border_color="#3b8ed0",            
            fg_color="#1A1A1A",                
            text_color="#ffffff",              
            placeholder_text_color="#757575",  
            justify="center"                   
        )
        self.code.pack(pady=(0, 10), fill="x", ipady=8)
        
        self.keypad = TouchKeypadFrame(self.right_panel, self.code)
        self.keypad.pack(fill="both", expand=True)
        
        self.arm_btn = tk.CTkButton(
            self.left_panel, 
            text="ARM SYSTEM (AWAY)",
            font=("Arial", 14, "bold"),
            height=130,                           
            corner_radius=12,                  
            fg_color=("#DCFCE7", "#15803D"),     
            hover_color=("#BBF7D0", "#166534"),
            text_color=("#14532D", "#FFFFFF"),
            command=self.toggle_stay_away
        )
        self.arm_btn.pack(pady=6, fill="x")

        self.stay_btn = tk.CTkButton(
            self.left_panel, 
            text="ARM SYSTEM (HOME)",
            font=("Arial", 14, "bold"),
            height=130,                          
            corner_radius=12,
            fg_color=("#E0F2FE", "#334155"),     
            hover_color=("#BAE6FD", "#475569"),
            text_color=("#0369A1", "#FAFAFA"),
            command=self.toggle_arm_state
        )
        self.stay_btn.pack(pady=6, fill="x")

        self.panic_btn = tk.CTkButton(
            self.left_panel, 
            text="TRIGGER PANIC ALARM",
            height=130,
            fg_color=("#FEE2E2", "#800000"),
            hover_color=("#FCA5A5", "#590000"),
            text_color=("#991B1B", "#FFFFFF"),
            font=("Arial", 16, "bold"),    
            corner_radius=12, 
            command=self.trigger_panic
        )
        self.panic_btn.pack(pady=6, fill="x")
        
        self.reset_btn = tk.CTkButton(
            self.left_panel, 
            text="DEACTIVATE ALARM",
            height=130,
            fg_color=("#FBF0EC", "#C25E43"),
            hover_color=("#F3DDD4", "#A64A32"),
            text_color=("#84311B", "#FAFAFA"),
            font=("Arial", 15, "bold"),
            corner_radius=12,
            command=self.toggle_reset
        )
        self.reset_btn.pack(pady=6, fill="x")
        
        self.theme_btn = tk.CTkButton(
            self,
            text="Toggle Display Mode",
            font=("Arial", 11),
            height=25,
            fg_color="transparent",
            text_color=("#64748B", "#94A3B8"),
            hover_color=("#E2E8F0", "#334155"),
            command=self.toggle_preview_mode
        )
        self.theme_btn.pack(side="bottom", pady=20)
        
        
        if self.is_armed:
            self.booted_alarm_state()
            
            
        tk.set_widget_scaling(1.0)
        tk.set_window_scaling(1.0)
        
        self.update_idletasks() 
        
        self.attributes("-fullscreen", True)         

        self.deiconify()

    def secret_settings(self):
        code = self.code.get()
        
        audio_folder = "audio"
        audio_option = os.listdir(audio_folder)
        
        if code == self.settings["Config_code"]:
            toplevel = tk.CTkToplevel(self)
            toplevel.title("Admin Settings")
            toplevel.geometry("600x500")
            toplevel.resizable(True, True)  
            
            
            toplevel.wm_transient(self)        
            toplevel.after(200, toplevel.lift) 
            toplevel.focus_set()               
            
            
            label = tk.CTkLabel(toplevel, text="Admin Control Panel", font=("Arial", 16, "bold"))
            label.pack(pady=20)
            
            side_banner = tk.CTkFrame(toplevel, height=60, fg_color="gray20")
            side_banner.pack(side="left", padx=10, pady=5, fill="y")
            
            sound_label = tk.CTkLabel(side_banner, text="Alarm Sound", font=("Arial", 16, "bold"))
            sound_label.pack(pady=35)
            
            dropdown = tk.CTkOptionMenu(
                master=toplevel,
                values=audio_option,
                width=350,
                height=45,                         
                font=("Arial", 15),                
                dropdown_font=("Arial", 14),       
                corner_radius=10,                  
                
                
                fg_color=("#E2E8F0", "#262626"),   
                button_color=("#CBD5E1", "#334155"), 
                button_hover_color=("#94A3B8", "#475569"),
                text_color=("#0F172A", "#FAFAFA"),
                
                
                dropdown_fg_color=("#F1F5F9", "#1E1E1E"),    
                dropdown_hover_color=("#CBD5E1", "#334155"), 
                dropdown_text_color=("#0F172A", "#FAFAFA"),
                
                dynamic_resizing=False,          
                command=self.update_sound_file
            )
            dropdown.pack(pady=40)
            
            dropdown.set(self.settings["audio_file"])
                
                        
            exit_btn = tk.CTkButton(
                toplevel,
                text="Exit Application",
                command=sys.exit,
                fg_color="#991B1B",
                hover=False
            )
            exit_btn.pack(padx=5, pady = 5, side="bottom", fill="x")
            
            exit_top = tk.CTkButton(
                toplevel,
                text="Exit Admin Window",
                command=toplevel.destroy,
                fg_color="#991B1B",
                hover=False
            )
            exit_top.pack(padx=5, pady = 5, side="bottom", fill="x")
            
            
            self.code.delete(0, 'end')
            
    def play_selected_audio(self, path, times = None):
        
        if self.is_playing is False:
            print(self.is_playing)
            self.siren = pygame.mixer.Sound(path)
            self.siren.play(loops=times)
            self.is_playing = True
            self.settings['sound_active'] = True
        else:
            print("Playing is True")
            
    def update_sound_file(self, sound):
        with open("config.json", "r") as file:
            data = json.load(file)

        data["audio_file"] = sound
        
        with open("config.json", "w") as file:
            json.dump(data, file, indent=4)
        
    def booted_alarm_state(self):
        self.status_label.configure(text="SYSTEM ARMED", text_color=("#FFE4E6", "#EF4444"))
        self.details_label.configure(text="Motion & Entry sensors monitoring")
        self.stay_btn.configure(state="disabled")
        self.arm_btn.configure(state="disabled")
        
            
    def stop_siren(self):
        if self.is_playing:
            self.siren.stop()
            self.is_playing = False
            self.settings["sound_active"] = False
        
    def toggle_alarm_counting(self, seconds):
        
        if seconds > 0 and self.count_down is True:
            self.status_label.configure(text=f"SYSTEM ARMED, {seconds} SECONDS TO EXIT", text_color=("#FFE4E6", "#EF4444"))
            self.details_label.configure(text="Motion & Entry sensors monitoring")
            self.arm_btn.configure(state="disabled")
            self.stay_btn.configure(state="disabled")
            self.panic_btn.configure(state="disabled")
            self.status_label.configure(text=f"{seconds} LEFT", text_color=("#FFE4E6", "#EF4444"))
            self.after(1000, self.toggle_alarm_counting, seconds - 1)
        elif self.count_down is False:
            self.is_armed = False
            self.status_label.configure(text="SYSTEM READY", text_color=("#DCFCE7", "#22C55E"))
            self.details_label.configure(text="All entry zones closed")
            self.arm_btn.configure(text="ARM SYSTEM (AWAY)", state="normal")
            self.stay_btn.configure(state="normal")
            self.reset_btn.configure(state="normal")
            self.panic_btn.configure(state="normal")
        else:
            self.is_armed = True
            self.update_arm_status(True)
            path = os.path.join("audio", "success.mp3")    
            self.play_selected_audio(path, 0)
            self.status_label.configure(text="SYSTEM ARMED", text_color=("#FFE4E6", "#EF4444"))
            self.arm_btn.configure(state="disabled")
            self.stay_btn.configure(state="distabled")
            self.reset_btn.configure(state="normal")
            self.panic_btn.configure(state="normal")
            
    def update_arm_status(self, status: bool):
        with open("config.json", "r") as file:
            data = json.load(file)

        data["activated"] = status
        
        with open("config.json", "w") as file:
            json.dump(data, file, indent=4)
    
        
    def toggle_stay_away(self):
        get_code = self.code.get()
        
        if get_code == self.CORRECT_PIN:
            if not self.is_armed:
                self.code.delete(0, tk.END)
                self.count_down = True
                self.toggle_alarm_counting(30)
            else:
                self.code.delete(0, tk.END)
                self.is_armed = False
                self.status_label.configure(text="SYSTEM READY", text_color=("#DCFCE7", "#22C55E"))
                self.details_label.configure(text="All entry zones closed")
                self.arm_btn.configure(text="ARM SYSTEM (AWAY)")
        else:
            self.status_label.configure(text="WRONG CODE", text_color=("#FFE4E6", "#EF4444"))
            
        
    def toggle_arm_state(self):
        """Simulates turning arm state on or off."""
        get_code = self.code.get()
        
        if get_code == self.CORRECT_PIN:
            if not self.is_armed:
                self.code.delete(0, tk.END)
                path = os.path.join("audio", "success.mp3")
                self.play_selected_audio(path, 0)
                self.is_armed = True
                self.update_arm_status(True)
                self.status_label.configure(text="SYSTEM ARMED", text_color=("#FFE4E6", "#EF4444"))
                self.details_label.configure(text="Motion & Entry sensors monitoring")
                self.arm_btn.configure(state="disabled")
            else:
                self.code.delete(0, tk.END)
                self.is_armed = False
                self.update_arm_status(False)
                self.status_label.configure(text="SYSTEM READY", text_color=("#DCFCE7", "#22C55E"))
                self.details_label.configure(text="All entry zones closed")
                self.stay_btn.configure(text="ARM SYSTEM (HOME)")
                self.arm_btn.configure(state="normal")
                self.siren.stop()
        else:
            self.status_label.configure(text="WRONG CODE", text_color=("#FFE4E6", "#EF4444"))

    def trigger_panic(self):
        
        if self.panic_clicks >= 2:
            # self.update_arm_status(True)
            
            with open("config.json", "r") as f:
                data=json.load(f)
            
            chosen_choice = data["audio_file"]
            print(chosen_choice)
            
            joined_path = os.path.join("audio", chosen_choice)
            
            self.play_selected_audio(joined_path, -1)
            print("Played sound")
            self.status_label.configure(text="ALARM TRIGGERED", text_color=("#FFE4E6", "#EF4444"))
            self.details_label.configure(text="Siren Active • Emergency broadcast sent")
            print("Panic dispatch protocol activated.")
        else:
            self.panic_clicks += 1

    def toggle_preview_mode(self):
        def update_settings(theme):
            with open("config.json", "r") as f:
                data = json.load(f)
                
            data["theme"] = theme
            
            with open("config.json", "w") as s:
                json.dump(data, s, indent=4)
            
        if tk.get_appearance_mode() == "Dark":
            tk.set_appearance_mode("Light")
            update_settings("light")
        else:
            tk.set_appearance_mode("Dark")
            update_settings("dark")
            
    def check_settings(self):
    
        file = "config.json"
        
        if not os.path.exists(file):
            self.create_default_data()
            
        
        with open(file, "r") as f:
            data = json.load(f)
            return data
        
    def save_new_code(self, code):
        
        with open("config.json", "r") as file:
            data = json.load(file)

        data["Pin_Code"] = code
        
        with open("config.json", "w") as file:
            json.dump(data, file, indent=4)
            
        self.settings = data
        self.CORRECT_PIN = code
    
            
    def toggle_reset(self):
        if self.status_label.cget("text") == "Entered Settings":
            code = self.code.get()
            
            if code == "0530#":
                self.status_label.configure(text="Error, code not allowed.", text_color=("#FFE4E6", "#EF4444"))
                return
            
            if not code:
                print(code)
                self.status_label.configure(text="ERROR, MUST ENTER CODE.", text_color=("#FFE4E6", "#EF4444"))
                return
            else:
                self.save_new_code(code)
            
        
        get_code = self.code.get()
        
        if get_code == self.CORRECT_PIN:
            self.code.delete(0, tk.END)
            self.stop_siren()
            self.panic_clicks = 0
            self.count_down = False
            self.is_armed = False
            self.update_arm_status(False)
            self.status_label.configure(text="SYSTEM READY", text_color=("#DCFCE7", "#22C55E"))
            self.details_label.configure(text="All entry zones closed")
            self.arm_btn.configure(text="ARM SYSTEM (AWAY)", state="normal")
            self.stay_btn.configure(state="normal", text="ARM SYSTEM (HOME)")
        elif get_code == self.settings["Config_code"]:
            self.status_label.configure(text="Entered Settings", text_color=("#DCFCE7", "#22C55E"))
        else:
            self.status_label.configure(text="WRONG CODE", text_color=("#FFE4E6", "#EF4444"))
        
            
    def create_default_data(self):
            
        default_data = {
            "activated": False
        }
        
        with open("config.json", "w") as f:
            json.dump(default_data, f, indent=4)
    

        
        
if __name__ == "__main__":
    root = Application()
    root.configure(fg_color="#E5E5E5")
    root.mainloop()