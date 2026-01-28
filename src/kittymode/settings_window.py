"""Settings window for Kitty Mode.

The control panel for customizing your cat's meow-havior!
Tweak the purrameters until everything is just right. 🐱⚙️
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .config import ConfigManager


class SettingsWindow:
    """Settings configuration window using tkinter with tabs.
    
    Every kitty needs their own purrsonalized settings! Adjust timing,
    add custom meows, and make Kitty Mode truly yours. Nya~
    """
    
    def __init__(
        self,
        config_manager: "ConfigManager",
        on_save: Optional[Callable[[Dict], None]] = None
    ):
        """Initialize settings window.
        
        Args:
            config_manager: ConfigManager instance for reading/writing settings
            on_save: Callback with new config when saved
        """
        self.config = config_manager
        self.on_save = on_save
        self.window: Optional[tk.Tk] = None
        self._is_showing = False
    
    def show(self) -> None:
        """Show the settings window."""
        if self._is_showing:
            if self.window:
                self.window.lift()
            return
        
        self._is_showing = True
        
        self.window = tk.Tk()
        self.window.title("Kitty Mode Settings")
        self.window.geometry("420x480")
        self.window.resizable(False, False)
        
        # Try to bring window to front
        self.window.attributes('-topmost', True)
        self.window.after(100, lambda: self.window.attributes('-topmost', False))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # General tab
        general_frame = ttk.Frame(notebook, padding=10)
        notebook.add(general_frame, text="General")
        self._create_general_tab(general_frame)
        
        # Custom Noises tab
        noises_frame = ttk.Frame(notebook, padding=10)
        notebook.add(noises_frame, text="Custom Noises")
        self._create_noises_tab(noises_frame)
        
        # About tab
        about_frame = ttk.Frame(notebook, padding=10)
        notebook.add(about_frame, text="About")
        self._create_about_tab(about_frame)
        
        # Buttons frame
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self._close).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Reset to Defaults", command=self._reset).pack(side='left', padx=5)
        
        self.window.protocol("WM_DELETE_WINDOW", self._close)
        self.window.mainloop()
    
    def _create_general_tab(self, parent: ttk.Frame) -> None:
        """Create the General settings tab.
        
        Args:
            parent: Parent frame
        """
        # Window Duration
        ttk.Label(parent, text="Capture Window Duration:").pack(anchor='w', pady=(10, 0))
        self.duration_var = tk.IntVar(value=self.config.get('window_duration_ms', 800))
        duration_frame = ttk.Frame(parent)
        duration_frame.pack(fill='x', pady=(5, 0))
        
        duration_scale = ttk.Scale(
            duration_frame, from_=300, to=2000,
            variable=self.duration_var, orient='horizontal', length=280
        )
        duration_scale.pack(side='left')
        self.duration_label = ttk.Label(duration_frame, text=f"{self.duration_var.get()} ms", width=10)
        self.duration_label.pack(side='left', padx=10)
        duration_scale.config(command=lambda v: self.duration_label.config(
            text=f"{int(float(v))} ms"
        ))
        
        ttk.Label(parent, text="How long to wait for more keypresses before converting",
                  foreground='gray').pack(anchor='w')
        
        # Typing Delay
        ttk.Label(parent, text="Typing Delay:").pack(anchor='w', pady=(20, 0))
        self.delay_var = tk.IntVar(value=self.config.get('typing_delay_ms', 0))
        delay_frame = ttk.Frame(parent)
        delay_frame.pack(fill='x', pady=(5, 0))
        
        delay_scale = ttk.Scale(
            delay_frame, from_=0, to=100,
            variable=self.delay_var, orient='horizontal', length=280
        )
        delay_scale.pack(side='left')
        self.delay_label = ttk.Label(delay_frame, text=f"{self.delay_var.get()} ms", width=10)
        self.delay_label.pack(side='left', padx=10)
        delay_scale.config(command=lambda v: self.delay_label.config(
            text=f"{int(float(v))} ms"
        ))
        
        ttk.Label(parent, text="Delay between each character when typing (0 = instant)",
                  foreground='gray').pack(anchor='w')
        
        # Start enabled checkbox
        self.start_enabled_var = tk.BooleanVar(value=self.config.get('enabled_by_default', False))
        ttk.Checkbutton(
            parent, text="Start enabled by default",
            variable=self.start_enabled_var
        ).pack(anchor='w', pady=(25, 0))
        
        # Hotkey info (read-only for now)
        ttk.Label(parent, text="Toggle Hotkey:").pack(anchor='w', pady=(20, 0))
        hotkey_frame = ttk.Frame(parent)
        hotkey_frame.pack(fill='x', pady=(5, 0))
        ttk.Label(hotkey_frame, text="Ctrl + Shift + K", font=('Courier', 10)).pack(anchor='w')
    
    def _create_noises_tab(self, parent: ttk.Frame) -> None:
        """Create the Custom Noises tab.
        
        Args:
            parent: Parent frame
        """
        ttk.Label(parent, text="Add your own cat noises:").pack(anchor='w')
        ttk.Label(parent, text="These will be randomly used alongside the built-in noises",
                  foreground='gray').pack(anchor='w', pady=(0, 10))
        
        # Entry for new noise
        entry_frame = ttk.Frame(parent)
        entry_frame.pack(fill='x', pady=5)
        self.noise_entry = ttk.Entry(entry_frame, width=30)
        self.noise_entry.pack(side='left')
        ttk.Button(entry_frame, text="Add", command=self._add_noise).pack(side='left', padx=5)
        
        # Bind Enter key to add noise
        self.noise_entry.bind('<Return>', lambda e: self._add_noise())
        
        # Listbox of custom noises
        ttk.Label(parent, text="Current custom noises:").pack(anchor='w', pady=(15, 5))
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill='both', expand=True)
        
        self.noise_listbox = tk.Listbox(list_frame, height=10)
        self.noise_listbox.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.noise_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.noise_listbox.config(yscrollcommand=scrollbar.set)
        
        # Load existing custom noises
        for noise in self.config.get_custom_noises():
            self.noise_listbox.insert(tk.END, noise)
        
        # Remove button
        ttk.Button(parent, text="Remove Selected", command=self._remove_noise).pack(anchor='w', pady=10)
    
    def _create_about_tab(self, parent: ttk.Frame) -> None:
        """Create the About tab.
        
        Args:
            parent: Parent frame
        """
        ttk.Label(parent, text="🐱 Kitty Mode", font=('Helvetica', 18, 'bold')).pack(pady=20)
        ttk.Label(parent, text="Version 1.0").pack()
        ttk.Label(parent, text="").pack(pady=5)
        ttk.Label(parent, text="Transform your keyboard into a cat!").pack()
        ttk.Label(parent, text="").pack(pady=10)
        
        ttk.Label(parent, text="How it works:", font=('Helvetica', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        ttk.Label(parent, text="• Toggle with Ctrl+Shift+K or via system tray").pack(anchor='w')
        ttk.Label(parent, text="• When enabled, your keypresses are captured").pack(anchor='w')
        ttk.Label(parent, text="• AI finds similar-sounding cat noises").pack(anchor='w')
        ttk.Label(parent, text="• Your typing is replaced with meows!").pack(anchor='w')
        
        ttk.Label(parent, text="").pack(pady=10)
        config_path = str(self.config.get_config_path())
        ttk.Label(parent, text=f"Config: {config_path}", foreground='gray', 
                  wraplength=350).pack(anchor='w')
    
    def _add_noise(self) -> None:
        """Add a noise from the entry to the listbox."""
        noise = self.noise_entry.get().strip()
        if noise:
            # Check if already exists
            existing = list(self.noise_listbox.get(0, tk.END))
            if noise not in existing:
                self.noise_listbox.insert(tk.END, noise)
            self.noise_entry.delete(0, tk.END)
    
    def _remove_noise(self) -> None:
        """Remove the selected noise from the listbox."""
        selection = self.noise_listbox.curselection()
        if selection:
            self.noise_listbox.delete(selection[0])
    
    def _save(self) -> None:
        """Save settings and close window."""
        # Get custom noises from listbox
        custom_noises = list(self.noise_listbox.get(0, tk.END))
        
        self.config.update({
            'window_duration_ms': int(self.duration_var.get()),
            'typing_delay_ms': int(self.delay_var.get()),
            'enabled_by_default': self.start_enabled_var.get(),
            'custom_noises': custom_noises
        })
        
        if self.on_save:
            self.on_save(self.config.config)
        
        self._close()
    
    def _reset(self) -> None:
        """Reset settings to defaults after confirmation."""
        if messagebox.askyesno("Reset Settings", "Reset all settings to defaults?"):
            self.config.reset_to_defaults()
            messagebox.showinfo("Reset", "Settings have been reset. Please reopen the settings window.")
            self._close()
    
    def _close(self) -> None:
        """Close the settings window."""
        self._is_showing = False
        if self.window:
            self.window.destroy()
            self.window = None
    
    def show_in_thread(self) -> threading.Thread:
        """Show the settings window in a separate thread.
        
        Returns:
            The thread running the window
        """
        thread = threading.Thread(target=self.show, daemon=True)
        thread.start()
        return thread
