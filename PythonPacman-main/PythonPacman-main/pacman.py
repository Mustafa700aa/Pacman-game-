import pygame
import sys
import random
import heapq

pygame.init()

WINDOW_SIZE = 800
GRID_SIZE = 20
CELL_SIZE = WINDOW_SIZE // GRID_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Pac-Man with A* and Static Path Ghosts")
class PacMan:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.score = 0

    def move(self, direction):
        if direction == 'UP':
            self.y -= 1
        elif direction == 'DOWN':
            self.y += 1
        elif direction == 'LEFT':
            self.x -= 1
        elif direction == 'RIGHT':
            self.x += 1
class Ghost:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.path = []

    def move(self, target, walls):
        if self.path:
            next_move = self.path[0]
            self.x, self.y = next_move
            self.path = self.path[1:]
        else:
            self.path = a_star((self.x, self.y), target, walls)


def a_star(start, goal, walls):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_list = []
    heapq.heappush(open_list, (0 + heuristic(start, goal), 0, start))
    came_from = {}
    cost_so_far = {start: 0}

    while open_list:
        _, current_cost, current = heapq.heappop(open_list)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < GRID_SIZE and 0 <= neighbor[1] < GRID_SIZE and neighbor not in walls:
                new_cost = current_cost + 1
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + heuristic(neighbor, goal)
                    heapq.heappush(open_list, (priority, new_cost, neighbor))
                    came_from[neighbor] = current

    return []
class Game:
    def __init__(self):
        self.setup_new_game()

    def setup_new_game(self):
        self.pacman = PacMan(10, 10)
        self.walls = self.create_walls(self.pacman.x, self.pacman.y)
        self.dots = self.generate_dots(50)
        self.ghosts = self.create_ghosts()
        self.path_to_dot = None
        self.pacman.path = []

    def create_ghosts(self):
        ghosts = [Ghost(5, 5), Ghost(15, 15), Ghost(7, 7)]
        return ghosts

    def move_pacman(self):
        if self.path_to_dot:
            next_step = self.path_to_dot[0]
            self.pacman.x, self.pacman.y = next_step[0], next_step[1]
            self.path_to_dot = self.path_to_dot[1:]

    def update(self):
        if len(self.dots) > 0:
            nearest_dot = self.find_nearest_dot()
            self.path_to_dot = a_star((self.pacman.x, self.pacman.y), nearest_dot, self.walls)

        self.move_pacman()

    def find_nearest_dot(self):
        closest_dot = None
        min_distance = float('inf')
        for dot in self.dots:
            distance = abs(self.pacman.x - dot[0]) + abs(self.pacman.y - dot[1])
            if distance < min_distance:
                closest_dot = dot
                min_distance = distance
        return closest_dot

    def generate_dots(self, count):
        dots = []
        while len(dots) < count:
            dot = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            if dot not in self.walls and dot != (self.pacman.x, self.pacman.y) and dot not in dots:
                dots.append(dot)
        return dots

    def create_walls(self, pacman_x, pacman_y):
        walls = set()
        for _ in range(50):
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if (x, y) != (pacman_x, pacman_y):
                walls.add((x, y))
        return walls

    def check_dot_collision(self):
        for dot in self.dots[:]:
            if (self.pacman.x, self.pacman.y) == dot:
                self.dots.remove(dot)
                self.pacman.score += 10
                return True
        return False

    def check_game_over(self):
        if (self.pacman.x, self.pacman.y) in [(ghost.x, ghost.y) for ghost in self.ghosts]:
            return "lose"
        if len(self.dots) == 0:
            return "win"
        return None

    def move_ghosts(self):
        for ghost in self.ghosts:
            ghost.move((self.pacman.x, self.pacman.y), self.walls)

    def draw_grid(self):
        for x in range(0, WINDOW_SIZE, CELL_SIZE):
            for y in range(0, WINDOW_SIZE, CELL_SIZE):
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, WHITE, rect, 1)

    def draw_pacman(self):
        pygame.draw.circle(screen, RED,
                           (self.pacman.x * CELL_SIZE + CELL_SIZE // 2, self.pacman.y * CELL_SIZE + CELL_SIZE // 2),
                           CELL_SIZE // 2 - 2)

    def draw_ghosts(self):
        for ghost in self.ghosts:
            pygame.draw.circle(screen, BLUE,
                               (ghost.x * CELL_SIZE + CELL_SIZE // 2, ghost.y * CELL_SIZE + CELL_SIZE // 2),
                               CELL_SIZE // 2 - 2)

    def draw_walls(self):
        for wall in self.walls:
            rect = pygame.Rect(wall[0] * CELL_SIZE, wall[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLUE, rect)

    def draw_dots(self):
        for dot in self.dots:
            pygame.draw.circle(screen, GREEN,
                               (dot[0] * CELL_SIZE + CELL_SIZE // 2, dot[1] * CELL_SIZE + CELL_SIZE // 2), 5)

    def show_start_screen(self):
        font = pygame.font.Font(None, 30)
        title_text = font.render("Pac-Man Game", True, YELLOW)
        question_text = font.render("Do you want to start the game? (Press Y for Yes or N for No)", True, YELLOW)

        screen.fill(BLACK)
        screen.blit(title_text, (WINDOW_SIZE // 3, WINDOW_SIZE // 3 - 80))
        screen.blit(question_text, (100, WINDOW_SIZE // 2 - 40))

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        waiting = False
                    elif event.key == pygame.K_n:
                        pygame.quit()
                        sys.exit()

    def show_invalid_input(self, message):
        font = pygame.font.Font(None, 40)
        text = font.render(message, True, RED)
        screen.fill(BLACK)
        screen.blit(text, (100, WINDOW_SIZE // 2 + 20))
        pygame.display.flip()
        pygame.time.wait(10000)

    def show_end_screen(self):
        font = pygame.font.Font(None, 50)
        result_text = "You Win!" if len(self.dots) == 0 else "Game Over"
        result = font.render(result_text, True, GREEN if len(self.dots) == 0 else RED)
        text_continue = font.render("Press R to Replay or Q to Quit", True, YELLOW)

        screen.fill(BLACK)
        screen.blit(result, (WINDOW_SIZE // 3, WINDOW_SIZE // 2 - 50))
        screen.blit(text_continue, (WINDOW_SIZE // 4, WINDOW_SIZE // 2 + 20))
        pygame.display.flip()

        pygame.time.wait(1000)

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.setup_new_game()
                        waiting = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

    def main(self):
        self.show_start_screen()
        clock = pygame.time.Clock()
        running = True

        while running:
            screen.fill(BLACK)
            self.draw_grid()
            self.draw_pacman()
            self.draw_ghosts()
            self.draw_walls()
            self.draw_dots()

            self.update()

            self.check_dot_collision()

            result = self.check_game_over()
            if result:
                self.show_end_screen()
                running = False

            self.move_ghosts()

            pygame.display.flip()
            clock.tick(15)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.main()
