import pygame
import sys
import os
import math
import random
 
# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512) # Init mixer lebih stabil
 
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Adventure Time: River Crossing Rescue - 16-Bit Pixel Edition")
clock = pygame.time.Clock()
 
# ── Colours (Saturated Retrowave / Pixel Art Palette) ────────────────────────
SKY_DARK   = (24,  28,  75)
SKY_MED    = (41,  89,  190)
SKY_LIGHT  = (102, 171, 238)
GRASS_SHAD = (17,  69,  31)
GRASS_MID  = (38,  121, 55)
GRASS_HIGH = (84,  183, 76)
RIVER_DEEP = (11,  23,  68)
RIVER_MID  = (21,  53,  120)
RIVER_SHAL = (36,  100, 186)
WAVE_PIX   = (112, 196, 246)
WHITE      = (255, 255, 255)
YELLOW     = (255, 224, 50)
RED        = (210,  40,  40)
GREEN      = (40,  190,  70)
GOLD       = (245, 170,   0)
BTN_COL    = (46,  49,  94)
BTN_HOV    = (75,  80,  150)
BTN_TXT    = (255, 224, 110)
 
# ── Asset path ────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
def asset(name):
    return os.path.join(BASE, "assets", name)
 
# ── Load Audio Files ──────────────────────────────────────────────────────────
def load_audio_sound(base_name):
    """Cuba cari fail bunyi dalam assets/ folder. Fallback ke silent jika gagal."""
    extensions = [".mp3", ".wav"]
    for ext in extensions:
        p = asset(base_name + ext)
        if os.path.exists(p):
            try:
                snd = pygame.mixer.Sound(p)
                print(f"[AUDIO] OK: {base_name}{ext}")
                return snd
            except Exception as e:
                print(f"[AUDIO] Gagal load {base_name}{ext}: {e}")
    print(f"[AUDIO] Tidak jumpa: {base_name} — guna senyap.")
    return pygame.mixer.Sound(buffer=b'\x00' * 44)

def load_audio_music(filename):
    """Muat muzik latar dari assets/ folder."""
    p = asset(filename)
    if os.path.exists(p):
        try:
            pygame.mixer.music.load(p)
            print(f"[AUDIO] BGM OK: {filename}")
            return True
        except Exception as e:
            print(f"[AUDIO] BGM gagal: {e}")
    else:
        print(f"[AUDIO] BGM tidak jumpa: {filename}")
    return False

# ── Muat SFX ──────────────────────────────────────────────────────────────────
sfx_click = load_audio_sound("click")
sfx_river = load_audio_sound("river")
sfx_win = load_audio_sound("win")
sfx_lose = load_audio_sound("lose")

# Volume SFX
sfx_click.set_volume(0.8)
sfx_river.set_volume(0.4)
sfx_win.set_volume(1.0)
sfx_lose.set_volume(1.0)

# Channel khas untuk bunyi sungai (loop)
river_channel = pygame.mixer.Channel(1)
# Channel khas untuk bunyi menang & kalah
win_channel = pygame.mixer.Channel(2)
lose_channel = pygame.mixer.Channel(3)

# ── Muat & Main BGM ───────────────────────────────────────────────────────────
bgm_loaded = load_audio_music("background.mp3")
if bgm_loaded:
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)   # loop selama-lamanya

# ── Fonts ─────────────────────────────────────────────────────────────────────
font_big   = pygame.font.SysFont("Courier New", 36, bold=True)
font_med   = pygame.font.SysFont("Courier New", 22, bold=True)
font_small = pygame.font.SysFont("Courier New", 16, bold=True)
font_tiny  = pygame.font.SysFont("Courier New", 13, bold=True)
 
# ── Images ────────────────────────────────────────────────────────────────────
def load_img(filename, size):
    try:
        img = pygame.image.load(asset(filename)).convert_alpha()
        return pygame.transform.scale(img, size)
    except Exception as e:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, (200, 80, 80), (0, 0, size[0], size[1]), border_radius=8)
        return surf
 
CHAR_SIZE = (64, 64)
BOAT_SIZE = (150, 72)
 
