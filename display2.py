import tkinter as tk
from tkinter import scrolledtext, ttk, Canvas, Frame, Scale
import sys
from io import StringIO
import math
from input import read
from heap_helperfunctions import insert_min, delete_min, min_heapify, heapify_up

class TreeNode:
    def __init__(self, canvas, x, y, value, radius=30):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.value = value
        self.radius = radius
        self.circle = None
        self.text = None
        
    def draw(self):
        # Draw circle with thicker outline
        self.circle = self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill="#4CAF50", outline="black", width=3  # Increased outline width and changed to black
        )
        
        # Draw text (bus number and time) with larger, bolder font
        bus_number, _, time, passengers, capacity = self.value
        display_text = f"{bus_number}\n{time}"
        self.text = self.canvas.create_text(
            self.x, self.y, text=display_text, font=("Arial", 11, "bold"), fill="white"  # Increased font size
        )
        
        # Draw tooltip with full info
        self.tooltip_text = f"Bus: {bus_number}\nTo: {self.value[1]}\nTime: {time}\nPassengers: {passengers}/{capacity}"
        
    def draw_connection(self, parent_x, parent_y):
        self.canvas.create_line(
            parent_x, parent_y,
            self.x, self.y,
            fill="black", width=3  # Changed to black and increased width
        )

class BusSimulationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bus Simulation Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f5f5f5")
        
        # Simulation control variables
        self.paused = False
        self.simulation_speed = 1000  # Default delay in milliseconds
        
        # Create styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Arial', 10), borderwidth=1)
        style.configure('TNotebook', background="#f5f5f5")
        style.configure('TNotebook.Tab', padding=[12, 6], font=('Arial', 10))
        
        # Create main frame
        main_frame = tk.Frame(root, bg="#f5f5f5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header with logo-like element
        header_frame = tk.Frame(main_frame, bg="#1976D2", height=70)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        header_text = tk.Label(
            header_frame, 
            text="🚌 Bus Simulation Dashboard", 
            font=("Arial", 22, "bold"), 
            bg="#1976D2", 
            fg="white",
            pady=15
        )
        header_text.pack()
        
        # Control panel frame
        control_frame = tk.Frame(main_frame, bg="#e0e0e0", padx=15, pady=15, relief=tk.RIDGE, bd=1)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Input controls
        input_frame = tk.Frame(control_frame, bg="#e0e0e0")
        input_frame.pack(fill=tk.X)
        
        tk.Label(input_frame, text="Input File:", bg="#e0e0e0", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.file_entry = tk.Entry(input_frame, width=30, font=("Arial", 10))
        self.file_entry.grid(row=0, column=1, padx=5, pady=10, sticky="w")
        self.file_entry.insert(0, "BUS.txt")  # Default value
        
        run_button = ttk.Button(
            input_frame, 
            text="Run Simulation", 
            command=self.run_simulation,
            style='TButton'
        )
        run_button.grid(row=0, column=2, padx=15, pady=10, sticky="w")
        
        # Pause/Resume button
        self.pause_button = ttk.Button(
            input_frame,
            text="Pause",
            command=self.toggle_pause,
            style='TButton'
        )
        self.pause_button.grid(row=0, column=3, padx=15, pady=10, sticky="w")
        
        # Speed control slider
        speed_frame = tk.Frame(control_frame, bg="#e0e0e0")
        speed_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Label(speed_frame, text="Simulation Speed:", bg="#e0e0e0", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        self.speed_slider = Scale(
            speed_frame,
            from_=500,
            to=3000,
            orient="horizontal",
            resolution=100,
            length=200,
            label="",
            command=self.update_speed
        )
        self.speed_slider.set(self.simulation_speed)
        self.speed_slider.pack(side=tk.LEFT, padx=5)
        
        tk.Label(speed_frame, text="Slower", bg="#e0e0e0", font=("Arial", 8)).pack(side=tk.LEFT)
        
        # Stats frame
        self.stats_frame = tk.Frame(control_frame, bg="#e0e0e0")
        self.stats_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Stats labels
        self.buses_processed = tk.StringVar(value="Buses Processed: 0")
        self.buses_departed = tk.StringVar(value="Departed: 0")
        self.buses_delayed = tk.StringVar(value="Delayed: 0")
        self.buses_cancelled = tk.StringVar(value="Cancelled: 0")
        
        tk.Label(self.stats_frame, textvariable=self.buses_processed, bg="#e0e0e0", font=("Arial", 10)).grid(row=0, column=0, padx=15, pady=5, sticky="w")
        tk.Label(self.stats_frame, textvariable=self.buses_departed, bg="#e0e0e0", font=("Arial", 10)).grid(row=0, column=1, padx=15, pady=5, sticky="w")
        tk.Label(self.stats_frame, textvariable=self.buses_delayed, bg="#e0e0e0", font=("Arial", 10)).grid(row=0, column=2, padx=15, pady=5, sticky="w")
        tk.Label(self.stats_frame, textvariable=self.buses_cancelled, bg="#e0e0e0", font=("Arial", 10)).grid(row=0, column=3, padx=15, pady=5, sticky="w")
        
        # Content frame with tabs
        content_frame = tk.Frame(main_frame, bg="#ffffff")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Heap Visualization
        self.heap_tab = tk.Frame(notebook, bg="#ffffff")
        notebook.add(self.heap_tab, text="Heap Visualization")
        
        self.heap_info_frame = tk.Frame(self.heap_tab, bg="#ffffff", height=50)
        self.heap_info_frame.pack(fill=tk.X)
        
        self.heap_info = tk.Label(self.heap_info_frame, text="Current Heap: 0 buses", font=("Arial", 12), bg="#ffffff")
        self.heap_info.pack(pady=10)
        
        # Canvas for heap visualization
        self.heap_canvas_frame = tk.Frame(self.heap_tab, bg="#ffffff")
        self.heap_canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.heap_canvas = Canvas(self.heap_canvas_frame, bg="#ffffff", highlightthickness=0)
        self.heap_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bus details panel
        self.bus_details_frame = tk.Frame(self.heap_tab, bg="#f0f0f0", height=150, pady=10, padx=10)
        self.bus_details_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Label(self.bus_details_frame, text="Current Bus Details", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(anchor="w")
        
        self.current_bus_info = tk.Text(self.bus_details_frame, height=5, font=("Consolas", 10), wrap=tk.WORD)
        self.current_bus_info.pack(fill=tk.X, pady=(5, 0))
        
        # Tab 2: Simulation Log
        self.log_tab = tk.Frame(notebook, bg="#ffffff")
        notebook.add(self.log_tab, text="Simulation Log")
        
        self.output_text = scrolledtext.ScrolledText(self.log_tab, wrap=tk.WORD, font=("Consolas", 10))
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 3: Records
        self.records_tab = tk.Frame(notebook, bg="#ffffff")
        notebook.add(self.records_tab, text="Final Records")
        
        self.records_frame = tk.Frame(self.records_tab, bg="#ffffff")
        self.records_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a treeview for records
        columns = ("Action", "Bus", "Destination", "Departing Time", "Passengers", "Capacity")
        self.records_tree = ttk.Treeview(self.records_frame, columns=columns, show='headings')
        
        # Define headings
        for col in columns:
            self.records_tree.heading(col, text=col)
            self.records_tree.column(col, width=100)
        
        self.records_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for treeview
        tree_scroll = ttk.Scrollbar(self.records_frame, orient="vertical", command=self.records_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.records_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to simulate")
        status_bar = tk.Label(
            main_frame, 
            textvariable=self.status_var, 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            bg="#f0f0f0",
            pady=5,
            padx=10
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Counters for statistics
        self.processed_count = 0
        self.departed_count = 0
        self.delayed_count = 0
        self.cancelled_count = 0
    
    def toggle_pause(self):
        """Toggle the pause state of the simulation"""
        self.paused = not self.paused
        
        if self.paused:
            self.pause_button.config(text="Resume")
            self.status_var.set("Simulation paused")
        else:
            self.pause_button.config(text="Pause")
            self.status_var.set("Simulation resumed")
            # Continue the simulation if it was paused
            self.root.event_generate("<<ContinueSimulation>>")
    
    def update_speed(self, value):
        """Update the simulation speed based on slider value"""
        self.simulation_speed = int(value)
        
    def time_add_30(self, time):
        """Adds 30 minutes to a time in HHMM format."""
        hours = time // 100
        minutes = time % 100
        minutes += 30
        if minutes >= 60:
            minutes -= 60
            hours += 1
        if hours >= 24:
            hours -= 24
        return hours * 100 + minutes
    
    def passengers_increase(self, passengers):
        increase = 0.2*(passengers)
        new = passengers + math.ceil(increase)
        return new

    def build_min_heap(self, heap):
        """Builds a min-heap by successive insertions."""
        temp = []
        for bus in heap:
            insert_min(temp, bus)
        heap.clear()
        heap.extend(temp)

    def draw_heap(self, heap):
        """Draw the heap as a binary tree on the canvas"""
        self.heap_canvas.delete("all")
        
        if not heap:
            self.heap_info.config(text="Current Heap: 0 buses")
            return
        
        self.heap_info.config(text=f"Current Heap: {len(heap)} buses")
        
        # Calculate dimensions
        canvas_width = self.heap_canvas.winfo_width()
        canvas_height = self.heap_canvas.winfo_height()
        
        # Ensure we have dimensions (wait for canvas to be rendered)
        if canvas_width <= 1:
            canvas_width = 1000
        if canvas_height <= 1:
            canvas_height = 600
            
        # Calculate number of levels in the heap
        levels = math.ceil(math.log2(len(heap) + 1))
        
        # Node radius - make nodes slightly larger
        radius = min(35, canvas_width / (2 ** levels) / 2.5)
        
        # Vertical spacing between levels
        level_height = canvas_height / (levels + 1)
        
        # Draw nodes
        nodes = []
        for i, bus in enumerate(heap):
            # Calculate position
            level = math.floor(math.log2(i + 1))
            nodes_in_level = 2 ** level
            position_in_level = i - (2 ** level - 1)
            
            # Horizontal position calculations
            section_width = canvas_width / (nodes_in_level + 1)
            x = section_width * (position_in_level + 1)
            
            # Vertical position
            y = level_height * (level + 1)
            
            # Create and draw node
            node = TreeNode(self.heap_canvas, x, y, bus, radius)
            nodes.append(node)
            
            # Draw connection to parent if not root
            if i > 0:
                parent_index = (i - 1) // 2
                parent_node = nodes[parent_index]
                node.draw_connection(parent_node.x, parent_node.y)
            
            node.draw()
            
            # Add tooltip behavior
            def create_tooltip(node_index):
                def show_tooltip(event):
                    self.current_bus_info.delete(1.0, tk.END)
                    self.current_bus_info.insert(tk.END, nodes[node_index].tooltip_text)
                return show_tooltip
            
            self.heap_canvas.tag_bind(node.circle, "<Button-1>", create_tooltip(i))
            self.heap_canvas.tag_bind(node.text, "<Button-1>", create_tooltip(i))
        
        # Add instructions
        self.heap_canvas.create_text(
            canvas_width/2, 30, 
            text="Click on a bus node to see details", 
            font=("Arial", 10, "italic"), 
            fill="#666666"
        )
        
        self.heap_canvas.update()

    def run_simulation(self):
        # Clear previous results
        self.output_text.delete(1.0, tk.END)
        self.heap_canvas.delete("all")
        self.current_bus_info.delete(1.0, tk.END)
        
        # Reset pause button state
        self.paused = False
        self.pause_button.config(text="Pause")
        
        # Clear the treeview
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)
        
        # Reset counters
        self.processed_count = 0
        self.departed_count = 0
        self.delayed_count = 0
        self.cancelled_count = 0
        self.update_stats()
        
        try:
            filename = self.file_entry.get()
            self.status_var.set(f"Running simulation with file: {filename}")
            self.root.update()
            
            # Capture print outputs
            old_stdout = sys.stdout
            output_capture = StringIO()
            sys.stdout = output_capture
            
            # Run simulation but with customized functions to update GUI
            self.simulation(filename)
            
            # Restore stdout
            sys.stdout = old_stdout
            
            # Display output
            output_text = output_capture.getvalue()
            self.output_text.insert(tk.END, output_text)
            
            self.status_var.set("Simulation completed successfully")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            self.output_text.insert(tk.END, f"Error: {str(e)}")
    
    def update_stats(self):
        """Update the statistics display"""
        self.buses_processed.set(f"Buses Processed: {self.processed_count}")
        self.buses_departed.set(f"Departed: {self.departed_count}")
        self.buses_delayed.set(f"Delayed: {self.delayed_count}")
        self.buses_cancelled.set(f"Cancelled: {self.cancelled_count}")
    
    def add_record_to_tree(self, action, bus_number, location, time, passengers, capacity):
        """Add a record to the treeview"""
        self.records_tree.insert(
            "", "end", 
            values=(action, bus_number, location, time, passengers, capacity)
        )
    
    def wait_if_paused(self):
        """Wait if the simulation is paused"""
        if self.paused:
            self.status_var.set("Simulation paused - waiting to resume")
            # Create a variable to track if we should continue
            self.root.wait_variable_or_event = True
            
            # Setup event handler to exit waiting
            def continue_handler(event):
                self.root.wait_variable_or_event = False
            
            self.root.bind("<<ContinueSimulation>>", continue_handler)
            
            # Wait until no longer paused
            while self.paused and self.root.wait_variable_or_event:
                self.root.update()
                self.root.after(100)  # Short delay to prevent CPU hogging
    
    def simulation(self, filename):
        # Step 1: Read data
        buses = read(filename)  # (bus_number, location, time, passengers, capacity)
        
        # Step 2: Build a min-heap based on current time
        self.build_min_heap(buses)
        
        # Track delays: bus_number -> number of delays
        delay_count = {}
        
        # Log what happens with each bus
        records = []
        
        # Initial heap visualization
        self.root.update()
        self.draw_heap(buses)
        self.root.update()
        
        print("Simulation started with file:", filename)
        print("Initial heap built with", len(buses), "buses.")
        
        # Step 3: Simulation loop
        while buses:
            # Check if simulation is paused
            self.wait_if_paused()
            
            self.processed_count += 1
            self.update_stats()
            
            current_bus = buses[0]  # Peek at the first bus (root)
            bus_number, location, time, passengers, capacity = current_bus
            
            # Update current bus details
            self.current_bus_info.delete(1.0, tk.END)
            self.current_bus_info.insert(tk.END, 
                f"Bus: {bus_number}\nTo: {location}\nTime: {time}\n" +
                f"Passengers: {passengers}/{capacity}\n" +
                f"Load Factor: {passengers/capacity:.2f}"
            )
            self.root.update()
            
            if passengers < 0.7 * capacity:
                # Check delay count
                if bus_number not in delay_count:
                    delay_count[bus_number] = 1
                else:
                    delay_count[bus_number] += 1
                
                if delay_count[bus_number] > 2:
                    # Cancel the bus
                    delete_min(buses)
                    record = f"Bus {bus_number} to {location} at {time} CANCELLED after 2 delays."
                    records.append(record)
                    print(record)
                    
                    self.cancelled_count += 1
                    self.update_stats()
                    
                    # Add to records tree
                    self.add_record_to_tree("CANCELLED", bus_number, location, time, passengers, capacity)
                else:
                    # Delay the bus by 30 minutes
                    new_time = self.time_add_30(time)
                    new_passengers = self.passengers_increase(passengers)
                    delayed_bus = (bus_number, location, new_time, new_passengers, capacity)
                    # delayed_bus = (bus_number, location, new_time, passengers, capacity)
                    
                    delete_min(buses)
                    insert_min(buses, delayed_bus)
                    
                    record = f"Bus {bus_number} to {location} DELAYED to {new_time} (Passengers: {passengers}, Capacity: {capacity})"
                    print(record)
                    records.append(record)
                    
                    self.delayed_count += 1
                    self.update_stats()
                    
                    # Add to records tree
                    self.add_record_to_tree("DELAYED", bus_number, location, new_time, passengers, capacity)
            
            else:
                # Depart the bus
                delete_min(buses)
                record = f"Bus {bus_number} to {location} DEPARTED at {time} (Passengers: {passengers}, Capacity: {capacity})"
                print(record)
                records.append(record)
                
                self.departed_count += 1
                self.update_stats()
                
                # Add to records tree
                self.add_record_to_tree("DEPARTED", bus_number, location, time, passengers, capacity)
            
            # Update heap visualization
            self.draw_heap(buses)
            self.root.update()
            
            # Use configurable simulation speed
            self.root.after(self.simulation_speed)
        
        print("\nSimulation complete.")
        print("\n=== FINAL RECORDS ===")
        for record in records:
            print(record)

if __name__ == "__main__":
    root = tk.Tk()
    app = BusSimulationGUI(root)
    root.mainloop()