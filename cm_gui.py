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
            # Initial color red
            self.color_instruction = Color(1, 0, 0, 1)  
            self.rect = Rectangle(size=Window.size)

        # Animate background color
        self.animate_background()

    def animate_background(self):
        # Animate the rgba property of the color instruction
        anim = Animation(rgba=(0, 1, 0, 1), duration=4) + \
               Animation(rgba=(0, 0, 1, 1), duration=4) + \
               Animation(rgba=(1, 1, 0, 1), duration=4) + \
               Animation(rgba=(1, 0, 1, 1), duration=4)
        anim.repeat = True
        anim.start(self.color_instruction)


class ScreensaverScreen(Screen):
    def on_enter(self, *args):
        # Add animated background first
        self.animated_background = AnimatedBackground()
        self.add_widget(self.animated_background)

        # Then add your screensaver image on top
        self.screensaver_image = Image(
            source='screensaver.png',
            allow_stretch=True,  # Allow the image to be scaled
            keep_ratio=True,  # Keep the image's aspect ratio
            size_hint=(1, 1),  # The image will fill its parent
        )
        self.screensaver_image.pos_hint = {'center_x': 0.5, 'center_y': 0.557}
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