img_finn  = load_img("finn.png",      CHAR_SIZE)
img_jake  = load_img("jake.png",      CHAR_SIZE)
img_bg    = load_img("bubblegum.png", CHAR_SIZE)
img_ice   = load_img("crown.png",     CHAR_SIZE)
img_boat  = load_img("boat.png",      BOAT_SIZE)
 
# ── Layout ────────────────────────────────────────────────────────────────────
BANK_L_W  = 210
BANK_R_X  = 690
GROUND_Y  = 380
WATER_Y   = GROUND_Y + 45
BOAT_Y    = WATER_Y + 18
BOAT_LEFT  = BANK_L_W + 8
BOAT_RIGHT = BANK_R_X - BOAT_SIZE[0] - 8
 
LEFT_SLOTS  = [(20, GROUND_Y-130),(90, GROUND_Y-130),
               (20, GROUND_Y- 65),(90, GROUND_Y- 65)]
RIGHT_SLOTS = [(BANK_R_X+20, GROUND_Y-130),(BANK_R_X+90, GROUND_Y-130),
               (BANK_R_X+20, GROUND_Y- 65),(BANK_R_X+90, GROUND_Y- 65)]

# ── Pixel Particles ───────────────────────────────────────────────────────────
particles = []
def spawn_particles(x, y, color=GOLD):
    for _ in range(12):
        particles.append({
            "x": x + CHAR_SIZE[0]//2 + random.randint(-10, 10),
            "y": y + CHAR_SIZE[1]//2 + random.randint(-10, 10),
            "vx": random.choice([-2, -1, 1, 2]),
            "vy": random.uniform(-4, -1),
            "size": random.choice([4, 6, 8]), 
            "life": 1.0,
            "color": color
        })

def update_and_draw_particles(surf):
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.15  
        p["life"] -= 0.04
        if p["life"] <= 0:
            particles.remove(p)
        else:
            p_surf = pygame.Surface((p["size"], p["size"]), pygame.SRCALPHA)
            p_surf.fill((*p["color"], int(p["life"] * 255)))
            surf.blit(p_surf, (int(p["x"]), int(p["y"])))

# ── Pixel Clouds ──────────────────────────────────────────────────────────────
clouds = [{"x": random.uniform(0, WIDTH), "y": random.randint(30, 140), "speed": random.uniform(0.15, 0.4)} for _ in range(3)]

def draw_pixel_cloud(surf, cx, cy):
    blocks = [
        (0, 12, 80, 20), (16, 4, 52, 12), (28, -4, 28, 10), (8, 8, 68, 20)
    ]
    for bx, by, bw, bh in blocks:
        pygame.draw.rect(surf, (255, 255, 255, 180), (cx + bx, cy + by, bw, bh))

def draw_clouds(surf):
    for c in clouds:
        c["x"] += c["speed"]
        if c["x"] > WIDTH:
            c["x"] = -100
            c["y"] = random.randint(30, 140)
        draw_pixel_cloud(surf, int(c["x"]), c["y"])
 
