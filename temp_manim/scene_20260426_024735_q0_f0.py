from manim import *

class ExplanationScene(Scene):
    def construct(self):
        # --- Configuration ---
        # Set up a friendly color scheme suitable for 4th graders
        COLOR_COOKIE = YELLOW_A
        COLOR_FRIEND = BLUE_B
        # COLOR_BACKGROUND = PURE_BLUE # This variable was defined but not used for the camera background.
        COLOR_TEXT = WHITE
        COLOR_HIGHLIGHT = GREEN_A
        COLOR_REMAINDER = RED_A
        COLOR_EQUATION_BG = BLACK.copy().set_opacity(0.6) # FIX: Added missing parenthesis

        # Set actual camera background color for good contrast with white text
        # Using a slightly darker blue than PURE_BLUE for better readability for 4th graders
        self.camera.background_color = BLUE_E

        # --- Helper Mobjects (Icons for Friends and Cookies) ---
        def create_cookie():
            """Creates a single cookie icon."""
            return Circle(radius=0.25, color=COLOR_COOKIE, fill_opacity=1, stroke_width=2, stroke_color=WHITE)

        def create_friend_icon():
            """Creates a simple stick figure-like friend icon."""
            body = Line(UP * 0.5, DOWN * 0.5, color=COLOR_FRIEND, stroke_width=4)
            head = Circle(radius=0.2, color=COLOR_FRIEND, fill_opacity=1, stroke_width=2, stroke_color=WHITE).next_to(body, UP, buff=0.1)
            arms = Line(body.get_center() + LEFT * 0.4, body.get_center() + RIGHT * 0.4, color=COLOR_FRIEND, stroke_width=4)
            legs = VGroup(
                Line(body.get_bottom(), body.get_bottom() + DL * 0.4, color=COLOR_FRIEND, stroke_width=4),
                Line(body.get_bottom(), body.get_bottom() + DR * 0.4, color=COLOR_FRIEND, stroke_width=4)
            )
            return VGroup(body, head, arms, legs).scale(0.8) # Scale down for better fitting in the scene

        # --- Scene: Introduction ---
        title = Text("Let's Learn Division!", font_size=72, color=COLOR_HIGHLIGHT).to_edge(UP)
        intro_text = Text("Sharing things equally is division!", font_size=48, color=COLOR_TEXT).next_to(title, DOWN, buff=0.8)

        self.play(Write(title))
        self.play(Write(intro_text))
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(intro_text))

        # --- Scene: Example 1 - No Remainder (6 Cookies, 3 Friends) ---
        num_cookies_1 = 6
        num_friends_1 = 3
        cookies_per_friend_1 = num_cookies_1 // num_friends_1

        # Create cookies
        cookies_group_1 = VGroup(*[create_cookie() for _ in range(num_cookies_1)]).arrange(RIGHT, buff=0.3)
        cookies_label_1 = Text(f"{num_cookies_1} Cookies", color=COLOR_TEXT).next_to(cookies_group_1, UP, buff=0.5)

        # Create friends
        friends_group_1 = VGroup(*[create_friend_icon() for _ in range(num_friends_1)]).arrange(RIGHT, buff=1.5) # Increased buff for better spacing
        friends_label_1 = Text(f"{num_friends_1} Friends", color=COLOR_TEXT).next_to(friends_group_1, UP, buff=0.5)

        # Position groups
        cookies_full_group_1 = VGroup(cookies_label_1, cookies_group_1).center().to_edge(UP, buff=1.5)
        friends_full_group_1 = VGroup(friends_label_1, friends_group_1).center().to_edge(DOWN, buff=1.5)

        self.play(FadeIn(cookies_full_group_1), FadeIn(friends_full_group_1))
        self.wait(1)

        explanation_text_1 = Text(f"How many cookies does each friend get if we share {num_cookies_1} cookies among {num_friends_1} friends?",
                                  font_size=36, color=COLOR_TEXT, disable_ligatures=True).to_edge(LEFT).shift(UP*1.5).scale(0.8)
        self.play(Write(explanation_text_1))
        self.wait(1)

        # Animate distribution
        dist_anims_1 = []

        # Distribute cookies one by one in rounds
        for round_idx in range(cookies_per_friend_1):
            for friend_idx in range(num_friends_1):
                cookie_idx = round_idx * num_friends_1 + friend_idx
                cookie = cookies_group_1[cookie_idx]
                
                # Calculate target position for cookie above the friend, stacking them neatly
                # Each stack of cookies is centered above its friend
                stack_offset_x = (round_idx - (cookies_per_friend_1 - 1) / 2) * (cookie.width + 0.1)
                target_pos = friends_group_1[friend_idx].get_top() + UP * 0.3 + RIGHT * stack_offset_x
                
                dist_anims_1.append(cookie.animate.move_to(target_pos))
            self.play(AnimationGroup(*dist_anims_1[-num_friends_1:], lag_ratio=0.2)) # Play each round of distribution
            self.wait(0.5)

        self.wait(1)
        self.play(FadeOut(explanation_text_1))

        # Show result and equation
        result_text_1 = Text(f"Each friend gets {cookies_per_friend_1} cookies!", color=COLOR_HIGHLIGHT, font_size=48).shift(UP)
        equation_1 = Text(
            f"{num_cookies_1}", "\\div", f"{num_friends_1}", "=", f"{cookies_per_friend_1}",
            color=COLOR_TEXT, font_size=60
        ).next_to(friends_full_group_1, UP, buff=1.0)
        
        # Create a background rectangle for the equation
        eq_rect_1 = Rectangle(width=equation_1.width + 0.5, height=equation_1.height + 0.3, 
                              color=COLOR_EQUATION_BG, fill_opacity=1, stroke_width=0)
        eq_rect_1.move_to(equation_1.get_center())
        
        equation_group_1 = VGroup(eq_rect_1, equation_1)

        self.play(Write(result_text_1))
        self.wait(1)
        self.play(FadeIn(eq_rect_1), Write(equation_1))
        self.wait(2)

        # Label terms
        dividend_label_1 = Text("Dividend", color=COLOR_HIGHLIGHT, font_size=30).next_to(equation_1[0], DOWN, buff=0.1)
        divisor_label_1 = Text("Divisor", color=COLOR_HIGHLIGHT, font_size=30).next_to(equation_1[2], DOWN, buff=0.1)
        quotient_label_1 = Text("Quotient", color=COLOR_HIGHLIGHT, font_size=30).next_to(equation_1[4], DOWN, buff=0.1)

        self.play(FadeIn(dividend_label_1), FadeIn(divisor_label_1), FadeIn(quotient_label_1))
        self.wait(2.5)

        self.play(FadeOut(cookies_full_group_1), FadeOut(friends_full_group_1),
                  FadeOut(result_text_1), FadeOut(equation_group_1),
                  FadeOut(dividend_label_1), FadeOut(divisor_label_1), FadeOut(quotient_label_1))
        self.wait(1)

        # --- Scene: Example 2 - With Remainder (7 Cookies, 3 Friends) ---
        num_cookies_2 = 7
        num_friends_2 = 3
        cookies_per_friend_2 = num_cookies_2 // num_friends_2
        remainder_cookies_2 = num_cookies_2 % num_friends_2

        # Create cookies
        cookies_group_2 = VGroup(*[create_cookie() for _ in range(num_cookies_2)]).arrange(RIGHT, buff=0.3)
        cookies_label_2 = Text(f"{num_cookies_2} Cookies", color=COLOR_TEXT).next_to(cookies_group_2, UP, buff=0.5)

        # Create friends
        friends_group_2 = VGroup(*[create_friend_icon() for _ in range(num_friends_2)]).arrange(RIGHT, buff=1.5)
        friends_label_2 = Text(f"{num_friends_2} Friends", color=COLOR_TEXT).next_to(friends_group_2, UP, buff=0.5)

        # Position groups
        cookies_full_group_2 = VGroup(cookies_label_2, cookies_group_2).center().to_edge(UP, buff=1.5)
        friends_full_group_2 = VGroup(friends_label_2, friends_group_2).center().to_edge(DOWN, buff=1.5)

        self.play(FadeIn(cookies_full_group_2), FadeIn(friends_full_group_2))
        self.wait(1)

        explanation_text_2 = Text(f"What if we have {num_cookies_2} cookies and {num_friends_2} friends?",
                                  font_size=36, color=COLOR_TEXT, disable_ligatures=True).to_edge(LEFT).shift(UP*1.5).scale(0.8)
        self.play(Write(explanation_text_2))
        self.wait(1)

        # Animate distribution
        dist_anims_2 = []

        for round_idx in range(cookies_per_friend_2):
            for friend_idx in range(num_friends_2):
                cookie_idx = round_idx * num_friends_2 + friend_idx
                cookie = cookies_group_2[cookie_idx]
                
                # Calculate target position for cookie above the friend, stacking them neatly
                stack_offset_x = (round_idx - (cookies_per_friend_2 - 1) / 2) * (cookie.width + 0.1)
                target_pos = friends_group_2[friend_idx].get_top() + UP * 0.3 + RIGHT * stack_offset_x
                
                dist_anims_2.append(cookie.animate.move_to(target_pos))
            self.play(AnimationGroup(*dist_anims_2[-num_friends_2:], lag_ratio=0.2))
            self.wait(0.5)

        self.play(FadeOut(explanation_text_2))

        # Handle remainder
        remainder_group = VGroup()
        if remainder_cookies_2 > 0:
            remainder_label_text = Text("These are leftover cookies, called the REMAINDER!", color=COLOR_REMAINDER, font_size=40).next_to(friends_full_group_2, UP, buff=1).to_edge(LEFT)
            
            # Identify and highlight remainder cookies
            start_remainder_idx = num_cookies_2 - remainder_cookies_2
            for i in range(remainder_cookies_2):
                cookie = cookies_group_2[start_remainder_idx + i]
                remainder_group.add(cookie)
                
            self.play(Write(remainder_label_text))
            self.play(remainder_group.animate.arrange(RIGHT, buff=0.3).next_to(remainder_label_text, DOWN, buff=0.5).set_color(COLOR_REMAINDER))
            self.wait(1.5)

        # Show result and equation
        result_text_2 = Text(f"Each friend gets {cookies_per_friend_2} cookies, with {remainder_cookies_2} leftover!",
                             color=COLOR_HIGHLIGHT, font_size=48).shift(UP)

        equation_2 = Text(
            f"{num_cookies_2}", "\\div", f"{num_friends_2}", "=", f"{cookies_per_friend_2}", "\\text{ R }", f"{remainder_cookies_2}",
            color=COLOR_TEXT, font_size=60
        ).next_to(friends_full_group_2, UP, buff=1)

        eq_rect_2 = Rectangle(width=equation_2.width + 0.5, height=equation_2.height + 0.3, 
                              color=COLOR_EQUATION_BG, fill_opacity=1, stroke_width=0)
        eq_rect_2.move_to(equation_2.get_center())
        
        equation_group_2 = VGroup(eq_rect_2, equation_2)

        self.play(Write(result_text_2))
        self.wait(1)
        self.play(FadeIn(eq_rect_2), Write(equation_2))
        self.wait(2)

        # Label terms including remainder
        dividend_label_2 = Text("Dividend", color=COLOR_HIGHLIGHT, font_size=30).next_to(equation_2[0], DOWN, buff=0.1)
        divisor_label_2 = Text("Divisor", color=COLOR_HIGHLIGHT, font_size=30).next_to(equation_2[2], DOWN, buff=0.1)
        quotient_label_2 = Text("Quotient", color=COLOR_HIGHLIGHT, font_size=30).next_to(equation_2[4], DOWN, buff=0.1)
        remainder_label_2 = Text("Remainder", color=COLOR_REMAINDER, font_size=30).next_to(equation_2[6], DOWN, buff=0.1) 

        self.play(FadeIn(dividend_label_2), FadeIn(divisor_label_2),
                  FadeIn(quotient_label_2), FadeIn(remainder_label_2))
        self.wait(3)

        self.play(FadeOut(cookies_full_group_2), FadeOut(friends_full_group_2),
                  FadeOut(remainder_group), FadeOut(remainder_label_text),
                  FadeOut(result_text_2), FadeOut(equation_group_2),
                  FadeOut(dividend_label_2), FadeOut(divisor_label_2),
                  FadeOut(quotient_label_2), FadeOut(remainder_label_2))
        self.wait(1)

        # --- Scene: Recap ---
        recap_title = Text("Key Words for Division!", font_size=60, color=COLOR_HIGHLIGHT).to_edge(UP)
        terms = VGroup(
            Text("Dividend: The total number of things you have.", color=COLOR_TEXT, font_size=40),
            Text("Divisor: How many groups you want to share into.", color=COLOR_TEXT, font_size=40),
            Text("Quotient: The number of things in each group (your answer!).", color=COLOR_TEXT, font_size=40),
            Text("Remainder: The things left over that couldn't be shared equally.", color=COLOR_REMAINDER, font_size=40)
        ).arrange(DOWN, buff=0.7, aligned_edge=LEFT).next_to(recap_title, DOWN, buff=1)

        self.play(Write(recap_title))
        self.wait(0.5)
        for term in terms:
            self.play(FadeIn(term, shift=UP), run_time=1.5)
            self.wait(1)
        
        final_message = Text("Keep practicing sharing!", font_size=48, color=COLOR_HIGHLIGHT).next_to(terms, DOWN, buff=1.5)
        self.play(Write(final_message))
        self.wait(3)
        self.play(FadeOut(VGroup(recap_title, terms, final_message)))
        self.wait(1)