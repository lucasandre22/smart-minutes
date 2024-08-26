import pandas as pd
import matplotlib.pyplot as plt

# Read benchmark results from CSV
df = pd.read_csv("benchmark_results.csv")

# Plotting the statistics
fig, axes = plt.subplots(4, 1, figsize=(20, 8))

# Execution Time
axes[0].plot(df["model_name"], df["execution_time_in_seconds"], marker='o', linestyle='-', color="blue")
axes[0].set_title("Execution Time (s)")
axes[0].set_xlabel("Model")
axes[0].set_ylabel("Time (s)")

# GPU Usage
axes[1].plot(df["model_name"], df["gpu_used_mb"], marker='o', linestyle='-', color="green")
axes[1].set_title("GPU Used (MB)")
axes[1].set_xlabel("Model")
axes[1].set_ylabel("Memory (MB)")

# CPU Usage
axes[2].plot(df["model_name"], df["cpu_usage_percent"], marker='o', linestyle='-', color="red")
axes[2].set_title("CPU Usage (%)")
axes[2].set_xlabel("Model")
axes[2].set_ylabel("Usage (%)")

# RAM Usage
axes[3].plot(df["model_name"], df["ram_usage_percent"], marker='o', linestyle='-', color="purple")
axes[3].set_title("RAM Usage (%)")
axes[3].set_xlabel("Model")
axes[3].set_ylabel("Usage (%)")

# Adjust layout
plt.tight_layout()
plt.show()
