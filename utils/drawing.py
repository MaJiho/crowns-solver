import pygame

from board.board import Board


def draw_board_with_pygame(board: Board, cell_size=50):
    """
    Draws the board using Pygame.
    :param board: Board object with cell information.
    :param cell_size: Size of each cell in pixels.
    """
    pygame.init()

    # Determine screen dimensions based on board size
    grid_size = len(board.cells)
    screen_width = grid_size * cell_size
    screen_height = grid_size * cell_size

    # Set up the display
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Crowns Board")

    # Initialize font for symbols
    pygame.font.init()
    font = pygame.font.Font(None, cell_size // 2)  # Adjust font size to cell size

    # Game loop
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw the board
        screen.fill((255, 255, 255))  # White background
        for row_index, row in enumerate(board.cells):
            for col_index, cell in enumerate(row):
                # Draw cell background using cell.color
                pygame.draw.rect(
                    screen,
                    cell.color,  # Cell background color
                    pygame.Rect(col_index * cell_size, row_index * cell_size, cell_size, cell_size),
                )

                # Draw default black border
                pygame.draw.rect(
                    screen,
                    (0, 0, 0),  # Black border
                    pygame.Rect(col_index * cell_size, row_index * cell_size, cell_size, cell_size),
                    1,
                )

                # Define neighbors and their respective line start/end points
                neighbors = {
                    "top": ((col_index * cell_size, row_index * cell_size),
                            (col_index * cell_size + cell_size, row_index * cell_size)),
                    "left": ((col_index * cell_size, row_index * cell_size),
                             (col_index * cell_size, row_index * cell_size + cell_size)),
                    "right": ((col_index * cell_size + cell_size, row_index * cell_size),
                              (col_index * cell_size + cell_size, row_index * cell_size + cell_size)),
                    "bottom": ((col_index * cell_size, row_index * cell_size + cell_size),
                               (col_index * cell_size + cell_size, row_index * cell_size + cell_size)),
                }

                # Check neighbors and draw thick borders where colors differ
                for direction, (start, end) in neighbors.items():
                    neighbor = None
                    if direction == "top" and row_index > 0:
                        neighbor = board.cells[row_index - 1][col_index]
                    elif direction == "left" and col_index > 0:
                        neighbor = board.cells[row_index][col_index - 1]
                    elif direction == "right" and col_index < len(row) - 1:
                        neighbor = board.cells[row_index][col_index + 1]
                    elif direction == "bottom" and row_index < len(board.cells) - 1:
                        neighbor = board.cells[row_index + 1][col_index]

                    if neighbor and neighbor.color != cell.color:  # Different area detected
                        pygame.draw.line(screen, (0, 0, 0), start, end, 4)  # Thicker border

                # Draw symbols based on cell state
                symbol = ""
                if cell.is_cross():
                    symbol = "X"
                elif cell.is_crown():
                    symbol = "C"

                if symbol:
                    # Render symbol text
                    text_surface = font.render(symbol, True, (0, 0, 0))  # Black text
                    text_rect = text_surface.get_rect(
                        center=(
                            col_index * cell_size + cell_size // 2,
                            row_index * cell_size + cell_size // 2,
                        )
                    )
                    screen.blit(text_surface, text_rect)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
