import matplotlib
# Try different backends in order of preference
try:
    matplotlib.use('TkAgg')  # Most reliable for Windows
except ImportError:
    try:
        matplotlib.use('Qt5Agg')  # Alternative GUI backend
    except ImportError:
        matplotlib.use('Agg')  # Fallback (no display)
        print("Warning: No GUI backend available, plots will not display")

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Circle
import numpy as np
from collections import deque
import threading
import time
from queue import Queue

class ECGDashboard:
    def __init__(self, window_size=1250, sampling_rate=125):
        """
        ECG Real-time Dashboard
        
        Args:
            window_size (int): Number of samples to display in the scrolling window
            sampling_rate (int): Sampling rate in Hz (for time axis)
        """
        print(f"ECG Dashboard initializing with matplotlib backend: {matplotlib.get_backend()}")
        self.window_size = window_size
        self.sampling_rate = sampling_rate
        self.time_window = window_size / sampling_rate  # seconds
        
        # Data storage
        self.ecg_data = deque(maxlen=window_size)  # Scrolling window for real-time display
        self.time_data = deque(maxlen=window_size)  # Scrolling window for real-time display
        
        # Permanent historical data storage (no length limit)
        self.all_ecg_data = []      # All ECG samples for historical navigation
        self.all_time_data = []     # All time points for historical navigation
        self.sample_count = 0
        
        # Segment tracking for highlighting
        self.segments = {
            'r_peaks': [],          # List of R-peak indices
            'detection_windows': [], # List of (start, end) tuples for detection windows
            'model_segments': [],   # List of (start, end, class, probability) tuples
        }
        
        # Colors for different highlights
        self.colors = {
            'r_peaks': 'red',
            'detection_windows': 'lightcoral',
            'model_segments': 'lightblue',
            'ecg_line': 'blue'
        }
        
        # Thread-safe data queue
        self.data_queue = Queue()
        self.segment_queue = Queue()
        
        # Setup the plot
        self.setup_plot()
        
        # Animation object (will be set when starting)
        self.animation = None
        
    def setup_plot(self):
        """Initialize the matplotlib figure and axis"""
        self.fig, self.ax = plt.subplots(figsize=(15, 8))
        self.fig.suptitle('Real-time ECG Dashboard - Use mouse to pan/zoom, keys for navigation', fontsize=14, fontweight='bold')
        
        # Initialize empty line for ECG data
        self.ecg_line, = self.ax.plot([], [], color=self.colors['ecg_line'], linewidth=1.2, label='ECG Signal')
        
        # Setup axis properties
        self.ax.set_xlim(0, self.time_window)
        self.ax.set_ylim(-0.1, 1.1)  # Adjust based on your ECG data range
        self.ax.set_xlabel('Time (seconds)', fontsize=20)
        self.ax.set_ylabel('Normalized ECG Amplitude', fontsize=20)
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='upper right')
        
        # Enable interactive navigation
        self.setup_navigation()
        
        # Text area for displaying information
        self.info_text = self.ax.text(0.02, 0.98, '', transform=self.ax.transAxes, 
                                    verticalalignment='top', fontsize=10,
                                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Navigation help text
        # self.help_text = self.ax.text(0.02, 0.02, 
        #                             '🖱️ Mouse: Pan & Zoom | ⌨️ Keys: ←→ scroll, ↑↓ zoom, R reset, Space follow\n'
        #                             '🎨 Highlights: Top=Predictions | Middle=Model Inputs (4 rows) | Bottom=Detection Windows (4 rows)', 
        #                             transform=self.ax.transAxes, fontsize=7,
        #                             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        # Storage for highlight patches
        self.highlight_patches = []
        
        # Navigation state
        self.follow_mode = True  # True = auto-follow latest data, False = manual navigation
        self.manual_xlim = None  # Store manual x-limits when not following

    def setup_navigation(self):
        """Setup interactive navigation capabilities"""
        # Enable built-in matplotlib navigation toolbar (pan/zoom)
        self.fig.canvas.toolbar_visible = True
        
        # Connect keyboard events for custom navigation
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        
        # Connect mouse events to detect manual interaction
        self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
    
    def on_key_press(self, event):
        """Handle keyboard navigation"""
        if event.key is None:
            return
            
        current_xlim = self.ax.get_xlim()
        window_size = current_xlim[1] - current_xlim[0]
        
        if event.key == 'left':
            # Scroll left
            self.follow_mode = False
            new_xlim = (current_xlim[0] - window_size * 0.1, current_xlim[1] - window_size * 0.1)
            self.ax.set_xlim(new_xlim)
            self.manual_xlim = new_xlim
            self.fig.canvas.draw()
            
        elif event.key == 'right':
            # Scroll right
            self.follow_mode = False
            new_xlim = (current_xlim[0] + window_size * 0.1, current_xlim[1] + window_size * 0.1)
            self.ax.set_xlim(new_xlim)
            self.manual_xlim = new_xlim
            self.fig.canvas.draw()
            
        elif event.key == 'up':
            # Zoom in (decrease window size)
            center = (current_xlim[0] + current_xlim[1]) / 2
            new_window_size = window_size * 0.8
            new_xlim = (center - new_window_size/2, center + new_window_size/2)
            self.ax.set_xlim(new_xlim)
            if not self.follow_mode:
                self.manual_xlim = new_xlim
            self.fig.canvas.draw()
            
        elif event.key == 'down':
            # Zoom out (increase window size)
            center = (current_xlim[0] + current_xlim[1]) / 2
            new_window_size = window_size * 1.25
            new_xlim = (center - new_window_size/2, center + new_window_size/2)
            self.ax.set_xlim(new_xlim)
            if not self.follow_mode:
                self.manual_xlim = new_xlim
            self.fig.canvas.draw()
            
        elif event.key == 'r':
            # Reset to auto-follow mode
            self.follow_mode = True
            self.manual_xlim = None
            # Will be updated in next animation frame
            
        elif event.key == ' ':  # Spacebar
            # Toggle follow mode
            if self.follow_mode:
                self.follow_mode = False
                self.manual_xlim = self.ax.get_xlim()
            else:
                self.follow_mode = True
                self.manual_xlim = None
    
    def on_mouse_press(self, event):
        """Handle mouse interaction - disable follow mode when manually panning/zooming"""
        if event.inaxes == self.ax and event.button in [1, 3]:  # Left or right click
            self.follow_mode = False
            # Store current limits as manual limits
            self.manual_xlim = self.ax.get_xlim()
        
    def add_data_point(self, value):
        """
        Thread-safe method to add a new ECG data point
        
        Args:
            value (float): ECG amplitude value
        """
        self.data_queue.put(('data', value))
        
    def add_r_peak(self, sample_index):
        """
        Add an R-peak marker
        
        Args:
            sample_index (int): Sample index where R-peak was detected
        """
        self.segment_queue.put(('r_peak', sample_index))
        
    def add_detection_window(self, start_index, end_index):
        """
        Add a detection window highlight
        
        Args:
            start_index (int): Start sample index
            end_index (int): End sample index
        """
        self.segment_queue.put(('detection_window', start_index, end_index))
        
    def add_model_segment(self, start_index, end_index, predicted_class, probability):
        """
        Add a model segment with prediction
        
        Args:
            start_index (int): Start sample index
            end_index (int): End sample index
            predicted_class (str): Predicted class name
            probability (float): Prediction probability
        """
        self.segment_queue.put(('model_segment', start_index, end_index, predicted_class, probability))
        
    def process_pending_segments(self, segment_type=None):
        """
        Force immediate processing of any pending segments in the queue.
        Useful when you need segments to be available immediately for subsequent operations.
        
        Args:
            segment_type (str, optional): If specified, only process segments of this type.
                                        Valid values: 'r_peak', 'detection_window', 'model_segment'
                                        If None, processes all segment types.
        """
        processed_segments = []
        temp_queue = []
        
        # Extract all items from queue
        while not self.segment_queue.empty():
            try:
                segment_data = self.segment_queue.get_nowait()
                
                # Check if we should process this segment type
                should_process = (segment_type is None) or (segment_data[0] == segment_type)
                
                if should_process:
                    # Process the segment
                    if segment_data[0] == 'r_peak':
                        self.segments['r_peaks'].append(segment_data[1])
                        processed_segments.append(segment_data[0])
                    elif segment_data[0] == 'detection_window':
                        self.segments['detection_windows'].append((segment_data[1], segment_data[2]))
                        processed_segments.append(segment_data[0])
                    elif segment_data[0] == 'model_segment':
                        self.segments['model_segments'].append((segment_data[1], segment_data[2], segment_data[3], segment_data[4]))
                        processed_segments.append(segment_data[0])
                else:
                    # Keep for later processing
                    temp_queue.append(segment_data)
            except:
                break
        
        # Put back unprocessed segments
        for segment_data in temp_queue:
            self.segment_queue.put(segment_data)
            
        return processed_segments
        
    def update_plot(self, frame):
        """Animation update function"""
        try:
            # Check if figure is still valid
            if not plt.fignum_exists(self.fig.number):
                return []
                
            # Process new data points
            while not self.data_queue.empty():
                try:
                    msg_type, value = self.data_queue.get_nowait()
                    if msg_type == 'data':
                        current_time = self.sample_count / self.sampling_rate
                        
                        # Add to scrolling window (for real-time display)
                        self.ecg_data.append(value)
                        self.time_data.append(current_time)
                        
                        # Add to permanent storage (for historical navigation)
                        self.all_ecg_data.append(value)
                        self.all_time_data.append(current_time)
                        
                        self.sample_count += 1
                except:
                    break
        except Exception as e:
            # Silently handle any animation errors
            return []
                
        # Process new segments
        while not self.segment_queue.empty():
            try:
                segment_data = self.segment_queue.get_nowait()
                if segment_data[0] == 'r_peak':
                    #print(f"DEBUG: Processing R-peak at index {segment_data[1]}")
                    self.segments['r_peaks'].append(segment_data[1])
                elif segment_data[0] == 'detection_window':
                    print(f"DEBUG: Processing detection window from {segment_data[1]} to {segment_data[2]}")
                    self.segments['detection_windows'].append((segment_data[1], segment_data[2]))
                elif segment_data[0] == 'model_segment':
                    print(f"DEBUG: Processing model segment from {segment_data[1]} to {segment_data[2]} with class {segment_data[3]} and probability {segment_data[4]}")
                    self.segments['model_segments'].append((segment_data[1], segment_data[2], segment_data[3], segment_data[4]))
            except:
                break
        
        # Update ECG line and axis limits
        self.update_ecg_display()
        
        # Clear old highlights
        for patch in self.highlight_patches:
            patch.remove()
        self.highlight_patches.clear()
        
        # Add current highlights
        self.draw_highlights()
        
        return [self.ecg_line] + self.highlight_patches
    
    def update_ecg_display(self):
        """Update ECG line display based on current navigation mode and visible window"""
        if len(self.all_ecg_data) == 0:
            return
            
        # Determine the time window to display
        if self.follow_mode and len(self.time_data) > 0:
            # Auto-follow mode: show most recent data
            latest_time = self.time_data[-1]
            if latest_time > self.time_window:
                view_start = latest_time - self.time_window
                view_end = latest_time
                self.ax.set_xlim(view_start, view_end)
            else:
                view_start = 0
                view_end = self.time_window
                self.ax.set_xlim(0, self.time_window)
        else:
            # Manual navigation mode: use current axis limits
            current_xlim = self.ax.get_xlim()
            if self.manual_xlim is not None:
                view_start, view_end = self.manual_xlim
                self.ax.set_xlim(self.manual_xlim)
            else:
                view_start, view_end = current_xlim
        
        # Filter data for the current view window
        visible_times = []
        visible_ecg = []
        
        for i, time_point in enumerate(self.all_time_data):
            if view_start <= time_point <= view_end:
                visible_times.append(time_point)
                visible_ecg.append(self.all_ecg_data[i])
        
        # Update the ECG line with visible data
        self.ecg_line.set_data(visible_times, visible_ecg)
        
        # Clear old highlights
        for patch in self.highlight_patches:
            patch.remove()
        self.highlight_patches.clear()
        
        # Add current highlights
        self.draw_highlights()
        
        # Update info text
        #self.update_info_display() #Uncomment if needed for debugging
        
        return [self.ecg_line] + self.highlight_patches
        
    def draw_highlights(self):
        """Draw all segment highlights"""
        if len(self.all_time_data) == 0:
            return
            
        # Get current visible time window from axis limits
        current_xlim = self.ax.get_xlim()
        window_start_time = current_xlim[0]
        window_end_time = current_xlim[1]
            
        # Draw detection windows (bottom area) - distributed across 4 sub-rows starting from top
        detection_count = 0
        for start_idx, end_idx in self.segments['detection_windows']:
            start_time = start_idx / self.sampling_rate
            end_time = end_idx / self.sampling_rate
            
            # Only draw if within current window
            if end_time >= window_start_time and start_time <= window_end_time:
                width = end_time - start_time
                
                # Distribute across 4 sub-rows in bottom area (y=-0.1 to y=0.0)
                # Sub-row 0: y=-0.025 to y=0.0 (height=0.025) - TOP
                # Sub-row 1: y=-0.05 to y=-0.025 (height=0.025)
                # Sub-row 2: y=-0.075 to y=-0.05 (height=0.025)
                # Sub-row 3: y=-0.1 to y=-0.075 (height=0.025) - BOTTOM
                row = detection_count % 4
                sub_row_height = 0.1 / 4  # 0.025
                y_pos = -0.025 - (row * sub_row_height)  # Start from top, go down
                
                rect = Rectangle((start_time, y_pos), width, sub_row_height, 
                               facecolor=self.colors['detection_windows'], 
                               alpha=0.6, label='Detection Window')
                self.ax.add_patch(rect)
                self.highlight_patches.append(rect)
                detection_count += 1
        
        # Draw model segments with layered positioning
        model_input_count = 0
        for start_idx, end_idx, pred_class, probability in self.segments['model_segments']:
            start_time = start_idx / self.sampling_rate
            end_time = end_idx / self.sampling_rate
            
            # Only draw if within current window
            if end_time >= window_start_time and start_time <= window_end_time:
                width = end_time - start_time
                
                if pred_class == 'Model Input':
                    # Model Input Windows: middle area (y=0.0 to y=0.1) - distributed across 4 sub-rows starting from top
                    # Sub-row 0: y=0.075 to y=0.1 (height=0.025) - TOP
                    # Sub-row 1: y=0.05 to y=0.075 (height=0.025)
                    # Sub-row 2: y=0.025 to y=0.05 (height=0.025)
                    # Sub-row 3: y=0.0 to y=0.025 (height=0.025) - BOTTOM
                    color = 'lightblue'
                    row = model_input_count % 4
                    sub_row_height = 0.1 / 4  # 0.025
                    y_pos = 0.075 - (row * sub_row_height)  # Start from top, go down
                    height = sub_row_height
                    text_y = y_pos + (sub_row_height / 2)  # Center text in sub-row
                    alpha = 0.6
                    model_input_count += 1
                elif pred_class in ['Normal', 'PVC']:
                    # Model Predictions: top 90% area (y=0.1 to y=1.1)
                    color = 'lightgreen' if pred_class == 'Normal' else 'lightcoral'
                    y_pos = 0.1
                    height = 1.0
                    text_y = 0.95
                    alpha = 0.4
                else:
                    # Other predictions: also use top area but with different color
                    color = 'lightyellow'
                    y_pos = 0.1
                    height = 1.0
                    text_y = 1.0
                    alpha = 0.4
                
                rect = Rectangle((start_time, y_pos), width, height, 
                               facecolor=color, alpha=alpha, 
                               label=f'{pred_class} ({probability:.2f})')
                self.ax.add_patch(rect)
                self.highlight_patches.append(rect)
                
                # Add text annotation
                mid_time = (start_time + end_time) / 2
                if pred_class == 'Model Input':
                    # Smaller text for model input windows
                    text = self.ax.text(mid_time, text_y, 'Input', 
                                      ha='center', va='center', fontsize=6, 
                                      bbox=dict(boxstyle='round,pad=0.1', facecolor='white', alpha=0.9))
                else:
                    # Regular text for predictions
                    text = self.ax.text(mid_time, text_y, f'{pred_class}\n{probability:.2f}', 
                                      ha='center', va='center', fontsize=16, 
                                      bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
                self.highlight_patches.append(text)
        
        # Draw R-peaks
        for r_peak_idx in self.segments['r_peaks']:
            peak_time = r_peak_idx / self.sampling_rate
            
            # Only draw if within current window
            if window_start_time <= peak_time <= window_end_time:
                # Find corresponding ECG value if available
                if len(self.all_time_data) > 0:
                    time_array = np.array(self.all_time_data)
                    closest_idx = np.argmin(np.abs(time_array - peak_time))
                    if closest_idx < len(self.all_ecg_data):
                        peak_value = self.all_ecg_data[closest_idx]
                        
                        # Draw R-peak marker using Circle patch
                        circle = Circle((peak_time, peak_value), radius=0.02, 
                                      facecolor='red', edgecolor='darkred', linewidth=2,
                                      zorder=15, alpha=1.0, label='R-peak')
                        self.ax.add_patch(circle)
                        self.highlight_patches.append(circle)
    
    def update_info_display(self):
        """Update the information display"""
        
        info_lines = []
        info_lines.append(f"Samples: {self.sample_count}")
        info_lines.append(f"R-peaks detected: {len(self.segments['r_peaks'])}")
        info_lines.append(f"Detection windows: {len(self.segments['detection_windows'])}")
        info_lines.append(f"Model predictions: {len(self.segments['model_segments'])}")
        
        # Show navigation mode
        mode_text = "🔄 FOLLOWING" if self.follow_mode else "🎯 MANUAL"
        info_lines.append(f"Mode: {mode_text}")
        
        # Show latest prediction if available
        if self.segments['model_segments']:
            latest_segment = self.segments['model_segments'][-1]
            info_lines.append(f"Latest: {latest_segment[2]} ({latest_segment[3]:.3f})")
        
        self.info_text.set_text('\n'.join(info_lines))
    
    def start_dashboard(self, interval=50):
        """
        Start the real-time dashboard
        
        Args:
            interval (int): Update interval in milliseconds
        """
        print("Setting up dashboard animation...")
        
        # Ensure the plot window is configured properly
        plt.ion()  # Turn on interactive mode
        
        # Create and store the animation object with safer settings
        self.animation = animation.FuncAnimation(
            self.fig, self.update_plot, interval=interval, 
            blit=False, cache_frame_data=False, repeat=True,
            save_count=None  # Disable frame caching to avoid memory issues
        )
        
        print("Dashboard animation created, showing plot...")
        
        # Show the plot window
        plt.show(block=False)  # Don't block initially
        plt.pause(0.1)  # Give time for window to appear
        
        # Keep the dashboard running
        try:
            # This keeps the dashboard alive and responsive
            while plt.get_fignums():  # Continue while figure windows are open
                plt.pause(0.1)  # Process events and updates
        except KeyboardInterrupt:
            print("Dashboard received Ctrl+C - but staying open!")
            print("Dashboard will continue running")
            print("Close the plot window manually to exit")
            # Continue running despite Ctrl+C - this is the persistent behavior we want
            try:
                while plt.get_fignums():  # Keep checking if window is open
                    plt.pause(0.1)
            except KeyboardInterrupt:
                # Even if user presses Ctrl+C again, stay open
                print("Ctrl+C pressed again - dashboard still staying open!")
                try:
                    while plt.get_fignums():
                        plt.pause(0.1)
                except:
                    pass
            except:
                pass
        finally:
            self.stop_dashboard()
        
    def stop_dashboard(self):
        """Stop the dashboard"""
        print("Stopping dashboard...")
        try:
            if self.animation and hasattr(self.animation, 'event_source'):
                self.animation.event_source.stop()
            self.animation = None
        except Exception as e:
            print(f"Warning: Error stopping animation: {e}")
            
        try:
            if hasattr(self, 'fig') and self.fig:
                plt.close(self.fig)
        except Exception as e:
            print(f"Warning: Error closing figure: {e}")
            
        try:
            plt.ioff()  # Turn off interactive mode
        except Exception as e:
            print(f"Warning: Error turning off interactive mode: {e}")
    
    def is_window_open(self):
        """Check if the dashboard window is still open"""
        return hasattr(self, 'fig') and plt.fignum_exists(self.fig.number)
    
    def test_dashboard(self):
        """Test method to verify dashboard functionality"""
        print("Testing dashboard with sample data...")
        import math
        
        # Generate some test ECG-like data
        for i in range(100):
            # Simple sine wave with some noise
            t = i / self.sampling_rate
            value = 0.5 + 0.3 * math.sin(2 * math.pi * 1.2 * t) + 0.1 * math.sin(2 * math.pi * 15 * t)
            self.add_data_point(value)  # Use correct method name
            time.sleep(0.01)
        
        print("Test data sent to dashboard")


# Example usage and integration class
class ECGDashboardIntegration:
    def __init__(self, dashboard):
        """
        Integration layer between serial communication and dashboard
        
        Args:
            dashboard (ECGDashboard): The dashboard instance
        """
        self.dashboard = dashboard
        self.sample_index = 0
        
        # Example: simulate R-peak detection parameters
        self.last_r_peak_index = -50  # Prevent immediate duplicate detection
        
        # Example: model segment parameters
        self.model_window_size = 100  # samples per model input
        self.model_overlap = 50       # overlap between consecutive segments
        
        # Storage for recent data (for R-peak detection simulation)
        self.recent_data = deque(maxlen=20)
        
    def process_new_sample(self, ecg_value):
        """
        Process a new ECG sample and update dashboard
        
        Args:
            ecg_value (float): New ECG sample value
        """
        # Add to dashboard
        self.dashboard.add_data_point(ecg_value)
        
        # Store for processing
        self.recent_data.append((self.sample_index, ecg_value))        
       
        # Model segment processing (simulate model inference)
        #self.process_model_segments()
        
        self.sample_index += 1
        
            
    def process_model_segments(self):
        return
    
            
    


# Example of how to integrate with your existing code
def example_integration():
    """
    Example showing how to integrate the dashboard with your serial communication
    """
    # Create dashboard
    dashboard = ECGDashboard(window_size=1250, sampling_rate=125)
    integration = ECGDashboardIntegration(dashboard)
    
    # Start dashboard in a separate thread
    dashboard_thread = threading.Thread(target=dashboard.start_dashboard, daemon=True)
    dashboard_thread.start()
    
    # Simulate data feeding (replace this with your actual serial data processing)
    # In your actual code, you would call integration.process_new_sample(value) 
    # each time you receive/send an ECG value
    
    return dashboard, integration

if __name__ == "__main__":
    # Test the dashboard with simulated data
    dashboard, integration = example_integration()
    
    # Simulate real-time data (this would be replaced by your serial communication)
    try:
        sample_data = [0.1467,0.1461,0.1352,0.1073,0.0402,0.0164,0.1867,0.5909,0.8462,0.3880] * 200
        
        for value in sample_data:
            integration.process_new_sample(value)
            time.sleep(0.008)  # 125 Hz simulation
            
    except KeyboardInterrupt:
        print("Stopping dashboard...")
        dashboard.stop_dashboard()