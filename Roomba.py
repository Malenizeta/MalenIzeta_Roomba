import pygame
import concurrent.futures

#Creación de la ventana
WIDTH, HEIGHT = 500, 250  
COLS, ROWS = 10, 5
CELL_SIZE = WIDTH // COLS 

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

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
    areas={}
   
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
    cantidad_pintura = sum(areas.values())+3
    print(f"\nCantidad de pintura total: {cantidad_pintura} cm²")

    running = True
    while running:
        screen.fill(WHITE)
        draw_grid(screen)
        pygame.display.flip()
       
    
    pygame.quit()

if __name__ == "__main__":
    main()