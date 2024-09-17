import pgzrun
from random import choice

# Set up the game window
WIDTH, HEIGHT = 800, 600

# Game state
game_state = 'start'

# Start button dimensions
button_width, button_height = 200, 50
button_x = WIDTH // 2 - button_width // 2
button_y = HEIGHT * 3 // 4 - button_height // 2

# Define the cloud character
cloud = Actor('cloud', (50, 50))  # Start position

# Maze layout (0 = wall, 1 = path)
maze = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0],
    [0,0,0,0,0,1,0,1,0,0,0,0,0,0,1,0],
    [0,1,1,1,0,1,1,1,0,1,1,1,1,0,1,0],
    [0,1,0,1,0,0,0,1,0,1,0,0,1,0,1,0],
    [0,1,0,1,1,1,1,1,1,1,0,1,1,0,1,0],
    [0,1,0,0,0,0,0,0,0,0,0,1,0,0,1,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,0,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
]

# Function to get valid positions in the maze
def get_valid_positions():
    return [(col * 50, row * 50) for row in range(len(maze)) for col in range(len(maze[0])) if maze[row][col] == 1]

# Create Actor objects for resources, VMs, and malware
valid_positions = get_valid_positions()
resource_nodes = [
    {'actor': Actor('cpu', choice(valid_positions)), 'type': 'cpu', 'collected': False},
    {'actor': Actor('ram', choice(valid_positions)), 'type': 'memory', 'collected': False},
    {'actor': Actor('storage.png', choice(valid_positions)), 'type': 'storage', 'collected': False}
]

vms = [
    {'actor': Actor('vm', choice(valid_positions)), 'name': 'VM1', 'resource_requirement': ['cpu', 'memory'], 'resources': []},
    {'actor': Actor('vm', choice(valid_positions)), 'name': 'VM2', 'resource_requirement': ['storage', 'cpu'], 'resources': []}
]

malware = [Actor('malware', choice(valid_positions)), Actor('malware', choice(valid_positions))]

# Add this near the top of your file, with other global variables
all_vms_solved_message_printed = False

def on_mouse_down(pos):
    global game_state
    if game_state == 'start':
        if button_x <= pos[0] <= button_x + button_width and button_y <= pos[1] <= button_y + button_height:
            game_state = 'prologue'  # Change to prologue state

