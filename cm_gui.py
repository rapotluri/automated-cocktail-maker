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
        super(AnimatedBackground, self).__init__(**kwargs)
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

        super(ScreensaverScreen, self).on_enter(*args)

    def on_touch_down(self, touch):
        App.get_running_app().sm.current = 'drink_selection'
        return super().on_touch_down(touch)

class ImageButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(ImageButton, self).__init__(**kwargs)
        self.always_release = True
        self.default_opacity = self.opacity

    def on_press(self):
        self.opacity = 0.7

    def on_release(self):
        self.opacity = self.default_opacity

class CustomScrollView(ScrollView):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.ud['is_scroll'] = False
            return super(CustomScrollView, self).on_touch_down(touch)
        return False

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            touch.ud['is_scroll'] = True
            return super(CustomScrollView, self).on_touch_move(touch)
        return False

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and touch.ud.get('is_scroll'):
            return super(CustomScrollView, self).on_touch_up(touch)
        elif self.collide_point(*touch.pos):
            for child in self.children:
                if child.dispatch('on_touch_up', touch):
                    break
        return False

class DrinkSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super(DrinkSelectionScreen, self).__init__(**kwargs)
        # Adjust the GridLayout for horizontal orientation
        self.layout = GridLayout(rows=1, spacing=10, size_hint_x=None)
        self.layout.bind(minimum_width=self.layout.setter('width'))

        drinks = {
            "Rum & Coke": "icons/rumcoke.png",
            "Vodka Cranberry": "icons/vodkacran.png",
            "Whiskey Iced Tea": "icons/wit.png",
            "Vodka Iced Tea": "icons/vit.png",
            "Whiskey & Coke": "icons/whiskeycoke.png",
            "Cranberry Rum": "icons/cranbrum.png"
        }

        for drink, img_path in drinks.items():
            # Set the width of the buttons based on the number of drinks
            btn_width = Window.width / 2.5  # Adjust this to change the button width
            btn = ImageButton(source=img_path, size_hint=(None, None), size=(btn_width, btn_width), allow_stretch=True)
            btn.id = drink
            btn.bind(on_release=self.select_drink)
            self.layout.add_widget(btn)

        # Adjust the ScrollView for horizontal scrolling
        scroll_view = CustomScrollView(size_hint=(None, 1), size=(Window.width, Window.height), do_scroll_x=True, do_scroll_y=False)
        scroll_view.add_widget(self.layout)
        self.add_widget(scroll_view)

    def select_drink(self, instance):
        print(f"{instance.id} selected")


class CocktailMakerApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(ScreensaverScreen(name='screensaver'))
        self.sm.add_widget(DrinkSelectionScreen(name='drink_selection'))
        return self.sm

if __name__ == '__main__':
    CocktailMakerApp().run()
