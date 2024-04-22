# Six Men Morris | Alpha-Beta Pruning
# Jhan Kyle V. Agullo
# BSCS 3B-M

import pygame
import sys
import random

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MARGIN = 100
INNER_MARGIN = 2 * MARGIN
POINT_RADIUS = 10
PIECE_RADIUS = 10
BOARD_COLOR = (255, 255, 255)
POINT_COLOR = (255, 255, 255)
PLAYER_COLOR = (0, 0, 255)
AI_COLOR = (255, 0, 0)
FONT_SIZE = 36
background_image = pygame.image.load("background.png")

class Game:
    def __init__(self):
        self.board_state = [0] * 16
        self.player_pieces_left = 6
        self.ai_pieces_left = 6
        self.remove_mode = False
        self.invalid_mills = []
        self.valid_again_mills = []
        self.current_player = 1
        self.selected_piece = None

    def handle_replay_button(self, pos):
        replay_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2, 100, 50)
        if replay_button_rect.collidepoint(pos):
            self.__init__()
            return True
        return False

    def handle_exit_button(self, pos):
        exit_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 + 60, 100, 50)
        if exit_button_rect.collidepoint(pos):
            pygame.quit()
            sys.exit()

    def check_for_win(self):
        if self.player_pieces_left == 0 and self.ai_pieces_left == 0:
            if sum(p == 1 for p in self.board_state) <= 2:
                return 2
            elif sum(p == 2 for p in self.board_state) <= 2:
                return 1

        # Check for a winner during the movement phase
        if self.player_pieces_left == 0:
            if sum(p == 1 for p in self.board_state) <= 2:
                return 2
        if self.ai_pieces_left == 0:
            if sum(p == 2 for p in self.board_state) <= 2:
                return 1

        return 0

    def is_valid_move(self, point, player):
        if self.board_state[point] != 0:
            return False

        if self.player_pieces_left > 0 and self.ai_pieces_left > 0:
            return True


        if (player == 1 and sum(p == 1 for p in self.board_state) == 3) or \
                (player == 2 and sum(p == 2 for p in self.board_state) == 3):
            return True

        if self.selected_piece is not None and point in self.get_adjacent_points(self.selected_piece):
            return True

        return False

    def get_adjacent_points(self, point):
        adjacency_list = [
            [1, 6],
            [0, 2, 4],
            [1, 9],
            [4, 7],
            [1, 3, 5],
            [4, 8],
            [0, 7, 13],
            [3, 6, 10],
            [5, 9, 12],
            [2, 8, 15],
            [7, 11],
            [10, 12, 14],
            [8, 11],
            [6, 14],
            [11, 13, 15],
            [9, 14]
        ]
        return adjacency_list[point]


    def check_for_mill(self, point, player):
        mill_combinations = [
            [0, 1, 2], [13, 14, 15],
            [0, 6, 13], [2, 9, 15],
            [3, 4, 5], [10, 11, 12],
            [3, 7, 10], [5, 8, 12],
        ]

        for mill in mill_combinations:
            if all(self.board_state[i] == player for i in mill):
                if mill not in self.invalid_mills or mill in self.valid_again_mills:
                    print("A mill has been formed!")
                    self.remove_opponent_piece(player, None)
                    if mill in self.valid_again_mills:
                        self.valid_again_mills.remove(mill)
                    self.invalid_mills.append(mill)
                    return True

        return False

    def is_part_of_mill(self, point, player):
        mill_combinations = [
            [0, 1, 2], [13, 14, 15],
            [0, 6, 13], [2, 9, 15],
            [3, 4, 5], [10, 11, 12],
            [3, 7, 10], [5, 8, 12],
        ]

        for mill in mill_combinations:
            if point in mill and all(self.board_state[i] == player for i in mill):
                return True

        return False

    def remove_opponent_piece(self, player, point_to_remove=None):
        opponent = 2 if player == 1 else 1

        opponent_pieces = [i for i, x in enumerate(self.board_state) if x == opponent]

        if opponent_pieces:
            if point_to_remove in opponent_pieces:
                if self.is_part_of_mill(point_to_remove, opponent):
                    if any(not self.is_part_of_mill(i, opponent) for i in opponent_pieces):
                        if self.player_pieces_left == 0 and self.ai_pieces_left == 0:
                            print(
                                "Cannot remove a piece that is part of a mill. There are other pieces not part of a mill.")
                            return False
                    self.board_state[point_to_remove] = 0
                    if player == 1:
                        print(f"Player has formed a mill and removed a piece from AI at point {point_to_remove}!")
                    else:
                        print(f"AI has formed a mill and removed a piece from player at point {point_to_remove}!")
                    self.remove_mode = False
                    return True
                else:
                    self.board_state[point_to_remove] = 0
                    if player == 1:
                        print(f"Player has formed a mill and removed a piece from AI at point {point_to_remove}!")
                    else:
                        print(f"AI has formed a mill and removed a piece from player at point {point_to_remove}!")
                    self.remove_mode = False
                    return True
            else:
                print("Invalid point to remove. No piece of the opponent at this point.")
        else:
            print("No opponent pieces left to remove.")
        return False

    def handle_player_move(self, x, y):
        point = self.get_clicked_point(x, y)
        if point is not None:
            if self.remove_mode:
                if self.board_state[point] == 2:
                    if not self.remove_opponent_piece(1, point):
                        self.current_player = 2
                    return True
            elif self.player_pieces_left > 0:
                if self.board_state[point] == 0:
                    self.board_state[point] = 1
                    self.player_pieces_left -= 1
                    print(f"Player has placed a piece at point {point}")
                    if self.check_for_mill(point, 1):
                        print("Player has formed a mill!")
                        self.remove_mode = True
                    if not self.remove_mode:
                        self.current_player = 2
                    return True
            elif self.selected_piece is None:
                if self.board_state[point] == 1:
                    self.selected_piece = point
            else:
                if self.is_valid_move(point, 1):
                    original_position = self.selected_piece
                    self.board_state[self.selected_piece] = 0
                    for mill in self.invalid_mills:
                        if original_position in mill and mill not in self.valid_again_mills:
                            self.valid_again_mills.append(mill)
                    self.board_state[point] = 1
                    print(f"Player has moved a piece from point {original_position} to point {point}")
                    if self.check_for_mill(point, 1):
                        print("Player has formed a mill!")
                        self.remove_mode = True
                    if not self.remove_mode:
                        self.current_player = 2
                    self.selected_piece = None
                    return True
        winner = self.check_for_win()
        if winner == 1:
            print("Player wins!")
        elif winner == 2:
            print("AI wins!")
        return False

    def handle_ai_move(self):
        if self.ai_pieces_left > 0:
            empty_points = [i for i, x in enumerate(self.board_state) if x == 0]
            if empty_points:
                best_score = float('-inf')
                best_move = None
                for point in empty_points:
                    self.board_state[point] = 2
                    self.ai_pieces_left -= 1
                    score = self.minimax(5, float('-inf'), float('inf'), False)
                    self.board_state[point] = 0
                    self.ai_pieces_left += 1
                    if score > best_score:
                        best_score = score
                        best_move = point
                self.board_state[best_move] = 2
                self.ai_pieces_left -= 1
                print(f"AI has placed a piece at point {best_move}")
                if self.check_for_mill(best_move, 2):
                    print("AI has formed a mill!")
                    opponent_pieces = [i for i, x in enumerate(self.board_state) if x == 1]
                    if opponent_pieces:
                        point_to_remove = random.choice(opponent_pieces)
                        self.remove_opponent_piece(2, point_to_remove)
                self.current_player = 1
        else:
            ai_pieces = [i for i, x in enumerate(self.board_state) if x == 2]
            if ai_pieces:
                best_score = float('-inf')
                best_move = None
                for selected_piece in ai_pieces:
                    adjacent_points = self.get_adjacent_points(selected_piece)
                    valid_moves = [point for point in adjacent_points if self.board_state[point] == 0]
                    for point in valid_moves:
                        original_position = selected_piece
                        self.board_state[selected_piece] = 0
                        self.board_state[point] = 2
                        score = self.minimax(5, float('-inf'), float('inf'), False)
                        self.board_state[selected_piece] = 2
                        self.board_state[point] = 0
                        if score > best_score:
                            best_score = score
                            best_move = (selected_piece, point)
                if best_move:
                    self.board_state[best_move[0]] = 0
                    self.board_state[best_move[1]] = 2
                    print(f"AI has moved a piece from point {best_move[0]} to point {best_move[1]}")
                    if self.check_for_mill(best_move[1], 2):
                        print("AI has formed a mill!")
                        opponent_pieces = [i for i, x in enumerate(self.board_state) if x == 1]
                        if opponent_pieces:
                            point_to_remove = random.choice(opponent_pieces)
                            self.remove_opponent_piece(2, point_to_remove)
                    self.current_player = 1
                else:
                    print("No valid moves for AI, player wins!")
                    return
        winner = self.check_for_win()
        if winner == 1:
            print("Player wins!")
        elif winner == 2:
            print("AI wins!")

    def get_clicked_point(self, x, y):
        points = [
            (MARGIN, MARGIN), (WINDOW_WIDTH // 2, MARGIN), (WINDOW_WIDTH - MARGIN, MARGIN),
            (INNER_MARGIN, INNER_MARGIN), (WINDOW_WIDTH // 2, INNER_MARGIN),
            (WINDOW_WIDTH - INNER_MARGIN, INNER_MARGIN),
            (MARGIN, WINDOW_HEIGHT // 2), (INNER_MARGIN, WINDOW_HEIGHT // 2),
            (WINDOW_WIDTH - INNER_MARGIN, WINDOW_HEIGHT // 2),
            (WINDOW_WIDTH - MARGIN, WINDOW_HEIGHT // 2),
            (INNER_MARGIN, WINDOW_HEIGHT - INNER_MARGIN), (WINDOW_WIDTH // 2, WINDOW_HEIGHT - INNER_MARGIN),
            (WINDOW_WIDTH - INNER_MARGIN, WINDOW_HEIGHT - INNER_MARGIN),
            (MARGIN, WINDOW_HEIGHT - MARGIN), (WINDOW_WIDTH // 2, WINDOW_HEIGHT - MARGIN),
            (WINDOW_WIDTH - MARGIN, WINDOW_HEIGHT - MARGIN)
        ]

        for i, point in enumerate(points):
            if (x - point[0]) ** 2 + (y - point[1]) ** 2 <= POINT_RADIUS ** 2:
                return i

        return None

    # ====== AI MINIMAX ALPHA BETA PRUNING ======

    def evaluate_state(self):
        player_pieces = sum(p == 1 for p in self.board_state)
        ai_pieces = sum(p == 2 for p in self.board_state)

        player_mills = sum(self.is_part_of_mill(i, 1) for i in range(16))
        ai_mills = sum(self.is_part_of_mill(i, 2) for i in range(16))

        player_moves = len(self.get_possible_moves(1))
        ai_moves = len(self.get_possible_moves(2))

        ai_score = ai_pieces * 3 + ai_mills * 5 + ai_moves
        player_score = player_pieces * 3 + player_mills * 5 + player_moves

        return ai_score - player_score

    def get_possible_moves(self, player):
        if (player == 1 and self.player_pieces_left > 0) or (player == 2 and self.ai_pieces_left > 0):
            return [i for i, x in enumerate(self.board_state) if x == 0]
        else:
            player_pieces = [i for i, x in enumerate(self.board_state) if x == player]
            return [i for piece in player_pieces for i in self.get_adjacent_points(piece) if self.board_state[i] == 0]

    def minimax(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.check_for_win():
            return self.evaluate_state()

        if maximizing_player:
            max_eval = float('-inf')
            for move in self.get_possible_moves(2):
                self.make_move(move, 2)
                eval = self.minimax(depth - 1, alpha, beta, False)
                self.undo_move(move, 2)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_possible_moves(1):
                self.make_move(move, 1)
                eval = self.minimax(depth - 1, alpha, beta, True)
                self.undo_move(move, 1)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def make_move(self, point, player):
        self.board_state[point] = player
        if player == 1:
            self.player_pieces_left -= 1
        else:
            self.ai_pieces_left -= 1

    def undo_move(self, point, player):
        self.board_state[point] = 0
        if player == 1:
            self.player_pieces_left += 1
        else:
            self.ai_pieces_left += 1

    def evaluate(self):
        return self.evaluate_state()

class Renderer:
    def __init__(self, window):
        self.window = window
        self.font = pygame.font.Font(None, FONT_SIZE)

    def draw_points(self, game):
        points = [
            (MARGIN, MARGIN), (WINDOW_WIDTH // 2, MARGIN), (WINDOW_WIDTH - MARGIN, MARGIN),
            (INNER_MARGIN, INNER_MARGIN), (WINDOW_WIDTH // 2, INNER_MARGIN),
            (WINDOW_WIDTH - INNER_MARGIN, INNER_MARGIN),
            (MARGIN, WINDOW_HEIGHT // 2), (INNER_MARGIN, WINDOW_HEIGHT // 2),
            (WINDOW_WIDTH - INNER_MARGIN, WINDOW_HEIGHT // 2),
            (WINDOW_WIDTH - MARGIN, WINDOW_HEIGHT // 2),
            (INNER_MARGIN, WINDOW_HEIGHT - INNER_MARGIN), (WINDOW_WIDTH // 2, WINDOW_HEIGHT - INNER_MARGIN),
            (WINDOW_WIDTH - INNER_MARGIN, WINDOW_HEIGHT - INNER_MARGIN),
            (MARGIN, WINDOW_HEIGHT - MARGIN), (WINDOW_WIDTH // 2, WINDOW_HEIGHT - MARGIN),
            (WINDOW_WIDTH - MARGIN, WINDOW_HEIGHT - MARGIN)
        ]

        for i, point in enumerate(points):
            if game.board_state[i] == 0:
                color = POINT_COLOR
            elif game.board_state[i] == 1:
                color = PLAYER_COLOR
            else:
                color = AI_COLOR

            pygame.draw.circle(self.window, color, point, POINT_RADIUS)

    def draw_board(self):
        board_color = (255, 255, 255)
        board_width = 2
        pygame.draw.rect(self.window, board_color,
                         pygame.Rect(MARGIN, MARGIN, WINDOW_WIDTH - 2 * MARGIN, WINDOW_HEIGHT - 2 * MARGIN),
                         board_width)
        pygame.draw.rect(self.window, board_color,
                         pygame.Rect(2 * MARGIN, 2 * MARGIN, WINDOW_WIDTH - 4 * MARGIN, WINDOW_HEIGHT - 4 * MARGIN),
                         board_width)

        pygame.draw.line(self.window, board_color, (WINDOW_WIDTH // 2, MARGIN), (WINDOW_WIDTH // 2, 2 * MARGIN),
                         board_width)
        pygame.draw.line(self.window, board_color, (WINDOW_WIDTH // 2, WINDOW_HEIGHT - MARGIN),
                         (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 2 * MARGIN), board_width)
        pygame.draw.line(self.window, board_color, (MARGIN, WINDOW_HEIGHT // 2), (2 * MARGIN, WINDOW_HEIGHT // 2),
                         board_width)
        pygame.draw.line(self.window, board_color, (WINDOW_WIDTH - MARGIN, WINDOW_HEIGHT // 2),
                         (WINDOW_WIDTH - 2 * MARGIN, WINDOW_HEIGHT // 2), board_width)

    def draw_pieces(self, game):
        piece_radius = 10
        spacing = 30

        player_text = self.font.render("Player", True, (255, 255, 255))
        self.window.blit(player_text, (WINDOW_WIDTH // 2 - player_text.get_width() // 2, 10))

        for i in range(game.player_pieces_left):
            piece_x = WINDOW_WIDTH // 2 - (
                        game.player_pieces_left - 1) * spacing // 2 + i * spacing
            piece_y = player_text.get_height() + 40
            pygame.draw.circle(self.window, PLAYER_COLOR, (piece_x, piece_y), piece_radius)

        computer_text = self.font.render("Computer", True, (255, 255, 255))
        self.window.blit(computer_text, (WINDOW_WIDTH // 2 - computer_text.get_width() // 2,
                                         WINDOW_HEIGHT - computer_text.get_height() - 10))

        for i in range(game.ai_pieces_left):
            piece_x = WINDOW_WIDTH // 2 - (
                        game.ai_pieces_left - 1) * spacing // 2 + i * spacing
            piece_y = WINDOW_HEIGHT - computer_text.get_height() - 40
            pygame.draw.circle(self.window, (0, 255, 0), (piece_x, piece_y), piece_radius)

    def draw_turn(self, game):
        if game.current_player == 1:
            turn_text = self.font.render("Player's turn", True, (255, 255, 255))
        else:
            turn_text = self.font.render("Computer's turn", True, (255, 255, 255))
        self.window.blit(turn_text, (
        WINDOW_WIDTH // 2 - turn_text.get_width() // 2, WINDOW_HEIGHT // 2 - turn_text.get_height() // 2))

    def draw_popup(self, winner):
        pygame.draw.rect(self.window, (200, 200, 200), pygame.Rect(WINDOW_WIDTH // 4, WINDOW_HEIGHT // 4, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        winner_text = self.font.render(f"{winner} wins!", True, (0, 0, 0))
        self.window.blit(winner_text, (WINDOW_WIDTH // 2 - winner_text.get_width() // 2, WINDOW_HEIGHT // 2 - winner_text.get_height() // 2 - 30))

        replay_button_rect = pygame.draw.rect(self.window, (0, 200, 0), pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2, 100, 50))
        replay_button_text = self.font.render("Play Again", True, (0, 0, 0))
        self.window.blit(replay_button_text, (WINDOW_WIDTH // 2 - replay_button_text.get_width() // 2, WINDOW_HEIGHT // 2 + replay_button_text.get_height() // 2))

        exit_button_rect = pygame.draw.rect(self.window, (200, 0, 0), pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 + 60, 100, 50))
        exit_button_text = self.font.render("Exit", True, (0, 0, 0))
        self.window.blit(exit_button_text, (WINDOW_WIDTH // 2 - exit_button_text.get_width() // 2, WINDOW_HEIGHT // 2 + 60 + exit_button_text.get_height() // 2))

    def draw_game_board(self, game):
        self.window.blit(background_image, (0, 0))
        self.draw_points(game)
        self.draw_pieces(game)
        self.draw_turn(game)


def main():
    pygame.init()
    background_image = pygame.image.load("background.png")
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Six Men's Morris")

    game = Game()
    renderer = Renderer(window)

    start_screen = True
    button_color = (0, 200, 0)
    button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 25, 100, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if start_screen and button_rect.collidepoint(pos):
                    start_screen = False
                elif game.handle_player_move(pos[0], pos[1]):
                    renderer.draw_game_board(game)
                    pygame.display.flip()
                    pygame.time.delay(0)
                    if not game.remove_mode:
                        game.handle_ai_move()
                    renderer.draw_game_board(game)
                    pygame.display.flip()

                winner = game.check_for_win()
                if winner:
                    if winner == 1:
                        winner_text = "Player"
                    else:
                        winner_text = "AI"
                    renderer.draw_popup(winner_text)
                    pygame.display.flip()

                    while True:
                        for event in pygame.event.get():
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                pos = pygame.mouse.get_pos()
                                if game.handle_replay_button(pos):
                                    break
                                game.handle_exit_button(pos)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if start_screen:
            window.blit(background_image, (0, 0))
            welcome_text = renderer.font.render("Welcome to Six Men Morris Game", True, (255, 255, 255))  # White text
            window.blit(welcome_text, (WINDOW_WIDTH // 2 - welcome_text.get_width() // 2,
                                       WINDOW_HEIGHT // 2 - welcome_text.get_height() // 2 - 60))
            button_text = renderer.font.render("Start Game", True, (0, 0, 0))  # White text
            text_width, text_height = button_text.get_size()
            padding = 10  # Padding value
            button_rect = pygame.Rect(
                WINDOW_WIDTH // 2 - text_width // 2 - padding,
                WINDOW_HEIGHT // 2 - text_height // 2 - padding,
                text_width + 2 * padding,
                text_height + 2 * padding
            )
            pygame.draw.rect(window, button_color, button_rect)
            window.blit(button_text,
                        (button_rect.x + padding, button_rect.y + padding))


        else:
            renderer.draw_game_board(game)

        pygame.display.flip()

if __name__ == "__main__":
    main()