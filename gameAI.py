import pygame
import time
import numpy as np

pygame.font.init()

global font
font = pygame.font.Font('freesansbold.ttf', 12)

class Brick():
    def __init__(self, windowWidth, windowHeight, n_x, n_y):
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        self.n_x = n_x
        self.n_y = n_y
        self.brickWidth = windowWidth // 10
        self.brickHeight = 10
        self.cordBricks = self.buildBricks()

    def buildBricks(self):
        y_ofs = 20
        cords = []
        for i in range(self.n_x):
            x_ofs = 10
            for j in range(self.n_y):
                cords.append([x_ofs, y_ofs, self.brickWidth, self.brickHeight])
                x_ofs += self.brickWidth + 8
            y_ofs += self.brickHeight + 10
        return cords

    def displayBricks(self, gameDisp):
        for idx, cord in enumerate(self.cordBricks):
            if idx < 8:
                pygame.draw.rect(gameDisp, (200, 0, 0), cord)
            elif idx < 16:
                pygame.draw.rect(gameDisp, (0, 200, 0), cord)
            elif idx < 24:
                pygame.draw.rect(gameDisp, (0, 0, 200), cord)
            elif idx < 32:
                pygame.draw.rect(gameDisp, (200, 0, 0), cord)
            elif idx < 40:
                pygame.draw.rect(gameDisp, (0, 200, 0), cord)


class Paddle:
    def __init__(self, windowWidth, windowHeight, step):
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        self.step = step
        self.paddleWidth = 80
        self.paddleHeight = 10
        self.x = windowWidth // 2 - self.paddleWidth // 2
        self.y = windowHeight - 40
        self.dead = False

    def drawPaddle(self, gameDisp):
        pygame.draw.rect(gameDisp, (0, 0, 255), (self.x, self.y, self.paddleWidth, self.paddleHeight))

    def moveLeft(self):
        self.x -= self.step

        if self.x < 0:
            self.x = 0

    def moveRight(self):
        self.x += self.step

        if self.x + self.paddleWidth > self.windowWidth:
            self.x = self.windowWidth - self.paddleWidth

