from manim import *
import numpy as np # Needed for random placement of chips

class DivisionBasics(Scene):
    def construct(self):
        # --- Scene Setup ---
        # Title
        title = Text("Sharing Equally: What is Division?", font_size=44).to_edge(UP)
        self.play(Write(title))
        self.wait(1) # Increased wait for better readability

        # --- Introduction to the Problem ---
        problem_intro = Text(
            "Imagine you have 12 delicious cookies...",
            font_size=36
        ).next_to(title, DOWN, buff=0.8)
        self.play(FadeIn(problem_intro, shift=DOWN))
        self.wait(1)

        # Create 12 cookies
        cookies_total = 12
        cookies = VGroup(*[
            Circle(radius=0.2, color=GOLD_D, fill_opacity=1).set_stroke(BLACK, width=1)
            for _ in range(cookies_total)
        ])
        cookies.arrange_in_grid(rows=3, cols=4, buff=0.3).move_to(ORIGIN)
        
        # Add a "chocolate chip" look to each cookie
        for cookie in cookies:
            for _ in range(3): # Add 3 chocolate chips
                # Generate random points within the cookie's circle
                angle = np.random.uniform(0, 2 * np.pi)
                dist = np.random.uniform(0, cookie.radius * 0.7) # Keep chips within central 70%
                chip_pos = cookie.get_center() + dist * np.array([np.cos(angle), np.sin(angle), 0])
                chip = Dot(point=chip_pos, radius=0.03, color=BROWN)
                cookie.add(chip) # Add chip as a part of the cookie VGroup

        self.play(FadeIn(cookies, scale=0.8))
        self.wait(1.5)

        # Introduce the sharing aspect
        sharing_text = Text(
            "...and you want to share them equally with 3 friends.",
            font_size=36
        ).next_to(problem_intro, DOWN, buff=0.8).shift(RIGHT*1.5) # Adjusted position
        sharing_text.align_to(problem_intro, LEFT) # Align for better flow

        self.play(
            problem_intro.animate.shift(LEFT*2.5).set_opacity(0.5), # Dim and move previous text
            FadeIn(sharing_text, shift=DOWN)
        )
        self.wait(1.5)

        # Create friend zones (circles with labels)
        num_friends = 3
        friend_zones_group = VGroup()
        for i in range(num_friends):
            label = Text(f"Friend {i+1}", font_size=28, color=BLUE)
            zone = Circle(radius=1.2, color=BLUE_A, stroke_width=2)
            zone_group = VGroup(zone, label.next_to(zone, UP, buff=0.2))
            friend_zones_group.add(zone_group)

        friend_zones_group.arrange(buff=1.5).shift(DOWN*2.5) # Position below cookies

        self.play(
            FadeOut(problem_intro), # Remove faded problem intro
            sharing_text.animate.to_edge(UP, buff=1).shift(LEFT*1.5), # Move sharing text up
            FadeIn(friend_zones_group)
        )
        self.wait(1)

        # --- Distribute Cookies Animation ---
        cookies_per_friend = cookies_total // num_friends
        
        # Collect cookies for each friend into separate VGroups
        cookies_in_each_zone = [VGroup() for _ in range(num_friends)]
        
        # Prepare cookies for sequential distribution
        self.play(
            cookies.animate.arrange(buff=0.2).next_to(sharing_text, DOWN, buff=0.5)
        )
        self.wait(0.5)

        # Animate distribution one-by-one, round-robin style
        distribution_anims_round = []
        for i, cookie in enumerate(cookies):
            friend_idx = i % num_friends # Distribute to friend 0, then 1, then 2, then 0 again

            # Move cookie to a temporary spot near the friend's zone
            # This makes the "picking up" and "giving" action clearer
            temp_target_pos = friend_zones_group[friend_idx][0].get_center() + UP*0.8
            distribution_anims_round.append(
                cookie.animate.move_to(temp_target_pos)
            )
            cookies_in_each_zone[friend_idx].add(cookie) # Add cookie to its final group

            if (i + 1) % num_friends == 0: # After each round (every friend gets one cookie)
                self.play(*distribution_anims_round, run_time=0.7)
                distribution_anims_round = [] # Reset for next round
                self.wait(0.2)
        
        # Play any remaining animations if total cookies is not a multiple of friends
        if distribution_anims_round:
            self.play(*distribution_anims_round, run_time=0.7)
            self.wait(0.2)

        self.wait(1)

        # Now, arrange the cookies neatly within each friend's zone
        final_arrangement_anims = []
        for i, friend_cookie_group in enumerate(cookies_in_each_zone):
            # Arrange cookies in a small grid within the friend zone
            # Since 4 cookies per friend, a 2x2 grid is perfect
            friend_cookie_group.arrange_in_grid(rows=2, cols=2, buff=0.1) 
            final_arrangement_anims.append(
                friend_cookie_group.animate.move_to(friend_zones_group[i][0].get_center())
            )

        self.play(*final_arrangement_anims, run_time=1.5)
        self.wait(1)

        # --- Count and State Result ---
        result_text = Text(
            f"Each friend gets {cookies_per_friend} cookies!",
            font_size=40, color=GREEN_B
        ).next_to(friend_zones_group, DOWN, buff=0.8)

        # Indicate one group to show the result
        self.play(Indicate(friend_zones_group[0][0]), run_time=0.8)
        self.play(FadeIn(result_text, shift=UP))
        self.wait(1.5)

        # --- Introduce Division Equation ---
        equation_text_intro = Text(
            "We can write this as a division problem:",
            font_size=32
        ).next_to(result_text, DOWN, buff=0.8)

        self.play(FadeIn(equation_text_intro, shift=UP))
        self.wait(1)

        division_equation = MathTex(
            f"{cookies_total} \\div {num_friends} = {cookies_per_friend}",
            font_size=60
        ).next_to(equation_text_intro, DOWN, buff=0.5)

        # Highlighting parts of the equation as it's written
        self.play(Write(division_equation[0]), run_time=0.5) # Total cookies
        self.play(Write(division_equation[1]), run_time=0.5) # division symbol
        self.play(Write(division_equation[2]), run_time=0.5) # Number of friends
        self.play(Write(division_equation[3]), run_time=0.5) # equals sign
        self.play(Write(division_equation[4]), run_time=0.5) # Result
        self.wait(2)

        # Explain the parts of the equation
        total_cookies_label = Text("Total Cookies", font_size=24, color=GOLD_D).next_to(division_equation[0], UP)
        num_friends_label = Text("Number of Friends", font_size=24, color=BLUE).next_to(division_equation[2], UP)
        cookies_each_label = Text("Cookies Each", font_size=24, color=GREEN_B).next_to(division_equation[4], UP)

        self.play(FadeIn(total_cookies_label, shift=UP),
                  FadeIn(num_friends_label, shift=UP),
                  FadeIn(cookies_each_label, shift=UP))
        self.wait(2)

        # Clear labels for next section
        self.play(FadeOut(total_cookies_label, num_friends_label, cookies_each_label))
        self.wait(0.5)

        # --- Definition of Division ---
        definition_title = Text("What is Division?", font_size=40).to_edge(UP)
        definition_text = Text(
            "Division is splitting a total amount into equal groups.",
            font_size=36
        ).next_to(definition_title, DOWN, buff=0.8)

        # Clear previous elements and present definition
        self.play(
            FadeOut(title, sharing_text, friend_zones_group, cookies, result_text,
                    equation_text_intro, division_equation),
            Transform(title, definition_title) # Transform the old title into the new one
        )
        self.play(Write(definition_text))
        self.wait(3)

        # --- Final Closing ---
        self.play(FadeOut(title, definition_text)) # Use the transformed title
        thanks_text = Text("Keep practicing sharing equally!", font_size=40, color=PURPLE)
        self.play(Write(thanks_text))
        self.wait(2)
        self.play(FadeOut(thanks_text))