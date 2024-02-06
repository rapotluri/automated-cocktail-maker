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
    "Rum": 9,
    "Coke": 27,
    "Vodka": 2,
    "Cranberry": 17,
    "Whiskey": 3,
    "Iced Tea": 4,
    "Sprite": 22
}
for pin in beverage_to_motor_map.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)  # HIGH signal deactivates relay



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
        
        accept_btn = Button(text='Accept', on_release=self._on_accept)
        decline_btn = Button(text='Decline', on_release=self.dismiss)
        
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
            "Cranberry Rum": "icons/cranbrum.png",
            "Vodka Soda": "icons/vs.png"
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
        "Rum & Coke": {"Rum": 20, "Coke": 60},
        "Vodka Cranberry": {"Vodka": 20, "Cranberry": 60},
        "Whiskey Iced Tea": {"Whiskey": 20, "Iced Tea": 60},
        "Vodka Iced Tea": {"Vodka": 20, "Iced Tea": 60},
        "Whiskey & Coke": {"Whiskey": 20, "Coke": 60},
        "Cranberry Rum": {"Rum": 20, "Cranberry": 60},
        "Vodka Soda": {"Vodka": 20, "Sprite": 60}
    }

    def on_enter(self, *args):
        super(DrinkSelectionScreen, self).on_enter(*args)
        # Reset the inactivity timer every time the drink selection screen is entered
        App.get_running_app().reset_inactivity_timer()
    

    def on_touch_down(self, touch):
        App.get_running_app().reset_inactivity_timer()
        return super().on_touch_down(touch)
    

    def select_drink(self, drink_name):
        def on_confirm():
            # Calculate total duration for the loading animation based on the recipe
            total_duration = max(self.drinks_recipe[drink_name].values())
            # Start preparing the drink in a separate thread
            threading.Thread(target=self.prepare_drink, args=(drink_name, total_duration)).start()

        # Show confirmation popup
        popup = ConfirmPopup(drink_name, on_confirm)
        popup.open()

    def prepare_drink(self, drink_name, total_duration):
        # Ensure GPIO operations are handled in the main thread if needed
        recipe = self.drinks_recipe[drink_name]

        # Start all motors for the drink simultaneously
        for beverage, _ in recipe.items():
            motor_pin = beverage_to_motor_map[beverage]
            GPIO.output(motor_pin, GPIO.LOW)  # Start motor
        
        # Show loading screen with the total duration
        Clock.schedule_once(lambda dt: App.get_running_app().show_loading_screen(total_duration), 0)

        # Schedule all motors to stop after their respective durations
        for beverage, duration in recipe.items():
            motor_pin = beverage_to_motor_map[beverage]
            Clock.schedule_once(lambda dt, pin=motor_pin: self.stop_motor(pin), duration)

    def stop_motor(self, motor_pin):
        # This function will be called to stop each motor after its duration
        GPIO.output(motor_pin, GPIO.HIGH)  # Stop the motor

    


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
    inactivity_event = None

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(ScreensaverScreen(name='screensaver'))
        self.sm.add_widget(DrinkSelectionScreen(name='drink_selection'))
        self.sm.add_widget(LoadingScreen(name='loading'))  # Ensure this line is present
        self.reset_inactivity_timer()  # Start the inactivity timer
        return self.sm
    
    def show_loading_screen(self, duration):
        # Ensure we're pausing the inactivity timer when loading starts
        Clock.schedule_once(lambda dt: self.pause_inactivity_timer(), 0)

        if self.sm.current != 'loading':
            self.sm.current = 'loading'
            loading_screen = self.sm.get_screen('loading')
            loading_screen.start_loading_animation(duration)
            # Ensure we're resuming the inactivity timer after loading completes
            Clock.schedule_once(lambda dt: self.reset_inactivity_timer(), duration)


    def finish_drink_preparation(self):
        # Check if we need to transition back to the screensaver
        if self.sm.current == 'loading':
            self.sm.current = 'screensaver'

    def reset_inactivity_timer(self):
        # Cancel any existing inactivity event
        if self.inactivity_event:
            self.inactivity_event.cancel()
        # Schedule a new inactivity event
        self.inactivity_event = Clock.schedule_once(self.go_to_screensaver, self.inactivity_time)

    def pause_inactivity_timer(self):
            # Cancel any existing inactivity event without rescheduling
            if self.inactivity_event:
                self.inactivity_event.cancel()
            self.inactivity_event = None


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
