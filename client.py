from pygame import *
import socket
import json
from threading import Thread

# ---ПУГАМЕ НАЛАШТУВАННЯ ---
WIDTH, HEIGHT = 800, 600
init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")
# ---СЕРВЕР ---
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080)) # ---- Підключення до сервера
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass


def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            game_state["winner"] = -1
            break

# --- ШРИФТИ ---
font_win = font.Font(None, 72)
font_main = font.Font(None, 36)
font_score = font.SysFont('Impact', 72)
# --- ЗОБРАЖЕННЯ ----
ball = transform.scale(image.load('assets/images/ball.png'), (20, 20))
left_platform = transform.scale(image.load('assets/images/left_platform.png'), (20, 100))
right_platform = transform.scale(image.load('assets/images/right_platform.png'), (20, 100))
# --- ЗВУКИ ---
mixer.init() # підключаємо модуль для роботи зі звуком
#фонова музика
mixer.music.load('assets/sounds/fon_music.mp3') # завантажуємо музику в гру
mixer.music.play() # pause, unpause, stop | play(-1) - постійно повторюється
#гучність фонової музики
mixer.music.set_volume(0.15) # встановлюємо гучність в межах від 0 до 1
print(mixer.music.get_volume()) # отримуємо поточний рівень гучності
#події
platform_hit = mixer.Sound('assets/sounds/pingpongbat.ogg') # завантаження звуку
wall_hit = mixer.Sound('assets/sounds/pingpongboard.ogg') # завантаження звуку
#гучність звуків
print(platform_hit.get_volume())
platform_hit.set_volume(0.5)
platform_hit.play()

# --- ГРА ---
game_over = False
winner = None
you_winner = None
def start_game():
    global my_id, game_state, buffer, client 
    my_id, game_state, buffer, client = connect_to_server()    
    Thread(target=receive, daemon=True).start()
    return my_id, game_state, buffer, client
class Btn():
    def __init__(self, x,y, width, height, color, text, text_color=(0,0,0)):
        self.rect = Rect(x,y,width,height)
        self.color = color
        self.text = text
        self.text_color = text_color
        self.font = font.Font(None, 28)
    
    def draw(self):
        draw.rect(screen, self.color, self.rect)
        text = self.font.render(self.text, True, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def is_clicked(self, e):
        return e.type == MOUSEBUTTONDOWN and self.rect.collidepoint(e.pos)
btn_play = Btn(268, 380, 264, 51, (100,200,100), 'Грати', (255,255,255))
btn_restart = Btn(268, 380, 264, 51, (100,200,100), '', (255,255,255))
btn_exit = Btn(268, 450, 264, 51, (160,40,40), 'Вихід', (255,255,255))
timer = 0
menu = True
while menu:

    screen.fill((0,0,0))
    for e in event.get():
        if e.type == QUIT:
            exit()
        if btn_play.is_clicked(e):
            menu = False
        if btn_exit.is_clicked(e):
            exit()
    logo_text = font_score.render(f"PING PONG", True, (255, 255, 255))
    screen.blit(logo_text, (WIDTH // 2 - logo_text.get_width() // 2, HEIGHT // 2 - logo_text.get_height() // 2))
    btn_play.draw()
    btn_exit.draw()
    display.update()
my_id, game_state, buffer, client = start_game()

while True:
    for e in event.get():
        if e.type == QUIT:
            exit()
        if btn_exit.is_clicked(e):
            exit()
        if btn_restart.is_clicked(e):
            client.close()
            my_id, game_state, buffer, client = start_game()

    if "countdown" in game_state and game_state["countdown"] > 0:
        screen.fill((0, 0, 0))
        countdown_text = font.Font(None, 72).render(str(game_state["countdown"]), True, (255, 255, 255))
        screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))
        display.update()
        continue  # Не малюємо гру до завершення відліку

    if "winner" in game_state and game_state["winner"] is not None:
        screen.fill((20, 20, 20))

        if you_winner is None:  # Встановлюємо тільки один раз
            if game_state["winner"] == my_id:
                you_winner = True
            else:
                you_winner = False

        if you_winner:
            text = "Ти переміг!"
        else:
            text = "Пощастить наступним разом!"

        win_text = font_win.render(text, True, (255, 215, 0))
        text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(win_text, text_rect)

        btn_restart.draw()
        btn_exit.draw()
        display.update()

        display.update()
        continue  # Блокує гру після перемоги

    if game_state:
        screen.fill((0, 0, 0))
        # draw.rect(screen, (0, 255, 0), (20, game_state['paddles']['0'], 20, 100))
        # draw.rect(screen, (255, 0, 255), (WIDTH - 40, game_state['paddles']['1'], 20, 100))
        
        screen.blit(left_platform, (20, game_state['paddles']['0']))
        screen.blit(right_platform, (WIDTH - 40, game_state['paddles']['1']))
        screen.blit(ball, 
                    (game_state['ball']['x'] - ball.get_width() // 2,
                     game_state['ball']['y']- ball.get_height() // 2
                    ))
        
        score_text_left = font_score.render(f"{game_state['scores'][0]}", True, (255, 255, 255))
        screen.blit(score_text_left, (WIDTH // 4 - score_text_left.get_width() // 2, 20))
        
        score_text_right = font_score.render(f"{game_state['scores'][1]}", True, (255, 255, 255))
        screen.blit(score_text_right, (WIDTH - WIDTH// 4 - score_text_right.get_width() // 2, 20))
        
        y = 5
        x = WIDTH // 2 
        for i in range(27):
            draw.line(screen, (255,255,255), (x,y), (x,y+10), 3)
            y+= 22.22
            
        if game_state['sound_event']:   
            if game_state['sound_event'] == 'wall_hit':
                # звук відбиття м'ячика від стін
                wall_hit.play()
            if game_state['sound_event'] == 'platform_hit':
                # звук відбиття м'ячика від платформи
                platform_hit.play()

    else:
        screen.fill((0,0,0))
        wating_text = font_main.render(f"Очікування гравців...", True, (255, 255, 255))
        if 0 < timer <= 20:
            wating_text = font_main.render(f"Очікування гравців.", True, (255, 255, 255))
        elif 20 < timer <= 40:
            wating_text = font_main.render(f"Очікування гравців..", True, (255, 255, 255))
        elif 40 < timer <= 60:
            wating_text = font_main.render(f"Очікування гравців...", True, (255, 255, 255))
        elif timer > 60:
            timer = 0
        timer += 1
        screen.blit(wating_text, (WIDTH // 2 - wating_text.get_width() // 2,  HEIGHT // 2 - wating_text.get_height() // 2))
                               
    display.update()
    clock.tick(60)

    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")
