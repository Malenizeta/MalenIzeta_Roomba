import pygame
import concurrent.futures
import os

# Configuración de la pantalla
WIDTH, HEIGHT = 1440, 720
COLS, ROWS = 12, 6
CELL_SIZE = WIDTH // COLS

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Level:
    def __init__(self, player_start, player_end, obstacles, painted_cell_image):
        self.player_start = player_start
        self.player_end = player_end
        self.obstacles = obstacles
        self.painted_cell_image = pygame.image.load(os.path.join("Tiles", painted_cell_image))
        self.painted_cell_image = pygame.transform.scale(self.painted_cell_image, (CELL_SIZE, CELL_SIZE))

        try:
            self.painted_cells = {player_start}
            self.pintura_restante = self.calcular_pintura()
        except pygame.error as e:
            print(f"Error al cargar la imagen de la celda pintada: {e}")
            self.painted_cell_image = None
    
    #Es un cálculo simple y rápido, por lo que no es necesario usar hilos
    #def calcular_pintura(self):
    #   with concurrent.futures.ThreadPoolExecutor() as executor:
    #       total_celdas = ROWS * COLS
    #       obstaculos_celdas = sum(executor.map(len, [obstacle["cells"] for obstacle in self.obstacles]))
    #        return total_celdas - obstaculos_celdas - len(self.painted_cells)
    
    def calcular_pintura(self):
        total_celdas = ROWS * COLS
        obstaculos_celdas = sum(len(obstacle["cells"]) for obstacle in self.obstacles)
        return total_celdas - obstaculos_celdas - len(self.painted_cells)
    
    def cargar_imagenes_obstaculos(self):
        obstacle_images = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_obstacle = {
                executor.submit(self.procesar_obstaculo, obstacle): obstacle for obstacle in self.obstacles
            }
            for future in concurrent.futures.as_completed(future_to_obstacle):
                result = future.result()
                if result:
                    obstacle_images.append(result)
        return obstacle_images

    def procesar_obstaculo(self, obstacle):
        obstacle_cells = list(obstacle["cells"])
        min_row, max_row = min(c[0] for c in obstacle_cells), max(c[0] for c in obstacle_cells)
        min_col, max_col = min(c[1] for c in obstacle_cells), max(c[1] for c in obstacle_cells)
        obstacle_rect = pygame.Rect(min_col * CELL_SIZE, min_row * CELL_SIZE, (max_col - min_col + 1) * CELL_SIZE, (max_row - min_row + 1) * CELL_SIZE)
        
        try:
            image_path = os.path.join("Tiles", obstacle["image"])
            image = pygame.image.load(image_path)
            image = pygame.transform.scale(image, (obstacle_rect.width, obstacle_rect.height))
        except pygame.error as e:
            print(f"Error al cargar la imagen del obstáculo {obstacle['image']}: {e}")
            image = None
        return (image, obstacle_rect)

