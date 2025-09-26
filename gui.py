import pygame
import random

class MazeGUI:
    def __init__(self, maze, kb):
        pygame.init()
        self.maze = maze
        self.kb = kb
        self.cell_size = 50
        self.cols = len(maze[0])
        self.rows = len(maze)
        free_cells = [(r, c) for r in range(self.rows)
                      for c in range(self.cols) if maze[r][c] == 0]
        self.true_pos = random.choice(free_cells)

        width = self.cols * self.cell_size
        height = self.rows * self.cell_size
        self.screen = pygame.display.set_mode((width * 2, height))
        pygame.display.set_caption('Maze Localization')
        self.font = pygame.font.SysFont(None, 24)

    def run(self):
        clock = pygame.time.Clock()
        steps = 0
        running = True
        while running and steps < 10:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    action = None
                    if event.key in (pygame.K_w, pygame.K_UP):
                        action = 'N'
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        action = 'S'
                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        action = 'E'
                    elif event.key in (pygame.K_a, pygame.K_LEFT):
                        action = 'W'
                    if action:
                        move = self._move_true(action)
                        percept = self._sense_actual(self.true_pos)
                        if move :
                            self.kb.add_observation(action, percept)
                        else :
                            self.kb.add_observation('O', percept)
                        steps += 1
            self._draw()
            pygame.display.flip()
            clock.tick(10)
        self._reveal_true_location()
        pygame.time.wait(2000)
        pygame.quit()

    def _move_true(self, action):
        dr, dc = {'N':(-1,0), 'S':(1,0), 'E':(0,1), 'W':(0,-1)}[action]
        r, c = self.true_pos
        nr, nc = r + dr, c + dc
        if 0 <= nr < self.rows and 0 <= nc < self.cols and self.maze[nr][nc] == 0:
            self.true_pos = (nr, nc)
            return True
        else : 
            return False

    def _sense_actual(self, pos):
        r, c = pos
        bits = []
        for dr, dc in [(-1,0),(1,0),(0,1),(0,-1)]:
            nr, nc = r+dr, c+dc
            bits.append('1' if (nr < 0 or nr >= self.rows or nc < 0 or nc >= self.cols or self.maze[nr][nc] == 1)
                        else '0')
        return ''.join(bits)

    def _draw(self):
        self.screen.fill((50,50,50))
        for r in range(self.rows):
            for c in range(self.cols):
                x = c * self.cell_size
                y = r * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                if self.maze[r][c] == 1:
                    color = (0,0,0)
                elif (r, c) in self.kb.belief:
                    color = (0,200,0)
                else:
                    color = (200,200,200)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (100,100,100), rect, 1)
        offset_x = self.cols * self.cell_size
        y = 10
        for action, percept in self.kb.history:
            text = f"{action}: {percept}"
            img = self.font.render(text, True, (255,255,255))
            self.screen.blit(img, (offset_x + 10, y))
            y += 25

    def _reveal_true_location(self):
        x = self.true_pos[1] * self.cell_size
        y = self.true_pos[0] * self.cell_size
        rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
        pygame.draw.rect(self.screen, (0,0,255), rect)
        pygame.display.flip()