import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
import random

# Set the window background color
Window.clearcolor = (0.95, 0.95, 0.98, 1)

class SettingsScreen(Screen):
    """
    The screen where the user can choose game settings, like the time limit and game mode.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize selections
        self.selected_time = None
        self.selected_mode = None
        
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=[40, 40], spacing=20)
        
        title = Label(text="Game Settings", font_size='40sp', bold=True, color=(0.1, 0.1, 0.1, 1), size_hint_y=0.2)
        layout.add_widget(title)
        
        # --- Time Selection ---
        time_label = Label(text="Choose Time Limit:", font_size='24sp', color=(0.3, 0.3, 0.3, 1), size_hint_y=0.1)
        layout.add_widget(time_label)
        
        self.time_buttons_layout = GridLayout(cols=2, spacing=15, size_hint_y=0.25)
        time_options = [30, 40, 50, 60]
        self.time_buttons = {}
        for time_val in time_options:
            button = Button(text=f"{time_val} seconds", font_size='20sp')
            button.bind(on_press=lambda instance, t=time_val: self.select_time(t))
            self.time_buttons[time_val] = button
            self.time_buttons_layout.add_widget(button)
        layout.add_widget(self.time_buttons_layout)
        
        # --- Mode Selection ---
        mode_label = Label(text="Choose Game Mode:", font_size='24sp', color=(0.3, 0.3, 0.3, 1), size_hint_y=0.1)
        layout.add_widget(mode_label)
        
        self.mode_buttons_layout = GridLayout(cols=1, spacing=15, size_hint_y=0.35)
        mode_options = {'addition': 'Addition', 'subtraction': 'Subtraction', 'mixed': 'Mixed'}
        self.mode_buttons = {}
        for mode_key, mode_text in mode_options.items():
            button = Button(text=mode_text, font_size='20sp')
            button.bind(on_press=lambda instance, m=mode_key: self.select_mode(m))
            self.mode_buttons[mode_key] = button
            self.mode_buttons_layout.add_widget(button)
        layout.add_widget(self.mode_buttons_layout)

        # Start Button
        self.start_button = Button(text="Start Game", font_size='28sp', size_hint_y=0.15, bold=True)
        self.start_button.bind(on_press=self.launch_game)
        layout.add_widget(self.start_button)
        
        self.add_widget(layout)
        self.reset_button_styles()

    def select_time(self, time_limit):
        """Saves the selected time and updates button appearance."""
        self.selected_time = time_limit
        for time, button in self.time_buttons.items():
            if time == time_limit:
                button.background_color = (0.1, 0.6, 0.2, 1) # Green for selected
            else:
                button.background_color = (0.2, 0.4, 0.8, 1) # Blue for default
            button.background_normal = ''

    def select_mode(self, mode):
        """Saves the selected mode and updates button appearance."""
        self.selected_mode = mode
        for m, button in self.mode_buttons.items():
            if m == mode:
                button.background_color = (0.1, 0.6, 0.2, 1) # Green
            else:
                button.background_color = (0.2, 0.4, 0.8, 1) # Blue
            button.background_normal = ''

    def launch_game(self, instance):
        """Starts the game if time and mode have been selected."""
        if self.selected_time and self.selected_mode:
            game_screen = self.manager.get_screen('game')
            game_screen.start_game(game_time=self.selected_time, game_mode=self.selected_mode)
            self.manager.current = 'game'
            self.reset_button_styles() # Reset appearance for the next game

    def reset_button_styles(self):
        """Returns buttons to their default style."""
        self.selected_time = None
        self.selected_mode = None
        for button in list(self.time_buttons.values()) + list(self.mode_buttons.values()):
            button.background_color = (0.2, 0.4, 0.8, 1)
            button.background_normal = ''
            
class GameScreen(Screen):
    """
    The screen where the actual game is played.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize game variables
        self.GAME_TIME = 30
        self.GAME_MODE = 'addition'
        self.MIN_NUM = 1
        self.MAX_NUM = 20
        self.score = 0
        self.total_questions = 0
        self.correct_answers = 0
        self.timer_event = None
        
        # Create widgets
        layout = BoxLayout(orientation='vertical', padding=[30, 20], spacing=15)
        stats_layout = GridLayout(cols=2, size_hint_y=None, height=40)
        self.score_label = Label(text="Score: 0", font_size='20sp', color=(0.3, 0.3, 0.3, 1))
        self.accuracy_label = Label(text="Accuracy: -", font_size='20sp', color=(0.3, 0.3, 0.3, 1))
        stats_layout.add_widget(self.score_label)
        stats_layout.add_widget(self.accuracy_label)
        layout.add_widget(stats_layout)

        self.timer_label = Label(text="Time: 0s", font_size='28sp', bold=True, color=(0.2, 0.4, 0.8, 1))
        layout.add_widget(self.timer_label)
        self.question_label = Label(text="Welcome!", font_size='48sp', bold=True, color=(0.1, 0.1, 0.1, 1)) # Added dark color
        layout.add_widget(self.question_label)
        self.feedback_label = Label(text="", font_size='20sp', size_hint_y=None, height=30)
        layout.add_widget(self.feedback_label)
        self.answer_input = TextInput(multiline=False, font_size='32sp', size_hint_y=None, height=60, halign='center', input_filter='int', disabled=True)
        self.answer_input.bind(on_text_validate=self.check_answer)
        layout.add_widget(self.answer_input)
        self.action_button = Button(text="Submit", font_size='24sp', size_hint_y=None, height=60)
        self.action_button.bind(on_press=self.check_answer)
        layout.add_widget(self.action_button)
        self.add_widget(layout)

    def start_game(self, game_time, game_mode):
        """Starts or resets the game with the chosen settings."""
        self.GAME_TIME = game_time
        self.GAME_MODE = game_mode
        self.score = 0
        self.total_questions = 0
        self.correct_answers = 0
        self.remaining_time = self.GAME_TIME
        self.game_active = True
        
        # Update display
        self.update_stats_display()
        self.timer_label.text = f"Time: {self.remaining_time}s"
        self.timer_label.color = (0.2, 0.4, 0.8, 1)
        self.feedback_label.text = ""
        self.answer_input.disabled = False
        self.answer_input.focus = True
        
        # Set button back to submit function
        self.action_button.text = "Submit Answer"
        self.action_button.background_color = (0.2, 0.4, 0.8, 1)
        try:
            self.action_button.unbind(on_press=self.reset_to_settings)
        except:
            pass
        self.action_button.bind(on_press=self.check_answer)

        # Start timer
        if self.timer_event: self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)
        self.generate_question()

    def update_timer(self, dt):
        """Called every second to update the timer."""
        self.remaining_time -= 1
        self.timer_label.text = f"Time: {self.remaining_time}s"
        if self.remaining_time <= 5: self.timer_label.color = (0.9, 0.2, 0.1, 1)
        if self.remaining_time <= 0: self.end_game()

    def generate_question(self):
        """Creates a new question based on the game mode."""
        op_mode = self.GAME_MODE
        if op_mode == 'mixed':
            op_mode = random.choice(['addition', 'subtraction'])

        if op_mode == 'addition':
            num1 = random.randint(self.MIN_NUM, self.MAX_NUM)
            num2 = random.randint(self.MIN_NUM, self.MAX_NUM)
            self.current_answer = num1 + num2
            self.question_label.text = f"{num1} + {num2} = ?"
        elif op_mode == 'subtraction':
            a = random.randint(self.MIN_NUM, self.MAX_NUM)
            b = random.randint(self.MIN_NUM, self.MAX_NUM)
            # Ensure the result is not negative
            num1, num2 = max(a, b), min(a, b)
            self.current_answer = num1 - num2
            self.question_label.text = f"{num1} - {num2} = ?"
            
        self.answer_input.text = ""

    def check_answer(self, *args):
        """Checks the answer entered by the user."""
        if not self.game_active: return
        try:
            user_answer = int(self.answer_input.text)
            self.total_questions += 1
            if user_answer == self.current_answer:
                self.score += 10
                self.correct_answers += 1
                self.feedback_label.text = "Correct! +10 Points"; self.feedback_label.color = (0.1, 0.6, 0.2, 1)
            else:
                self.feedback_label.text = f"Wrong! The answer was: {self.current_answer}"; self.feedback_label.color = (0.9, 0.2, 0.1, 1)
        except ValueError:
            self.total_questions += 1
            self.feedback_label.text = "Invalid input."; self.feedback_label.color = (0.9, 0.2, 0.1, 1)
        self.update_stats_display()
        self.generate_question()

    def update_stats_display(self):
        """Updates the score and accuracy labels."""
        self.score_label.text = f"Score: {self.score}"
        if self.total_questions > 0:
            accuracy = (self.correct_answers / self.total_questions) * 100
            self.accuracy_label.text = f"Accuracy: {accuracy:.1f}%"
        else:
            self.accuracy_label.text = "Accuracy: -"

    def end_game(self):
        """Ends the game and shows the 'Play Again' option."""
        self.game_active = False
        if self.timer_event: self.timer_event.cancel()
        self.question_label.text = "Time's Up!"
        self.feedback_label.text = f"Final Score: {self.score}"
        self.feedback_label.color = (0.1, 0.1, 0.1, 1)
        self.answer_input.disabled = True
        
        # Change the button function to return to the menu
        self.action_button.text = "Play Again"
        self.action_button.background_color = (0.1, 0.6, 0.2, 1)
        self.action_button.unbind(on_press=self.check_answer)
        self.action_button.bind(on_press=self.reset_to_settings)

    def reset_to_settings(self, instance):
        """Switches back to the settings screen."""
        self.manager.current = 'settings'

class MathGameApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    MathGameApp().run()