# ══════════════════════════════════════════════════════════════════════════════
# CLASSES
# ══════════════════════════════════════════════════════════════════════════════
class Character:
    def __init__(self, name, image):
        self.name     = name
        self.image    = image
        self.side     = "left"   
        self.on_boat  = False
        self.x        = 0.0
        self.y        = 0.0
        self._tx      = 0.0
        self._ty      = 0.0
        self.speed    = 8.0  
 
    def snap(self, x, y):
        self.x = self._tx = float(x)
        self.y = self._ty = float(y)
 
    def move_to(self, x, y):
        self._tx = float(x)
        self._ty = float(y)
 
    def update(self):
        dx = self._tx - self.x
        dy = self._ty - self.y
        d  = (dx*dx + dy*dy) ** 0.5
        if d > self.speed:
            self.x += dx/d * self.speed
            self.y += dy/d * self.speed
        else:
            self.x, self.y = self._tx, self._ty
 
    def draw(self, surf, bob_y=0):
        ix, iy = int(self.x), int(self.y) + int(bob_y)
        
        shadow = pygame.Surface((48, 8), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 70))
        surf.blit(shadow, (ix + 8, iy + CHAR_SIZE[1] - 4))
        
        surf.blit(self.image, (ix, iy))
        
        lbl = font_tiny.render(self.name.upper(), True, WHITE)
        bg_rect = pygame.Rect(ix + CHAR_SIZE[0]//2 - lbl.get_width()//2 - 4, iy + CHAR_SIZE[1] + 2, lbl.get_width() + 8, 14)
        pygame.draw.rect(surf, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(surf, GOLD, bg_rect, 1)
        surf.blit(lbl, (ix + CHAR_SIZE[0]//2 - lbl.get_width()//2, iy + CHAR_SIZE[1] + 2))

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), CHAR_SIZE[0], CHAR_SIZE[1])
 
class Boat:
    MAX_PASS = 2   
 
    def __init__(self):
        self.x          = float(BOAT_LEFT)
        self._tx        = float(BOAT_LEFT)
        self.y          = float(BOAT_Y)
        self.side       = "left"
        self.moving     = False
        self.speed      = 5.0
        self.passengers = []   
 
    def add(self, char):
        if len(self.passengers) < self.MAX_PASS:
            self.passengers.append(char)
            char.on_boat = True
            spawn_particles(char.x, char.y, GREEN)
            return True
        return False
 
    def remove(self, char):
        if char in self.passengers:
            self.passengers.remove(char)
            char.on_boat = False
            spawn_particles(self.x + 35, self.y, YELLOW)
 
    def sail(self, destination):
        self._tx    = float(BOAT_RIGHT if destination == "right" else BOAT_LEFT)
        self.side   = destination
        self.moving = True
 
    def update(self):
        dx = self._tx - self.x
        if abs(dx) > self.speed:
            self.x += self.speed if dx > 0 else -self.speed
        else:
            self.x    = self._tx
            self.moving = False
 
    def draw(self, surf, bob_y):
        bx, by = int(self.x), int(self.y) + int(bob_y)
        
        b_shadow = pygame.Surface((BOAT_SIZE[0], 8), pygame.SRCALPHA)
        b_shadow.fill((0, 0, 0, 90))
        surf.blit(b_shadow, (bx, by + BOAT_SIZE[1] - 4))
        
        surf.blit(img_boat, (bx, by))
 
        slot_x = bx + 16
        for p in self.passengers:
            p.x = float(slot_x)
            p.y = float(by - CHAR_SIZE[1] + 16 - bob_y)
            p.draw(surf, bob_y)
            slot_x += CHAR_SIZE[0] + 12
 
    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), BOAT_SIZE[0], BOAT_SIZE[1])
 
