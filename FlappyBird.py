import pygame
import random
import numpy as np
import queue

class FlappyBirdGame:
    def __init__(self, frames, state_queue, action_queue, episodes=1, num_agents=2):
        self.screen = None
        self.clock = None
        self.game_font = None
        self.game_start = False
        self.score = 0.0
        self.frames = frames
        self.state_queue = state_queue
        self.action_queue = action_queue
        self.episodes = episodes
        self.num_agents = num_agents
        self.birds = [{'rect': None, 'movement': 0, 'score': 0.0, 'active': True} for _ in range(num_agents)]
        
    def game_close(self):
        pygame.quit()

    def game_on(self):
        return self.game_start

    def draw_floor(self, floor_surface, floor_x_pos):
        self.screen.blit(floor_surface, (floor_x_pos, 900))
        self.screen.blit(floor_surface, (floor_x_pos + 576, 900))

    def create_pipe(self, pipe_surface, pipe_height):
        difference = random.randint(150, 400)
        random_pipe_pos = random.choice(pipe_height)
        bottom_pipe = pipe_surface.get_rect(midtop=(700, random_pipe_pos))
        top_pipe = pipe_surface.get_rect(midbottom=(700, random_pipe_pos - difference))
        return bottom_pipe, top_pipe

    def move_pipes(self, pipes):
        for pipe in pipes:
            pipe.centerx -= 500 / self.frames
        return pipes

    def draw_pipes(self, pipe_surface, pipes):
        for pipe in pipes:
            if pipe.bottom >= 1024:
                self.screen.blit(pipe_surface, pipe)
            else:
                flip_pipe = pygame.transform.flip(pipe_surface, False, True)
                self.screen.blit(flip_pipe, pipe)

    def check_collison(self, bird_rect, pipes):
        for pipe in pipes:
            if bird_rect.colliderect(pipe):
                return True
        if bird_rect.top <= -100 or bird_rect.bottom >= 900:
            return True
        return False

    def rotate_bird(self, bird, bird_movement):
        new_bird = pygame.transform.rotozoom(bird, -bird_movement * 3, 1)
        return new_bird

    def score_display(self, game_mode):
        game_font = pygame.font.Font(None, 40)
        if game_mode == 'main_game':
            score_surface = game_font.render(str(int(self.score)), True, (0, 0, 0))
            score_rect = score_surface.get_rect(center=(288, 100))
            self.screen.blit(score_surface, score_rect)

        if game_mode == 'game_over':
            score_surface = game_font.render(str(int(self.score)), True, (0, 0, 0))
            score_rect = score_surface.get_rect(center=(288, 100))
            self.screen.blit(score_surface, score_rect)

            high_score_surface = game_font.render(f'Highscore: ' + str(int(self.high_score)), True, (0, 0, 0))
            high_score_rect = high_score_surface.get_rect(center=(288, 150))
            self.screen.blit(high_score_surface, high_score_rect)

    def start_game(self):
        pygame.init()
        self.screen = pygame.display.set_mode((576, 1024))
        self.clock = pygame.time.Clock()
        self.game_start = True
    
    def get_action(self):
        try:
            action = self.action_queue.get(timeout=0.01)
        except queue.Empty:
            action = [0 for _ in range(self.num_agents)]

        return action

    def get_state(self, prev_bird_position, bird_rect, pipe_list, score, agent_num):
        bottom_pipe_pos = 0
        top_pipe_pos = 0
        distance_bird_pipe = 0
        bird_velocity = bird_rect.center[1] - prev_bird_position
        if len(pipe_list) != 0:
            bottom_pipe_pos = pipe_list[0].y
            top_pipe_pos = pipe_list[1].y
            distance_bird_pipe = pipe_list[0].x - 100
        
        state = [bird_rect.center[0], bird_rect.center[1], bird_velocity, bottom_pipe_pos, top_pipe_pos, distance_bird_pipe, score, agent_num]
        return state

    def play_game(self):
        for i in range(self.episodes):
            gravity = 0.25
            bird_movement = 0
            game_active = True
            current_frame = 0
            action_time = 10

            bg_surface = pygame.image.load('assets/background-day.png').convert()
            bg_surface = pygame.transform.scale2x(bg_surface)

            floor_surface = pygame.image.load('assets/base.png').convert()
            floor_surface = pygame.transform.scale2x(floor_surface)
            floor_x_pos = 0

            bird_surface = pygame.image.load('assets/bluebird-midflap.png').convert_alpha()
            bird_surface = pygame.transform.scale2x(bird_surface)
            for bird in self.birds:
                bird["rect"] = bird_surface.get_rect(center=(100, 512))
            bird_rect = bird_surface.get_rect(center=(100, 312))

            pipe_surface = pygame.image.load('assets/pipe-green.png')
            pipe_surface = pygame.transform.scale2x(pipe_surface)
            pipe_list = []

            state = []
            bird_position = []
            
            SPAWNPIPE = pygame.USEREVENT
            pygame.time.set_timer(SPAWNPIPE, 1200)
            pipe_height = [400, 600, 800]

            while game_active:
                if current_frame % action_time == 0:
                    action = self.get_action()
                else:
                    action = [0 for _ in range(self.num_agents)]
                for i in range(self.num_agents):
                    bird = self.birds[i]
                    if bird['active']:
                        if action[i] == 1:
                            bird['movement'] = -6
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                    if event.type == SPAWNPIPE:
                        pipe_list.extend(self.create_pipe(pipe_surface, pipe_height))
                
                for bird in self.birds: 
                    bird['movement'] += gravity
                    bird['rect'].centery += bird['movement']
                bird_movement += gravity
                rotated_bird = self.rotate_bird(bird_surface, bird_movement)
                bird_rect.centery += bird_movement

                self.screen.blit(bg_surface, (0, 0))
                bird_count = self.num_agents
                for bird in self.birds:
                    if bird['active']:
                        self.screen.blit(bird_surface, bird['rect'])
                        bird['score'] += 0.005
                        bird['active'] = not self.check_collison(bird['rect'], pipe_list)
                    else:
                        bird_count -= 1

                if bird_count == 0:
                    game_active = False

                pipe_list = self.move_pipes(pipe_list)
                self.draw_pipes(pipe_surface, pipe_list)
                self.draw_floor(floor_surface, floor_x_pos)
                self.score_display("main_game")
                
                self.state_queue.put(state)
                self.state_queue.put(bird_position)
                self.clock.tick(self.frames)

                self.game_on()
