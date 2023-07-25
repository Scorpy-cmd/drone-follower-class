import pygame

WIDTH = 800
HEIGHT = 600
FPS = 60
clock = pygame.time.Clock()


class Buttons:
    def __init__(self, display, Butt_X, Butt_Y, Butt_Width, Butt_Height, image, action=None, args=None):
        self.display = display
        self.Butt_X = Butt_X
        self.Butt_Y = Butt_Y
        self.Butt_Width = Butt_Width
        self.Butt_Height = Butt_Height
        self.image = image
        self.action = action
        self.args = args
        # self.message = message
        # self.color_message = color_message

    def pressed(self, mouse):
        click = pygame.mouse.get_pressed()
        if self.Butt_X < mouse[0] < self.Butt_X + self.Butt_Width:
            if self.Butt_Y < mouse[1] < self.Butt_Y + self.Butt_Height:
                if click[0] == 1:
                    pygame.time.delay(200)
                    # print("Loading")
                    self.action(self.args)

    def Button_Create(self):
        self.display.blit(self.image, (self.Butt_X, self.Butt_Y))
        self.pressed(pygame.mouse.get_pos())


def Menu(condition, running):
    cycle = True
    Background1 = pygame.image.load("Resource/Sprites/CyberBackground.png")
    Start = pygame.image.load("Resource/Sprites/Start.png")

    # Создаем окно
    pygame.init()
    pygame.mixer.init()
    display = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Interface")

    args = [display, condition, running]
    Button_Start = Buttons(display, WIDTH / 2 + 150, HEIGHT / 2 + 100, 280, 190, Start, Loading, args)

    while cycle:
        display.blit(Background1, (0, 0))
        Button_Start.Button_Create()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cycle = False
                quit()
        clock.tick(FPS)
        pygame.display.update()


def Loading(args):
    display = args[0]
    args[1][0] = True
    cycle = True

    Background1 = pygame.image.load("Resource/Sprites/CyberBackground.png")
    Loading_Text = pygame.image.load("Resource/Sprites/Text_Loading.png")
    Stop_Button = pygame.image.load("Resource/Sprites/stop.jpg")

    new_args = [args[2]]
    Button_Stop = Buttons(display, 10, HEIGHT / 2 + 100, 280, 190, Stop_Button, stop, new_args)

    while cycle:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cycle = False
                quit()
        display.blit(Background1, (0, 0))
        display.blit(Loading_Text, (WIDTH / 2 - 350, HEIGHT / 2 - 175))
        Button_Stop.Button_Create()
        
        clock.tick(FPS)
        pygame.display.update()

    cycle = False
    pygame.quit()
    quit()
        # Вызов Фунции запуска дрона


def stop(args):
    args[0][0] = False
    pygame.quit()
    quit()


if __name__ == "__main__":
    Menu([False], [True])