class GameManager:
    TOTAL_TIME = 180
 
    def __init__(self):
        self.shake_amount = 0
        self.reset()
 
    def reset(self):
        self.finn       = Character("Finn",      img_finn)
        self.jake       = Character("Jake",      img_jake)
        self.bubblegum  = Character("Bubblegum", img_bg)
        self.ice_king   = Character("Ice King",  img_ice)
        self.characters = [self.finn, self.jake, self.bubblegum, self.ice_king]
        self.boat = Boat()
        if bgm_loaded:
            pygame.mixer.music.play(-1)
 
        for c in self.characters:
            c.side    = "left"
            c.on_boat = False
 
        self.finn.on_boat = False
        self.finn.snap(*LEFT_SLOTS[0])
        self.jake.snap(*LEFT_SLOTS[1])
        self.bubblegum.snap(*LEFT_SLOTS[2])
        self.ice_king.snap(*LEFT_SLOTS[3])
 
        self.timer    = float(self.TOTAL_TIME)
        self.moves    = 0
        self.score    = 0
        self.state    = "playing"   
        self.message  = ""
        self.msg_timer = 0
        self.wave_off  = 0
        self.game_time = 0.0
 
    def _check_bank(self, side):
        on_bank = [c for c in self.characters if c.side == side and not c.on_boat]
        names = {c.name for c in on_bank}
        if "Finn" in names:
            return True, ""
        if "Ice King" in names and "Bubblegum" in names:
            self.shake_amount = 14
            return False, "ICE KING KIDNAPPED PRINCESS! 😱"
        if "Jake" in names and "Ice King" in names and "Bubblegum" not in names:
            self.shake_amount = 14
            return False, "JAKE & ICE KING CAUSED CHAOS! 🔥"
        return True, ""
 
    def _validate(self):
        for side in ("left", "right"):
            ok, msg = self._check_bank(side)
            if not ok:
                return False, msg
        return True, ""
 
    def board(self, char):
        if self.state != "playing" or self.boat.moving:
            return
        if char.side != self.boat.side:
            self._msg(f"{char.name.upper()} IS ON OTHER SIDE!")
            return
        if len(self.boat.passengers) >= self.boat.MAX_PASS:
            self._msg("BOAT IS FULL! (MAX 2)")
            return
        self.boat.add(char)
        self._msg(f"{char.name.upper()} BOARDED.")
 
    def disembark(self, char):
        if char not in self.boat.passengers:
            return
        self.boat.remove(char)
        char.side = self.boat.side
        occupied = {(c.x, c.y) for c in self.characters
                    if c.side == char.side and not c.on_boat and c != char}
        slots = LEFT_SLOTS if char.side == "left" else RIGHT_SLOTS
        for sx, sy in slots:
            if (float(sx), float(sy)) not in occupied:
                char.move_to(sx, sy)
                break
        self._msg(f"{char.name.upper()} DISEMBARKED.")
 
    def sail(self):
        if not self.boat.passengers:
            self._msg("NEED AT LEAST 1 PILOT!")
            return
        if self.state != "playing" or self.boat.moving:
            return
        dest = "right" if self.boat.side == "left" else "left"
        self.boat.sail(dest)
        for p in self.boat.passengers:
            p.side = dest
        self.moves += 1
        sfx_click.play()  # bunyi sail
 
    def update(self, dt):
        self.game_time += dt
        if self.shake_amount > 0:
            self.shake_amount -= 0.5
            if self.shake_amount < 0: self.shake_amount = 0

        if self.state != "playing":
            return
 
        self.timer -= dt
        if self.timer <= 0:
            self.timer = 0
            self.state   = "lose"
            self.shake_amount = 12
            self.message = "TIME'S UP! OOO IS DOOMED! ⏰"
            river_channel.stop()
            pygame.mixer.music.stop()
            sfx_lose.play()
            return
 
        was_moving = self.boat.moving
        self.boat.update()
 
        if was_moving and not self.boat.moving:
            ok, msg = self._validate()
            if not ok:
                self.state   = "lose"
                self.message = msg
                river_channel.stop()
                pygame.mixer.music.stop()
                lose_channel.play(sfx_lose)
                return
            if all(c.side == "right" for c in self.characters):
                self.state   = "win"
                self.score   = max(0, int(self.timer)*10 - self.moves*5)
                self.message = f"OOO IS SAVED! SCORE: {self.score}"
                river_channel.stop()
                pygame.mixer.music.stop()
                win_channel.play(sfx_win)
 
        for c in self.characters:
            if not c.on_boat:
                c.update()
 
        self.wave_off = (self.wave_off + 1) % 80
        if self.msg_timer > 0:
            self.msg_timer -= 1
 
    def _msg(self, text):
        self.message   = text
        self.msg_timer = 140
 
