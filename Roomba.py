import pygame
import concurrent.futures

#Creación de la ventana
WIDTH, HEIGHT = 500, 500  
ROWS, COLS = 10, 10  
CELL_SIZE = WIDTH // COLS 

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


obstacles = {
    (2, 2), (2, 3), (3, 2),
    (5, 7), (6, 7), (6, 8),
    (7, 3), (8, 3), (8, 4), (8, 5),
    (4, 6), (4, 7), (5, 6)
}

def calcular_area_disponible(rows, cols, obstacles):
    #Calcula el área total disponible para pintar con 3 vidas adicionales
    return (rows * cols - len(obstacles)) + 3

def draw_grid(screen):
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect)  # Dibujo la celda en blanco
            pygame.draw.rect(screen, BLACK, rect, 1)  # Dibujo el borde de la celda en blanco
            if (row, col) in obstacles:
                pygame.draw.rect(screen, BLACK, rect)  # Dibujo los obstáculos en negro
            

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
  
    
    # Calculo el área total disponible usando concurrencia
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_area = executor.submit(calcular_area_disponible, ROWS, COLS, obstacles)
        pintura_restante = future_area.result()
    
    running = True
    while running:
        screen.fill(WHITE)
        draw_grid(screen)
        pygame.display.flip()
       
    
    pygame.quit()

if __name__ == "__main__":
    main()