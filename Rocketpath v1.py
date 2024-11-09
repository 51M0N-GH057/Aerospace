import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tkinter as tk
from tkinter import font as tkFont
from tkinter import messagebox, filedialog
import pandas as pd  # Import pandas for saving data to CSV

# Constants
g = 9.81  

# Global variables to store simulation data
global_times = []
global_altitudes = []
global_rocket = None  # To store the rocket object for metrics
metrics_saved = False  # Flag to check if metrics have been saved

class Rocket:
    def __init__(self, mass, thrust, burn_time):
        self.mass = mass  
        self.thrust = thrust 
        self.burn_time = burn_time 
        self.velocity = 0  
        self.altitude = 0 
        self.time = 0  
        self.max_altitude = 0  
        self.max_velocity = 0 
        self.propellant_mass_factor = 0.8

    def update(self, dt):
        if self.time < self.burn_time:
            # Apply thrust
            acceleration = (self.thrust / self.mass) - g
        else:
            acceleration = -g

        # Update velocity and altitude
        self .velocity += acceleration * dt
        self.altitude += self.velocity * dt
        self.time += dt

        # Update max altitude and max velocity
        if self.altitude > self.max_altitude:
            self.max_altitude = self.altitude
        if self.velocity > self.max_velocity:
            self.max_velocity = self.velocity

        return self.altitude

    def calculate_mass_flow_rate(self):
        # Calculate propellant mass based on the factor
        propellant_mass = self.mass * self.propellant_mass_factor
        mass_flow_rate = propellant_mass / self.burn_time if self.burn_time > 0 else 0
        return mass_flow_rate

    def calculate_specific_impulse(self):
        mass_flow_rate = self.calculate_mass_flow_rate()
        weight_flow_rate = mass_flow_rate * g  # Weight flow rate in Newtons
        specific_impulse = self.thrust / weight_flow_rate if weight_flow_rate > 0 else 0
        return specific_impulse

    def calculate_performance(self):
        total_flight_time = self.time
        total_distance_traveled = self.max_altitude  # Use max altitude as total distance
        average_velocity = total_distance_traveled / total_flight_time if total_flight_time > 0 else 0
        thrust_to_weight_ratio = self.thrust / (self.mass * g)
        total_impulse = self.thrust * self.burn_time  # Calculate total impulse
        
        # Calculate propellant mass
        propellant_mass = self.mass * self.propellant_mass_factor

        return {
            "Max Altitude (m)": self.max_altitude,
            "Total Flight Time (s)": total_flight_time,
            "Max Velocity (m/s)": self.max_velocity,
            "Average Velocity (m/s)": average_velocity,
            "Thrust-to-Weight Ratio": thrust_to_weight_ratio,
            "Total Impulse (Ns)": total_impulse,  # Include total impulse
            "Propellant Mass (kg)": propellant_mass,  # Include propellant mass
            "Mass Flow Rate (kg/s)": self.calculate_mass_flow_rate(),  # Include mass flow rate
            "Specific Impulse (s)": self.calculate_specific_impulse()  # Include specific impulse
        }

def simulate_rocket(rocket, dt=0.1):
    altitudes = []
    velocities = []  # Store velocities for later use
    times = []

    while rocket.altitude >= 0:  # Only run while the rocket is above ground
        altitude = rocket.update(dt)
        altitudes.append(altitude)
        velocities.append(rocket.velocity)  # Capture the velocity
        times.append(rocket.time)

    return times, altitudes, velocities  # Return velocities as well

def perform_simulation():
    try:
        mass = float(mass_entry.get())
        thrust = float(thrust_entry.get())
        burn_time = float(burn_time_entry.get())

        # Check for negative values
        if mass < 0 or thrust < 0 or burn_time < 0:
            messagebox.showerror("Error", "Mass, thrust, and burn time must be non-negative values.")
            return

        # Create rocket object
        rocket = Rocket(mass, thrust, burn_time)

        # Simulate rocket's trajectory
        times, altitudes, velocities = simulate_rocket(rocket)

        return rocket, times, altitudes, velocities

    except ValueError:
        messagebox.showerror("Error", "Invalid input. Please enter valid numbers for mass, thrust, and burn time.")

