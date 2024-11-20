import pygame
import random

# 初始化 Pygame
pygame.init()

# 定义常量
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
CARD_WIDTH, CARD_HEIGHT = 60, 90
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)

# 创建屏幕对象
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Notty Card Game")

# 定义字体
font = pygame.font.Font(None, 36)

# 操作记录
actions_log = []
log_font = pygame.font.Font(None, 24)

# 卡牌类
class Card:
    def __init__(self, colour, number):
        self.colour = colour
        self.number = number
        self.rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)

    def draw(self, surface, x, y):
        self.rect.topleft = (x, y)
        pygame.draw.rect(surface, self.colour, self.rect)
        text = font.render(str(self.number), True, BLACK)
        surface.blit(text, (x + 10, y + 30))

# 游戏模式选择
mode_selected = False
num_players = 0

# 玩家和卡牌
deck = []
player_hands = []
current_player = 0  # 当前玩家
selected_cards = []  # 选中的卡牌
has_drawn = False  # 当前玩家是否已经抽过牌
has_taken_card = False  # 当前玩家是否已经从其他玩家手中抽牌
show_draw_options = False  # 是否显示抽卡选项
show_take_options = False  # 是否显示抽取卡牌选项

# 初始化卡牌
colours = [RED, BLUE, GREEN, YELLOW]
for colour in colours:
    for number in range(1, 11):
        deck.append(Card(colour, number))
        deck.append(Card(colour, number))  # 每种组合有两张

def deal_cards(num_players):
    global player_hands
    random.shuffle(deck)
    player_hands = [[] for _ in range(num_players)]
    for _ in range(5):
        for hand in player_hands:
            hand.append(deck.pop())

def next_player():
    global current_player, selected_cards, has_drawn, has_taken_card, show_draw_options, show_take_options
    current_player = (current_player + 1) % num_players
    selected_cards = []
    has_drawn = False
    has_taken_card = False
    show_draw_options = False
    show_take_options = False
    check_for_winner()

def is_valid_group(cards):
    if len(cards) < 3:
        return False

    same_colour = all(card.colour == cards[0].colour for card in cards)
    if same_colour:
        numbers = sorted(card.number for card in cards)
        consecutive = all(numbers[i] + 1 == numbers[i + 1] for i in range(len(numbers) - 1))
        if consecutive:
            return True

    same_number = all(card.number == cards[0].number for card in cards)
    if same_number:
        colours = {card.colour for card in cards}
        if len(colours) == len(cards):
            return True

    return False

def ai_turn(player_index):
    global has_drawn, has_taken_card

    # 尝试丢弃有效组合
    for i in range(len(player_hands[player_index])):
        for j in range(i + 3, len(player_hands[player_index]) + 1):
            group = player_hands[player_index][i:j]
            if is_valid_group(group):
                for card in group:
                    player_hands[player_index].remove(card)
                deck.extend(group)
                random.shuffle(deck)
                actions_log.append(f"AI Player {player_index + 1} discarded a valid group of cards.")
                return

    # 尝试从其他玩家手中抽取一张牌
    if not has_taken_card:
        target_player = random.choice([i for i in range(num_players) if i != player_index])
        if player_hands[target_player]:
            random_card = random.choice(player_hands[target_player])
            player_hands[target_player].remove(random_card)
            player_hands[player_index].append(random_card)
            actions_log.append(f"AI Player {player_index + 1} took a card from Player {target_player + 1}.")
            has_taken_card = True
            return

    # 抽取最多三张牌
    if not has_drawn:
        cards_to_draw = min(3, len(deck))
        for _ in range(cards_to_draw):
            player_hands[player_index].append(deck.pop())
        actions_log.append(f"AI Player {player_index + 1} drew {cards_to_draw} card(s).")
        has_drawn = True

def check_for_winner():
    for i, hand in enumerate(player_hands):
        if not hand:  # 如果玩家没有手牌
            winner = "Player" if i == 0 else f"AI Player {i + 1}"
            actions_log.append(f"{winner} wins the game!")
            display_winner_message(winner)
            pygame.time.delay(2000)  # 延迟以显示胜利消息
            pygame.quit()
            exit()

def display_winner_message(winner):
    winner_message = f"Congratulations, {winner} wins!"
    winner_text = font.render(winner_message, True, BLUE)
    screen.fill(WHITE)
    screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2 - winner_text.get_height() // 2))
    pygame.display.flip()
    pygame.time.delay(3000)

