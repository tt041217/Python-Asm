students = [
    ("Alice", "Blue"),
    ("Bob", "Red"),
    ("Charlie", "Blue"),
    ("Diana", "Green"),
    ("Ethan", "Red")
]

unique_colors = set()

color_counts = {}

for name, color in students:
    unique_colors.add(color)
    
    if color in color_counts:
        color_counts[color] += 1
    else:
        color_counts[color] = 1
        
print("Unique colors:", unique_colors)
print("Color popularity:")
for color, count in color_counts.items():
    print(f"{color}: {count} student{'s' if count > 1 else ''}")