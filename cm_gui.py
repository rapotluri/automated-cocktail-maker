from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.config import Config
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

# Configure the app to full screen, suitable for a 5-inch display
Config.set('graphics', 'fullscreen', 'auto')


class AnimatedBackground(Screen):
    def __init__(self, **kwargs):
        super(AnimatedBackground, self).__init__(**kwargs)
        with self.canvas.before:
            self.color = Color(1, 0, 0, 1)  # Initial color red
            self.rect = Rectangle(size=Window.size)

        # Animate background color
        self.animate_background()

    def animate_background(self):
        # Create an animation sequence to change the color
        anim = Animation(color=(0, 1, 0, 1), duration=2) + \
               Animation(color=(0, 0, 1, 1), duration=2) + \
               Animation(color=(1, 1, 0, 1), duration=2) + \
               Animation(color=(1, 0, 1, 1), duration=2)
        anim.repeat = True
        anim.start(self.color)


class ScreensaverScreen(Screen):
    def on_enter(self, *args):
        # Add animated background first
        self.animated_background = AnimatedBackground()
        self.add_widget(self.animated_background)

        # Then add your screensaver image on top
        self.screensaver_image = Image(source='your_screensaver_image.png', allow_stretch=True)
        self.screensaver_image.size = Window.size
        self.add_widget(self.screensaver_image)

        super(ScreensaverScreen, self).on_enter(*args)

    def on_touch_down(self, touch):
        app.sm.current = 'drink_selection'
        return super().on_touch_down(touch)


class DrinkSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super(DrinkSelectionScreen, self).__init__(**kwargs)
        layout = GridLayout(cols=2, padding=10, spacing=10)

        # Add buttons for each drink
        for drink in ["Rum & Coke", "Vodka Cranberry", "Whiskey Iced Tea",
                      "Vodka Iced Tea", "Rum Cranberry", "Whiskey & Coke"]:
            btn = Button(text=drink, on_press=self.select_drink)
            layout.add_widget(btn)

        self.add_widget(layout)

    def select_drink(self, instance):
        print(f"{instance.text} selected")  # Replace with GPIO control logic



class CocktailMakerApp(App):
    def build(self):
        global app
        app = self
        self.sm = ScreenManager()
        self.sm.add_widget(ScreensaverScreen(name='screensaver'))
        self.sm.add_widget(DrinkSelectionScreen(name='drink_selection'))
        return self.sm


if __name__ == '__main__':
    CocktailMakerApp().run()
