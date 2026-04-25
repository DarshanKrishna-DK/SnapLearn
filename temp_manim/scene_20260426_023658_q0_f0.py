from manim import *

class DecimalsBasics(Scene):
    def construct(self):
        # --- Configuration ---
        title_color = BLUE_D
        text_color = WHITE
        highlight_color_1 = YELLOW_C
        highlight_color_2 = GREEN_C
        focus_color = RED_C
        # background_color = BLACK # Manim's default background is black, no need to explicitly set.

        # --- Scene 1: Introduction ---
        title = Text("Decimals: Parts of a Whole!", font_size=60, color=title_color)
        subtitle = Text("Grade 4 Basics", font_size=30, color=text_color).next_to(title, DOWN)

        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=UP))
        self.wait(1.5)
        self.play(FadeOut(title, shift=UP), FadeOut(subtitle, shift=UP))

        # --- Scene 2: What are Decimals? ---
        question = Text("What are decimals?", font_size=48, color=highlight_color_1).to_edge(UP)
        explanation_1 = Text("Decimals are a way to write parts of a whole number.", font_size=36, color=text_color).next_to(question, DOWN, buff=0.8)
        explanation_2 = Text("They use a decimal point to separate the whole part from the fractional part.", font_size=36, color=text_color).next_to(explanation_1, DOWN)

        self.play(Write(question))
        self.wait(0.5)
        self.play(FadeIn(explanation_1, shift=LEFT))
        self.play(FadeIn(explanation_2, shift=LEFT))
        self.wait(2)
        self.play(FadeOut(VGroup(question, explanation_1, explanation_2), shift=UP))

        # --- Scene 3: Connecting to Fractions (Tenths) ---
        frac_intro = Text("Let's connect decimals to fractions!", font_size=40, color=highlight_color_2).to_edge(UP)
        self.play(Write(frac_intro))
        self.wait(1)

        fraction_label = MathTex(r"\frac{1}{10}", font_size=90, color=text_color)

        # Visual for 1/10: A square divided into 10 columns, one highlighted
        square = Square(side_length=3, color=text_color).to_edge(LEFT, buff=1)
        # Vertical dividing lines
        div_lines = VGroup(*[Line(square.get_corner(DL) + RIGHT * (i * square.width / 10),
                                   square.get_corner(UL) + RIGHT * (i * square.width / 10))
                             for i in range(1, 10)]).set_opacity(0.5)
        # Rectangle representing one-tenth
        one_tenth_rect = Rectangle(width=square.width / 10, height=square.height,
                                   fill_opacity=0.7, color=focus_color).align_to(square, DL).shift(RIGHT * (square.width/20))

        self.play(Create(square), Create(div_lines))
        self.play(FadeIn(one_tenth_rect, shift=RIGHT))

        fraction_explanation = Text("This is 1 out of 10 equal parts.", font_size=30, color=text_color).next_to(square, DOWN)
        self.play(Write(fraction_explanation))
        self.wait(1)

        # Move the visual to the corner and introduce the fraction and decimal form
        self.play(FadeOut(fraction_explanation, shift=DOWN))
        self.play(
            one_tenth_rect.animate.move_to(square.get_center_of_mass()), # Center the highlight within the square
            square.animate.set_opacity(0.2).scale(0.5).to_corner(UL), # Shrink and move the whole square
            div_lines.animate.set_opacity(0.2).scale(0.5).to_corner(UL), # Shrink and move the lines
            one_tenth_rect.animate.scale(0.5).to_corner(UL).shift(RIGHT*0.1) # Move the highlight with the square
        )
        self.play(fraction_label.animate.move_to(ORIGIN)) # Bring fraction label to center
        self.wait(0.5)

        equals_sign = MathTex(r"=", font_size=90, color=text_color).next_to(fraction_label, RIGHT, buff=0.7)
        decimal_label = MathTex(r"0.1", font_size=90, color=text_color).next_to(equals_sign, RIGHT, buff=0.7)

        self.play(FadeIn(equals_sign, scale=0.5))
        self.play(Write(decimal_label))

        # Group everything and center it for better presentation
        final_frac_decimal_group = VGroup(fraction_label, equals_sign, decimal_label).center()
        # Re-center the group nicely, useful if elements shifted slightly
        self.play(Transform(VGroup(fraction_label, equals_sign, decimal_label), final_frac_decimal_group))

        self.wait(2)
        # Clean up the scene
        self.play(FadeOut(VGroup(frac_intro, final_frac_decimal_group, square, div_lines, one_tenth_rect), shift=DOWN))
        self.wait(0.5)

        # --- Scene 4: Place Value ---
        place_value_title = Text("Decimal Place Value", font_size=48, color=highlight_color_1).to_edge(UP)
        self.play(Write(place_value_title))
        self.wait(0.5)

        # Define place value texts
        ones_text = Text("Ones", color=text_color)
        decimal_point_text = Text(".", color=highlight_color_2).shift(UP * 0.05) # Adjust decimal point slightly
        tenths_text = Text("Tenths", color=focus_color)
        hundredths_text = Text("Hundredths", color=highlight_color_1)

        # Arrange them in a group
        place_value_group = VGroup(ones_text, decimal_point_text, tenths_text, hundredths_text).arrange(RIGHT, buff=0.5).move_to(ORIGIN).shift(UP*1.5)

        self.play(FadeIn(ones_text, shift=UP))
        self.wait(0.3)
        self.play(Write(decimal_point_text))
        self.wait(0.3)
        self.play(FadeIn(tenths_text, shift=UP))
        self.wait(0.3)
        self.play(FadeIn(hundredths_text, shift=UP))
        self.wait(1.5)

        # Show an example: 0.7
        example_num_07 = MathTex(r"0.7", font_size=90, color=text_color).next_to(place_value_group, DOWN, buff=1.5)
        self.play(Write(example_num_07))
        self.wait(0.5)

        # Arrows and labels for 0.7
        arrow_0_07 = Arrow(example_num_07[0][0].get_center(), ones_text.get_center(), buff=0.1, color=text_color)
        arrow_dp_07 = Arrow(example_num_07[0][1].get_center(), decimal_point_text.get_center(), buff=0.1, color=text_color)
        arrow_7_07 = Arrow(example_num_07[0][2].get_center(), tenths_text.get_center(), buff=0.1, color=text_color)

        label_0_07 = Text("0 Ones", font_size=28, color=text_color).next_to(arrow_0_07, DOWN, buff=0.1)
        label_7_07 = Text("7 Tenths", font_size=28, color=text_color).next_to(arrow_7_07, DOWN, buff=0.1)

        self.play(GrowArrow(arrow_0_07), FadeIn(label_0_07))
        self.play(GrowArrow(arrow_dp_07))
        self.play(GrowArrow(arrow_7_07), FadeIn(label_7_07))
        self.wait(2)

        self.play(FadeOut(VGroup(arrow_0_07, arrow_dp_07, arrow_7_07, label_0_07, label_7_07)))
        self.wait(0.5)

        # Show 0.25 example
        example_num_025 = MathTex(r"0.25", font_size=90, color=text_color).move_to(example_num_07.get_center())
        self.play(Transform(example_num_07, example_num_025)) # Transform 0.7 to 0.25
        self.wait(0.5)

        # Recreate arrows and labels for 0.25
        arrow_0_025 = Arrow(example_num_025[0][0].get_center(), ones_text.get_center(), buff=0.1, color=text_color)
        arrow_dp_025 = Arrow(example_num_025[0][1].get_center(), decimal_point_text.get_center(), buff=0.1, color=text_color)
        arrow_2_025 = Arrow(example_num_025[0][2].get_center(), tenths_text.get_center(), buff=0.1, color=text_color)
        arrow_5_025 = Arrow(example_num_025[0][3].get_center(), hundredths_text.get_center(), buff=0.1, color=text_color)

        label_0_025 = Text("0 Ones", font_size=28, color=text_color).next_to(arrow_0_025, DOWN, buff=0.1)
        label_2_025 = Text("2 Tenths", font_size=28, color=text_color).next_to(arrow_2_025, DOWN, buff=0.1)
        label_5_025 = Text("5 Hundredths", font_size=28, color=text_color).next_to(arrow_5_025, DOWN, buff=0.1)

        self.play(
            GrowArrow(arrow_0_025), FadeIn(label_0_025),
            GrowArrow(arrow_dp_025),
            GrowArrow(arrow_2_025), FadeIn(label_2_025),
            GrowArrow(arrow_5_025), FadeIn(label_5_025)
        )
        self.wait(2.5)

        # Clean up the scene
        self.play(FadeOut(VGroup(place_value_title, place_value_group, example_num_025,
                                 arrow_0_025, arrow_dp_025, arrow_2_025, arrow_5_025,
                                 label_0_025, label_2_025, label_5_025), shift=DOWN))

        # --- Scene 5: Conclusion ---
        summary_text_1 = Text("Decimals help us understand parts of a whole.", font_size=40, color=highlight_color_2)
        summary_text_2 = Text("Remember the decimal point and place values!", font_size=40, color=highlight_color_1).next_to(summary_text_1, DOWN, buff=0.8)
        thanks_text = Text("Keep exploring decimals!", font_size=50, color=title_color).next_to(summary_text_2, DOWN, buff=1.5)

        self.play(Write(summary_text_1))
        self.wait(1)
        self.play(FadeIn(summary_text_2, shift=UP))
        self.wait(1.5)
        self.play(Write(thanks_text))
        self.wait(3)
        self.play(FadeOut(VGroup(summary_text_1, summary_text_2, thanks_text)))