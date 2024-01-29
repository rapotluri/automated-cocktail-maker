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

    def on_touch_down(self, touch):
        App.get_running_app().reset_inactivity_timer()
        return super().on_touch_down(touch)

    def select_drink(self, drink_name):
        # Open the confirmation popup
        popup = ConfirmPopup(drink_name)
        popup.open()
    
    def proceed_with_drink(self, drink_name):
        # User has accepted the confirmation, switch to the loading screen
        print(f"Preparing {drink_name}...")
        self.manager.current = 'loading'

class ConfirmPopup(Popup):
    def __init__(self, drink_name, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.8, 0.5)
        self.title = 'Confirm Drink Selection'
        self.drink_name = drink_name
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        message = Label(text=f'Would you like to prepare {self.drink_name}?')
        button_layout = BoxLayout(height=50, size_hint_y=None)
        
        accept_button = Button(text='Accept', on_release=self.accept)
        decline_button = Button(text='Decline', on_release=self.dismiss_popup)
        
        button_layout.add_widget(accept_button)
        button_layout.add_widget(decline_button)
        
        content.add_widget(message)
        content.add_widget(button_layout)
        
        self.content = content

    def accept(self, instance):
        # Proceed with preparing the drink
        self.dismiss()
        App.get_running_app().root.get_screen('drink_selection').proceed_with_drink(self.drink_name)

    def dismiss_popup(self, instance):
        # Dismiss the popup
        self.dismiss()

class LoadingScreen(Screen):
    def __init__(self, **kwargs):
        super(LoadingScreen, self).__init__(**kwargs)

        # Draw the loading bar first so it's behind the background image
        with self.canvas.before:
            self.color_instruction = Color(0, 1, 0, 1)  # Green color for the loading bar
            self.loading_bar = Rectangle(size=(0, 500), pos=(self.x, 20))

        # Then draw the background image on top of the loading bar
        with self.canvas.before:
            # Reset the color to white for the background image
            Color(1, 1, 1, 1)
            self.bg = Rectangle(source='loading.png', size=Window.size)

        # Animate the loading bar on entering the screen
        self.bind(size=self.update_bg, pos=self.update_bg)

    def update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos
        # Update the loading bar's position as well
        self.loading_bar.pos = (self.x, 20)

    def animate_background(self):
        # Start the animation with the width of the loading bar being zero
        self.loading_bar.size = (0, 500)
        # Animate the width of the loading bar to match the width of the window
        anim = Animation(size=(Window.width, 500), duration=10)
        anim.start(self.loading_bar)

    def on_enter(self, *args):
        self.animate_background()
        # After 5 seconds, simulate the drink being ready
        Clock.schedule_once(lambda dt: self.finished_loading(), 10)

    def finished_loading(self, *args):
        self.manager.current = 'screensaver'

    def on_leave(self, *args):
        # Reset the loading bar size when leaving the screen
        self.loading_bar.size = (0, 50)



class CocktailMakerApp(App):
    inactivity_time = 30  # Inactivity timeout in seconds

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(ScreensaverScreen(name='screensaver'))
        self.sm.add_widget(DrinkSelectionScreen(name='drink_selection'))
        self.sm.add_widget(LoadingScreen(name='loading'))  # Ensure this line is present
        self.reset_inactivity_timer()  # Start the inactivity timer
        return self.sm

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
