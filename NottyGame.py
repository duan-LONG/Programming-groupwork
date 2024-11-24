import pygame
import random

# 初始化 Pygame
pygame.init()

# 定义常量
SCREEN_WIDTH, SCREEN_HEIGHT = int(pygame.display.Info().current_w * 0.75), int(pygame.display.Info().current_h * 0.75)
CARD_WIDTH, CARD_HEIGHT = 80, 120
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
font = pygame.font.Font(None, 48)

# 操作记录
actions_log = []
log_font = pygame.font.Font(None, 32)

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
        surface.blit(text, (x + 10, y + 40))

# 游戏模式选择
mode_selected = False
difficulty_selected = False
num_players = 0

difficulty = None  # 游戏难度

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
            print(f"Valid group by same colour: {[f'{card.colour}-{card.number}' for card in cards]}")
            return True

    same_number = all(card.number == cards[0].number for card in cards)
    if same_number:
        colours = {card.colour for card in cards}
        if len(colours) == len(cards):
            print(f"Valid group by same number: {[f'{card.colour}-{card.number}' for card in cards]}")
            return True

    return False


def find_valid_groups(player_hand):
    n = len(player_hand)
    valid_groups = []
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                for l in range(k + 1, n):  # 四张卡片的组合
                    group = [player_hand[i], player_hand[j], player_hand[k],player_hand[l]]
                    if is_valid_group(group):
                        valid_groups.append(group)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j+1,n):
                group =[player_hand[i],player_hand[j],player_hand[k]]
                if is_valid_group(group):
                    valid_groups.append(group)
    print(f"AI's valid groups: {valid_groups}")  # 添加调试日志
    return valid_groups



