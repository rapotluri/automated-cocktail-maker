from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.animation import Animation
from kivy.config import Config
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
import RPi.GPIO as GPIO
import threading

GPIO.setmode(GPIO.BCM)
beverage_to_motor_map = {
    "Rum": 2,
    "Coke": 3,
    "Vodka": 4,
    "Cranberry": 17,
    "Whiskey": 27,
    "Iced Tea": 22
}
for pin in beverage_to_motor_map.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)  # Assuming HIGH signal deactivates relay



# Configure the app to full screen, suitable for a 5-inch display
Config.set('graphics', 'fullscreen', 'auto')

class AnimatedBackground(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.color_instruction = Color(1, 0, 0, 1)
            self.rect = Rectangle(size=Window.size)
        self.animate_background()

    def animate_background(self):
        anim = Animation(rgba=(0, 1, 0, 1), duration=4) + \
               Animation(rgba=(0, 0, 1, 1), duration=4) + \
               Animation(rgba=(1, 1, 0, 1), duration=4) + \
               Animation(rgba=(1, 0, 1, 1), duration=4)
        anim.repeat = True
        anim.start(self.color_instruction)

class ScreensaverScreen(Screen):
    def on_enter(self, *args):
        self.animated_background = AnimatedBackground()
        self.add_widget(self.animated_background)

        self.screensaver_image = Image(
            source='screensaver.png',
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 1)
        )
        self.screensaver_image.pos_hint = {'center_x': 0.5, 'center_y': 0.557}
        self.add_widget(self.screensaver_image)

    def on_touch_down(self, touch):
        self.manager.current = 'drink_selection'
        return super().on_touch_down(touch)

class ImageButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.always_release = True

    def on_press(self):
        self.opacity *= 0.7

    def on_release(self):
        self.opacity = 1

class ConfirmPopup(Popup):
    def __init__(self, drink_name, on_confirm, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.8, 0.4)
        self.title = f'Confirm {drink_name}'
        self.drink_name = drink_name
        self.on_confirm = on_confirm

        content = BoxLayout(orientation='vertical')
        message = Label(text=f'Prepare {self.drink_name}?')
        btn_layout = BoxLayout(size_hint_y=None, height='50dp')
        
        accept_btn = Button(text='Yes', on_release=self._on_accept)
        decline_btn = Button(text='No', on_release=self.dismiss)
        
        btn_layout.add_widget(accept_btn)
        btn_layout.add_widget(decline_btn)
        
        content.add_widget(message)
        content.add_widget(btn_layout)
        
        self.content = content

    def _on_accept(self, instance):
        self.dismiss()
        self.on_confirm()

class DrinkSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load the background image
        with self.canvas.before:
            self.bg = Rectangle(source='drinkbg.png', size=Window.size)   

        self.layout = GridLayout(rows=1, spacing=30, size_hint_x=None, padding=(30, 100, 30, 30))
        self.layout.bind(minimum_width=self.layout.setter('width'))

        
        drinks = {
            "Rum & Coke": "icons/rumcoke.png",
            "Vodka Cranberry": "icons/vodkacran.png",
            "Whiskey Iced Tea": "icons/wit.png",
            "Vodka Iced Tea": "icons/vit.png",
            "Whiskey & Coke": "icons/whiskeycoke.png",
            "Cranberry Rum": "icons/cranbrum.png"
        }
        

        btn_width = Window.width / 2.5
        for drink, img_path in drinks.items():
            btn = ImageButton(source=img_path, size_hint=(None, None), size=(btn_width, btn_width), allow_stretch=True)
            btn.bind(on_release=lambda btn, drink_name=drink: self.select_drink(drink_name))
            self.layout.add_widget(btn)

        scroll_view = ScrollView(size_hint=(None, None), size=(Window.width, Window.height), do_scroll_x=True, do_scroll_y=False)
        scroll_view.add_widget(self.layout)
        self.add_widget(scroll_view)


    drinks_recipe = {
        "Rum & Coke": {"Rum": 5, "Coke": 10},
        "Vodka Cranberry": {"Vodka": 5, "Cranberry": 5},
        "Whiskey Iced Tea": {"Whiskey": 5, "Iced Tea": 10},
    }
    

    def on_touch_down(self, touch):
        App.get_running_app().reset_inactivity_timer()
        return super().on_touch_down(touch)
    

    def select_drink(self, drink_name):
        def on_confirm():
            # Calculate total duration for the loading animation
            total_duration = sum(self.drinks_recipe[drink_name].values())
            # Show loading screen immediately with the correct duration
            App.get_running_app().show_loading_screen(total_duration)
            # Start preparing the drink in a separate thread
            threading.Thread(target=self.prepare_drink, args=(drink_name,)).start()

        popup = ConfirmPopup(drink_name, on_confirm)
        popup.open()
    
    def prepare_drink(self, drink_name):
        self.preparation_steps = self.calculate_preparation_steps(drink_name)
        self.next_step()

    def calculate_preparation_steps(self, drink_name):
        recipe = self.drinks_recipe[drink_name]
        steps = []
        for beverage, duration in recipe.items():
            motor_pin = beverage_to_motor_map[beverage]
            steps.append((motor_pin, duration))
        return steps

    def next_step(self, dt=None):
        if self.preparation_steps:
            motor_pin, duration = self.preparation_steps.pop(0)
            GPIO.output(motor_pin, GPIO.LOW)  # Start motor
            # Schedule the motor to stop after the duration
            Clock.schedule_once(lambda dt: self.stop_motor(motor_pin), duration)
        else:
            # All steps are done, finish preparation
            Clock.schedule_once(lambda dt: App.get_running_app().finish_drink_preparation(), 0)

    def stop_motor(self, motor_pin):
        GPIO.output(motor_pin, GPIO.HIGH)  # Stop motor
        # Proceed to the next step
        Clock.schedule_once(self.next_step, 0.5)  # Add a small delay before the next step



