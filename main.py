import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
import threading
import random
import requests
import time

# Set theme colors
BACKGROUND_COLOR = get_color_from_hex('#212121')
PRIMARY_COLOR = get_color_from_hex('#2196F3')
TEXT_COLOR = get_color_from_hex('#FFFFFF')
SECONDARY_COLOR = get_color_from_hex('#757575')

# Set default window size for testing
Window.size = (360, 640)
Window.clearcolor = BACKGROUND_COLOR

class CustomButton(Button):
    def __init__(self, **kwargs):
        super(CustomButton, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_color = PRIMARY_COLOR
        self.color = TEXT_COLOR
        self.size_hint_y = None
        self.height = dp(50)
        self.font_size = dp(16)

class CustomTextInput(TextInput):
    def __init__(self, **kwargs):
        super(CustomTextInput, self).__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(40)
        self.multiline = False
        self.padding = [dp(10), dp(10), dp(10), dp(10)]
        self.background_color = SECONDARY_COLOR
        self.foreground_color = TEXT_COLOR
        self.cursor_color = TEXT_COLOR
        self.font_size = dp(16)

class CustomLabel(Label):
    def __init__(self, **kwargs):
        super(CustomLabel, self).__init__(**kwargs)
        self.color = TEXT_COLOR
        self.font_size = dp(16)
        self.size_hint_y = None
        self.height = dp(30)
        self.halign = 'left'
        self.valign = 'middle'
        self.text_size = (Window.width - dp(40), None)

class WordWallAPI:
    @staticmethod
    def generate_random_number(min_val, max_val):
        return str(random.randint(min_val, max_val))
    
    @staticmethod
    def find_template_id(game_id):
        try:
            url = f"https://wordwall.net/resource/{game_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                'Pragma': 'no-cache',
                'Accept': '*/*'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response_text = response.text

            start = 's.templateId=Number('
            end = ');s.feedbackTemplateId='

            start_index = response_text.find(start)
            end_index = response_text.find(end, start_index)

            if start_index != -1 and end_index != -1:
                start_index += len(start)
                template_id = response_text[start_index:end_index].strip()
                return template_id
            else:
                return None
        except Exception as e:
            return None
    
    @staticmethod
    def submit_score(score, nickname, game_id, template_id, time_ms, multiple=False):
        try:
            url = "https://wordwall.net/leaderboardajax/addentry"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                'Pragma': 'no-cache',
                'Accept': '*/*'
            }
            
            if multiple:
                results = []
                for _ in range(20):  # Submit 20 scores
                    random_suffix = WordWallAPI.generate_random_number(10, 999)
                    data = {
                        'score': score,
                        'time': time_ms,
                        'name': nickname + random_suffix,
                        'mode': '1',
                        'activityId': game_id,
                        'templateId': template_id
                    }
                    
                    response = requests.post(url, headers=headers, data=data, timeout=10)
                    results.append(response.text)
                    time.sleep(0.2)  # Add small delay
                
                return "Multiple scores submitted successfully"
            else:
                data = {
                    'score': score,
                    'time': time_ms,
                    'name': nickname,
                    'mode': '1',
                    'activityId': game_id,
                    'templateId': template_id
                }
                
                response = requests.post(url, headers=headers, data=data, timeout=10)
                return response.text
        except Exception as e:
            return f"Error: {str(e)}"

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        title = CustomLabel(text="WordWall Score App", font_size=dp(24), height=dp(40))
        title.halign = 'center'
        
        find_template_btn = CustomButton(text="Find Template ID")
        find_template_btn.bind(on_release=lambda x: self.manager.transition.direction = 'left' or self.manager.current == 'template')
        
        submit_score_btn = CustomButton(text="Submit Score")
        submit_score_btn.bind(on_release=lambda x: self.manager.transition.direction = 'left' or self.manager.current == 'score')
        
        layout.add_widget(title)
        layout.add_widget(Label(size_hint_y=None, height=dp(20)))  # Spacing
        layout.add_widget(find_template_btn)
        layout.add_widget(submit_score_btn)
        
        self.add_widget(layout)

