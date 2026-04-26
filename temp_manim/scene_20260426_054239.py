from manim import *

class BasicsOfGeometry(Scene):
    def construct(self):
        # --- 1. Title Card ---
        title = Text("Let's Explore Geometry!", font_size=64, color=BLUE_B)
        subtitle = Text("Shapes, Sizes, and Spaces!", font_size=36, color=LIGHT_GRAY).next_to(title, DOWN)

        self.play(Write(title))
        self.play(Write(subtitle))
        self.wait(2)
        self.play(FadeOut(title, shift=UP), FadeOut(subtitle, shift=DOWN))
        self.wait(0.5)

        # --- 2. What is Geometry? ---
        heading_geometry = Text("What is Geometry?", font_size=48, color=GREEN).to_edge(UP)
        definition_geometry = Text(
            "Geometry is the study of shapes, sizes, and positions of things.",
            font_size=32, color=WHITE
        ).next_to(heading_geometry, DOWN, buff=0.8)

        self.play(Write(heading_geometry))
        self.play(Write(definition_geometry))
        self.wait(1.5)

        # Showing simple shapes
        square = Square(side_length=1.5, color=YELLOW_B, fill_opacity=0.5).shift(LEFT * 3 + DOWN * 0.5)
        circle = Circle(radius=0.9, color=ORANGE, fill_opacity=0.5).shift(DOWN * 0.5)
        triangle = Triangle(color=RED_B, fill_opacity=0.5).scale(1.2).shift(RIGHT * 3 + DOWN * 0.5)

        self.play(Create(square), Create(circle), Create(triangle))
        self.wait(2)
        self.play(FadeOut(VGroup(heading_geometry, definition_geometry, square, circle, triangle)))
        self.wait(0.5)

        # --- 3. Point ---
        heading_point = Text("1. Point", font_size=48, color=GREEN).to_edge(UP)
        definition_point = Text(
            "A point is an exact location or position.",
            font_size=32, color=WHITE
        ).next_to(heading_point, DOWN, buff=0.8)

        self.play(Write(heading_point))
        self.play(Write(definition_point))
        self.wait(1.5)

        dot = Dot(point=ORIGIN, radius=0.15, color=RED)
        label_A = MathTex("A", font_size=40, color=RED).next_to(dot, DR, buff=0.1)
        point_text = Text("This is point A", font_size=32, color=WHITE).next_to(dot, DOWN, buff=0.8)

        self.play(Create(dot))
        self.play(Write(label_A))
        self.play(Write(point_text))
        self.wait(2)
        self.play(FadeOut(VGroup(heading_point, definition_point, dot, label_A, point_text)))
        self.wait(0.5)

        # --- 4. Line ---
        heading_line = Text("2. Line", font_size=48, color=GREEN).to_edge(UP)
        definition_line = Text(
            "A line is a straight path that goes on forever in both directions.",
            font_size=32, color=WHITE
        ).next_to(heading_line, DOWN, buff=0.8)

        self.play(Write(heading_line))
        self.play(Write(definition_line))
        self.wait(1.5)

        # Create a line with arrows
        line_obj = Line(start=LEFT * 5, end=RIGHT * 5, color=YELLOW)
        arrow_left = Arrow(start=line_obj.get_start() + RIGHT * 0.5, end=line_obj.get_start(), buff=0, color=YELLOW)
        arrow_right = Arrow(start=line_obj.get_end() + LEFT * 0.5, end=line_obj.get_end(), buff=0, color=YELLOW)
        full_line = VGroup(line_obj, arrow_left, arrow_right)

        # Add points on the line
        point_B = Dot(point=LEFT * 2, radius=0.1, color=RED)
        label_B = MathTex("B", font_size=40, color=RED).next_to(point_B, UP)
        point_C = Dot(point=RIGHT * 2, radius=0.1, color=RED)
        label_C = MathTex("C", font_size=40, color=RED).next_to(point_C, UP)

        # Notation for a line
        notation_line = MathTex(r"\overleftrightarrow{BC}", font_size=60, color=WHITE).next_to(full_line, DOWN, buff=0.8)
        notation_text = Text("We can call it Line BC", font_size=30, color=WHITE).next_to(notation_line, DOWN)

        self.play(Create(full_line))
        self.play(Create(point_B), Write(label_B), Create(point_C), Write(label_C))
        self.play(Write(notation_line))
        self.play(Write(notation_text))
        self.wait(2)
        self.play(FadeOut(VGroup(heading_line, definition_line, full_line, point_B, label_B, point_C, label_C, notation_line, notation_text)))
        self.wait(0.5)

        # --- 5. Line Segment ---
        heading_segment = Text("3. Line Segment", font_size=48, color=GREEN).to_edge(UP)
        definition_segment = Text(
            "A line segment is a part of a line with two endpoints.",
            font_size=32, color=WHITE
        ).next_to(heading_segment, DOWN, buff=0.8)

        self.play(Write(heading_segment))
        self.play(Write(definition_segment))
        self.wait(1.5)

        # Create a line segment
        segment_obj = Line(start=LEFT * 3, end=RIGHT * 3, color=BLUE)
        # Add endpoints
        endpoint_D = Dot(point=LEFT * 3, radius=0.1, color=RED)
        label_D = MathTex("D", font_size=40, color=RED).next_to(endpoint_D, UP)
        endpoint_E = Dot(point=RIGHT * 3, radius=0.1, color=RED)
        label_E = MathTex("E", font_size=40, color=RED).next_to(endpoint_E, UP)

        # Notation for a line segment
        notation_segment = MathTex(r"\overline{DE}", font_size=60, color=WHITE).next_to(segment_obj, DOWN, buff=0.8)
        notation_segment_text = Text("We can call it Line Segment DE", font_size=30, color=WHITE).next_to(notation_segment, DOWN)

        self.play(Create(segment_obj))
        self.play(Create(endpoint_D), Write(label_D), Create(endpoint_E), Write(label_E))
        self.play(Write(notation_segment))
        self.play(Write(notation_segment_text))
        self.wait(2)
        self.play(FadeOut(VGroup(heading_segment, definition_segment, segment_obj, endpoint_D, label_D, endpoint_E, label_E, notation_segment, notation_segment_text)))
        self.wait(0.5)

        # --- 6. Ray ---
        heading_ray = Text("4. Ray", font_size=48, color=GREEN).to_edge(UP)
        definition_ray = Text(
            "A ray is a part of a line with one endpoint and goes on forever in one direction.",
            font_size=32, color=WHITE
        ).next_to(heading_ray, DOWN, buff=0.8)

        self.play(Write(heading_ray))
        self.play(Write(definition_ray))
        self.wait(1.5)

        # Create a ray with one arrow
        ray_obj = Line(start=LEFT * 3, end=RIGHT * 4, color=PURPLE)
        arrow_ray = Arrow(start=ray_obj.get_end() + LEFT * 0.5, end=ray_obj.get_end(), buff=0, color=PURPLE)
        full_ray = VGroup(ray_obj, arrow_ray)

        # Add endpoint and another point on the ray
        endpoint_F = Dot(point=LEFT * 3, radius=0.1, color=RED)
        label_F = MathTex("F", font_size=40, color=RED).next_to(endpoint_F, UP)
        point_G = Dot(point=RIGHT * 1, radius=0.1, color=RED)
        label_G = MathTex("G", font_size=40, color=RED).next_to(point_G, UP)

        # Notation for a ray
        notation_ray = MathTex(r"\overrightarrow{FG}", font_size=60, color=WHITE).next_to(full_ray, DOWN, buff=0.8)
        notation_ray_text = Text("We can call it Ray FG", font_size=30, color=WHITE).next_to(notation_ray, DOWN)

        self.play(Create(full_ray))
        self.play(Create(endpoint_F), Write(label_F), Create(point_G), Write(label_G))
        self.play(Write(notation_ray))
        self.play(Write(notation_ray_text))
        self.wait(2)
        self.play(FadeOut(VGroup(heading_ray, definition_ray, full_ray, endpoint_F, label_F, point_G, label_G, notation_ray, notation_ray_text)))
        self.wait(0.5)

        # --- 7. Worked Example: Let's Practice! ---
        practice_heading = Text("Let's Practice!", font_size=48, color=GREEN).to_edge(UP)
        self.play(Write(practice_heading))
        self.wait(1)

        # Example 1: Line Segment
        question1 = Text("What is this figure?", font_size=36, color=WHITE).next_to(practice_heading, DOWN, buff=0.8)
        seg_ex1 = Line(LEFT * 2 + UP * 1, RIGHT * 2 + UP * 1, color=BLUE)
        dot_A1 = Dot(point=LEFT * 2 + UP * 1, radius=0.1, color=RED)
        label_A1 = MathTex("X", font_size=40, color=RED).next_to(dot_A1, UP)
        dot_B1 = Dot(point=RIGHT * 2 + UP * 1, radius=0.1, color=RED)
        label_B1 = MathTex("Y", font_size=40, color=RED).next_to(dot_B1, UP)
        figure1 = VGroup(seg_ex1, dot_A1, label_A1, dot_B1, label_B1).shift(DOWN*0.5)

        self.play(Write(question1))
        self.play(Create(figure1))
        self.wait(2)

        answer1 = Text("This is a Line Segment XY!", font_size=36, color=YELLOW_B).next_to(figure1, DOWN, buff=1.0)
        self.play(Write(answer1))
        self.wait(2)
        self.play(FadeOut(question1, figure1, answer1))
        self.wait(0.5)

        # Example 2: Ray
        question2 = Text("What is this figure?", font_size=36, color=WHITE).next_to(practice_heading, DOWN, buff=0.8)
        ray_ex2_obj = Line(LEFT * 2 + UP * 1, RIGHT * 2 + UP * 1, color=PURPLE)
        arrow_ray_ex2 = Arrow(start=ray_ex2_obj.get_end() + LEFT * 0.5, end=ray_ex2_obj.get_end(), buff=0, color=PURPLE)
        dot_C2 = Dot(point=LEFT * 2 + UP * 1, radius=0.1, color=RED)
        label_C2 = MathTex("P", font_size=40, color=RED).next_to(dot_C2, UP)
        dot_D2 = Dot(point=RIGHT * 0 + UP * 1, radius=0.1, color=RED) # Another point to define the ray direction
        label_D2 = MathTex("Q", font_size=40, color=RED).next_to(dot_D2, UP)
        figure2 = VGroup(ray_ex2_obj, arrow_ray_ex2, dot_C2, label_C2, dot_D2, label_D2).shift(DOWN*0.5)

        self.play(Write(question2))
        self.play(Create(figure2))
        self.wait(2)

        answer2 = Text("This is a Ray PQ!", font_size=36, color=YELLOW_B).next_to(figure2, DOWN, buff=1.0)
        self.play(Write(answer2))
        self.wait(2)
        self.play(FadeOut(question2, figure2, answer2))
        self.wait(0.5)

        # Example 3: Line
        question3 = Text("What is this figure?", font_size=36, color=WHITE).next_to(practice_heading, DOWN, buff=0.8)
        line_ex3_obj = Line(LEFT * 2.5 + UP * 1, RIGHT * 2.5 + UP * 1, color=YELLOW)
        arrow_left_ex3 = Arrow(start=line_ex3_obj.get_start() + RIGHT * 0.5, end=line_ex3_obj.get_start(), buff=0, color=YELLOW)
        arrow_right_ex3 = Arrow(start=line_ex3_obj.get_end() + LEFT * 0.5, end=line_ex3_obj.get_end(), buff=0, color=YELLOW)
        dot_E3 = Dot(point=LEFT * 1 + UP * 1, radius=0.1, color=RED)
        label_E3 = MathTex("S", font_size=40, color=RED).next_to(dot_E3, UP)
        dot_F3 = Dot(point=RIGHT * 1 + UP * 1, radius=0.1, color=RED)
        label_F3 = MathTex("T", font_size=40, color=RED).next_to(dot_F3, UP)
        figure3 = VGroup(line_ex3_obj, arrow_left_ex3, arrow_right_ex3, dot_E3, label_E3, dot_F3, label_F3).shift(DOWN*0.5)

        self.play(Write(question3))
        self.play(Create(figure3))
        self.wait(2)

        answer3 = Text("This is a Line ST!", font_size=36, color=YELLOW_B).next_to(figure3, DOWN, buff=1.0)
        self.play(Write(answer3))
        self.wait(2)
        self.play(FadeOut(question3, figure3, answer3, practice_heading))
        self.wait(0.5)

        # --- 8. Summary Slide ---
        summary_heading = Text("What We Learned Today!", font_size=56, color=BLUE_B).to_edge(UP)
        self.play(Write(summary_heading))
        self.wait(1)

        summary_points = VGroup(
            Text("• Point: An exact location (like a tiny dot).", font_size=34, color=WHITE),
            Text("• Line: A straight path that goes on forever in both directions.", font_size=34, color=WHITE),
            Text("• Line Segment: A part of a line with two endpoints.", font_size=34, color=WHITE),
            Text("• Ray: A part of a line with one endpoint and goes on forever in one direction.", font_size=34, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.7).next_to(summary_heading, DOWN, buff=1.0).to_edge(LEFT, buff=1.0)

        for point_text in summary_points:
            self.play(Write(point_text))
            self.wait(1.5)

        farewell = Text("Great job, young geometricians!", font_size=36, color=GREEN_A).next_to(summary_points, DOWN, buff=1.5)
        self.play(Write(farewell))
        self.wait(3)
        self.play(FadeOut(VGroup(summary_heading, summary_points, farewell)))
        self.wait(0.5)