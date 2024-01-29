from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior   
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
    
class ImageButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(ImageButton, self).__init__(**kwargs)
        self.always_release = True
        self.default_opacity = self.opacity

    def on_press(self):
        # Reduce opacity to 70% when pressed
        self.opacity = 0.7

    def on_release(self):
        # Return to original opacity
        self.opacity = self.default_opacity


class DrinkSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super(DrinkSelectionScreen, self).__init__(**kwargs)
        # Create a GridLayout within a ScrollView
        self.layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        # Dictionary of drinks and their corresponding image paths
        drinks = {
            "Rum & Coke": "icons/rumcoke.png",
            "Vodka Cranberry": "icons/vodkacran.png",
            "Whiskey Iced Tea": "icons/wit.png",
            "Vodka Iced Tea": "icons/vit.png",
            "Whiskey & Coke": "icons/whiskeycoke.png",
            "Cranberry Rum": "icons/cranbrum.png"
        }

        # Add image buttons for each drink
        for drink, img_path in drinks.items():
            btn = ImageButton(source=img_path, size_hint_y=None, height=150)
            btn.id = drink
            btn.bind(on_release=lambda btn: self.select_drink(btn))
            self.layout.add_widget(btn)

        # Create the scroll view and add the layout to it
        scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        scroll_view.add_widget(self.layout)
        self.add_widget(scroll_view)

    def button_press(self, instance):
        instance.opacity = 0.7  # Dim the button

    def button_release(self, instance):
        instance.opacity = 1  # Return to full opacity
        self.select_drink(instance)

    def select_drink(self, instance):
        print(f"{instance.id} selected")  # Print the selected drink's name

    



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
