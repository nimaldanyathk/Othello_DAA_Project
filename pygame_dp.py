import pygame
import sys
from ui.pygame_gui import PyGameUI, STATE_MENU, STATE_PLAYING, MODE_PvCPU, MODE_PvP
from model.board import Board
from model.game_state import GameState
from algorithms.divide_and_conquer import get_dnc_move_generator, weighted_heuristic
from algorithms.dp import get_dp_move_generator

class DncOthelloUI(PyGameUI):
    def __init__(self):
        super().__init__()
        pygame.display.set_caption("Othello - Divide & Conquer vs DP (Minimax)")
        self.use_dp = False # Toggle between standard D&C and DP
        self.message = ""
        self.message_timer = 0
        self.dp_hit_count = 0
        self.dp_hit_timer = 0
        
    def show_message(self, text, duration=60):
        self.message = text
        self.message_timer = duration

    def update_ai(self):

        if not self.ai_generator:
            if self.use_dp:
                self.ai_generator = get_dp_move_generator(self.game_state, depth=3)
            else:
                self.ai_generator = get_dnc_move_generator(self.game_state, depth=3)
            
        try:
            vis = next(self.ai_generator)
            if vis['type'] == 'result':
                self.game_state = vis['state']
                
                self.last_eval_score = weighted_heuristic(self.game_state.board, Board.BLACK)
                
                self.ai_generator = None
                self.current_vis_data = None
                self.play_sound('move')
            elif vis['type'] == 'dp_hit':
                 # Visual Feedback for DP Hit
                 self.dp_hit_count += 1
                 self.dp_hit_timer = 45 # Show for ~1.5 seconds
                 self.current_vis_data = vis
                 self.play_sound('flip')

            else:
                self.current_vis_data = vis
        except StopIteration:
            self.ai_generator = None

    def run(self):

        while self.running:
            mx, my = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        pygame.display.toggle_fullscreen()

                if event.type == pygame.VIDEORESIZE:
                    self.calculate_layout(event.w, event.h)

                if self.app_state == STATE_MENU:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                         self.handle_menu_click((mx, my))
                         
                elif self.app_state == STATE_PLAYING:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_h:
                            self.algo_mode = not self.algo_mode
                        
                        if event.key == pygame.K_m:
                            self.heatmap_mode = not self.heatmap_mode
                            self.play_sound('flip')
                            
                        if event.key == pygame.K_e:
                            self.show_eval_bar = not self.show_eval_bar
                            self.play_sound('flip')

                        if event.key == pygame.K_d:
                            self.use_dp = not self.use_dp
                            if self.use_dp:
                                self.algo_mode = True
                            mode_name = "DP Mode" if self.use_dp else "Standard D&C"
                            self.show_message(f"Switched to {mode_name}")
                            self.play_sound('flip')
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        can_move = False
                        if self.game_mode == MODE_PvP:
                            can_move = True 
                        elif self.game_mode == MODE_PvCPU:
                            if self.game_state.player == self.human_player:
                                can_move = True
                                
                        if can_move:
                             if mx < self.board_area_size:
                                 c, r = mx // self.cell_size, my // self.cell_size
                                 if self.game_state.board.is_valid_move(r, c, self.game_state.player):
                                     new_board, _ = self.game_state.board.apply_move(r, c, self.game_state.player)
                                     self.play_sound('move')
                                     
                                     successors = self.game_state.get_successors()
                                     for s in successors:
                                         if s.board.grid == new_board.grid:
                                             self.game_state = s
                                             self.last_eval_score = weighted_heuristic(self.game_state.board, Board.BLACK)
                                             break
                        
                        if hasattr(self, 'btn_restart') and self.btn_restart.collidepoint((mx, my)):
                             self.app_state = STATE_MENU
                             self.play_sound('flip')

            if self.app_state == STATE_MENU:
                self.draw_menu()
            elif self.app_state == STATE_PLAYING:
                self.draw_board()
                
                # Draw ephemeral message
                if self.message_timer > 0:
                    msg_surf = self.font_title.render(self.message, True, (255, 215, 0))
                    self.screen.blit(msg_surf, (self.board_area_size//2 - msg_surf.get_width()//2, self.board_area_size//2))
                    self.message_timer -= 1
                
                if self.game_mode == MODE_PvCPU and self.game_state.player == self.ai_player and not self.game_state.is_terminal():
                    if self.algo_mode:
                        self.update_ai()
                    else:
                        for _ in range(20): 
                            if self.game_state.player == self.ai_player:
                                self.update_ai()
                            else:
                                break

                if self.game_mode == MODE_PvP or (self.game_mode == MODE_PvCPU and self.game_state.player == self.human_player):
                     if not self.game_state.is_terminal():
                         if not self.game_state.board.get_valid_moves(self.game_state.player):
                             succ = self.game_state.get_successors()
                             if succ:
                                 t = self.font_title.render("PASS!", True, (255, 0, 0))
                                 self.screen.blit(t, (self.board_area_size//2 - t.get_width()//2, self.board_area_size//2))
                                 pygame.display.flip()
                                 pygame.time.delay(1000)
                                 
                                 self.game_state = succ[0]
                                 self.current_vis_data = None

            pygame.display.flip()
            self.clock.tick(30 if self.algo_mode else 60)

        pygame.quit()

    def _draw_side_panel(self):

        panel_x = self.board_area_size
        pygame.draw.rect(self.screen, (60, 60, 60), (panel_x, 0, self.screen_width-panel_x, self.screen_height))
        x = panel_x + 20
        y = 20
        
        mode_str = "1 PLAYER (CPU)" if self.game_mode == MODE_PvCPU else "2 PLAYERS (PvP)"
        self.screen.blit(self.small_font.render(mode_str, True, (200, 200, 100)), (x, y))
        y += 40
        
        turn_str = "BLACK" if self.game_state.player == Board.BLACK else "WHITE"
        turn_col = (0,0,0) if self.game_state.player == Board.BLACK else (255,255,255)
        lbl = self.font_title.render(turn_str, True, turn_col, (100,100,100))
        self.screen.blit(lbl, (x, y))
        y += 60
        
        b, w = self.game_state.board.get_counts()
        self.screen.blit(self.font.render(f"Black: {b}", True, self.COLOR_WHITE), (x, y))
        y += 30
        self.screen.blit(self.font.render(f"White: {w}", True, self.COLOR_WHITE), (x, y))
        y += 60
        
        mode_txt = "ON" if self.algo_mode else "OFF"
        mode_col = (0, 255, 0) if self.algo_mode else (100, 100, 100)
        self.screen.blit(self.font.render("Algo View (H)", True, (200,200,200)), (x, y))
        self.screen.blit(self.font_title.render(mode_txt, True, mode_col), (x + 140, y - 5))
        y += 40
        
        # New DP Toggle
        dp_txt = "ON" if self.use_dp else "OFF"
        dp_col = (255, 215, 0) if self.use_dp else (100, 100, 100) # Gold for DP
        self.screen.blit(self.font.render("DP Mode (D)", True, (200,200,200)), (x, y))
        self.screen.blit(self.font_title.render(dp_txt, True, dp_col), (x + 140, y - 5))
        y += 40
        
        hm_txt = "ON" if self.heatmap_mode else "OFF"
        hm_col = (0, 255, 0) if self.heatmap_mode else (100, 100, 100)
        self.screen.blit(self.font.render("Heatmap (M)", True, (200,200,200)), (x, y))
        self.screen.blit(self.font_title.render(hm_txt, True, hm_col), (x + 140, y - 5))
        y += 40
        
        ev_txt = "ON" if self.show_eval_bar else "OFF"
        ev_col = (0, 255, 0) if self.show_eval_bar else (100, 100, 100)
        self.screen.blit(self.font.render("Eval Bar (E)", True, (200,200,200)), (x, y))
        self.screen.blit(self.font_title.render(ev_txt, True, ev_col), (x + 140, y - 5))
        y += 50

        if self.show_eval_bar:
            self._draw_eval_bar(x, y, 40, 150)
            sc = self.last_eval_score
            col = (0, 255, 0) if sc > 0 else (255, 0, 0)
            self.screen.blit(self.small_font.render(f"Eval: {sc}", True, col), (x + 50, y + 70))
        
        y += 170
        
        # Check for DP Hit Visualization in Side Panel?
        # Stats
        self.screen.blit(self.font.render(f"DP Hits: {self.dp_hit_count}", True, (255, 215, 0)), (x, y))
        y += 40
        
        # Check for DP Hit Visualization in Side Panel?
        if self.dp_hit_timer > 0:
             alpha = int(255 * (self.dp_hit_timer / 45)) if self.dp_hit_timer < 45 else 255
             dp_hit_surf = self.font_title.render("DP HIT!", True, (255, 215, 0))
             dp_hit_surf.set_alpha(alpha)
             self.screen.blit(dp_hit_surf, (x, y))
             self.dp_hit_timer -= 1

        if self.game_state.is_terminal():
            winner = self.game_state.get_winner()
            t = "Black Wins!" if winner==1 else "White Wins!" if winner==-1 else "Draw!"
            self.screen.blit(self.font_title.render(t, True, (255,255,0)), (x, y))
            self.play_sound('win')

        # Restart
        self.btn_restart = pygame.Rect(x, self.screen_height - 80, 160, 50)
        pygame.draw.rect(self.screen, (200, 50, 50), self.btn_restart, border_radius=5)
        oms = self.font.render("MENU", True, self.COLOR_WHITE)
        self.screen.blit(oms, (self.btn_restart.centerx - oms.get_width()//2, self.btn_restart.centery - oms.get_height()//2))


if __name__ == "__main__":
    app = DncOthelloUI()
    app.run()
