from manim import *

class BasicsOfGeometry(Scene):
    def construct(self):
        # --- 1. Title Card ---
        title = Text("Basics of Geometry", font_size=60, color=BLUE_E, gradient=(BLUE, PURPLE))
        subtitle = Text("Points, Lines, Line Segments, and Rays", font_size=36, color=WHITE)
        subtitle.next_to(title, DOWN, buff=0.8)

        self.play(
            LaggedStart(
                Write(title, run_time=2),
                FadeIn(subtitle, shift=DOWN),
                lag_ratio=0.5
            )
        )
        self.wait(2)
        self.play(FadeOut(title, shift=UP), FadeOut(subtitle, shift=DOWN))
        self.wait(0.5)

        # --- 2. Scene: What is a Point? ---
        point_title = Text("1. What is a Point?", font_size=48, color=YELLOW).to_edge(UP)
        self.play(Write(point_title))
        self.wait(0.5)

        point_a = Dot(point=ORIGIN, radius=0.15, color=RED)
        label_a = Text("A", font_size=30, color=RED).next_to(point_a, DR, buff=0.1)
        point_text_1 = Text("A Point shows an exact location.", font_size=36).next_to(point_a, LEFT, buff=1.5)
        point_text_2 = Text("It has no size, only position.", font_size=36).next_to(point_text_1, DOWN, aligned_edge=LEFT)

        self.play(Create(point_a))
        self.play(Write(label_a))
        self.play(Write(point_text_1))
        self.wait(1)
        self.play(Write(point_text_2))
        self.wait(2)

        self.play(
            FadeOut(point_title, shift=UP),
            FadeOut(point_a, shift=DOWN),
            FadeOut(label_a, shift=DOWN),
            FadeOut(point_text_1, shift=DOWN),
            FadeOut(point_text_2, shift=DOWN)
        )
        self.wait(0.5)

        # --- 3. Scene: What is a Line? ---
        line_title = Text("2. What is a Line?", font_size=48, color=YELLOW).to_edge(UP)
        self.play(Write(line_title))
        self.wait(0.5)

        line = Line(start=LEFT * 5, end=RIGHT * 5, color=GREEN)
        # Manually create arrow tips to emphasize infinite extension
        arrow_left = Arrow(start=line.get_start() + LEFT*0.2, end=line.get_start(), buff=0, color=GREEN, tip_length=0.2)
        arrow_right = Arrow(start=line.get_end() - RIGHT*0.2, end=line.get_end(), buff=0, color=GREEN, tip_length=0.2)
        
        point_b = Dot(line.point_from_proportion(0.2), radius=0.15, color=RED)
        point_c = Dot(line.point_from_proportion(0.8), radius=0.15, color=RED)
        label_b = Text("B", font_size=30, color=RED).next_to(point_b, UL, buff=0.1)
        label_c = Text("C", font_size=30, color=RED).next_to(point_c, UR, buff=0.1)

        line_text_1 = Text("A Line is a straight path.", font_size=36).to_corner(DR).shift(LEFT)
        line_text_2 = Text("It goes on forever in both directions.", font_size=36).next_to(line_text_1, DOWN, aligned_edge=LEFT)
        line_notation = MathTex(r"\overleftrightarrow{BC}", font_size=40, color=BLUE).next_to(line_text_2, DOWN, aligned_edge=LEFT, buff=0.5)
        line_notation_expl = Text("This is how we write it.", font_size=30).next_to(line_notation, RIGHT)


        self.play(Create(line), Create(arrow_left), Create(arrow_right))
        self.play(Create(point_b), Create(point_c))
        self.play(Write(label_b), Write(label_c))
        self.play(Write(line_text_1))
        self.wait(1)
        self.play(Write(line_text_2))
        self.wait(1)
        self.play(Write(line_notation), Write(line_notation_expl))
        self.wait(2)

        self.play(
            FadeOut(line_title, shift=UP),
            FadeOut(line, shift=DOWN),
            FadeOut(arrow_left, shift=DOWN),
            FadeOut(arrow_right, shift=DOWN),
            FadeOut(point_b, shift=DOWN),
            FadeOut(point_c, shift=DOWN),
            FadeOut(label_b, shift=DOWN),
            FadeOut(label_c, shift=DOWN),
            FadeOut(line_text_1, shift=DOWN),
            FadeOut(line_text_2, shift=DOWN),
            FadeOut(line_notation, shift=DOWN),
            FadeOut(line_notation_expl, shift=DOWN),
        )
        self.wait(0.5)

        # --- 4. Scene: What is a Line Segment? ---
        segment_title = Text("3. What is a Line Segment?", font_size=48, color=YELLOW).to_edge(UP)
        self.play(Write(segment_title))
        self.wait(0.5)

        segment = Line(start=LEFT * 2, end=RIGHT * 2, color=PURPLE)
        point_d = Dot(segment.get_start(), radius=0.15, color=RED)
        point_e = Dot(segment.get_end(), radius=0.15, color=RED)
        label_d = Text("D", font_size=30, color=RED).next_to(point_d, DL, buff=0.1)
        label_e = Text("E", font_size=30, color=RED).next_to(point_e, DR, buff=0.1)

        segment_text_1 = Text("A Line Segment is a part of a line.", font_size=36).to_corner(UL).shift(RIGHT)
        segment_text_2 = Text("It has two clear endpoints.", font_size=36).next_to(segment_text_1, DOWN, aligned_edge=LEFT)
        segment_notation = MathTex(r"\overline{DE}", font_size=40, color=BLUE).next_to(segment_text_2, DOWN, aligned_edge=LEFT, buff=0.5)
        segment_notation_expl = Text("This is how we write it.", font_size=30).next_to(segment_notation, RIGHT)

        self.play(Create(segment))
        self.play(Create(point_d), Create(point_e))
        self.play(Write(label_d), Write(label_e))
        self.play(Write(segment_text_1))
        self.wait(1)
        self.play(Write(segment_text_2))
        self.wait(1)
        self.play(Write(segment_notation), Write(segment_notation_expl))
        self.wait(2)

        self.play(
            FadeOut(segment_title, shift=UP),
            FadeOut(segment, shift=DOWN),
            FadeOut(point_d, shift=DOWN),
            FadeOut(point_e, shift=DOWN),
            FadeOut(label_d, shift=DOWN),
            FadeOut(label_e, shift=DOWN),
            FadeOut(segment_text_1, shift=DOWN),
            FadeOut(segment_text_2, shift=DOWN),
            FadeOut(segment_notation, shift=DOWN),
            FadeOut(segment_notation_expl, shift=DOWN)
        )
        self.wait(0.5)

        # --- 5. Scene: What is a Ray? ---
        ray_title = Text("4. What is a Ray?", font_size=48, color=YELLOW).to_edge(UP)
        self.play(Write(ray_title))
        self.wait(0.5)

        ray_line = Line(start=LEFT * 2, end=RIGHT * 5, color=ORANGE)
        arrow_ray = Arrow(start=ray_line.get_end() - RIGHT*0.2, end=ray_line.get_end(), buff=0, color=ORANGE, tip_length=0.2)
        point_f = Dot(ray_line.get_start(), radius=0.15, color=RED)
        point_g = Dot(ray_line.point_from_proportion(0.5), radius=0.15, color=RED) # A point *on* the ray
        label_f = Text("F", font_size=30, color=RED).next_to(point_f, DL, buff=0.1)
        label_g = Text("G", font_size=30, color=RED).next_to(point_g, UP, buff=0.1)


        ray_text_1 = Text("A Ray is a part of a line too.", font_size=36).to_corner(UL).shift(RIGHT)
        ray_text_2 = Text("It has one endpoint and goes on forever in one direction.", font_size=36).next_to(ray_text_1, DOWN, aligned_edge=LEFT)
        ray_notation = MathTex(r"\overrightarrow{FG}", font_size=40, color=BLUE).next_to(ray_text_2, DOWN, aligned_edge=LEFT, buff=0.5)
        ray_notation_expl = Text("Remember the endpoint comes first!", font_size=30).next_to(ray_notation, RIGHT)

        self.play(Create(ray_line), Create(arrow_ray))
        self.play(Create(point_f))
        self.play(Write(label_f))
        self.play(Write(ray_text_1))
        self.wait(1)
        self.play(Write(ray_text_2))
        self.play(Create(point_g), Write(label_g)) # Show point G after the text, as it's not an 'endpoint'
        self.wait(1)
        self.play(Write(ray_notation), Write(ray_notation_expl))
        self.wait(2)

        self.play(
            FadeOut(ray_title, shift=UP),
            FadeOut(ray_line, shift=DOWN),
            FadeOut(arrow_ray, shift=DOWN),
            FadeOut(point_f, shift=DOWN),
            FadeOut(point_g, shift=DOWN),
            FadeOut(label_f, shift=DOWN),
            FadeOut(label_g, shift=DOWN),
            FadeOut(ray_text_1, shift=DOWN),
            FadeOut(ray_text_2, shift=DOWN),
            FadeOut(ray_notation, shift=DOWN),
            FadeOut(ray_notation_expl, shift=DOWN)
        )
        self.wait(0.5)

        # --- 6. Worked Example: Identify Them! ---
        example_title = Text("Let's Practice: Identify Them!", font_size=48, color=YELLOW).to_edge(UP)
        self.play(Write(example_title))
        self.wait(1)

        # Example 1: Point
        question_1_text = Text("What is this?", font_size=36).move_to(LEFT * 4 + UP * 2.5)
        ex1_point = Dot(ORIGIN + LEFT * 4 + UP * 1, radius=0.15, color=RED)
        answer_1_text = Text("A Point!", font_size=36, color=BLUE).next_to(ex1_point, DOWN)

        # Example 2: Line Segment
        question_2_text = Text("What is this?", font_size=36).move_to(RIGHT * 4 + UP * 2.5)
        ex2_segment = Line(start=ORIGIN + RIGHT * 2.5 + UP * 1, end=ORIGIN + RIGHT * 5.5 + UP * 1, color=PURPLE)
        ex2_dot1 = Dot(ex2_segment.get_start(), radius=0.1, color=RED)
        ex2_dot2 = Dot(ex2_segment.get_end(), radius=0.1, color=RED)
        answer_2_text = Text("A Line Segment!", font_size=36, color=BLUE).next_to(ex2_segment, DOWN)

        # Example 3: Line
        question_3_text = Text("What is this?", font_size=36).move_to(LEFT * 4 + DOWN * 0.5)
        ex3_line = Line(start=ORIGIN + LEFT * 5.5 + DOWN * 2, end=ORIGIN + LEFT * 2.5 + DOWN * 2, color=GREEN)
        ex3_arrow_left = Arrow(start=ex3_line.get_start() + LEFT*0.2, end=ex3_line.get_start(), buff=0, color=GREEN, tip_length=0.2)
        ex3_arrow_right = Arrow(start=ex3_line.get_end() - RIGHT*0.2, end=ex3_line.get_end(), buff=0, color=GREEN, tip_length=0.2)
        answer_3_text = Text("A Line!", font_size=36, color=BLUE).next_to(ex3_line, DOWN)

        # Example 4: Ray
        question_4_text = Text("What is this?", font_size=36).move_to(RIGHT * 4 + DOWN * 0.5)
        ex4_ray_line = Line(start=ORIGIN + RIGHT * 2.5 + DOWN * 2, end=ORIGIN + RIGHT * 5.5 + DOWN * 2, color=ORANGE)
        ex4_arrow = Arrow(start=ex4_ray_line.get_end() - RIGHT*0.2, end=ex4_ray_line.get_end(), buff=0, color=ORANGE, tip_length=0.2)
        ex4_dot = Dot(ex4_ray_line.get_start(), radius=0.1, color=RED)
        answer_4_text = Text("A Ray!", font_size=36, color=BLUE).next_to(ex4_ray_line, DOWN)

        # Show Question 1
        self.play(Write(question_1_text))
        self.play(Create(ex1_point))
        self.wait(1.5)
        self.play(Write(answer_1_text))
        self.wait(1.5)

        # Show Question 2
        self.play(Write(question_2_text))
        self.play(Create(ex2_segment), Create(ex2_dot1), Create(ex2_dot2))
        self.wait(1.5)
        self.play(Write(answer_2_text))
        self.wait(1.5)

        # Show Question 3
        self.play(Write(question_3_text))
        self.play(Create(ex3_line), Create(ex3_arrow_left), Create(ex3_arrow_right))
        self.wait(1.5)
        self.play(Write(answer_3_text))
        self.wait(1.5)

        # Show Question 4
        self.play(Write(question_4_text))
        self.play(Create(ex4_ray_line), Create(ex4_arrow), Create(ex4_dot))
        self.wait(1.5)
        self.play(Write(answer_4_text))
        self.wait(2)

        self.play(
            FadeOut(example_title, shift=UP),
            FadeOut(VGroup(question_1_text, ex1_point, answer_1_text), shift=DOWN),
            FadeOut(VGroup(question_2_text, ex2_segment, ex2_dot1, ex2_dot2, answer_2_text), shift=DOWN),
            FadeOut(VGroup(question_3_text, ex3_line, ex3_arrow_left, ex3_arrow_right, answer_3_text), shift=DOWN),
            FadeOut(VGroup(question_4_text, ex4_ray_line, ex4_arrow, ex4_dot, answer_4_text), shift=DOWN)
        )
        self.wait(0.5)

        # --- 7. Summary Slide ---
        summary_title = Text("Summary", font_size=60, color=YELLOW).to_edge(UP)
        self.play(Write(summary_title))
        self.wait(0.5)

        # Point summary
        sum_point_text = Text("Point:", font_size=38, color=WHITE).move_to(LEFT * 4 + UP * 2.5)
        sum_point_dot = Dot(sum_point_text.get_right() + RIGHT * 0.8, radius=0.1, color=RED)
        sum_point_label = Text("A", font_size=25, color=RED).next_to(sum_point_dot, DR, buff=0.05)
        sum_point_desc = Text("Exact location, no size.", font_size=30).next_to(sum_point_dot, RIGHT, buff=0.8)
        
        # Line summary
        sum_line_text = Text("Line:", font_size=38, color=WHITE).next_to(sum_point_text, DOWN, buff=0.8, aligned_edge=LEFT)
        sum_line_obj = Line(start=sum_line_text.get_right() + RIGHT * 0.2 + LEFT * 1.5, end=sum_line_text.get_right() + RIGHT * 0.2 + RIGHT * 1.5, color=GREEN)
        sum_line_arr_l = Arrow(start=sum_line_obj.get_start() + LEFT*0.15, end=sum_line_obj.get_start(), buff=0, color=GREEN, tip_length=0.15)
        sum_line_arr_r = Arrow(start=sum_line_obj.get_end() - RIGHT*0.15, end=sum_line_obj.get_end(), buff=0, color=GREEN, tip_length=0.15)
        sum_line_desc = Text("Goes on forever in both directions.", font_size=30).next_to(sum_line_obj, RIGHT, buff=0.4)

        # Line Segment summary
        sum_segment_text = Text("Line Segment:", font_size=38, color=WHITE).next_to(sum_line_text, DOWN, buff=0.8, aligned_edge=LEFT)
        sum_segment_obj = Line(start=sum_segment_text.get_right() + RIGHT * 0.2, end=sum_segment_text.get_right() + RIGHT * 0.2 + RIGHT * 2, color=PURPLE)
        sum_segment_dot1 = Dot(sum_segment_obj.get_start(), radius=0.1, color=RED)
        sum_segment_dot2 = Dot(sum_segment_obj.get_end(), radius=0.1, color=RED)
        sum_segment_desc = Text("Has two endpoints.", font_size=30).next_to(sum_segment_obj, RIGHT, buff=0.4)

        # Ray summary
        sum_ray_text = Text("Ray:", font_size=38, color=WHITE).next_to(sum_segment_text, DOWN, buff=0.8, aligned_edge=LEFT)
        sum_ray_obj = Line(start=sum_ray_text.get_right() + RIGHT * 0.2, end=sum_ray_text.get_right() + RIGHT * 0.2 + RIGHT * 2, color=ORANGE)
        sum_ray_arr = Arrow(start=sum_ray_obj.get_end() - RIGHT*0.15, end=sum_ray_obj.get_end(), buff=0, color=ORANGE, tip_length=0.15)
        sum_ray_dot = Dot(sum_ray_obj.get_start(), radius=0.1, color=RED)
        sum_ray_desc = Text("One endpoint, goes on forever in one direction.", font_size=30).next_to(sum_ray_obj, RIGHT, buff=0.4)


        self.play(Write(sum_point_text), Create(sum_point_dot), Write(sum_point_label), Write(sum_point_desc))
        self.wait(1)
        self.play(Write(sum_line_text), Create(sum_line_obj), Create(sum_line_arr_l), Create(sum_line_arr_r), Write(sum_line_desc))
        self.wait(1)
        self.play(Write(sum_segment_text), Create(sum_segment_obj), Create(sum_segment_dot1), Create(sum_segment_dot2), Write(sum_segment_desc))
        self.wait(1)
        self.play(Write(sum_ray_text), Create(sum_ray_obj), Create(sum_ray_arr), Create(sum_ray_dot), Write(sum_ray_desc))
        self.wait(3)

        farewell_text = Text("Great Job Learning Geometry Basics!", font_size=48, color=BLUE_E, gradient=(BLUE, GREEN)).to_edge(DOWN, buff=0.8)
        self.play(Write(farewell_text))
        self.wait(2)
        self.play(FadeOut(self.mobjects))
        self.wait(1)