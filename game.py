"""
Snake Game - Pygamepy -3.11 Implementation
A stable, grid-based Snake game with a modern dark theme.
Compatible with Python 3.11+
"""

import pygame  # Import pygame library for game development
import sys  # Import sys for system operations like exit
import random  # Import random for generating random food positions

# Initialize Pygame modules (must be called before using pygame features)
pygame.init()

# Constants - Define game dimensions and settings
WINDOW_WIDTH = 800  # Screen width in pixels
WINDOW_HEIGHT = 600  # Screen height in pixels
GRID_SIZE = 20  # Size of each grid cell (snake moves one cell at a time)
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE  # Number of grid cells horizontally
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE  # Number of grid cells vertically
FPS = 10  # Frames per second (controls game speed)

# Color definitions using RGB values
BLACK = (0, 0, 0)  # Pure black for background
DARK_GRAY = (15, 15, 15)  # Very dark gray for subtle grid lines
NEON_GREEN = (0, 255, 100)  # Bright neon green for snake
WHITE = (255, 255, 255)  # White for text and food
RED = (255, 0, 0)  # Red for food

# Game states - constants to track what screen to show
PLAYING = 1  # Game is running
GAME_OVER = 2  # Game has ended

# Initialize the display window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))  # Create the game window
pygame.display.set_caption("Snake Game")  # Set window title

# Initialize clock to control frame rate
clock = pygame.time.Clock()  # Clock object for FPS control

# Initialize font for displaying text
font = pygame.font.Font(None, 36)  # Default font, size 36 pixels


class Snake:
    """Snake class that manages the snake's body and movement."""
    
    def __init__(self):
        """Initialize snake at center of screen."""
        # Starting position (in grid coordinates, not pixels)
        start_x = GRID_WIDTH // 2  # Center horizontally
        start_y = GRID_HEIGHT // 2  # Center vertically
        
        # Snake body: list of [x, y] grid positions (not pixel positions)
        # Head is at index 0, tail is at the end
        self.body = [[start_x, start_y]]  # Start with just the head
        
        # Direction: [x_change, y_change] for grid movement
        # [1, 0] = right, [-1, 0] = left, [0, 1] = down, [0, -1] = up
        self.direction = [1, 0]  # Start moving right
        self.next_direction = [1, 0]  # Queued direction for next move
    
    def update(self):
        """Update snake position - move one grid cell in current direction."""
        # Update direction from queued direction (allows one queued direction)
        self.direction = self.next_direction.copy()
        
        # Get current head position
        head_x, head_y = self.body[0]
        
        # Calculate new head position by adding direction
        new_head_x = head_x + self.direction[0]  # Move in X direction
        new_head_y = head_y + self.direction[1]  # Move in Y direction
        
        # Add new head to the front of the body
        self.body.insert(0, [new_head_x, new_head_y])
    
    def grow(self):
        """Make snake grow by NOT removing the tail next update."""
        # Snake grows by keeping the tail when moving
        # This is handled in update() - we just don't pop the tail
        pass
    
    def shrink(self):
        """Remove tail segment (called after moving to keep length constant)."""
        # Remove last segment (tail) if snake hasn't grown
        if len(self.body) > 1:  # Only remove if more than head exists
            self.body.pop()  # Remove the last element (tail)
    
    def change_direction(self, new_direction):
        """Change snake direction (prevents reversing into itself)."""
        # Prevent snake from reversing into itself
        # Check if new direction is opposite of current direction
        if new_direction[0] != -self.direction[0] or new_direction[1] != -self.direction[1]:
            # Safe to change direction
            self.next_direction = new_direction.copy()
    
    def check_collision(self):
        """Check if snake collides with walls or itself. Returns True if collision."""
        head_x, head_y = self.body[0]  # Get head position
        
        # Check wall collision - head outside grid boundaries
        if head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT:
            return True  # Hit a wall
        
        # Check self collision - head overlaps with any body segment
        for segment in self.body[1:]:  # Skip head, check rest of body
            if head_x == segment[0] and head_y == segment[1]:  # Same grid position
                return True  # Hit itself
        
        return False  # No collision
    
    def draw(self, surface):
        """Draw the snake on the screen using rounded rectangles."""
        for i, segment in enumerate(self.body):  # Loop through each body segment
            # Convert grid coordinates to pixel coordinates
            pixel_x = segment[0] * GRID_SIZE  # Multiply by grid size
            pixel_y = segment[1] * GRID_SIZE  # Multiply by grid size
            
            # Create rectangle for this segment
            rect = pygame.Rect(pixel_x, pixel_y, GRID_SIZE, GRID_SIZE)
            
            # Draw rounded rectangle (head slightly brighter, body standard green)
            # Parameters: surface, color, rect, border_radius (rounded corners)
            if i == 0:  # Head segment
                # Head: bright neon green, slightly larger rounded corners
                pygame.draw.rect(surface, NEON_GREEN, rect, border_radius=5)
            else:  # Body segments
                # Body: same green, standard rounded corners
                pygame.draw.rect(surface, NEON_GREEN, rect, border_radius=3)


