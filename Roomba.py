import pygame
import concurrent.futures
import os

# Creación de la ventana
WIDTH, HEIGHT = 1440, 720  
COLS, ROWS = 10, 5
CELL_SIZE = WIDTH // COLS 

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


player_fin = (ROWS - 1, COLS - 1)
painted_cells = {}

zonas = {
    'Zona 1': (3, 5),
    'Zona 2': (7, 2),
    'Zona 3': (1, 7),
    'Zona 4': (2, 4)
 }

obstacles = {
    (2,3), (2,4), (2,5), (3,3), (3,4), (3,5)
}

def calcular_area(filas,columnas):
    return filas*columnas

            
def draw_grid(screen):
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if (row, col) in painted_cells:
                pygame.draw.rect(screen, BLUE, rect)
            elif (row, col) in obstacles:
                pygame.draw.rect(screen, BLACK, rect)
            elif (row, col) == player_fin:
                pygame.draw.rect(screen, RED, rect)
            pygame.draw.rect(screen, WHITE, rect, 1)

def draw_text(screen, text, position, font, color=BLACK):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def main():
    player_pos = [0, 0]
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    areas = {}
    font_path = os.path.join(os.path.dirname(__file__), "Royale.ttf")
    font = pygame.font.Font(font_path, 18)
    painted_cells[0,0] = 3
   
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Asignamos cada cálculo a un hilo
        future_to_zona = {
            executor.submit(calcular_area, filas, columnas): zona
            for zona, (filas, columnas) in zonas.items()
        }
        
        # Recogemos los resultados a medida que se van completando
        for future in concurrent.futures.as_completed(future_to_zona):
            zona = future_to_zona[future]
            try:
                area = future.result()
            except Exception as exc:
                print(f"{zona} generó una excepción: {exc}")
            else:
                areas[zona] = area
                print(f"{zona}: {area} cm²")
            
    # Calcular la superficie total sumando las áreas parciales
    pintura_restante = sum(areas.values()) + 2
    print(f"\nCantidad de pintura total: {pintura_restante} cm²")

    running = True
    while running:
        screen.fill(WHITE)
        draw_grid(screen)
        pygame.draw.rect(screen, GREEN, (player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
         # Mostrar la cantidad de pintura restante y las celdas que quedan por pintar
        celdas_restantes = sum(areas.values()) - len(painted_cells)
        draw_text(screen, f"PINTURA RESTANTE: {pintura_restante}", (10, 10), font)
        draw_text(screen, f"CELDAS RESTANTES: {celdas_restantes}", (10, 50), font)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                new_pos = player_pos[:]
                if event.key == pygame.K_UP:
                    new_pos[0] -= 1
                elif event.key == pygame.K_DOWN:
                    new_pos[0] += 1
                elif event.key == pygame.K_LEFT:
                    new_pos[1] -= 1
                elif event.key == pygame.K_RIGHT:
                    new_pos[1] += 1
               
                # Verifico si la nueva posición es válida
                if (0 <= new_pos[0] < ROWS and 0 <= new_pos[1] < COLS and tuple(new_pos) not in obstacles):
                    
                    pintura_restante -= 1  # Restar pintura disponible
                    painted_cells[tuple(new_pos)] = 3
                    player_pos = new_pos  # Mover al jugador
               
        # Verificar si la pintura se ha agotado
        if pintura_restante <= 0:
            print("¡Se ha acabado la pintura! Fin del juego.")
            running = False

        if len(painted_cells) == (ROWS * COLS - len(obstacles)) and tuple(player_pos) == player_fin:
            print("¡Has cubierto toda el área y llegaste al destino! Ganaste!")
            running = False
           
    pygame.quit()

if __name__ == "__main__":
    main()

    