# List of students and their favorite colors (tuples)
students = [
    ("Alice", "Blue"),
    ("Bob", "Red"),
    ("Charlie", "Blue"),
    ("Diana", "Green"),
    ("Ethan", "Red")
]

# Initialize a set to store unique colors
unique_colors = set()

# Initialize a dictionary to count the occurrences of each color
color_counts = {}

# Process each student's favorite color
for name, color in students:
    # Add the color to the set (automatically handles uniqueness)
    unique_colors.add(color)

    # Count the color occurrences using the dictionary
    if color in color_counts:
        color_counts[color] += 1
    else:
        color_counts[color] = 1

# Display the results
print("Unique colors:", unique_colors)
print("Color popularity:")
for color, count in color_counts.items():
    print(f"{color}: {count} student{'s' if count > 1 else ''}")