class Food:
    """Food class that manages food position and appearance."""
    
    def __init__(self, snake_body):
        """Initialize food at a random position, avoiding snake body."""
        # Generate food position that doesn't overlap with snake
        self.position = self.generate_position(snake_body)
    
    def generate_position(self, snake_body):
        """Generate random food position that doesn't overlap with snake."""
        while True:  # Keep trying until we find valid position
            # Random grid coordinates within boundaries
            x = random.randint(0, GRID_WIDTH - 1)  # Random X (0 to GRID_WIDTH-1)
            y = random.randint(0, GRID_HEIGHT - 1)  # Random Y (0 to GRID_HEIGHT-1)
            
            # Check if position overlaps with snake body
            valid = True  # Assume valid initially
            for segment in snake_body:  # Check each snake segment
                if x == segment[0] and y == segment[1]:  # Overlaps with snake
                    valid = False  # Position is invalid
                    break
            
            if valid:  # Found valid position
                return [x, y]  # Return grid coordinates
    
    def draw(self, surface):
        """Draw food on the screen as a rounded rectangle."""
        # Convert grid coordinates to pixel coordinates
        pixel_x = self.position[0] * GRID_SIZE  # Multiply by grid size
        pixel_y = self.position[1] * GRID_SIZE  # Multiply by grid size
        
        # Create rectangle for food
        rect = pygame.Rect(pixel_x, pixel_y, GRID_SIZE, GRID_SIZE)
        
        # Draw rounded rectangle (red food with rounded corners)
        pygame.draw.rect(surface, RED, rect, border_radius=8)


def check_food_collision(snake, food):
    """Check if snake head is on same grid cell as food. Returns True if collision."""
    head_x, head_y = snake.body[0]  # Get snake head position
    food_x, food_y = food.position  # Get food position
    
    # Check if head and food are on same grid cell
    if head_x == food_x and head_y == food_y:
        return True  # Snake ate the food
    return False  # No collision


def draw_score(score):
    """Draw the score in the top-left corner of the screen."""
    # Create text surface with score
    score_text = font.render(f"Score: {score}", True, WHITE)  # White text
    screen.blit(score_text, (10, 10))  # Draw at position (10, 10) from top-left


def draw_game_over(score):
    """Draw game over screen with score and restart instructions."""
    # Fill screen with semi-transparent black overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))  # Create overlay surface
    overlay.set_alpha(180)  # Set transparency (0-255, lower = more transparent)
    overlay.fill(BLACK)  # Fill with black
    screen.blit(overlay, (0, 0))  # Draw overlay on screen
    
    # Create and draw "GAME OVER" text
    game_over_text = font.render("GAME OVER", True, WHITE)  # White text
    text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))  # Center horizontally, slightly above center vertically
    screen.blit(game_over_text, text_rect)  # Draw centered text
    
    # Create and draw final score
    score_text = font.render(f"Final Score: {score}", True, NEON_GREEN)  # Green text
    score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))  # Center of screen
    screen.blit(score_text, score_rect)  # Draw centered score
    
    # Create and draw restart instructions
    restart_text = font.render("Press R to Restart | ESC to Quit", True, WHITE)  # White text
    restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))  # Center horizontally, slightly below center
    screen.blit(restart_text, restart_rect)  # Draw centered instructions