def plot_velocity_vs_time(times, velocities):
    plt.figure(figsize=(10, 5))
    plt.plot(times, velocities, color='blue', label='Velocity (m/s)')
    plt.title('Velocity vs Time')
    plt.xlabel('Time (s)')
    plt.ylabel('Velocity (m/s)')
    plt.grid(True)
    plt.legend()
    plt.show()

def save_simulation_data(rocket):
    global metrics_saved  # Use the global flag to track metrics saving
    if not global_times or not global_altitudes:
        messagebox.showerror("Error", "No simulation data to save. Please run the simulation first.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if file_path:
        data = {
            'Time (s)': global_times,
            'Altitude (m)': global_altitudes
        }
        performance_metrics = rocket.calculate_performance()
        if not metrics_saved:  # Check if metrics have already been saved
            for key, value in performance_metrics.items():
                data[key] = [value] * len(global_times)  # Repeat the metric for each time entry
                metrics_saved = True  # Set the flag to True after saving metrics
                df = pd.DataFrame(data)
                df.to_csv(file_path, index=False)
        messagebox.showinfo("Success", "Simulation data saved successfully.")

def run_simulation():
    global global_times, global_altitudes, global_rocket, metrics_saved  # Declare the global variables
    metrics_saved = False  # Reset the metrics saved flag for a new simulation
    try:
        rocket, times, altitudes, velocities = perform_simulation()

        # Store the times and altitudes for saving later
        global_times = times
        global_altitudes = altitudes
        global_rocket = rocket  # Store the rocket object for saving metrics

        # Create a figure for the animation and velocity graph
        fig, ax1 = plt.subplots(figsize=(10, 5))
        
        # Altitude Plot
        ax1.set_xlim(0, max(times) + 1)  # Set x-axis limits based on flight time
        ax1.set_ylim(0, max(altitudes) + 10)  # Set y-axis limits based on max altitude
        ax1.set_title('Trajectory Simulation', fontsize=10)
        ax1.set_xlabel('Time (s)', fontsize=8)
        ax1.set_ylabel('Altitude (m)', fontsize=8)
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.set_facecolor('#87CEEB')

        line, = ax1.plot([], [], lw=1, color='black', label='Altitude')
        rocket_marker, = ax1.plot([], [], marker='o', markersize=5, color='red', label='Rocket Position')
        ax1.legend()

        # Trajectory animation
        def init():
            line.set_data([], [])
            rocket_marker.set_data([], [])
            return line, rocket_marker, 

        # Animation function
        def animate(i):
            if i < len(times):
                # Update the line data for altitude
                line.set_data(times[:i+1], altitudes[:i+1])
                rocket_marker.set_data([times[i]], [altitudes[i]])  # Use lists for x and y
            return line, rocket_marker, 

        ani = animation.FuncAnimation(fig, animate, frames=len(times), init_func=init, blit=True, interval=100)

        plt.show()

        # Call the new function to plot velocity vs time
        plot_velocity_vs_time(times, velocities)

    except ValueError:
        messagebox.showerror("Error", "Invalid input. Please enter valid numbers for mass, thrust, and burn time.")

def display_metrics():
    try:
        rocket, times, altitudes, velocities = perform_simulation()

        # Calculate performance metrics
        performance_metrics = rocket.calculate_performance()

        # Create a new window for displaying performance metrics
        metrics_window = tk.Toplevel(root)
        metrics_window.title("Rocket Performance Metrics")

        # Create a text widget to display the metrics
        metrics_text_widget = tk.Text(metrics_window, width=100, height=20, bg="white", fg="black", font=("Arial", 12))
        metrics_text_widget.pack(padx=10, pady=10)

        # Format the metrics text
        metrics_text = "Rocket Performance Metrics:\n\n"
        for key, value in performance_metrics.items():
            metrics_text += f"{key}: {value:.2f}\n"

        # Add analysis summary with suggestions
        metrics_text += "\n\n--- Analysis Summary ---\n\n"

        # Suggestions based on performance metrics
        if performance_metrics['Max Altitude (m)'] < 1000:
            metrics_text += "> Consider increasing thrust or reducing mass to achieve a higher altitude.\n\n"
        else:
            metrics_text += "Great job! The rocket achieved a high altitude.\n\n"

        if performance_metrics['Total Flight Time (s)'] < 30:
            metrics_text += "> The flight time is relatively short. You may want to increase the burn time for longer flights.\n\n"
        else:
            metrics_text += "The flight time is satisfactory.\n\n"

        if performance_metrics['Average Velocity (m/s)'] < 50:
            metrics_text += "> The average velocity is low. Increasing thrust could improve this.\n\n"
        else:
            metrics_text += "Good average velocity achieved!\n\n"

        if performance_metrics['Thrust-to-Weight Ratio'] < 1:
            metrics_text += "Warning: The thrust-to-weight ratio is below 1. The rocket may not be able to lift off effectively.\n\n"
        else:
            metrics_text += "The thrust-to-weight ratio is adequate for a successful launch.\n\n"

        if performance_metrics['Specific Impulse (s)'] < 200:
            metrics_text += "> The specific impulse is low. Consider optimizing the engine design for better efficiency.\n\n"
        else:
            metrics_text += "The specific impulse is good, indicating efficient engine performance.\n\n"

        metrics_text_widget.insert(tk.END, metrics_text)

    except ValueError:
        messagebox.showerror("Error", "Invalid input. Please enter valid numbers for mass, thrust, and burn time.")
def reset_inputs():
    mass_entry.delete(0, tk.END)
    thrust_entry.delete(0, tk.END)
    burn_time_entry.delete(0, tk.END)

# GUI Setup
root = tk.Tk()
root.title("Rocketpath - Rocket Trajectory Simulation Tool")

# Set a background color
root.configure(bg="#ccffcc")  # Light blue background

# Create a custom font
custom_font = tkFont.Font(family="Helvetica", size=12)

# Input fields
tk.Label(root, text="Mass (kg):", font=custom_font, bg="#ccffcc").grid(row=0, column=0, padx=10, pady=10)
mass_entry = tk.Entry(root, font=custom_font)
mass_entry.grid(row=0, column=1, pady=10)

tk.Label(root, text="Thrust (N):", font=custom_font, bg="#ccffcc").grid(row=1, column=0, padx=10, pady=10)
thrust_entry = tk.Entry(root, font=custom_font)
thrust_entry.grid(row=1, column=1, pady=10)

tk.Label(root, text=" Burn Time (s):", font=custom_font, bg="#ccffcc").grid(row=2, column=0, padx=10, pady=10)
burn_time_entry = tk.Entry(root, font=custom_font)
burn_time_entry.grid(row=2, column=1, pady=10)

# Create a frame for buttons
button_frame = tk.Frame(root, bg="#ccffcc")
button_frame.grid(row=3, column=0, columnspan=2, pady=20)

# Buttons with hover effect
def on_enter(e):
    e.widget['background'] = '#87ceeb'  # Change color on hover

def on_leave(e):
    e.widget['background'] = '#ffffff'  # Change back to original color

run_button = tk.Button(button_frame, text="Run Trajectory Simulation", command=run_simulation, font=custom_font, bg="#ffffff")
run_button.bind("<Enter>", on_enter)
run_button.bind("<Leave>", on_leave)
run_button.pack(side=tk.LEFT, padx=10)

metrics_button = tk.Button(button_frame, text="Display Performance Metrics", command=display_metrics, font=custom_font, bg="#ffffff")
metrics_button.bind("<Enter>", on_enter)
metrics_button.bind("<Leave>", on_leave)
metrics_button.pack(side=tk.LEFT, padx=10)

reset_button = tk.Button(button_frame, text="Reset", command=reset_inputs, font=custom_font, bg="#ffffff")
reset_button.bind("<Enter>", on_enter)
reset_button.bind("<Leave>", on_leave)
reset_button.pack(side=tk.LEFT, padx=10)

# New button for saving simulation data
save_button = tk.Button(root, text="Save Simulation Data", command=lambda: save_simulation_data(global_rocket), font=custom_font, bg="#ffffff")
save_button.bind("<Enter>", on_enter)
save_button.bind("<Leave>", on_leave)
save_button.grid(row=3, column=5, columnspan=2, pady=20, padx=10)

root.mainloop()