class Game:
    def __init__(self, levels):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.font = pygame.font.Font("Royale.ttf", 18)
        self.levels = levels
        self.current_level_index = 0
        self.load_level()

    def load_level(self):
        self.level = self.levels[self.current_level_index]
        self.obstacle_images = self.level.cargar_imagenes_obstaculos()
        self.player_pos = list(self.level.player_start)  
        self.level.painted_cells = {self.level.player_start: 3} 
        self.level.pintura_restante = self.level.calcular_pintura()   
    
    def draw_grid(self):
        for row in range(ROWS):
            for col in range(COLS):
                rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if (row, col) in self.level.painted_cells:
                    self.screen.blit(self.level.painted_cell_image, rect)
                elif any((row, col) in obstacle["cells"] for obstacle in self.level.obstacles):
                    pygame.draw.rect(self.screen, BLACK, rect)
                elif (row, col) == self.level.player_end:
                    pygame.draw.rect(self.screen, BLACK, rect)
        for img, rect in self.obstacle_images:
            self.screen.blit(img, rect)
      
    def reset_level(self):
        self.player_pos = list(self.level.player_start)
        self.level.painted_cells = {self.level.player_start: 3}
        self.level.pintura_restante = self.level.calcular_pintura()
        print("Nivel reiniciado")
    
    def next_level(self):
        self.current_level_index += 1
        if self.current_level_index < len(self.levels):
            self.load_level()
        else:
            print("¡Juego completado!")
            pygame.quit()
            exit()

    def move_player(self, event):
        new_pos = self.player_pos[:]
        if event.key == pygame.K_UP:
            new_pos[0] -= 1
        elif event.key == pygame.K_DOWN:
            new_pos[0] += 1
        elif event.key == pygame.K_LEFT:
            new_pos[1] -= 1
        elif event.key == pygame.K_RIGHT:
            new_pos[1] += 1
        
        if (0 <= new_pos[0] < ROWS and 0 <= new_pos[1] < COLS and tuple(new_pos) not in [cell for obs in self.level.obstacles for cell in obs["cells"]]):
            if tuple(new_pos) in self.level.painted_cells:
                self.reset_level()
            else:
                self.level.pintura_restante -= 1
                self.level.painted_cells[tuple(new_pos)] = 1
                self.player_pos = new_pos
        if self.level.pintura_restante <= 0 and tuple(self.player_pos) == self.level.player_end:
             self.next_level()

    def run(self):
        running = True
        while running:
            self.screen.fill(WHITE)
            self.draw_grid()
            pygame.draw.rect(self.screen, BLACK, (self.player_pos[1] * CELL_SIZE, self.player_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.move_player(event)
        pygame.quit()
    
   
if __name__ == "__main__":
    levels = [
        Level(
            (0, 0), (5, 10), 
            [
                {"cells": {(2, 3), (2, 4), (2, 5), (3, 3), (3, 4), (3, 5)}, "image": "obstacle1.jpg"},
                {"cells": {(1, 7), (1, 8), (2, 7), (2, 8)}, "image": "obstacle2.jpg"},
                {"cells": {(0, 10), (0, 11), (1, 10), (1, 11), (2, 10), (2, 11)}, "image": "obstacle3.jpg"},
                {"cells": {(3, 0), (3, 1), (4, 0), (4, 1), (5, 0), (5, 1)}, "image": "obstacle3.jpg"}
            ], 
            "Tile1.jpg"
        ),
        Level(
            (2, 4), (1, 10), 
            [ 
                {"cells": {(1, 2), (2, 2), (3, 2), (4, 2),(1, 3), (2, 3), (3, 3), (4, 3),}, "image": "obstacle5.jpg"},
                {"cells": {(2, 6), (3, 6)}, "image": "obstacle6.jpg"},
                {"cells": {(3, 9), (3, 10), (4, 9), (4, 10)}, "image": "obstacle7.jpg"}
            ], 
            "Tile2.jpg"
        ),
        Level(
            (0, 0), (0, 9), 
            [
                {"cells": {(2, 3), (2, 4), (3,3), (3,4), (4,3), (4,4), (5,3), (5,4) }, "image": "obstacle8.jpg"},
                {"cells": {(2, 9), (2, 10), (3,9), (3,10), (4,9), (4,10)}, "image": "obstacle9.jpg"},
                {"cells": {(0,7), (0,8), (1,7), (1,8)}, "image": "obstacle10.jpg"}
                
            ], 
            "Tile3.jpg"
        ),
        Level(
            (0, 0), (0, 11), 
            [
                {"cells": {(5, 4), (5, 5)}, "image": "obstacle3.jpg"},
                {"cells": {(4, 6), (4, 7), (5,6), (5,7)}, "image": "obstacle3.jpg"},
                {"cells": {(3, 8), (3, 9), (4,8), (4,9), (5,8), (5,9)}, "image": "obstacle3.jpg"},
                {"cells": {(2, 10), (2, 11), (3,10), (3,11), (4,10), (4,11), (5,10), (5,11)}, "image": "obstacle3.jpg"},
                
                {"cells": {(2, 4)}, "image": "obstacle3.jpg"},
                {"cells": {(1,7)}, "image": "obstacle3.jpg"},
                {"cells": {(0, 9)}, "image": "obstacle3.jpg"},
                
            ], 
            "Tile1.jpg")
    ]
    Game(levels).run()
