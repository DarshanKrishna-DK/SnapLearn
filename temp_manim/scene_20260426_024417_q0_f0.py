from manim import *

class DivisionBasics(Scene):
    def construct(self):
        # --- Configuration ---
        # Define a consistent color palette for clarity and engagement
        COLOR_PRIMARY = BLUE_C
        COLOR_ACCENT = YELLOW_A
        COLOR_ITEMS = RED_E
        COLOR_GROUPS = GREEN_C
        COLOR_TEXT = WHITE
        COLOR_BG_TITLE = "#2C3E50" # Dark blue-grey for title background

        # --- Problem Parameters (Grade 4 appropriate) ---
        total_items = 10 # E.g., cookies
        num_groups = 3   # E.g., friends

        items_per_group_actual = total_items // num_groups # How many each group gets
        remainder_count = total_items % num_groups         # How many are left over

        # --- Scene 1: Title and Introduction ---
        title_bg = Rectangle(width=FRAME_WIDTH, height=1.5, color=COLOR_BG_TITLE, fill_opacity=1).to_edge(UP, buff=0)
        title_text = Text("Understanding Division", font_size=60, color=COLOR_TEXT).next_to(title_bg, DOWN, buff=0.2)
        title_group = VGroup(title_bg, title_text)

        self.play(FadeIn(title_group), run_time=1.5)
        self.wait(1)

        intro_text = Text(
            "Division is about splitting a total number of items into equal groups.",
            font_size=36, color=COLOR_TEXT
        ).move_to(ORIGIN)
        
        self.play(FadeIn(intro_text), run_time=1.5)
        self.play(title_group.animate.scale(0.5).to_corner(UL).shift(DOWN*0.1 + RIGHT*0.1), intro_text.animate.to_edge(UP, buff=1.5), run_time=1.5)
        self.wait(1)

        # --- Scene 2: The Problem ---
        problem_text_1 = Text(f"Let's imagine we have {total_items} delicious cookies!", font_size=40, color=COLOR_TEXT)
        problem_text_1.next_to(intro_text, DOWN, buff=0.5)
        self.play(FadeIn(problem_text_1))
        self.wait(1)

        # Create cookies (circles)
        cookies = VGroup(*[
            Circle(radius=0.2, color=COLOR_ITEMS, fill_opacity=0.8) for _ in range(total_items)
        ]).arrange(RIGHT, buff=0.2).shift(DOWN*1.5) # Initial position below the problem text
        
        self.play(Create(cookies), run_time=2)
        self.wait(1)

        problem_text_2 = Text(f"And we want to share them equally among {num_groups} friends.", font_size=40, color=COLOR_TEXT)
        problem_text_2.next_to(intro_text, DOWN, buff=0.5)
        self.play(Transform(problem_text_1, problem_text_2)) # Replace text
        self.wait(1)

        # Create friends/groups (rectangles with labels)
        friends = VGroup()
        for i in range(num_groups):
            friend_rect = Rectangle(width=2, height=2, color=COLOR_GROUPS, fill_opacity=0.2, stroke_width=2)
            friend_label = Text(f"Friend {i+1}", font_size=28, color=COLOR_GROUPS).move_to(friend_rect.get_center() + UP*0.8)
            friends.add(VGroup(friend_rect, friend_label))

        friends.arrange(RIGHT, buff=0.5).shift(DOWN*0.5) # Position friends
        
        self.play(FadeOut(intro_text), Transform(problem_text_1, friends), run_time=2) # Fade out old text, transform problem_text_1 into friends
        self.wait(1)
        
        # Adjust cookies position for distribution (above the friends)
        self.play(cookies.animate.next_to(friends, UP, buff=0.8), run_time=1)
        self.wait(1)

        # --- Scene 3: Distributing Cookies ---
        distribute_text = Text("Let's distribute the cookies one by one...", font_size=36, color=COLOR_TEXT)
        distribute_text.to_edge(UP, buff=1.5)
        self.play(FadeIn(distribute_text))
        self.wait(0.5)

        animations = []
        distributed_cookie_mobjects_in_groups = [[] for _ in range(num_groups)] # Store references to cookies moved into groups

        for i in range(total_items):
            if i < total_items - remainder_count: # These cookies will be distributed
                current_friend_index = i % num_groups
                num_in_this_group = len(distributed_cookie_mobjects_in_groups[current_friend_index])
                
                # Calculate target position for the cookie within its friend's rectangle
                # Distribute horizontally within the group's rectangle, slightly below label
                friend_rect_center = friends[current_friend_index][0].get_center()
                
                # Calculate an x-offset to arrange cookies within the rectangle
                # For `items_per_group_actual` cookies, they will be centered.
                x_offset = (- (items_per_group_actual - 1) * 0.4 / 2) + (num_in_this_group * 0.4)
                
                target_pos = friend_rect_center + RIGHT * x_offset + DOWN * 0.3 # Place cookies below the friend label
                
                animations.append(cookies[i].animate.move_to(target_pos))
                distributed_cookie_mobjects_in_groups[current_friend_index].append(cookies[i]) # Store the mobject reference

            # The remainder cookies (if any) will simply stay in their initial positions
            # or could be moved to a specific "remainder area". For this example, they stay put.

        self.play(LaggedStart(*animations, lag_ratio=0.1), run_time=5) # Distribute all relevant cookies with a slight lag
        self.wait(1)
        self.play(FadeOut(distribute_text))

        # --- Scene 4: The Result ---
        result_text_1 = Text(f"Each friend received {items_per_group_actual} cookies!", font_size=40, color=COLOR_TEXT)
        result_text_1.to_edge(UP, buff=1.5)
        self.play(FadeIn(result_text_1))
        self.wait(1)

        # Highlight cookies for each friend and their group box
        highlight_animations = []
        for i in range(num_groups):
            group_cookies_mobjects = VGroup(*distributed_cookie_mobjects_in_groups[i])
            highlight_animations.append(group_cookies_mobjects.animate.set_color(COLOR_ACCENT))
            highlight_animations.append(friends[i][0].animate.set_stroke(color=COLOR_ACCENT, width=5))
            
        self.play(LaggedStart(*highlight_animations, lag_ratio=0.05), run_time=2)
        self.wait(1)
        
        # Reset colors/strokes after highlighting
        reset_animations = []
        for i in range(num_groups):
            group_cookies_mobjects = VGroup(*distributed_cookie_mobjects_in_groups[i])
            reset_animations.append(group_cookies_mobjects.animate.set_color(COLOR_ITEMS))
            reset_animations.append(friends[i][0].animate.set_stroke(color=COLOR_GROUPS, width=2))
        self.play(LaggedStart(*reset_animations, lag_ratio=0.05), run_time=1)
        self.wait(0.5)

        if remainder_count > 0:
            remainder_text = Text(f"And there is {remainder_count} cookie remaining!", font_size=40, color=COLOR_TEXT)
            remainder_text.next_to(result_text_1, DOWN, buff=0.5)

            # Highlight the remainder cookie(s) - these are the last 'remainder_count' from the original 'cookies' VGroup
            remainder_mobjects = VGroup(*cookies[total_items - remainder_count:])
            self.play(FadeIn(remainder_text), remainder_mobjects.animate.set_color(COLOR_ACCENT).scale(1.2))
            self.wait(2)
            self.play(FadeOut(remainder_text), remainder_mobjects.animate.set_color(COLOR_ITEMS).scale(1/1.2))
        else:
            self.wait(2) # If no remainder, just wait

        self.play(FadeOut(result_text_1))

        # --- Scene 5: Formal Notation ---
        division_equation_str = f"{total_items} \\div {num_groups} = {items_per_group_actual}"
        substrings_to_isolate_list = [str(total_items), str(num_groups), str(items_per_group_actual)]

        if remainder_count > 0:
            division_equation_str += f" \\text{{ R }} {remainder_count}"
            substrings_to_isolate_list.append(f"\\text{{ R }} {remainder_count}")

        division_equation = Text(
            division_equation_str,
            substrings_to_isolate=substrings_to_isolate_list,
            color=COLOR_TEXT, font_size=60
        ).to_edge(UP, buff=1.5)

        self.play(FadeIn(division_equation))
        self.wait(1)

        # Explain terms
        term_dividend = Text("Dividend (Total items)", font_size=32, color=COLOR_PRIMARY)
        term_divisor = Text("Divisor (Number of groups)", font_size=32, color=COLOR_PRIMARY)
        term_quotient = Text("Quotient (Items per group)", font_size=32, color=COLOR_PRIMARY)
        term_remainder = Text("Remainder (Items left over)", font_size=32, color=COLOR_PRIMARY)

        # Highlight Dividend
        self.play(FadeIn(term_dividend), division_equation[str(total_items)].animate.set_color(COLOR_ACCENT))
        self.play(term_dividend.animate.next_to(division_equation[str(total_items)], DOWN), run_time=0.8)
        self.wait(1)
        self.play(FadeOut(term_dividend), division_equation[str(total_items)].animate.set_color(COLOR_TEXT))

        # Highlight Divisor
        self.play(FadeIn(term_divisor), division_equation[str(num_groups)].animate.set_color(COLOR_ACCENT))
        self.play(term_divisor.animate.next_to(division_equation[str(num_groups)], DOWN), run_time=0.8)
        self.wait(1)
        self.play(FadeOut(term_divisor), division_equation[str(num_groups)].animate.set_color(COLOR_TEXT))

        # Highlight Quotient
        self.play(FadeIn(term_quotient), division_equation[str(items_per_group_actual)].animate.set_color(COLOR_ACCENT))
        self.play(term_quotient.animate.next_to(division_equation[str(items_per_group_actual)], DOWN), run_time=0.8)
        self.wait(1)
        self.play(FadeOut(term_quotient), division_equation[str(items_per_group_actual)].animate.set_color(COLOR_TEXT))

        # Highlight Remainder (if any)
        if remainder_count > 0:
            remainder_part_tex_key = f"\\text{{ R }} {remainder_count}"
            remainder_group_mobject = division_equation[remainder_part_tex_key]
            
            # To highlight just the number '1' from "R 1", we access it within the isolated group
            actual_remainder_digit_mobject = remainder_group_mobject.get_parts_by_tex(str(remainder_count))
            
            self.play(FadeIn(term_remainder), actual_remainder_digit_mobject.animate.set_color(COLOR_ACCENT))
            self.play(term_remainder.animate.next_to(actual_remainder_digit_mobject, DOWN), run_time=0.8)
            self.wait(1)
            self.play(FadeOut(term_remainder), actual_remainder_digit_mobject.animate.set_color(COLOR_TEXT))

        self.wait(1)
        
        # --- Scene 6: Conclusion ---
        self.play(FadeOut(cookies, friends, division_equation))

        conclusion_text = Text(
            "So, division helps us share things equally and find out what's left over!",
            font_size=42, color=COLOR_TEXT
        ).move_to(ORIGIN)

        self.play(FadeIn(conclusion_text))
        self.wait(3)
        self.play(FadeOut(conclusion_text, title_group))
        self.wait(1)