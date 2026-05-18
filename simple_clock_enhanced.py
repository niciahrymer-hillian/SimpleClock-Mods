import tkinter as tk
from tkinter import font
from datetime import datetime
import pytz
import threading
import time

class SimpleClock:
    """
    Enhanced digital clock application with threading, UI improvements,
    and time format/timezone toggles.
    
    Why threading: Replaces infinite loop; prevents UI freezing by running
    time updates on a background thread.
    
    Why format/timezone toggles: Provides user control over time display
    without restarting the application.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Clock - Enhanced")
        self.root.geometry("500x520")
        self.root.resizable(False, False)
        
        # Time format state: True = 24-hour, False = 12-hour
        self.is_24_hour = False
        # Timezone state: True = GMT, False = Local
        self.is_gmt = False
        # Control flag for graceful thread shutdown
        self.running = True
        
        # Create main container with padding
        self.main_frame = tk.Frame(root, bg="#1a1a1a", padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Time display labels with improved styling
        self.time_label = tk.Label(
            self.main_frame,
            font=("Arial", 60, "bold"),
            bg="#1a1a1a",
            fg="#12d99d"
        )
        self.time_label.pack(pady=(10, 5))
        
        self.day_label = tk.Label(
            self.main_frame,
            font=("Arial", 28, "bold"),
            bg="#1a1a1a",
            fg="#ffffff"
        )
        self.day_label.pack(pady=2)
        
        self.date_label = tk.Label(
            self.main_frame,
            font=("Arial", 20),
            bg="#1a1a1a",
            fg="#cccccc"
        )
        self.date_label.pack(pady=2)
        
        # Zone/format display
        self.info_label = tk.Label(
            self.main_frame,
            font=("Arial", 12),
            bg="#1a1a1a",
            fg="#999999"
        )
        self.info_label.pack(pady=5)
        
        # Button container with padding
        button_frame = tk.Frame(self.main_frame, bg="#1a1a1a", padx=10, pady=5)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Format toggle button
        self.format_btn = tk.Button(
            button_frame,
            text="Switch to 24-Hour",
            command=self.toggle_format,
            font=("Arial", 11),
            bg="#333333",
            fg="#12d99d",
            padx=15,
            pady=8,
            relief=tk.RAISED
        )
        self.format_btn.pack(side=tk.LEFT, padx=10)
        
        # Timezone toggle button
        self.tz_btn = tk.Button(
            button_frame,
            text="Switch to GMT",
            command=self.toggle_timezone,
            font=("Arial", 11),
            bg="#333333",
            fg="#12d99d",
            padx=15,
            pady=8,
            relief=tk.RAISED
        )
        self.tz_btn.pack(side=tk.LEFT, padx=10)
        
        # Start background thread for time updates
        self.update_thread = threading.Thread(target=self.update_time_loop, daemon=True)
        self.update_thread.start()
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def toggle_format(self):
        """
        Why: Switches between 12-hour (12:30:45 PM) and 24-hour (14:30:45) formats.
        Effect: Updates button text and time_label on next refresh.
        """
        self.is_24_hour = not self.is_24_hour
        btn_text = "Switch to 12-Hour" if self.is_24_hour else "Switch to 24-Hour"
        self.format_btn.config(text=btn_text)
    
    def toggle_timezone(self):
        """
        Why: Switches between local system time and GMT/UTC timezone.
        Effect: Updates date_label and time_label on next refresh.
        """
        self.is_gmt = not self.is_gmt
        btn_text = "Switch to Local" if self.is_gmt else "Switch to GMT"
        self.tz_btn.config(text=btn_text)
    
    def get_current_time(self):
        """
        Why: Centralizes time retrieval logic; enables easy timezone switching.
        Returns: datetime object in either GMT or local timezone.
        """
        if self.is_gmt:
            return datetime.now(pytz.UTC)
        else:
            return datetime.now()
    
    def update_time_loop(self):
        """
        Why: Runs on background thread to prevent UI freezing.
        Effect: Updates display every 1 second without blocking main thread.
        Note: This replaces the infinite loop pattern used in original Java code.
        """
        while self.running:
            try:
                current_time = self.get_current_time()
                
                # Format time based on user selection
                time_format = "%H:%M:%S" if self.is_24_hour else "%I:%M:%S %p"
                time_str = current_time.strftime(time_format)
                
                day_str = current_time.strftime("%A")
                date_str = current_time.strftime("%d %B, %Y")
                
                # Display timezone info
                tz_info = "GMT" if self.is_gmt else "Local Time"
                hour_info = "24-Hour" if self.is_24_hour else "12-Hour"
                info_str = f"{tz_info} | {hour_info} Format"
                
                # Update UI safely from main thread
                self.root.after(0, self._update_display, time_str, day_str, date_str, info_str)
                
                time.sleep(1)
            except Exception as e:
                print(f"Error in time update: {e}")
    
    def _update_display(self, time_str, day_str, date_str, info_str):
        """
        Why: Bridges thread-safe UI updates (must run on main thread in tkinter).
        Parameters: Pre-formatted time strings from update_time_loop.
        """
        self.time_label.config(text=time_str)
        self.day_label.config(text=day_str)
        self.date_label.config(text=date_str)
        self.info_label.config(text=info_str)
    
    def on_closing(self):
        """
        Why: Gracefully shutdown background thread before window closes.
        Effect: Sets running flag to False, allowing update_time_loop to exit.
        """
        self.running = False
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleClock(root)
    root.mainloop()
