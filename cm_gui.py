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

    def select_drink(self, drink_name):
        print(f"{drink_name} selected")

class CocktailMakerApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ScreensaverScreen(name='screensaver'))
        sm.add_widget(DrinkSelectionScreen(name='drink_selection'))
        return sm

if __name__ == '__main__':
    CocktailMakerApp().run()