running = True
deck_rect = pygame.Rect(SCREEN_WIDTH // 2 - CARD_WIDTH // 2, 50, CARD_WIDTH, CARD_HEIGHT)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not mode_selected:
            mouse_x, mouse_y = event.pos
            if 150 <= mouse_x <= 350 and 200 <= mouse_y <= 250:
                num_players = 2
                mode_selected = True
                deal_cards(num_players)
                actions_log.append("Game started with 2 players (1 AI).")
            elif 450 <= mouse_x <= 650 and 200 <= mouse_y <= 250:
                num_players = 3
                mode_selected = True
                deal_cards(num_players)
                actions_log.append("Game started with 3 players (2 AI).")
        elif event.type == pygame.MOUSEBUTTONDOWN and mode_selected:
            mouse_x, mouse_y = event.pos
            if deck_rect.collidepoint(mouse_x, mouse_y) and current_player == 0 and not has_drawn:
                show_draw_options = True
            elif show_draw_options:
                if draw_one_button.collidepoint(mouse_x, mouse_y):
                    cards_to_draw = 1
                elif draw_two_button.collidepoint(mouse_x, mouse_y):
                    cards_to_draw = 2
                elif draw_three_button.collidepoint(mouse_x, mouse_y):
                    cards_to_draw = 3
                else:
                    cards_to_draw = 0

                if cards_to_draw > 0 and len(deck) >= cards_to_draw:
                    for _ in range(cards_to_draw):
                        player_hands[current_player].append(deck.pop())
                    actions_log.append(f"Player {current_player + 1} drew {cards_to_draw} card(s).")
                    has_drawn = True
                    show_draw_options = False
            elif play_for_me_button.collidepoint(mouse_x, mouse_y) and current_player == 0:
                actions_log.append(f"Player {current_player + 1} chose 'Play for Me'.")
                next_player()
            elif take_card_button.collidepoint(mouse_x, mouse_y) and current_player == 0 and not has_taken_card:
                if num_players == 2:
                    # 从电脑玩家手牌中随机抽取一张
                    target_player = 1  # 唯一的电脑玩家
                    if player_hands[target_player]:
                        random_card = random.choice(player_hands[target_player])
                        player_hands[target_player].remove(random_card)
                        player_hands[current_player].append(random_card)
                        actions_log.append(f"Player {current_player + 1} took a card from AI Player {target_player + 1}.")
                        has_taken_card = True
                elif num_players == 3:
                    # 显示从两个电脑玩家中选择的按钮
                    show_take_options = True
            elif show_take_options:
                if take_from_ai1_button.collidepoint(mouse_x, mouse_y):
                    target_player = 1
                elif take_from_ai2_button.collidepoint(mouse_x, mouse_y):
                    target_player = 2
                else:
                    target_player = None

                if target_player is not None and player_hands[target_player]:
                    random_card = random.choice(player_hands[target_player])
                    player_hands[target_player].remove(random_card)
                    player_hands[current_player].append(random_card)
                    actions_log.append(f"Player {current_player + 1} took a card from AI Player {target_player + 1}.")
                    has_taken_card = True
                    show_take_options = False
            elif drop_card_button.collidepoint(mouse_x, mouse_y) and current_player == 0:
                if selected_cards:
                    for card in selected_cards:
                        player_hands[current_player].remove(card)
                    deck.extend(selected_cards)
                    random.shuffle(deck)
                    actions_log.append(f"Player {current_player + 1} dropped {len(selected_cards)} card(s).")
                    selected_cards = []
            else:
                for card in player_hands[current_player]:
                    if card.rect.collidepoint(mouse_x, mouse_y):
                        if card in selected_cards:
                            selected_cards.remove(card)
                        else:
                            selected_cards.append(card)
        elif event.type == pygame.KEYDOWN and mode_selected:
            if event.key == pygame.K_RETURN and current_player == 0:
                if is_valid_group(selected_cards):
                    for card in selected_cards:
                        player_hands[current_player].remove(card)
                    deck.extend(selected_cards)
                    random.shuffle(deck)
                    actions_log.append(f"Player {current_player + 1} discarded a valid group of cards.")
                    selected_cards = []

    if mode_selected and current_player != 0:
        ai_turn(current_player)
        next_player()

    screen.fill(WHITE)

    if not mode_selected:
        two_player_button = pygame.Rect(150, 200, 200, 50)
        pygame.draw.rect(screen, BLUE, two_player_button)
        two_player_text = font.render("2 Players (1 AI)", True, WHITE)
        screen.blit(two_player_text, (two_player_button.x + 20, two_player_button.y + 10))

        three_player_button = pygame.Rect(450, 200, 200, 50)
        pygame.draw.rect(screen, GREEN, three_player_button)
        three_player_text = font.render("3 Players (2 AI)", True, WHITE)
        screen.blit(three_player_text, (three_player_button.x + 20, three_player_button.y + 10))
    else:
        for i, hand in enumerate(player_hands):
            x_offset = 100
            y_offset = SCREEN_HEIGHT - CARD_HEIGHT - 20 - (i * (CARD_HEIGHT + 100))
            for card in hand:
                card.draw(screen, x_offset, y_offset)
                if card in selected_cards:
                    pygame.draw.rect(screen, BLACK, card.rect, 2)
                x_offset += CARD_WIDTH + 10

            player_label = "Player" if i == 0 else f"AI Player {i}"
            player_text = font.render(player_label, True, BLACK)
            screen.blit(player_text, (x_offset + 20, y_offset + 20))

        pygame.draw.rect(screen, GRAY, deck_rect)
        deck_text = font.render("Deck", True, BLACK)
        screen.blit(deck_text, (deck_rect.x + 10, deck_rect.y + CARD_HEIGHT // 2 - 10))

        if show_draw_options:
            draw_one_button = pygame.Rect(deck_rect.x - 100, deck_rect.y + CARD_HEIGHT + 10, 80, 40)
            draw_two_button = pygame.Rect(deck_rect.x, deck_rect.y + CARD_HEIGHT + 10, 80, 40)
            draw_three_button = pygame.Rect(deck_rect.x + 100, deck_rect.y + CARD_HEIGHT + 10, 80, 40)

            pygame.draw.rect(screen, BLUE, draw_one_button)
            pygame.draw.rect(screen, BLUE, draw_two_button)
            pygame.draw.rect(screen, BLUE, draw_three_button)

            screen.blit(font.render("Draw 1", True, WHITE), (draw_one_button.x + 10, draw_one_button.y + 5))
            screen.blit(font.render("Draw 2", True, WHITE), (draw_two_button.x + 10, draw_two_button.y + 5))
            screen.blit(font.render("Draw 3", True, WHITE), (draw_three_button.x + 10, draw_three_button.y + 5))

        if show_take_options:
            take_from_ai1_button = pygame.Rect(300, 300, 200, 50)
            take_from_ai2_button = pygame.Rect(300, 370, 200, 50)

            pygame.draw.rect(screen, BLUE, take_from_ai1_button)
            pygame.draw.rect(screen, BLUE, take_from_ai2_button)

            screen.blit(font.render("Take from AI 1", True, WHITE), (take_from_ai1_button.x + 10, take_from_ai1_button.y + 10))
            screen.blit(font.render("Take from AI 2", True, WHITE), (take_from_ai2_button.x + 10, take_from_ai2_button.y + 10))

        play_for_me_button = pygame.Rect(50, 50, 200, 50)
        button_color = BLUE if current_player == 0 else GRAY
        pygame.draw.rect(screen, button_color, play_for_me_button)
        play_for_me_text = font.render("Play for Me", True, WHITE)
        screen.blit(play_for_me_text, (play_for_me_button.x + 20, play_for_me_button.y + 10))

        take_card_button = pygame.Rect(50, 120, 200, 50)
        button_color = BLUE if current_player == 0 and not has_taken_card else GRAY
        pygame.draw.rect(screen, button_color, take_card_button)
        take_card_text = font.render("Take Card", True, WHITE)
        screen.blit(take_card_text, (take_card_button.x + 20, take_card_button.y + 10))

        drop_card_button = pygame.Rect(50, 200, 200, 50)
        button_color = BLUE if current_player == 0 and selected_cards else GRAY
        pygame.draw.rect(screen, button_color, drop_card_button)
        drop_card_text = font.render("Drop Card", True, WHITE)
        screen.blit(drop_card_text, (drop_card_button.x + 20, drop_card_button.y + 10))

        current_player_text = font.render(f"Current Player: Player {current_player + 1}", True, BLACK)
        screen.blit(current_player_text, (50, 280))

        log_rect = pygame.Rect(SCREEN_WIDTH - 250, 50, 200, 600)
        pygame.draw.rect(screen, BLACK, log_rect, 2)
        log_y_offset = 80
        screen.blit(font.render("Actions Log", True, BLACK), (SCREEN_WIDTH - 240, 60))
        for log in actions_log[-25:]:
            log_text = log_font.render(log, True, BLACK)
            screen.blit(log_text, (SCREEN_WIDTH - 240, log_y_offset))
            log_y_offset += 20
            if log_y_offset > log_rect.y + log_rect.height - 20:
                break

    pygame.display.flip()

pygame.quit()