def ai_turn(player_index):
    global has_drawn, has_taken_card

    # 打印 AI 当前手牌
    print(f"AI Player {player_index + 1}'s hand before action: {[f'{card.colour}-{card.number}' for card in player_hands[player_index]]}")

    # 找到所有有效牌组并丢弃
    valid_groups = find_valid_groups(player_hands[player_index])
    if valid_groups:
        for group in valid_groups:
            # 确保 group 中的卡牌都存在于 player_hands
            if all(card in player_hands[player_index] for card in group):  # 确保 group 是完整的
                for card in group:
                    player_hands[player_index].remove(card)
                deck.extend(group)  # 完整地添加到牌堆
        random.shuffle(deck)  # 重新洗牌
        actions_log.append(f"AI Player {player_index + 1} discarded {len(valid_groups)} valid group(s) of cards.")
        print(f"AI Player {player_index + 1} discarded: {[f'{card.colour}-{card.number}' for group in valid_groups for card in group]}")
        return

    # 若没有有效组，尝试从其他玩家手中抽取一张牌
    if not has_taken_card:
        if num_players == 3:
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
            if deck:  # 确保牌堆有牌
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
deck_rect = pygame.Rect(SCREEN_WIDTH // 2 - CARD_WIDTH // 2, 100, CARD_WIDTH, CARD_HEIGHT)

# 游戏主循环
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not mode_selected:
            mouse_x, mouse_y = event.pos
            if 150 <= mouse_x <= 350 and 200 <= mouse_y <= 250:
                num_players = 2
                mode_selected = True
                actions_log.append("Game started with 2 players (1 AI).")
            elif 450 <= mouse_x <= 650 and 200 <= mouse_y <= 250:
                num_players = 3
                mode_selected = True
                actions_log.append("Game started with 3 players (2 AI).")
        elif event.type == pygame.MOUSEBUTTONDOWN and mode_selected and not difficulty_selected:
            mouse_x, mouse_y = event.pos
            if 150 <= mouse_x <= 350 and 300 <= mouse_y <= 350:
                difficulty = 'Easy'
                difficulty_selected = True
                deal_cards(num_players)
                actions_log.append("Difficulty set to Easy.")
            elif 450 <= mouse_x <= 650 and 300 <= mouse_y <= 350:
                difficulty = 'Hard'
                difficulty_selected = True
                deal_cards(num_players)
                actions_log.append("Difficulty set to Hard.")
            elif 750 <= mouse_x <= 950 and 300 <= mouse_y <= 350:
                difficulty = 'Hell'
                difficulty_selected = True
                deal_cards(num_players)
                actions_log.append("Difficulty set to Hell.")
        elif event.type == pygame.MOUSEBUTTONDOWN and mode_selected and difficulty_selected:
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
            elif skip_my_turn_button.collidepoint(mouse_x, mouse_y) and current_player == 0:
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
                if selected_cards and is_valid_group(selected_cards):
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
        elif event.type == pygame.KEYDOWN and mode_selected and difficulty_selected:
            if event.key == pygame.K_RETURN and current_player == 0:
                if is_valid_group(selected_cards):
                    for card in selected_cards:
                        player_hands[current_player].remove(card)
                    deck.extend(selected_cards)
                    random.shuffle(deck)
                    actions_log.append(f"Player {current_player + 1} discarded a valid group of cards.")
                    selected_cards = []

    if mode_selected and difficulty_selected and current_player != 0:
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
    elif mode_selected and not difficulty_selected:
        easy_button = pygame.Rect(150, 300, 200, 50)
        pygame.draw.rect(screen, GREEN, easy_button)
        easy_text = font.render("Easy", True, WHITE)
        screen.blit(easy_text, (easy_button.x + 50, easy_button.y + 10))

        hard_button = pygame.Rect(450, 300, 200, 50)
        pygame.draw.rect(screen, YELLOW, hard_button)
        hard_text = font.render("Hard", True, WHITE)
        screen.blit(hard_text, (hard_button.x + 50, hard_button.y + 10))

        hell_button = pygame.Rect(750, 300, 200, 50)
        pygame.draw.rect(screen, RED, hell_button)
        hell_text = font.render("Hell", True, WHITE)
        screen.blit(hell_text, (hell_button.x + 50, hell_button.y + 10))
    else:
        for i, hand in enumerate(player_hands):
            x_offset = 100
            y_offset = SCREEN_HEIGHT - CARD_HEIGHT - 20 - (i * (CARD_HEIGHT + 150))
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
        deck_count_text = font.render(f"Cards: {len(deck)}", True, BLACK)
        screen.blit(deck_count_text, (deck_rect.x + CARD_WIDTH + 20, deck_rect.y + CARD_HEIGHT // 2 - 10))

        current_turn_text = font.render(f"Current Turn: {'Player' if current_player == 0 else f'AI Player {current_player + 1}'}", True, BLACK)
        screen.blit(current_turn_text, (SCREEN_WIDTH // 2 - current_turn_text.get_width() // 2, 20))

        if show_draw_options:
            draw_one_button = pygame.Rect(deck_rect.x - 150, deck_rect.y + CARD_HEIGHT + 20, 120, 50)
            draw_two_button = pygame.Rect(deck_rect.x, deck_rect.y + CARD_HEIGHT + 20, 120, 50)
            draw_three_button = pygame.Rect(deck_rect.x + 150, deck_rect.y + CARD_HEIGHT + 20, 120, 50)

            pygame.draw.rect(screen, BLUE, draw_one_button)
            pygame.draw.rect(screen, BLUE, draw_two_button)
            pygame.draw.rect(screen, BLUE, draw_three_button)

            screen.blit(font.render("Draw 1", True, WHITE), (draw_one_button.x + 10, draw_one_button.y + 10))
            screen.blit(font.render("Draw 2", True, WHITE), (draw_two_button.x + 10, draw_two_button.y + 10))
            screen.blit(font.render("Draw 3", True, WHITE), (draw_three_button.x + 10, draw_three_button.y + 10))

        if show_take_options:
            take_from_ai1_button = pygame.Rect(300, 400, 200, 50)
            take_from_ai2_button = pygame.Rect(300, 470, 200, 50)

            pygame.draw.rect(screen, BLUE, take_from_ai1_button)
            pygame.draw.rect(screen, BLUE, take_from_ai2_button)

            screen.blit(font.render("Take from AI 1", True, WHITE), (take_from_ai1_button.x + 10, take_from_ai1_button.y + 10))
            screen.blit(font.render("Take from AI 2", True, WHITE), (take_from_ai2_button.x + 10, take_from_ai2_button.y + 10))

        skip_my_turn_button = pygame.Rect(50, 50, 200, 50)
        button_color = BLUE if current_player == 0 else GRAY
        pygame.draw.rect(screen, button_color, skip_my_turn_button)
        skip_my_turn_text = font.render("Skip My Turn", True, WHITE)
        screen.blit(skip_my_turn_text, (skip_my_turn_button.x + 20, skip_my_turn_button.y + 10))

        take_card_button = pygame.Rect(50, 120, 200, 50)
        button_color = BLUE if current_player == 0 and not has_taken_card else GRAY
        pygame.draw.rect(screen, button_color, take_card_button)
        take_card_text = font.render("Take Card", True, WHITE)
        screen.blit(take_card_text, (take_card_button.x + 20, take_card_button.y + 10))

        drop_card_button = pygame.Rect(50, 200, 200, 50)
        button_color = BLUE if current_player == 0 and selected_cards and is_valid_group(selected_cards) else GRAY
        pygame.draw.rect(screen, button_color, drop_card_button)
        drop_card_text = font.render("Drop Card", True, WHITE)
        screen.blit(drop_card_text, (drop_card_button.x + 20, drop_card_button.y + 10))

        current_player_text = font.render(f"Current Player: Player {current_player + 1}", True, BLACK)
        screen.blit(current_player_text, (50, 280))

        log_rect = pygame.Rect(SCREEN_WIDTH - 300, 50, 250, 600)
        pygame.draw.rect(screen, BLACK, log_rect, 2)
        log_y_offset = 80
        screen.blit(font.render("Actions Log", True, BLACK), (SCREEN_WIDTH - 290, 60))
        for log in actions_log[-25:]:
            log_text = log_font.render(log, True, BLACK)
            screen.blit(log_text, (SCREEN_WIDTH - 290, log_y_offset))
            log_y_offset += 24
            if log_y_offset > log_rect.y + log_rect.height - 20:
                break

    pygame.display.flip()

pygame.quit()