def main():
    """Main function that runs the game loop."""
    # Initialize game state
    game_state = PLAYING  # Start in playing state
    score = 0  # Start with zero score
    
    # Create snake object
    snake = Snake()
    
    # Create food object (pass snake body to avoid overlap)
    food = Food(snake.body)
    
    # Main game loop - runs until window is closed
    running = True  # Loop control variable
    while running:
        # Handle all events (keyboard, mouse, window close, etc.)
        for event in pygame.event.get():  # Get all events from event queue
            if event.type == pygame.QUIT:  # User clicked window close button
                running = False  # Exit loop
                break  # Exit event loop
            
            if event.type == pygame.KEYDOWN:  # User pressed a key
                if event.key == pygame.K_ESCAPE:  # ESC key pressed
                    running = False  # Exit game
                    break  # Exit event loop
                
                # Handle arrow key input (only when playing)
                if game_state == PLAYING:  # Only process movement during gameplay
                    if event.key == pygame.K_UP:  # Up arrow
                        snake.change_direction([0, -1])  # Move up (y decreases)
                    elif event.key == pygame.K_DOWN:  # Down arrow
                        snake.change_direction([0, 1])  # Move down (y increases)
                    elif event.key == pygame.K_LEFT:  # Left arrow
                        snake.change_direction([-1, 0])  # Move left (x decreases)
                    elif event.key == pygame.K_RIGHT:  # Right arrow
                        snake.change_direction([1, 0])  # Move right (x increases)
                
                # Handle restart on game over screen
                if event.key == pygame.K_r and game_state == GAME_OVER:  # R key when game over
                    # Reset game state
                    game_state = PLAYING  # Back to playing
                    score = 0  # Reset score
                    snake = Snake()  # Create new snake
                    food = Food(snake.body)  # Create new food
        
        # Update game logic (only when playing)
        if game_state == PLAYING:  # Only update during gameplay
            # Move snake forward one grid cell
            snake.update()  # Add new head in current direction
            
            # Check if snake ate food
            if check_food_collision(snake, food):  # Head on food cell
                snake.grow()  # Snake grows (don't remove tail)
                score += 10  # Increase score by 10
                food = Food(snake.body)  # Create new food at random position
            else:  # Didn't eat food
                snake.shrink()  # Remove tail (keep length constant)
            
            # Check for collisions (walls or self)
            if snake.check_collision():  # Collision detected
                game_state = GAME_OVER  # Change to game over state
        
        # Draw everything on screen
        screen.fill(BLACK)  # Clear screen with black background
        
        # Draw subtle grid lines (optional visual aid)
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):  # Vertical lines
            pygame.draw.line(screen, DARK_GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)  # Thin dark gray line
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):  # Horizontal lines
            pygame.draw.line(screen, DARK_GRAY, (0, y), (WINDOW_WIDTH, y), 1)  # Thin dark gray line
        
        # Draw game elements
        food.draw(screen)  # Draw food on screen
        snake.draw(screen)  # Draw snake on screen
        draw_score(score)  # Draw score in top-left
        
        # Draw game over overlay if needed
        if game_state == GAME_OVER:  # Game has ended
            draw_game_over(score)  # Draw game over screen
        
        # Update display - show everything we drew
        pygame.display.update()  # Refresh the screen (required for changes to be visible)
        
        # Control frame rate - wait until next frame should be displayed
        clock.tick(FPS)  # Limit to FPS frames per second
    
    # Cleanup - game loop has ended
    pygame.quit()  # Uninitialize pygame modules
    sys.exit()  # Exit Python program


# Entry point - run main() when script is executed directly
if __name__ == "__main__":  # Check if this file is being run (not imported)
    main()  # Start the game