# ── PIXEL ART BACKGROUND GENERATOR ────────────────────────────────────────────
def draw_background(surf, wave_off):
    pygame.draw.rect(surf, SKY_DARK,  (0, 0, WIDTH, 100))
    pygame.draw.rect(surf, SKY_MED,   (0, 100, WIDTH, 140))
    pygame.draw.rect(surf, SKY_LIGHT, (0, 240, WIDTH, GROUND_Y - 240))
 
    draw_clouds(surf)
 
    # Tebing Kiri
    pygame.draw.rect(surf, GRASS_HIGH, (0, GROUND_Y, BANK_L_W, HEIGHT-GROUND_Y))
    pygame.draw.rect(surf, GRASS_MID,  (0, GROUND_Y, BANK_L_W, 16))
    pygame.draw.rect(surf, GRASS_SHAD, (0, GROUND_Y+16, BANK_L_W, 12))
    for px, py in [(40,420), (120,450), (70,510), (160,400), (30,550)]:
        pygame.draw.rect(surf, GRASS_SHAD, (px, py, 12, 6))
 
    # Tebing Kanan
    pygame.draw.rect(surf, GRASS_HIGH, (BANK_R_X, GROUND_Y, WIDTH-BANK_R_X, HEIGHT-GROUND_Y))
    pygame.draw.rect(surf, GRASS_MID,  (BANK_R_X, GROUND_Y, WIDTH-BANK_R_X, 16))
    pygame.draw.rect(surf, GRASS_SHAD, (BANK_R_X, GROUND_Y+16, WIDTH-BANK_R_X, 12))
    for px, py in [(720,430), (810,460), (750,530), (840,410)]:
        pygame.draw.rect(surf, GRASS_SHAD, (px, py, 12, 6))
 
    # Air Sungai Pixel
    pygame.draw.rect(surf, RIVER_SHAL, (BANK_L_W, GROUND_Y, BANK_R_X-BANK_L_W, 60))
    pygame.draw.rect(surf, RIVER_MID,  (BANK_L_W, GROUND_Y+60, BANK_R_X-BANK_L_W, 90))
    pygame.draw.rect(surf, RIVER_DEEP, (BANK_L_W, GROUND_Y+150, BANK_R_X-BANK_L_W, HEIGHT-(GROUND_Y+150)))
 
    # Gelombang Air Bentuk Blok
    river_w = BANK_R_X - BANK_L_W
    for i in range(7):
        wx = BANK_L_W + (i * 85 + wave_off * 3) % river_w
        wy = WATER_Y + 15 + (i % 3) * 26
        pygame.draw.rect(surf, WAVE_PIX, (wx, wy, 24, 6))
        pygame.draw.rect(surf, WAVE_PIX, (wx + 6, wy - 4, 12, 4))
 
    _pixel_tree(surf, 150, GROUND_Y-80)
    _pixel_tree(surf, 730, GROUND_Y-80)
 
def _pixel_tree(surf, x, y):
    pygame.draw.rect(surf, (90, 50, 15), (x + 16, y + 30, 12, 50))
    pygame.draw.rect(surf, GRASS_SHAD, (x, y + 10, 44, 25))
    pygame.draw.rect(surf, GRASS_MID,  (x + 4, y, 36, 20))
    pygame.draw.rect(surf, GRASS_HIGH, (x + 10, y - 8, 24, 14))
 
