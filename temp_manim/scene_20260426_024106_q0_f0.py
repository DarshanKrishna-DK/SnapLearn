from manim import *

class DecimalsBasics(Scene):
    def construct(self):
        # --- Configuration ---
        # A light, friendly background color suitable for a 4th grader.
        self.camera.background_color = "#F0F8FF" # AliceBlue

        # --- Personalization & Educational Intent ---
        # Keeping language simple and encouraging for a 4th grader.
        # Focusing on visual representation and connection to fractions (tenths).

        # --- 1. Introduction ---
        title = Text("Decimals Basics!", font_size=72, color=BLUE_E, weight=BOLD)
        subtitle = Text("A special way to write parts of a whole.", font_size=40, color=DARK_BROWN)
        subtitle.next_to(title, DOWN, buff=0.5)

        self.play(Write(title))
        self.wait(0.7)
        self.play(FadeIn(subtitle, shift=UP))
        self.wait(1.5)
        self.play(FadeOut(title, shift=UP), FadeOut(subtitle, shift=UP))
        self.wait(0.5)

        # --- 2. Understanding "Tenths" with a visual ---
        what_are_tenths_text = Text("Let's look at parts of a whole!", font_size=48, color=TEAL_D)
        self.play(Write(what_are_tenths_text))
        self.wait(1)
        self.play(what_are_tenths_text.animate.to_edge(UP, buff=0.8))

        # Create a rectangle divided into 10 parts
        whole_rect = Rectangle(width=6, height=1, color=GRAY, fill_opacity=0.1, grid_x=10).center()
        
        # Create individual parts for highlighting
        parts = VGroup()
        for i in range(10):
            part = Rectangle(width=0.6, height=1, color=BLUE_A, fill_opacity=0.0)
            part.move_to(whole_rect.get_left() + RIGHT * (0.3 + i * 0.6))
            parts.add(part)
        
        # Create the lines that divide the rectangle visually
        dividers = VGroup()
        for i in range(1, 10):
            divider_x = whole_rect.get_left()[0] + i * 0.6
            divider = Line([divider_x, whole_rect.get_bottom()[1]], [divider_x, whole_rect.get_top()[1]], color=GRAY)
            dividers.add(divider)
        
        # Group all visual elements for easier manipulation
        all_parts_visual = VGroup(whole_rect, parts, dividers)

        self.play(Create(whole_rect), Create(dividers), Create(parts), run_time=2)
        self.wait(0.5)

        one_tenth_desc_text = Text("This is 1 whole divided into 10 equal parts.", font_size=36, color=DARK_BLUE)
        one_tenth_desc_text.next_to(all_parts_visual, DOWN, buff=0.8)
        self.play(Write(one_tenth_desc_text))
        self.wait(1.5)

        # Highlight one part
        first_part = parts[0]
        self.play(first_part.animate.set_fill(BLUE_E, opacity=0.8), run_time=1)
        self.wait(0.5)

        fraction_1_10 = MathTex(r"\frac{1}{10}", font_size=96, color=MAROON_E).next_to(all_parts_visual, RIGHT, buff=1.5)
        fraction_text = Text("One tenth", font_size=40, color=MAROON_D).next_to(fraction_1_10, DOWN, buff=0.3)

        self.play(Write(fraction_1_10), FadeIn(fraction_text, shift=UP))
        self.wait(1.5)
        self.play(FadeOut(one_tenth_desc_text))

        # --- 3. Introducing the Decimal Form ---
        decimal_0_1 = MathTex("0.1", font_size=96, color=GREEN_E).next_to(fraction_1_10, RIGHT, buff=1.5)
        decimal_text = Text("Zero point one", font_size=40, color=GREEN_D).next_to(decimal_0_1, DOWN, buff=0.3)

        self.play(
            TransformFromCopy(fraction_1_10, decimal_0_1),
            FadeIn(decimal_text, shift=UP)
        )
        self.wait(1.5)

        connect_text = Text("1/10 is the same as 0.1!", font_size=48, color=PURPLE_E).next_to(all_parts_visual, DOWN, buff=0.8)
        self.play(Write(connect_text))
        self.wait(1.5)
        self.play(FadeOut(connect_text))

        # Place value explanation
        # Use decimal_0_1[0][1] for '.', decimal_0_1[0][2] for '1'
        decimal_point_ind = Underline(decimal_0_1[0][1], color=RED) 
        tenths_place_ind = Underline(decimal_0_1[0][2], color=ORANGE) 

        dp_label = Text("Decimal Point", font_size=30, color=RED).next_to(decimal_point_ind, UP, buff=0.3)
        tp_label = Text("Tenths Place", font_size=30, color=ORANGE).next_to(tenths_place_ind, UP, buff=0.3)

        self.play(GrowFromCenter(decimal_point_ind), Write(dp_label))
        self.wait(1)
        self.play(GrowFromCenter(tenths_place_ind), Write(tp_label))
        self.wait(2)
        
        self.play(
            FadeOut(decimal_point_ind), FadeOut(dp_label),
            FadeOut(tenths_place_ind), FadeOut(tp_label)
        )

        # --- 4. Another Example (0.3) ---
        self.play(
            what_are_tenths_text.animate.move_to(UP*3.5), # move current top text up
            FadeOut(fraction_1_10), FadeOut(fraction_text),
            FadeOut(decimal_0_1), FadeOut(decimal_text)
        )
        self.wait(0.5)

        new_question = Text("What if we have 3 parts out of 10?", font_size=48, color=TEAL_D).move_to(what_are_tenths_text.get_center())
        self.play(Transform(what_are_tenths_text, new_question))
        self.wait(1)

        # Highlight 3 parts
        self.play(
            parts[0].animate.set_fill(BLUE_E, opacity=0.8),
            parts[1].animate.set_fill(BLUE_E, opacity=0.8),
            parts[2].animate.set_fill(BLUE_E, opacity=0.8),
            run_time=1.5
        )
        self.wait(1)

        fraction_3_10 = MathTex(r"\frac{3}{10}", font_size=96, color=MAROON_E).next_to(all_parts_visual, RIGHT, buff=1.5)
        decimal_0_3 = MathTex("0.3", font_size=96, color=GREEN_E).next_to(fraction_3_10, RIGHT, buff=1.5)

        self.play(
            Write(fraction_3_10),
            Write(decimal_0_3)
        )
        self.wait(2)

        # --- 5. Conclusion ---
        self.play(
            FadeOut(all_parts_visual),
            FadeOut(what_are_tenths_text),
            FadeOut(fraction_3_10),
            FadeOut(decimal_0_3),
        )

        summary_text = Text("Decimals help us show parts of a whole easily!", font_size=56, color=BLUE_E, weight=BOLD)
        encouragement_text = Text("You're doing great, Super Learner!", font_size=48, color=ORANGE).next_to(summary_text, DOWN, buff=0.8)

        self.play(Write(summary_text))
        self.wait(1)
        self.play(FadeIn(encouragement_text, shift=DOWN))
        self.wait(3)
        self.play(FadeOut(summary_text, shift=UP), FadeOut(encouragement_text, shift=UP))
        self.wait(1)