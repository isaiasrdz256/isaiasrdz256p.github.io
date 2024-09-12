import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load images
PARTS = {
    'CPU': pygame.image.load('cpu.png'),
    'RAM': pygame.image.load('ram.png'),
    'GPU': pygame.image.load('gpu.png'),
}
BACKGROUND = pygame.image.load('background.png')
PC_SHELL = [pygame.image.load(f'PC_shell_({i}).png') for i in range(1,4)]

# Classes
class Part:
    def __init__(self, name, image):
        self.name = name
        self.image = image
        self.rect = self.image.get_rect()
        self.draggable = False

class Order:
    def __init__(self):
        self.parts = random.sample(list(PARTS.keys()), k=3)  # Random order of 3 parts

class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Computer Builder')
        self.clock = pygame.time.Clock()
        scale_factor = 0.5  # Adjust this value to make pieces larger or smaller
        self.parts = [Part(name, pygame.transform.scale(image, 
                           (int(image.get_width() * scale_factor), 
                            int(image.get_height() * scale_factor))))
                      for name, image in PARTS.items()]
        self.assembly_area = pygame.Rect(0, HEIGHT - 150, WIDTH, 150)
        self.current_order = Order()
        self.dragging_part = None
        self.dragging_offset = (0, 0)
        self.pc_shell_rect = PC_SHELL[0].get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.pc_slots = self.create_pc_slots()
        self.assembled_parts = {}
        self.current_shell = 0
        self.total_shells = len(PC_SHELL)
        self.game_state = "START"
        self.start_button = Button(WIDTH//2 - 50, HEIGHT//2 - 25, 100, 50, "Start", (0, 255, 0), WHITE)
        self.slide_speed = 50

        # Initialize the mixer
        pygame.mixer.init()
        
        # Load and play background music

 # -1 means loop indefinitely

    def create_pc_slots(self):
        # Define slots relative to the PC shell
        shell_width, shell_height = self.pc_shell_rect.size
        return {
            "CPU": pygame.Rect(shell_width * 0.2, shell_height * 0.2, 60, 60),
            "GPU": pygame.Rect(shell_width * 0.2, shell_height * 0.5, 60, 60),
            "RAM": pygame.Rect(shell_width * 0.5, shell_height * 0.2, 60, 60),
            
            # Add more slots as needed
        }

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == "START":
                    if self.start_button.rect.collidepoint(event.pos):
                        self.game_state = "PLAY"
                else:
                    self.start_dragging(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.stop_dragging(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                self.drag_part(event.pos)
        return True

    def start_dragging(self, pos):
        for part in self.parts:
            if part.rect.collidepoint(pos):
                self.dragging_part = part
                self.dragging_offset = (pos[0] - part.rect.x, pos[1] - part.rect.y)
                break

    def stop_dragging(self, pos):
        if self.dragging_part:
            snapped = False
            for part_name, slot in self.pc_slots.items():
                slot_rect = slot.move(self.pc_shell_rect.topleft)
                if slot_rect.collidepoint(pos) and part_name == self.dragging_part.name and part_name not in self.assembled_parts:
                    # Snap the part into place
                    self.dragging_part.rect = slot_rect.copy()
                    self.assembled_parts[part_name] = self.dragging_part
                    if self.dragging_part in self.parts:
                        self.parts.remove(self.dragging_part)
                    snapped = True
                    break
            
            if not snapped and self.dragging_part not in self.assembled_parts.values():
                # Return the part to its original position only if it's not already assembled
                self.parts.append(self.dragging_part)
            
            self.dragging_part = None

            # Check if all parts are assembled
            if self.check_all_parts_assembled():
                self.move_to_next_shell()

    def drag_part(self, pos):
        if self.dragging_part:
            self.dragging_part.rect.x = pos[0] - self.dragging_offset[0]
            self.dragging_part.rect.y = pos[1] - self.dragging_offset[1]

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_event(event)

            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

    def handle_event(self, event):
        if self.game_state == "START":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.start_button.rect.collidepoint(event.pos):
                    self.game_state = "SLIDING_IN"
        elif self.game_state == "PLAYING":
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_down(event.pos)
            if event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_up()
            if event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event.pos)

    def update(self):
        if self.game_state == "SLIDING_IN":
            self.pc_shell_rect.x += self.slide_speed
            if self.pc_shell_rect.left >= 0:
                self.pc_shell_rect.left = 0
                self.game_state = "PLAYING"
        elif self.game_state == "SLIDING_OUT":
            self.pc_shell_rect.x += self.slide_speed
            if self.pc_shell_rect.left >= WIDTH:
                self.game_state = "SLIDING_IN"
                self.pc_shell_rect.right = -100
                self.current_order = Order()

    def draw(self):
        self.screen.blit(BACKGROUND, (0, 0))
        if self.game_state == "START":
            # Draw title background
            font = pygame.font.Font(None, 64)
            title_text = "Isaias' Computer Shop"
            title_surface = font.render(title_text, True, WHITE)
            title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
            
            # Create a slightly larger rect for the background
            bg_rect = title_rect.inflate(20, 10)  # 20 pixels wider, 10 pixels taller
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            
            # Draw the title text
            self.screen.blit(title_surface, title_rect)
            
            # Draw start button
            self.start_button.draw(self.screen)
        else:
            self.screen.blit(PC_SHELL[self.current_shell], self.pc_shell_rect)
            
            # Draw assembly area
            pygame.draw.rect(self.screen, BLACK, self.assembly_area)
            
            # Draw PC slots and assembled parts
            for part_name, slot in self.pc_slots.items():
                slot_rect = slot.move(self.pc_shell_rect.topleft)
                if part_name in self.assembled_parts:
                    # Draw the assembled part
                    self.screen.blit(self.assembled_parts[part_name].image, slot_rect)
                else:
                    # Draw empty slot
                    pygame.draw.rect(self.screen, (255, 255, 0), slot_rect, 3)
                    font = pygame.font.Font(None, 24)
                    text_surface = font.render(part_name, True, (255, 255, 0))
                    text_rect = text_surface.get_rect(center=slot_rect.center)
                    self.screen.blit(text_surface, text_rect)
            
            # Draw unassembled parts
            self.draw_parts()

            # Draw the dragged part last so it appears on top
            if self.dragging_part:
                self.screen.blit(self.dragging_part.image, self.dragging_part.rect)

        pygame.display.flip()
        self.clock.tick(FPS)

    def handle_mouse_down(self, pos):
        for part in self.parts:
            if part.rect.collidepoint(pos):
                self.dragging_part = part
                part.draggable = True

    def handle_mouse_up(self):
        if self.dragging_part:
            # Check if part is dropped in valid area
            self.dragging_part.draggable = False
            self.dragging_part = None

    def handle_mouse_motion(self, pos):
        if self.dragging_part:
            self.dragging_part.rect.center = pos

    def draw_parts(self):
        total_width = sum(part.rect.width for part in self.parts) + 10 * (len(self.parts) - 1)
        start_x = (WIDTH - total_width) // 2
        for i, part in enumerate(self.parts):
            if part != self.dragging_part:
                part.rect.bottomleft = (start_x + i * (part.rect.width + 10), HEIGHT - 20)
                self.screen.blit(part.image, part.rect)

    def check_all_parts_assembled(self):
        return len(self.assembled_parts) == len(self.pc_slots)

    def move_to_next_shell(self):
        print("Good job! All pieces are correctly placed.")
        self.current_shell += 1
        if self.current_shell < self.total_shells:
            print(f"Moving to shell {self.current_shell + 1}")
            self.pc_shell_rect = PC_SHELL[self.current_shell].get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.assembled_parts.clear()
            self.parts = [Part(name, image) for name, image in PARTS.items()]
        else:
            print("Congratulations! You've completed all shells!")
            # You can add game completion logic here

# Main function
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
