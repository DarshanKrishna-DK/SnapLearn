from manim import *

class ThumbnailScene(Scene):
    def construct(self):
        # Background
        bg = Rectangle(width=16, height=9, fill_color=DARK_BLUE, fill_opacity=1)
        self.add(bg)
        
        # Main title
        title = Text("Division Basics", font_size=48, color=WHITE, weight=BOLD)
        title.move_to(UP * 1.5)
        self.add(title)
        
        # Visual elements based on content
        
        
        
        
        # SnapLearn branding
        brand = Text("SnapLearn AI", font_size=24, color=YELLOW)
        brand.move_to(DOWN * 3.5 + RIGHT * 5)
        self.add(brand)
