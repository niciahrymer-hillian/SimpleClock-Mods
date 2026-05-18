# [IMPORT] Standard library: tkinter for GUI framework
import tkinter as tk
# [IMPORT] tkinter.font: Not used in this version but available for Font objects
from tkinter import font
# [IMPORT] datetime: For timestamp and timezone handling
from datetime import datetime
# [IMPORT] pytz: External library for timezone conversions (pip install pytz)
import pytz
# [IMPORT] threading: For background time update loop (prevents UI freeze)
import threading
# [IMPORT] time: For sleep() to update display every second
import time

# [CLASS] SimpleClock - Main application controller
class SimpleClock:
    """
    Enhanced digital clock application with threading, UI improvements,
    and time format/timezone toggles.
    
    [WHY] threading: Replaces infinite loop; prevents UI freezing by running
    time updates on a background thread (solves Java swing blocking issue).
    
    [WHY] format/timezone toggles: Provides user control over time display
    without restarting the application (improves user experience).
    
    [ARCHITECTURE]
    - Main thread: Handles UI and button clicks (tkinter requirement)
    - Background thread: Updates time every 1 second via threading.Thread
    - State flags: Control format and timezone without modifying display logic
    """
    
    # [METHOD] __init__ - Constructor; sets up window and starts background thread
    def __init__(self, root):
        """
        [PARAMETER] root: tk.Tk() window object passed from main
        [EFFECT] Initializes UI components, state flags, and launches update thread
        """
        # [FIELD] root: Reference to main tkinter window
        self.root = root
        self.root.title("Digital Clock - Enhanced")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        # [FIELD] is_24_hour: Boolean state flag controlling time format
        # [PURPOSE] True=24-hour (14:30:45), False=12-hour (02:30:45 PM)
        self.is_24_hour = False
        
        # [FIELD] is_gmt: Boolean state flag controlling timezone
        # [PURPOSE] True=GMT/UTC, False=local system time
        self.is_gmt = False
        
        # [FIELD] running: Control flag for graceful thread shutdown
        # [PURPOSE] When False, update_time_loop exits; prevents orphan threads
        self.running = True
        
        # ===== [UI_SETUP] Main container frame with padding =====
        # [WHY] Create padded frame: Original Java code had no margins (FlowLayout)
        # [ENHANCEMENT] tk.Frame with padx/pady solves "Make the UI look better"
        self.main_frame = tk.Frame(root, bg="#1a1a1a", padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== [UI_LABELS] Three display elements for time, day, date =====
        # [LABEL] Time display (HH:MM:SS or HH:MM:SS AM/PM)
        # [STYLING] Large 72pt bold font, green text on dark background (terminal-like look)
        self.time_label = tk.Label(
            self.main_frame,
            font=("Arial", 72, "bold"),  # [FONT] Large, bold for readability
            bg="#1a1a1a",                 # [COLOR] Dark background (#1a1a1a = almost black)
            fg="#12d99d"                  # [COLOR] Teal-green text (digital clock aesthetic)
        )
        self.time_label.pack(pady=(20, 10))  # [PADDING] Top=20, bottom=10 (emphasize time)
        
        # [LABEL] Day display (Monday, Tuesday, etc.)
        # [STYLING] 28pt bold white; secondary display
        self.day_label = tk.Label(
            self.main_frame,
            font=("Arial", 28, "bold"),
            bg="#1a1a1a",
            fg="#ffffff"                 # [COLOR] White text for high contrast
        )
        self.day_label.pack(pady=5)
        
        # [LABEL] Date display (18 May, 2026)
        # [STYLING] 20pt regular font; tertiary information
        self.date_label = tk.Label(
            self.main_frame,
            font=("Arial", 20),
            bg="#1a1a1a",
            fg="#cccccc"                 # [COLOR] Light gray (less emphasis than day)
        )
        self.date_label.pack(pady=5)
        
        # [LABEL] Timezone and format info
        # [PURPOSE] Shows user current state: "GMT | 24-Hour Format"
        self.info_label = tk.Label(
            self.main_frame,
            font=("Arial", 12),
            bg="#1a1a1a",
            fg="#999999"                 # [COLOR] Darker gray (metadata, not primary)
        )
        self.info_label.pack(pady=10)
        
        # ===== [BUTTON_CONTAINER] Frame for control buttons with padding =====
        # [ENHANCEMENT] Separate frame for buttons improves layout organization
        button_frame = tk.Frame(self.main_frame, bg="#1a1a1a", padx=10, pady=10)
        button_frame.pack(fill=tk.X, pady=20)
        
        # ===== [BUTTON_1] Format toggle (12/24 hour) =====
        # [FEATURE] "Add a button which switches between 12/24 hr format"
        # [CALLBACK] Calls self.toggle_format() when clicked
        # [STATE_MANAGEMENT] Updates is_24_hour flag; next refresh shows new format
        self.format_btn = tk.Button(
            button_frame,
            text="Switch to 24-Hour",      # [TEXT] Initial text (12-hour is default)
            command=self.toggle_format,    # [CALLBACK] Function to execute on click
            font=("Arial", 11),
            bg="#333333",                  # [COLOR] Dark gray button
            fg="#00ff00",                  # [COLOR] Green text (matches time label)
            padx=15,                       # [PADDING] Horizontal: makes button wider
            pady=8,                        # [PADDING] Vertical: makes button taller
            relief=tk.RAISED               # [STYLE] 3D raised button effect
        )
        self.format_btn.pack(side=tk.LEFT, padx=10)  # [LAYOUT] Left side, space between
        
        # ===== [BUTTON_2] Timezone toggle (Local/GMT) =====
        # [FEATURE] "Add a button which switches between local time and GMT"
        # [CALLBACK] Calls self.toggle_timezone() when clicked
        # [STATE_MANAGEMENT] Updates is_gmt flag; next refresh shows new timezone
        self.tz_btn = tk.Button(
            button_frame,
            text="Switch to GMT",          # [TEXT] Initial text (local time is default)
            command=self.toggle_timezone,  # [CALLBACK] Function to execute on click
            font=("Arial", 11),
            bg="#333333",
            fg="#00ff00",
            padx=15,
            pady=8,
            relief=tk.RAISED
        )
        self.tz_btn.pack(side=tk.LEFT, padx=10)
        
        # ===== [THREADING] Background thread for time updates =====
        # [FEATURE] "Modify this to use a Thread rather than an infinite loop"
        # [WHY] Original Java had while(true) infinite loop in setTimer()
        # [EFFECT] Moves time updates off main thread; UI remains responsive
        # [DAEMON] daemon=True: Thread auto-terminates when main window closes
        self.update_thread = threading.Thread(
            target=self.update_time_loop,  # [TARGET] Function to run in background
            daemon=True                    # [DAEMON] Die with main thread
        )
        self.update_thread.start()  # [START] Launch thread immediately
        
        # ===== [WINDOW_PROTOCOL] Handle window close event =====
        # [PURPOSE] Graceful shutdown: Set running=False before window closes
        # [EFFECT] update_time_loop checks running flag and exits cleanly
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    # [METHOD] toggle_format - Button callback; switches between 12/24 hour
    def toggle_format(self):
        """
        [FEATURE] "Add a button which switches between 12/24 hr format"
        [WHY] User clicks button → toggle_format() flips is_24_hour flag
        [EFFECT] Next time update_time_loop runs, it sees new format and applies it
        [LOGIC] No immediate display update needed; happens on next 1-second refresh
        """
        # [STATE_UPDATE] Flip the boolean flag (True ↔ False)
        self.is_24_hour = not self.is_24_hour
        
        # [UI_UPDATE] Change button text to show next action
        btn_text = "Switch to 12-Hour" if self.is_24_hour else "Switch to 24-Hour"
        self.format_btn.config(text=btn_text)
    
    # [METHOD] toggle_timezone - Button callback; switches between local/GMT
    def toggle_timezone(self):
        """
        [FEATURE] "Add a button which switches between local time and GMT"
        [WHY] User clicks button → toggle_timezone() flips is_gmt flag
        [EFFECT] Next time update_time_loop runs, it fetches time in new timezone
        [LOGIC] Uses pytz.UTC for GMT; datetime.now() for local
        """
        # [STATE_UPDATE] Flip the boolean flag (True ↔ False)
        self.is_gmt = not self.is_gmt
        
        # [UI_UPDATE] Change button text to show next action
        btn_text = "Switch to Local" if self.is_gmt else "Switch to GMT"
        self.tz_btn.config(text=btn_text)
    
    # [METHOD] get_current_time - Encapsulates timezone logic
    def get_current_time(self):
        """
        [PURPOSE] Centralizes time retrieval; single point for timezone switching
        [RETURN] datetime object (either GMT or local) based on is_gmt flag
        [WHY] Separation of concerns: timezone decision in one place
        [USAGE] Called from update_time_loop every second
        """
        if self.is_gmt:
            # [BRANCH] User selected GMT: return UTC time using pytz
            return datetime.now(pytz.UTC)
        else:
            # [BRANCH] User selected Local: return system local time
            return datetime.now()
    
    # [METHOD] update_time_loop - Main loop; runs on background thread
    def update_time_loop(self):
        """
        [FEATURE] "Modify this to use a Thread rather than an infinite loop"
        [WHY] Original Java had: while(true) { Thread.sleep(1000); update_display(); }
              This approach blocks the UI thread, freezing the GUI.
              Solution: Run entire loop on separate daemon thread.
        
        [EFFECT] Time updates every 1 second without freezing UI
        [THREAD_SAFETY] Uses self.root.after() to marshal updates back to main thread
        [LOOP_CONTROL] Checks self.running flag; exits cleanly on window close
        
        [ARCHITECTURE]
        1. While self.running is True:
           - Get current time (respects is_24_hour and is_gmt flags)
           - Format strings (time_str, day_str, date_str, info_str)
           - Marshall to main thread via self.root.after()
           - Sleep 1 second
        2. When self.running becomes False (on_closing sets it):
           - Loop exits, thread terminates cleanly
        """
        # [LOOP] Infinite loop (but controlled by self.running flag)
        while self.running:
            try:
                # [FETCH_TIME] Get current time in appropriate timezone
                current_time = self.get_current_time()
                
                # [FORMAT_TIME] Build time string based on format flag
                # [LOGIC] "%H:%M:%S" = 24-hour, "%I:%M:%S %p" = 12-hour with AM/PM
                time_format = "%H:%M:%S" if self.is_24_hour else "%I:%M:%S %p"
                time_str = current_time.strftime(time_format)
                
                # [FORMAT_DAY] Extract day of week (Monday, Tuesday, etc.)
                day_str = current_time.strftime("%A")
                
                # [FORMAT_DATE] Extract full date (18 May, 2026)
                date_str = current_time.strftime("%d %B, %Y")
                
                # [FORMAT_INFO] Build info label showing current state
                # [PURPOSE] Displays timezone and format to user
                tz_info = "GMT" if self.is_gmt else "Local Time"
                hour_info = "24-Hour" if self.is_24_hour else "12-Hour"
                info_str = f"{tz_info} | {hour_info} Format"
                
                # [THREAD_SAFETY] Use self.root.after() to update UI from main thread
                # [WHY] tkinter requires all UI updates on main thread
                # [AFTER] Schedules _update_display() to run ASAP on main thread
                self.root.after(0, self._update_display, time_str, day_str, date_str, info_str)
                
                # [SLEEP] Wait 1 second before next update
                # [EFFECT] Clock updates every second, not every millisecond
                time.sleep(1)
            
            except Exception as e:
                # [ERROR_HANDLING] Print errors but don't crash thread
                print(f"Error in time update: {e}")
    
    # [METHOD] _update_display - Thread-safe UI update wrapper
    def _update_display(self, time_str, day_str, date_str, info_str):
        """
        [PURPOSE] Bridge method: Receives pre-formatted strings and updates labels
        [PARAMETER] time_str: Formatted time (e.g., "14:30:45" or "02:30:45 PM")
        [PARAMETER] day_str: Day name (e.g., "Monday")
        [PARAMETER] date_str: Full date (e.g., "18 May, 2026")
        [PARAMETER] info_str: Status info (e.g., "GMT | 24-Hour Format")
        
        [WHY] Separate method: Called via self.root.after() for thread safety
        [EFFECT] Updates all four labels in sync with minimal UI work
        [THREAD_SAFETY] This method runs on main thread (guaranteed by after())
        """
        # [UPDATE] Set time label text
        self.time_label.config(text=time_str)
        
        # [UPDATE] Set day label text
        self.day_label.config(text=day_str)
        
        # [UPDATE] Set date label text
        self.date_label.config(text=date_str)
        
        # [UPDATE] Set info label text
        self.info_label.config(text=info_str)
    
    # [METHOD] on_closing - Window close handler; graceful shutdown
    def on_closing(self):
        """
        [PURPOSE] Cleanly shutdown background thread before window closes
        [WHY] If we don't wait for thread, Python may hang or raise warnings
        [EFFECT] Sets self.running = False, allowing update_time_loop to exit
        [SEQUENCE] 1. Set running=False → 2. update_time_loop exits → 3. destroy window
        """
        # [STATE_UPDATE] Signal background thread to stop
        self.running = False
        
        # [WINDOW] Close the tkinter window (triggers GUI shutdown)
        self.root.destroy()


# [MAIN] Entry point
if __name__ == "__main__":
    # [CREATE] Instantiate tkinter root window
    root = tk.Tk()
    
    # [INSTANTIATE] Create SimpleClock app (passes root window)
    app = SimpleClock(root)
    
    # [MAINLOOP] Start tkinter event loop (blocks until window closes)
    root.mainloop()