def draw_hud(surf, gm):
    pygame.draw.rect(surf, (10, 10, 25), (10, 10, 260, 40))
    pygame.draw.rect(surf, WHITE, (10, 10, 260, 40), 2)
    
    t_ratio = gm.timer / gm.TOTAL_TIME
    bar_col = GREEN if t_ratio > 0.5 else (YELLOW if t_ratio > 0.25 else RED)
    pygame.draw.rect(surf, bar_col, (14, 14, int(252 * t_ratio), 32))
    surf.blit(font_med.render(f"TIME: {int(gm.timer)}S", True, WHITE), (20, 18))
 
    pygame.draw.rect(surf, (10, 10, 25), (WIDTH - 160, 10, 150, 40))
    pygame.draw.rect(surf, WHITE, (WIDTH - 160, 10, 150, 40), 2)
    mv = font_small.render(f"MOVES: {gm.moves}", True, GOLD)
    surf.blit(mv, (WIDTH - 160 + 75 - mv.get_width()//2, 20))
 
    if gm.msg_timer > 0:
        ms = font_med.render(gm.message, True, YELLOW)
        m_rect = pygame.Rect(WIDTH//2 - ms.get_width()//2 - 16, HEIGHT-56, ms.get_width() + 32, 34)
        pygame.draw.rect(surf, (10, 10, 25), m_rect)
        pygame.draw.rect(surf, WHITE, m_rect, 2)
        surf.blit(ms, (WIDTH//2 - ms.get_width()//2, HEIGHT-50))
 
    for i, line in enumerate(["[CLICK CHAR] -> BOARD / DISEMBARK",
                               "[SPACE / SAIL] -> CROSS RIVER  |  [ESC] -> PAUSE  |  [R] -> RESTART"]):
        s = font_tiny.render(line, True, WHITE)
        surf.blit(s, (15, HEIGHT-74+i*18))
 
def draw_sail_btn(surf, game_time):
    bx, by, bw, bh = WIDTH//2-70, HEIGHT-94, 140, 42
    hover = pygame.Rect(bx,by,bw,bh).collidepoint(pygame.mouse.get_pos())
    
    pulse = int(math.cos(game_time * 6) * 2) if not hover else 0
    p_rect = pygame.Rect(bx - pulse, by - pulse, bw + pulse*2, bh + pulse*2)

    pygame.draw.rect(surf, BTN_HOV if hover else BTN_COL, p_rect)
    pygame.draw.rect(surf, WHITE, p_rect, 2)
    lbl = font_med.render("SAIL >", True, BTN_TXT)
    surf.blit(lbl, (bx+bw//2-lbl.get_width()//2, by+bh//2-lbl.get_height()//2))
    return pygame.Rect(bx,by,bw,bh)
 
def draw_panel(surf, title, lines, btn_labels):
    overlay = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
    overlay.fill((0,0,0,160))
    surf.blit(overlay,(0,0))
    
    pw,ph = 500,240
    px,py = WIDTH//2-pw//2, HEIGHT//2-ph//2
    pygame.draw.rect(surf,(15, 15, 30),(px,py,pw,ph))
    pygame.draw.rect(surf,GOLD,(px,py,pw,ph),3)
    
    t = font_big.render(title,True,GOLD)
    surf.blit(t,(px+pw//2-t.get_width()//2, py+20))
    
    for i,line in enumerate(lines):
        l = font_small.render(line.upper(),True,WHITE)
        surf.blit(l,(px+pw//2-l.get_width()//2, py+85+i*28))
        
    rects=[]
    bw,bh=140,40
    total=len(btn_labels)
    sx=px+pw//2-(total*bw+(total-1)*14)//2
    by2=py+ph-60
    for i,txt in enumerate(btn_labels):
        bx2=sx+i*(bw+14)
        r=pygame.Rect(bx2,by2,bw,bh)
        hover=r.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(surf,BTN_HOV if hover else BTN_COL,r)
        pygame.draw.rect(surf,WHITE,r,1)
        l=font_small.render(txt.upper(),True,BTN_TXT)
        surf.blit(l,(bx2+bw//2-l.get_width()//2,by2+bh//2-l.get_height()//2))
        rects.append(r)
    return rects
 
def draw_menu(surf):
    draw_background(surf, 0)
    
    pygame.draw.rect(surf,(10,10,25),(WIDTH//2-320,80,640,130))
    pygame.draw.rect(surf,GOLD,(WIDTH//2-320,80,640,130),3)
    t1=font_big.render("ADVENTURE TIME",True,GOLD)
    t2=font_big.render("RIVER CROSSING RESCUE",True,WHITE)
    surf.blit(t1,(WIDTH//2-t1.get_width()//2,95))
    surf.blit(t2,(WIDTH//2-t2.get_width()//2,145))
    
    buttons = [
        {"txt": "[ PLAY GAME ]", "col": GREEN},
        {"txt": "[ HOW TO PLAY ]", "col": BTN_COL},
        {"txt": "[ QUIT GAME ]", "col": RED}
    ]
    
    rects = []
    bw, bh = 260, 48
    start_y = 280
    
    for i, b in enumerate(buttons):
        bx = WIDTH//2 - bw//2
        by = start_y + i * 68
        r = pygame.Rect(bx, by, bw, bh)
        hover = r.collidepoint(pygame.mouse.get_pos())
        c = tuple(min(v+35, 255) for v in b["col"]) if hover else b["col"]
        
        pygame.draw.rect(surf, c, r)
        pygame.draw.rect(surf, WHITE, r, 1)
        
        l = font_med.render(b["txt"], True, WHITE)
        surf.blit(l, (bx+bw//2-l.get_width()//2, by+bh//2-l.get_height()//2))
        rects.append(r)
        
    return rects[0], rects[1], rects[2]

def draw_instruction_screen(surf):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surf.blit(overlay, (0, 0))
    
    pw, ph = 680, 440
    px, py = WIDTH//2 - pw//2, HEIGHT//2 - ph//2
    pygame.draw.rect(surf, (10, 10, 25), (px, py, pw, ph))
    pygame.draw.rect(surf, GOLD, (px, py, pw, ph), 3)
    
    title = font_big.render("MISSION MANUAL", True, GOLD)
    surf.blit(title, (WIDTH//2 - title.get_width()//2, py + 25))
    
    lines = [
        "> OBJECTIVE:",
        "  MOVE FINN, JAKE, PB & ICE KING TO THE RIGHT BANK.",
        "",
        "> BOAT RULES:",
        "  BOAT CARRIES UP TO 2 CHARACTERS MAXIMUM.",
        "",
        "> GAME CONSTRAINTS:",
        "  - ICE KING + BUBBLEGUM ALONE ON BANK = KIDNAP!",
        "  - JAKE + ICE KING ALONE (NO BUBBLEGUM) = CHAOS!",
        "",
        "> CONTROLS:",
        "  - CLICK CHARACTER TO BOARD / DISEMBARK.",
        "  - CLICK 'SAIL' BUTTON OR SPACEBAR TO CROSS RIVER.",
    ]
    
    for i, line in enumerate(lines):
        color = GOLD if ">" in line else WHITE
        l = font_small.render(line, True, color)
        surf.blit(l, (px + 40, py + 95 + i * 22))
        
    bx, by, bw, bh = WIDTH//2 - 80, py + ph - 55, 160, 38
    r = pygame.Rect(bx, by, bw, bh)
    hover = r.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(surf, RED if hover else BTN_COL, r)
    pygame.draw.rect(surf, WHITE, r, 1)
    
    lbl = font_med.render("< BACK", True, WHITE)
    surf.blit(lbl, (bx+bw//2-lbl.get_width()//2, by+bh//2-lbl.get_height()//2))
    return r

# ══════════════════════════════════════════════════════════════════════════════
# Main loop
# ══════════════════════════════════════════════════════════════════════════════
def main():
    global gm
    gm    = GameManager()
    scene = "menu"   
    display_surface = pygame.Surface((WIDTH, HEIGHT))

    while True:
        dt = clock.tick(60) / 1000.0
        bob_y = int(math.sin(gm.game_time * 5) * 3) if scene == "playing" else 0

        # Kawal audio air sungai
        if scene == "playing" and gm.state == "playing":
            if not river_channel.get_busy():
                river_channel.play(sfx_river, loops=-1)
        else:
            river_channel.stop()

        # ── SCENE: MENU ───────────────────────────────────────────────────────
        if scene == "menu":
            play_r, inst_r, quit_r = draw_menu(display_surface)
            screen.blit(display_surface, (0, 0))
            pygame.display.flip()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if play_r.collidepoint(ev.pos):
                        sfx_click.play()
                        gm.reset(); scene = "playing"
                    elif inst_r.collidepoint(ev.pos):
                        sfx_click.play()
                        scene = "instructions"
                    elif quit_r.collidepoint(ev.pos):
                        sfx_click.play()
                        pygame.quit(); sys.exit()
            continue
 
        # ── SCENE: INSTRUCTIONS ───────────────────────────────────────────────
        if scene == "instructions":
            back_r = draw_instruction_screen(display_surface)
            screen.blit(display_surface, (0, 0))
            pygame.display.flip()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if back_r.collidepoint(ev.pos):
                        sfx_click.play()
                        scene = "menu"
            continue

        # ── UPDATE ────────────────────────────────────────────────────────────
        if scene == "playing":
            gm.update(dt)
 
        # ── DRAW BASE GAME ────────────────────────────────────────────────────
        draw_background(display_surface, gm.wave_off)
 
        for c in gm.characters:
            if not c.on_boat:
                c.draw(display_surface)
 
        gm.boat.draw(display_surface, bob_y)
        update_and_draw_particles(display_surface)
 
        draw_hud(display_surface, gm)
        sail_rect = draw_sail_btn(display_surface, gm.game_time)
 
        # ── OVERLAY: WIN ──────────────────────────────────────────────────────
        if gm.state == "win":
            btns = draw_panel(display_surface, "VICTORY!",
                              [gm.message, f"TOTAL MOVES: {gm.moves}"],
                              ["Play Again","Menu","Quit"])
            screen.blit(display_surface, (0,0))
            pygame.display.flip()
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: pygame.quit();sys.exit()
                if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                    if btns[0].collidepoint(ev.pos): sfx_click.play(); gm.reset()
                    elif btns[1].collidepoint(ev.pos): sfx_click.play(); scene="menu"
                    elif btns[2].collidepoint(ev.pos): sfx_click.play(); pygame.quit();sys.exit()
            continue
 
        # ── OVERLAY: LOSE ─────────────────────────────────────────────────────
        if gm.state == "lose":
            btns = draw_panel(display_surface, "GAME OVER",
                              [gm.message,"TRY AGAIN?"],
                              ["Retry","Menu","Quit"])
            cx = random.randint(int(-gm.shake_amount), int(gm.shake_amount))
            cy = random.randint(int(-gm.shake_amount), int(gm.shake_amount))
            screen.fill((0,0,0))
            screen.blit(display_surface, (cx, cy))
            pygame.display.flip()
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: pygame.quit();sys.exit()
                if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                    if btns[0].collidepoint(ev.pos): sfx_click.play(); gm.reset()
                    elif btns[1].collidepoint(ev.pos): sfx_click.play(); scene="menu"
                    elif btns[2].collidepoint(ev.pos): sfx_click.play(); pygame.quit();sys.exit()
            continue
 
        # ── OVERLAY: PAUSED ────────────────────────────────────────────────────
        if scene == "paused":
            btns = draw_panel(display_surface, "PAUSED", ["GAME IS PAUSED"],
                              ["Resume","Restart","Menu"])
            screen.blit(display_surface, (0,0))
            pygame.display.flip()
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: pygame.quit();sys.exit()
                if ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE:
                    sfx_click.play()
                    scene="playing"
                if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                    if btns[0].collidepoint(ev.pos): sfx_click.play(); scene="playing"
                    elif btns[1].collidepoint(ev.pos): sfx_click.play(); gm.reset();scene="playing"
                    elif btns[2].collidepoint(ev.pos): sfx_click.play(); scene="menu"
            continue
 
        # Render Utama
        cx = random.randint(int(-gm.shake_amount), int(gm.shake_amount))
        cy = random.randint(int(-gm.shake_amount), int(gm.shake_amount))
        screen.fill((0,0,0))
        screen.blit(display_surface, (cx, cy))
        pygame.display.flip()
 
        # ── EVENTS ────────────────────────────────────────────────────────────
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                pygame.quit();sys.exit()
 
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE: sfx_click.play(); scene="paused"
                if ev.key==pygame.K_r:      sfx_click.play(); gm.reset()
                if ev.key==pygame.K_SPACE:  sfx_click.play(); gm.sail()
 
            if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                mx,my = ev.pos
                if sail_rect.collidepoint(mx,my):
                    sfx_click.play()
                    gm.sail(); continue
 
                clicked_pass = False
                for p in list(gm.boat.passengers):
                    if p.get_rect().collidepoint(mx,my):
                        sfx_click.play()
                        gm.disembark(p)
                        clicked_pass = True
                        break
 
                if not clicked_pass:
                    for c in gm.characters:
                         if not c.on_boat and c.get_rect().collidepoint(mx,my):
                            sfx_click.play()
                            gm.board(c)
                            break
 
if __name__ == "__main__":
    main()