class Agent(Paddle):
    def __init__(self, windowWidth, windowHeight, step, states, actions, lr = 0.01, gamma = 0.99):
        super().__init__(windowWidth, windowHeight, step)
        self.states = states
        self.actions = actions
        self.lr = lr
        self.gamma = gamma
        try:
            self.Qtable = np.load("Brain.npy")
        except:
            self.Qtable = np.zeros((states, actions))

    def act(self, state, gameNo):
        return np.argmax(self.Qtable[state, :] + np.random.randn(1, self.actions) * (1 / (gameNo + 1)))

    def learn(self, state, action, reward, stateDash):
        self.Qtable[state, action] += self.lr * (reward + self.gamma * np.max(self.Qtable[stateDash, :]) - self.Qtable[state, action])

    def reset(self):
        self.x, self.y = (self.windowWidth // 2 - self.paddleWidth // 2, self.windowHeight - 40)
        self.dead = False

    def saveAgent(self):
        np.save("Brain.npy", self.Qtable)

class Ball:
    def __init__(self, windowWidth, windowHeight, vel_x=1, vel_y=5, rad=10):
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        self.vel_x = vel_x
        self.vel_y = np.random.randint(1, vel_y)
        self.rad = rad
        self.x = windowWidth // 2
        self.y = windowHeight // 2

    def drawBall(self, gameDisp):
        pygame.draw.circle(gameDisp, (200, 0, 150), (int(self.x), int(self.y)), self.rad)

    def reset(self):
        self.x, self.y = (self.windowWidth // 2, self.windowHeight // 2)
        self.vel_x = self.vel_x
        self.vel_y = np.random.randint(1, 5)

class Game:
    def __init__(self, windowWidth=400, windowHeight=600):
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        self.gameDisplay = pygame.display.set_mode((windowWidth, windowHeight))
        self.bricks = Brick(windowWidth, windowHeight, n_x=5, n_y=8)
        self.player = Agent(windowWidth, windowHeight, 10, 3, 3)
        self.ball = Ball(windowWidth, windowHeight)
        self.score = 0
        self.maxScore = 0
        pygame.display.set_caption('Breakout')

    def ballMove(self):
        self.ball.y += self.ball.vel_y
        self.ball.x += self.ball.vel_x

        # Check if ball collides with left wall
        if self.ball.x - self.ball.rad < 0:
            self.ball.vel_x = -self.ball.vel_x
        # Check if ball collides with right wall
        if self.ball.x + self.ball.rad > self.windowWidth:
            self.ball.vel_x = -self.ball.vel_x
        # Check if ball touches upper screen
        if self.ball.y - self.ball.rad < 0:
            self.ball.vel_y = -self.ball.vel_y

        # Checking if ball is within range of X range of paddle
        if (self.player.x <= self.ball.x <= self.player.x + self.player.paddleWidth) and \
                (self.ball.y >= self.player.y):  # checking Y
            self.ball.vel_y = -self.ball.vel_y

        # Checking if ball touches a block
        for idx, cord in enumerate(self.bricks.cordBricks):
            try:
                if ((cord[0] <= self.ball.x - self.ball.rad <= cord[0] + cord[2]) or \
                    (cord[0] <= self.ball.x + self.ball.rad <= cord[0] + cord[2])) \
                and ((cord[1]<= self.ball.y - self.ball.rad <= cord[1] + cord[3]) or \
                     (cord[1]<= self.ball.y + self.ball.rad <= cord[1] + cord[3])):
                    self.bricks.cordBricks.remove(cord)
                    self.ball.vel_y = -self.ball.vel_y
                    self.score += 1

                #if (cord[0] <= self.ball.x <= cord[0] + cord[2]) and (self.ball.y + self.ball.rad <= cord[1]):
                #    self.bricks.cordBricks.remove(cord)
                #    self.ball.vel_y = -self.ball.vel_y
                #    self.score += 1
            except:
                break

        self.checkDead()

    def getState(self):
        if self.ball.x <= self.player.x:
            return 0
        if self.player.x < self.ball.x < self.player.x + self.player.paddleWidth:
            return 1
        if self.ball.x >= self.player.x + self.player.paddleWidth:
            return 2

    def checkDead(self):
        if (self.player.x <= self.ball.x <= self.player.x + self.player.paddleWidth) and \
                (self.ball.y + self.ball.rad >= self.player.y):
            return 2

        if (self.ball.x - self.ball.rad < 0) or (self.ball.x + self.ball.rad > self.windowWidth):
            return 1

        if self.ball.y > self.player.y:
            self.player.dead = True
            return -1
        return 0

    def reset(self):
        self.player.reset()
        self.ball.reset()
        self.player.saveAgent()
        self.bricks.cordBricks = self.bricks.buildBricks()
        if self.score > self.maxScore:
            self.maxScore = self.score
        self.score = 0

    def sayMessage(self, msg, color=((200, 150, 230)), loc=(10, 0)):
        self.gameDisplay.blit(font.render(msg, True, color), loc)

    def startGame(self, episode):
        left = right = False
        state = self.getState()
        while not self.player.dead:
            reward = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        left = True
                    if event.key == pygame.K_RIGHT:
                        right = True

            action = self.player.act(state, episode)

                # if event.type == pygame.KEYUP:
                #     if event.key == pygame.K_LEFT:
                #         left = False
                #     if event.key == pygame.K_RIGHT:
                #         right = False

            if action == 0:
                left = True
            elif action == 1:
                left = right = False
            elif action == 2:
                right = True

            if left:
                self.player.moveLeft()
                left = False
            if right:
                self.player.moveRight()
                right = False

            stateDash = self.getState()

            self.gameDisplay.fill((23, 24, 25))
            self.bricks.displayBricks(self.gameDisplay)
            self.player.drawPaddle(self.gameDisplay)
            self.ball.drawBall(self.gameDisplay)
            self.sayMessage('Score: ' + str(self.score))
            self.sayMessage('M. Score: ' + str(self.maxScore), loc=((self.windowWidth // 2 - 120, 0)))
            self.sayMessage('BREAKOUT', color=(200, 150, 230), loc=(self.windowWidth // 2 - 30, 0))
            self.sayMessage('Episode ' + str(episode), color=(200, 150, 230), loc=(self.windowWidth - 100, 0))
            #print(self.player.Qtable)
            self.ballMove()

            if (self.player.x <= self.ball.x <= self.player.x + self.player.paddleWidth) and \
                    (self.ball.y + self.ball.rad >= self.player.y):
                reward += 5
            reward += self.checkDead()
            self.player.learn(state, action, reward, stateDash)
            state = stateDash

            # Check if ball is out of bounds, then Game Over
            # if self.player.dead:
            #     self.sayMessage('GAME OVER', loc=(self.windowWidth // 2 - 50, self.windowHeight // 2))
            #     pygame.display.update()
            #     time.sleep(2)
            #
            if len(self.bricks.cordBricks) == 0:
                self.sayMessage('YOU WON!!!', loc=(self.windowWidth // 2 - 50, self.windowHeight // 2))
                pygame.display.update()
                time.sleep(2)
                pygame.quit()

            pygame.display.update()

game = Game()
for episode in range(1000):
    game.startGame(episode)
    game.reset()
pygame.quit()


