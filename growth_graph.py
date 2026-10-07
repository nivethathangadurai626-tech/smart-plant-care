import matplotlib.pyplot as plt

# Plant growth data
days = [1, 3, 5, 7]
growth = [10, 13, 17, 21]

# Create graph
plt.plot(days, growth, marker="o")

plt.title("Plant Growth Monitoring")
plt.xlabel("Days")
plt.ylabel("Plant Height (cm)")

plt.xticks(days)
plt.grid(True)

# Save graph
plt.savefig("plant_growth_graph.png")

# Display graph
plt.show()