# class ConfirmPopup(Popup):
#     def __init__(self, drink_name, **kwargs):
#         super().__init__(**kwargs)
#         self.size_hint = (0.8, 0.5)
#         self.title = 'Confirm Drink Selection'
#         self.drink_name = drink_name
        
#         content = BoxLayout(orientation='vertical', padding=10, spacing=10)
#         message = Label(text=f'Would you like to prepare {self.drink_name}?')
#         button_layout = BoxLayout(height=50, size_hint_y=None)
        
#         accept_button = Button(text='Accept', on_release=self.accept)
#         decline_button = Button(text='Decline', on_release=self.dismiss_popup)
        
#         button_layout.add_widget(accept_button)
#         button_layout.add_widget(decline_button)
        
#         content.add_widget(message)
#         content.add_widget(button_layout)
        
#         self.content = content

#     def accept(self, instance):
#         # Proceed with preparing the drink
#         self.dismiss()
#         App.get_running_app().root.get_screen('drink_selection').proceed_with_drink(self.drink_name)

#     def dismiss_popup(self, instance):
#         # Dismiss the popup
#         self.dismiss()

class LoadingScreen(Screen):
    def __init__(self, **kwargs):
        super(LoadingScreen, self).__init__(**kwargs)
        with self.canvas.before:
            # Setup the loading bar with explicit dimensions and position
            self.color_instruction = Color(0, 1, 0, 1)  # Green for the loading bar
            # Adjust the position and size below as needed for your 5-inch display
            self.loading_bar_position = (150, 130)  # Example position
            self.loading_bar_height = 100  # Example height
            self.loading_bar_width = Window.width - 295  # Example width, adjust as needed
            self.loading_bar = Rectangle(pos=self.loading_bar_position, size=(0, self.loading_bar_height))
            
            # Background image
            Color(1, 1, 1, 1)
            self.bg = Rectangle(source='loading.png', size=Window.size, pos=self.pos)

    def start_loading_animation(self, duration):
        # Start with a width of 0 and animate to the full width
        self.loading_bar.size = (0, self.loading_bar_height)
        anim = Animation(size=(self.loading_bar_width, self.loading_bar_height), duration=(duration))
        anim.start(self.loading_bar)

    def update_bg(self, *args):
        # Keep the background image fitting the screen
        self.bg.size = self.size
        self.bg.pos = self.pos
        # The loading bar's position and size are fixed, so no need to update them here




class CocktailMakerApp(App):
    inactivity_time = 30  # Inactivity timeout in seconds

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(ScreensaverScreen(name='screensaver'))
        self.sm.add_widget(DrinkSelectionScreen(name='drink_selection'))
        self.sm.add_widget(LoadingScreen(name='loading'))  # Ensure this line is present
        self.reset_inactivity_timer()  # Start the inactivity timer
        return self.sm
    
    def show_loading_screen(self, duration):
        if self.sm.current != 'loading':
            self.sm.current = 'loading'
            loading_screen = self.sm.get_screen('loading')
            loading_screen.start_loading_animation(duration)

    def finish_drink_preparation(self):
        # Check if we need to transition back to the screensaver
        if self.sm.current == 'loading':
            self.sm.current = 'screensaver'

    def reset_inactivity_timer(self):
        # Reset the inactivity timer
        self.last_activity = Clock.get_boottime()
        Clock.unschedule(self.go_to_screensaver)
        Clock.schedule_once(self.go_to_screensaver, self.inactivity_time)

    def on_touch_down(self, touch):
        # Whenever there's a touch down event, reset the inactivity timer
        self.reset_inactivity_timer()
        return super(CocktailMakerApp, self).on_touch_down(touch)

    def go_to_screensaver(self, *args):
        # After inactivity, go to the screensaver screen
        if self.sm.current != 'screensaver':
            self.sm.current = 'screensaver'
            self.reset_inactivity_timer()

if __name__ == '__main__':
    CocktailMakerApp().run()
