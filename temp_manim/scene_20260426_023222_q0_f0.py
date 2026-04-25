from manim import *

class FractionsBasics(Scene):
    def construct(self):
        self.camera.background_color = "#FDF6E3" # Warm, light background

        # --- Scene 1: Introduction to a Whole ---
        title = Text("What are Fractions?", font_size=48, color=BLACK).to_edge(UP)
        self.play(FadeIn(title))
        self.wait(0.5)

        whole_shape = Circle(radius=1.5, color=BLUE_E, fill_opacity=0.2).center()
        whole_label = Text("This is 1 WHOLE!", font_size=36, color=BLACK).next_to(whole_shape, DOWN, buff=0.5)
        
        self.play(Create(whole_shape))
        self.play(Write(whole_label))
        self.wait(1)

        # --- Scene 2: Dividing the Whole (Denominator) ---
        self.play(FadeOut(whole_label))

        explanation_text = Text("Fractions are parts of a whole.", font_size=32, color=BLACK).next_to(whole_shape, DOWN, buff=0.5)
        self.play(Write(explanation_text))
        self.wait(1)

        # Divide the circle into 4 equal parts
        sector1 = Sector(outer_radius=1.5, start_angle=0, angle=PI/2, color=BLUE_E, fill_opacity=0.2, stroke_color=BLUE_D)
        sector2 = Sector(outer_radius=1.5, start_angle=PI/2, angle=PI/2, color=BLUE_E, fill_opacity=0.2, stroke_color=BLUE_D)
        sector3 = Sector(outer_radius=1.5, start_angle=PI, angle=PI/2, color=BLUE_E, fill_opacity=0.2, stroke_color=BLUE_D)
        sector4 = Sector(outer_radius=1.5, start_angle=3*PI/2, angle=PI/2, color=BLUE_E, fill_opacity=0.2, stroke_color=BLUE_D)
        
        divided_shape = VGroup(sector1, sector2, sector3, sector4).center()

        self.play(Transform(whole_shape, divided_shape), FadeOut(explanation_text))
        self.wait(0.5)

        denominator_text = Text("We divided it into 4 EQUAL parts.", font_size=32, color=BLACK).next_to(divided_shape, DOWN, buff=0.5)
        self.play(Write(denominator_text))
        self.wait(1)
        
        denominator_label = Text("The DENOMINATOR (bottom number) tells us the TOTAL number of equal parts.", font_size=28, color=DARK_BLUE).to_edge(DOWN)
        self.play(Write(denominator_label))
        self.wait(1.5)

        # --- Scene 3: Selecting Parts (Numerator) ---
        self.play(FadeOut(denominator_text))

        # Highlight one part
        highlight_sector = Sector(outer_radius=1.5, start_angle=0, angle=PI/2, color=GREEN_E, fill_opacity=0.7, stroke_color=GREEN_D).center()
        
        self.play(Transform(sector1, highlight_sector))
        self.wait(0.5)

        numerator_text = Text("We are looking at 1 of these parts.", font_size=32, color=BLACK).next_to(divided_shape, DOWN, buff=0.5)
        self.play(Write(numerator_text))
        self.wait(1)

        numerator_label = Text("The NUMERATOR (top number) tells us how many parts we are looking at.", font_size=28, color=DARK_GREEN).to_edge(DOWN)
        self.play(Transform(denominator_label, numerator_label)) # Transform to save space and keep focus
        self.wait(1.5)

        # --- Scene 4: Putting it Together (The Fraction) ---
        self.play(FadeOut(numerator_text))

        # Create the fraction 1/4
        num_1 = Text("1", font_size=50, color=DARK_GREEN)
        line = Line(LEFT * 0.7, RIGHT * 0.7, color=BLACK)
        den_4 = Text("4", font_size=50, color=DARK_BLUE)
        
        fraction_group = VGroup(num_1, line, den_4).arrange(DOWN, buff=0.1).next_to(divided_shape, RIGHT, buff=1.0)
        
        self.play(
            FadeOut(denominator_label), # Fade out the transformed label
            Write(num_1),
            ApplyMethod(divided_shape.shift, LEFT * 2), # Shift the circle slightly left
            run_time=1
        )
        self.play(Create(line))
        self.play(Write(den_4))
        self.wait(1)

        read_fraction_text = Text("This is called 'one fourth' or 'one quarter'.", font_size=32, color=BLACK).next_to(fraction_group, DOWN, buff=0.5)
        self.play(Write(read_fraction_text))
        self.wait(1.5)

        # --- Scene 5: Quick Example/Review ---
        self.play(FadeOut(read_fraction_text, title))

        # New example: 2/3
        square_whole = Square(side_length=2, color=BLUE_E, fill_opacity=0.2, stroke_color=BLUE_D).center()
        line1 = Line(square_whole.get_corner(UL), square_whole.get_corner(DR), color=BLUE_D)
        line2 = Line(square_whole.get_corner(DL), square_whole.get_corner(UR), color=BLUE_D)
        
        # Approximate division into 3 parts visually
        rect1 = Rectangle(width=2, height=2/3, color=BLUE_E, fill_opacity=0.2, stroke_color=BLUE_D).align_to(square_whole, UP)
        rect2 = Rectangle(width=2, height=2/3, color=BLUE_E, fill_opacity=0.2, stroke_color=BLUE_D).move_to(square_whole.get_center())
        rect3 = Rectangle(width=2, height=2/3, color=BLUE_E, fill_opacity=0.2, stroke_color=BLUE_D).align_to(square_whole, DOWN)
        
        divided_square = VGroup(rect1, rect2, rect3).arrange(DOWN, buff=0).move_to(divided_shape.get_center())
        
        self.play(Transform(divided_shape, divided_square))
        self.wait(0.5)

        # Shade 2 parts
        shaded_rect1 = rect1.copy().set_color(GREEN_E).set_fill(GREEN_E, opacity=0.7)
        shaded_rect2 = rect2.copy().set_color(GREEN_E).set_fill(GREEN_E, opacity=0.7)
        
        self.play(Transform(rect1, shaded_rect1), Transform(rect2, shaded_rect2))
        self.wait(0.5)

        # New fraction 2/3
        new_num = Text("2", font_size=50, color=DARK_GREEN)
        new_line = Line(LEFT * 0.7, RIGHT * 0.7, color=BLACK)
        new_den = Text("3", font_size=50, color=DARK_BLUE)
        
        new_fraction_group = VGroup(new_num, new_line, new_den).arrange(DOWN, buff=0.1).move_to(fraction_group)
        
        self.play(Transform(fraction_group, new_fraction_group))
        self.wait(1)

        question = Text("What fraction is this?", font_size=36, color=BLACK).to_edge(DOWN)
        self.play(Write(question))
        self.wait(2) # Allow time for the student to think

        self.play(FadeOut(question, divided_shape, fraction_group))
        self.wait(0.5)

        # Final message
        good_job = Text("Great job learning about fractions!", font_size=40, color=BLACK).center()
        self.play(Write(good_job))
        self.wait(1)

        self.play(FadeOut(good_job))
        self.wait(0.5)