class TemplateScreen(Screen):
    def __init__(self, **kwargs):
        super(TemplateScreen, self).__init__(**kwargs)
        
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        title = CustomLabel(text="Find Template ID", font_size=dp(24), height=dp(40))
        title.halign = 'center'
        
        self.game_id_input = CustomTextInput(hint_text="Game ID")
        
        find_btn = CustomButton(text="Find Template")
        find_btn.bind(on_release=self.find_template)
        
        self.result_label = CustomLabel(text="", height=dp(60))
        self.result_label.halign = 'center'
        
        back_btn = CustomButton(text="Back")
        back_btn.bind(on_release=lambda x: self.manager.transition.direction == 'right' or setattr(self.manager, 'current', 'home'))
        
        use_template_btn = CustomButton(text="Use Template ID")
        use_template_btn.bind(on_release=self.use_template)
        
        self.layout.add_widget(title)
        self.layout.add_widget(Label(size_hint_y=None, height=dp(20)))  # Spacing
        self.layout.add_widget(CustomLabel(text="Enter Game ID:"))
        self.layout.add_widget(self.game_id_input)
        self.layout.add_widget(find_btn)
        self.layout.add_widget(self.result_label)
        self.layout.add_widget(use_template_btn)
        self.layout.add_widget(Label(size_hint_y=1))  # Spacer
        self.layout.add_widget(back_btn)
        
        self.add_widget(self.layout)
        
        self.template_id = None
        self.game_id = None
    
    def find_template(self, instance):
        game_id = self.game_id_input.text.strip()
        
        if not game_id:
            self.result_label.text = "Please enter a Game ID"
            return
        
        self.result_label.text = "Finding template ID..."
        
        def find_template_thread():
            template_id = WordWallAPI.find_template_id(game_id)
            
            if template_id:
                self.template_id = template_id
                self.game_id = game_id
                self.result_label.text = f"Template ID: {template_id}"
            else:
                self.result_label.text = "Template ID not found"
        
        threading.Thread(target=find_template_thread).start()
    
    def use_template(self, instance):
        if self.template_id and self.game_id:
            score_screen = self.manager.get_screen('score')
            score_screen.template_id_input.text = self.template_id
            score_screen.game_id_input.text = self.game_id
            self.manager.transition.direction = 'left'
            self.manager.current = 'score'
        else:
            self.result_label.text = "Find a template ID first"

class ScoreScreen(Screen):
    def __init__(self, **kwargs):
        super(ScoreScreen, self).__init__(**kwargs)
        
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        title = CustomLabel(text="Submit Score", font_size=dp(24), height=dp(40))
        title.halign = 'center'
        
        self.score_input = CustomTextInput(hint_text="Score")
        self.nickname_input = CustomTextInput(hint_text="Nickname")
        self.game_id_input = CustomTextInput(hint_text="Game ID")
        self.template_id_input = CustomTextInput(hint_text="Template ID")
        self.time_input = CustomTextInput(hint_text="Time in seconds")
        
        submit_one_btn = CustomButton(text="Submit Single Score")
        submit_one_btn.bind(on_release=lambda x: self.submit_score(False))
        
        submit_many_btn = CustomButton(text="Submit Multiple Scores")
        submit_many_btn.bind(on_release=lambda x: self.submit_score(True))
        
        self.result_label = CustomLabel(text="", height=dp(60))
        self.result_label.halign = 'center'
        
        back_btn = CustomButton(text="Back")
        back_btn.bind(on_release=lambda x: self.manager.transition.direction == 'right' or setattr(self.manager, 'current', 'home'))
        
        self.layout.add_widget(title)
        self.layout.add_widget(Label(size_hint_y=None, height=dp(10)))  # Spacing
        self.layout.add_widget(CustomLabel(text="Score:"))
        self.layout.add_widget(self.score_input)
        self.layout.add_widget(CustomLabel(text="Nickname:"))
        self.layout.add_widget(self.nickname_input)
        self.layout.add_widget(CustomLabel(text="Game ID:"))
        self.layout.add_widget(self.game_id_input)
        self.layout.add_widget(CustomLabel(text="Template ID:"))
        self.layout.add_widget(self.template_id_input)
        self.layout.add_widget(CustomLabel(text="Time (seconds):"))
        self.layout.add_widget(self.time_input)
        self.layout.add_widget(submit_one_btn)
        self.layout.add_widget(submit_many_btn)
        self.layout.add_widget(self.result_label)
        self.layout.add_widget(Label(size_hint_y=1))  # Spacer
        self.layout.add_widget(back_btn)
        
        self.add_widget(self.layout)
    
    def validate_inputs(self):
        score = self.score_input.text.strip()
        nickname = self.nickname_input.text.strip()
        game_id = self.game_id_input.text.strip()
        template_id = self.template_id_input.text.strip()
        time_seconds = self.time_input.text.strip()
        
        if not all([score, nickname, game_id, template_id, time_seconds]):
            self.result_label.text = "All fields are required"
            return None
        
        try:
            time_ms = str(int(float(time_seconds) * 1000))
        except ValueError:
            self.result_label.text = "Time must be a number"
            return None
        
        return {
            'score': score,
            'nickname': nickname,
            'game_id': game_id,
            'template_id': template_id,
            'time_ms': time_ms
        }
    
    def submit_score(self, multiple):
        input_data = self.validate_inputs()
        
        if not input_data:
            return
        
        self.result_label.text = "Submitting score(s)..."
        
        def submit_score_thread():
            result = WordWallAPI.submit_score(
                input_data['score'],
                input_data['nickname'],
                input_data['game_id'],
                input_data['template_id'],
                input_data['time_ms'],
                multiple
            )
            
            self.result_label.text = "Success!" if "Success" in result or multiple else "Failed"
        
        threading.Thread(target=submit_score_thread).start()

class WordWallApp(App):
    def build(self):
        sm = ScreenManager()
        
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(TemplateScreen(name='template'))
        sm.add_widget(ScoreScreen(name='score'))
        
        return sm

if __name__ == "__main__":
    WordWallApp().run()