def update():
    global resource_nodes, vms, all_vms_solved_message_printed, game_state
    if game_state == 'playing':
        # Move the cloud character
        new_x, new_y = cloud.x, cloud.y
        if keyboard.left:
            new_x -= 5
        if keyboard.right:
            new_x += 5
        if keyboard.up:
            new_y -= 5
        if keyboard.down:
            new_y += 5

        # Check if the new position is valid (not a wall)
        grid_x, grid_y = int(new_x // 50), int(new_y // 50)
        if 0 <= grid_y < len(maze) and 0 <= grid_x < len(maze[0]) and maze[grid_y][grid_x] == 1:
            cloud.x, cloud.y = new_x, new_y

        # Check for resource collection
        for resource in resource_nodes:
            if cloud.colliderect(resource['actor']) and not resource['collected']:
                resource['collected'] = True
                print(f"Collected {resource['type']}")

        # Check for VM puzzle-solving
        for vm in vms:
            if cloud.colliderect(vm['actor']):
                for resource in resource_nodes:
                    if resource['collected'] and resource['type'] in vm['resource_requirement'] and resource['type'] not in [r['type'] for r in vm['resources']]:
                        vm['resources'].append(resource)
                        resource['collected'] = False
                        resource['actor'].pos = vm['actor'].pos
                        print(f"Placed {resource['type']} on {vm['name']}")

        # Check if all VMs are solved
        all_vms_solved = all(set(vm['resource_requirement']) == set(r['type'] for r in vm['resources']) for vm in vms)

        if all_vms_solved and not all_vms_solved_message_printed:
            print("Good job! All VMs are correctly configured.")
            all_vms_solved_message_printed = True
            game_state = 'completed'  # Change game state to 'completed'

def draw():
    screen.clear()
    if game_state == 'start':
        screen.draw.text("Welcome to Cloud Resource Manager", center=(WIDTH/2, HEIGHT/4), fontsize=40, color="white")
        screen.draw.text("Navigate the maze, collect resources, and configure VMs!", center=(WIDTH/2, HEIGHT/2), fontsize=30, color="white")
        
        # Draw start button
        screen.draw.filled_rect(Rect((button_x, button_y), (button_width, button_height)), color="light blue")
        screen.draw.rect(Rect((button_x, button_y), (button_width, button_height)), color="navy")
        screen.draw.text("Start", center=(WIDTH/2, button_y + button_height/2), fontsize=30, color="navy")
    
    elif game_state == 'prologue':
        screen.draw.text("Introduction to Cloud Computing", center=(WIDTH/2, HEIGHT/6), fontsize=40, color="white")
        prologue_text = [
            "Cloud computing is like renting a powerful computer over the internet.",
            "Instead of owning physical hardware, you can use virtual resources",
            "such as processing power, memory, and storage.",
            "",
            "In this game, you'll manage cloud resources:",
            "- Collect CPU, RAM, and Storage",
            "- Configure Virtual Machines (VMs) with these resources",
            "- So that they can run your applications smoothly",
            "- And users can access them from anywhere in the world",
            "- Avoid malware that can harm your cloud infrastructure",
            "",
            "Press SPACE to continue to instructions"
        ]
        for i, line in enumerate(prologue_text):
            screen.draw.text(line, center=(WIDTH/2, HEIGHT/3 + i*30), fontsize=20, color="white")
    
    elif game_state == 'instructions':
        screen.draw.text("Instructions", center=(WIDTH/2, HEIGHT/4), fontsize=40, color="white")
        screen.draw.text("1. Use arrow keys to move the cloud.", center=(WIDTH/2, HEIGHT/2 - 30), fontsize=30, color="white")
        screen.draw.text("2. Collect resources and configure VMs.", center=(WIDTH/2, HEIGHT/2), fontsize=30, color="white")
        screen.draw.text("3. Avoid malware.", center=(WIDTH/2, HEIGHT/2 + 30), fontsize=30, color="white")
        screen.draw.text("Press SPACE to start playing", center=(WIDTH/2, HEIGHT*3/4), fontsize=30, color="white")
    
    elif game_state == 'playing':
        # Draw the maze
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                if cell == 0:
                    screen.draw.filled_rect(Rect((x*50, y*50), (50, 50)), color="gray")

        # Draw the game elements
        cloud.draw()
        for resource in resource_nodes:
            if not resource['collected']:
                resource['actor'].draw()
                screen.draw.text(resource['type'], resource['actor'].pos)
        for vm in vms:
            vm['actor'].draw()
            screen.draw.text(vm['name'], vm['actor'].pos)
            for i, resource in enumerate(vm['resources']):
                resource['actor'].draw()
                screen.draw.text(resource['type'], (vm['actor'].x, vm['actor'].y + 30 + i * 30))
        for enemy in malware:
            enemy.draw()
            screen.draw.text("Malware", enemy.pos)

    elif game_state == 'completed':
        screen.fill("black")
        screen.draw.text("Congratulations!", center=(WIDTH/2, HEIGHT/3), fontsize=60, color="white")
        screen.draw.text("You've completed the game!", center=(WIDTH/2, HEIGHT/2), fontsize=40, color="white")
        screen.draw.text("Press SPACE to view credits", center=(WIDTH/2, HEIGHT*2/3), fontsize=30, color="white")
    elif game_state == 'credits':
        draw_credits()

def on_key_down(key):
    global game_state
    if game_state == 'prologue' and key == keys.SPACE:
        game_state = 'instructions'
    elif game_state == 'instructions' and key == keys.SPACE:
        game_state = 'playing'
    elif game_state == 'completed' and key == keys.SPACE:
        game_state = 'credits'
    elif game_state == 'credits' and key == keys.SPACE:
        reset_game()
        game_state = 'start'

def reset_game():
    global cloud, resource_nodes, vms, malware, all_vms_solved_message_printed
    
    # Reset cloud position
    cloud.pos = (50, 50)
    
    # Reset resources
    valid_positions = get_valid_positions()
    for resource in resource_nodes:
        resource['actor'].pos = choice(valid_positions)
        resource['collected'] = False
    
    # Reset VMs
    for vm in vms:
        vm['actor'].pos = choice(valid_positions)
        vm['resources'] = []
    
    # Reset malware positions
    for m in malware:
        m.pos = choice(valid_positions)
    
    # Reset completion flag
    all_vms_solved_message_printed = False

def draw_credits():
    screen.fill("black")
    credits = [
        "Cloud Resource Manager",
        "",
        "Developed by:",
        "Isaias Rodriguez",
        "",
        "Graphics:",
        "Isaias Rodriguez",
        "",
        "Special Thanks:",
        "Chat GPT, Claude, PLC, ",
        ""
        "and all the creators of these tools that made this possible"
        "",
        ""
        "Press SPACE to restart"
    ]
    for i, line in enumerate(credits):
        screen.draw.text(line, center=(WIDTH/2, 50 + i * 30), fontsize=30, color="white")

pgzrun.go()
