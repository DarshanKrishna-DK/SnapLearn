from manim import *

class GeometryBasics(Scene):
    def construct(self):
        # 1. Title Card
        title = Text("Basics of Geometry", font_size=48, color=BLUE)
        subtitle = Text("Grade 4 Math", font_size=32, color=GRAY).next_to(title, DOWN)
        
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

        # 2. Points, Lines, Rays, and Segments
        scene_1_title = Text("The Building Blocks", font_size=40, color=YELLOW).to_edge(UP)
        self.play(Write(scene_1_title))

        # Point
        point_dot = Dot(point=LEFT*3 + UP*1, color=WHITE)
        point_label = Text("Point", font_size=24).next_to(point_dot, DOWN)
        self.play(Create(point_dot), Write(point_label))

        # Line Segment
        seg_start = LEFT*1 + UP*1
        seg_end = RIGHT*2 + UP*1
        segment = Line(seg_start, seg_end, color=GREEN)
        dot_a = Dot(seg_start)
        dot_b = Dot(seg_end)
        seg_label = Text("Line Segment", font_size=24).next_to(segment, DOWN)
        self.play(Create(dot_a), Create(dot_b), Create(segment), Write(seg_label))

        # Ray
        ray_start = LEFT*3 + DOWN*1.5
        ray_end = LEFT*1 + DOWN*1.5
        ray = Line(ray_start, ray_end + RIGHT*1.5, color=ORANGE).add_tip()
        ray_dot = Dot(ray_start)
        ray_label = Text("Ray", font_size=24).next_to(ray, DOWN)
        self.play(Create(ray_dot), Create(ray), Write(ray_label))

        # Line
        line_path = Line(RIGHT*0.5 + DOWN*1.5, RIGHT*3.5 + DOWN*1.5, color=PINK).add_tip().add_tip(at_start=True)
        line_label = Text("Line", font_size=24).next_to(line_path, DOWN)
        self.play(Create(line_path), Write(line_label))
        
        self.wait(3)
        self.play(FadeOut(scene_1_title), FadeOut(point_dot), FadeOut(point_label), 
                 FadeOut(segment), FadeOut(dot_a), FadeOut(dot_b), FadeOut(seg_label),
                 FadeOut(ray), FadeOut(ray_dot), FadeOut(ray_label),
                 FadeOut(line_path), FadeOut(line_label))

        # 3. Angles
        scene_2_title = Text("Understanding Angles", font_size=40, color=YELLOW).to_edge(UP)
        self.play(Write(scene_2_title))

        # Right Angle
        l1 = Line(ORIGIN, RIGHT*2)
        l2 = Line(ORIGIN, UP*2)
        right_angle_symbol = RightAngle(l1, l2, length=0.4, quadrant=(1,1))
        angle_label = Text("Right Angle (90°)", font_size=28).next_to(l1, DOWN)
        
        self.play(Create(l1), Create(l2), Create(right_angle_symbol))
        self.play(Write(angle_label))
        self.wait(1.5)
        
        # Acute and Obtuse
        acute_l2 = Line(ORIGIN, UR*2)
        obtuse_l2 = Line(ORIGIN, UL*2)
        
        acute_label = Text("Acute Angle (Smaller)", font_size=28).next_to(l1, DOWN)
        self.play(ReplacementTransform(l2, acute_l2), 
                 FadeOut(right_angle_symbol),
                 ReplacementTransform(angle_label, acute_label))
        self.wait(1.5)
        
        obtuse_label = Text("Obtuse Angle (Larger)", font_size=28).next_to(l1, DOWN)
        self.play(ReplacementTransform(acute_l2, obtuse_l2),
                 ReplacementTransform(acute_label, obtuse_label))
        self.wait(2)

        self.play(FadeOut(scene_2_title), FadeOut(l1), FadeOut(obtuse_l2), FadeOut(obtuse_label))

        # 4. Common Shapes
        scene_3_title = Text("Basic Shapes", font_size=40, color=YELLOW).to_edge(UP)
        self.play(Write(scene_3_title))

        square = Square(side_length=2, color=BLUE).shift(LEFT*4)
        triangle = Triangle(color=GREEN).shift(ORIGIN)
        circle = Circle(radius=1, color=RED).shift(RIGHT*4)

        labels = VGroup(
            Text("Square", font_size=24).next_to(square, DOWN),
            Text("Triangle", font_size=24).next_to(triangle, DOWN),
            Text("Circle", font_size=24).next_to(circle, DOWN)
        )

        self.play(Create(square), Create(triangle), Create(circle))
        self.play(Write(labels))
        self.wait(2)
        self.play(FadeOut(scene_3_title), FadeOut(square), FadeOut(triangle), FadeOut(circle), FadeOut(labels))

        # 5. Worked Example: Identifying Properties
        example_title = Text("Worked Example", font_size=40, color=YELLOW).to_edge(UP)
        self.play(Write(example_title))

        rect = Rectangle(width=4, height=2, color=PURPLE)
        rect_text = Text("How many sides and vertices?", font_size=30).next_to(rect, UP)
        self.play(Create(rect), Write(rect_text))
        self.wait(1)

        # Counting Sides
        side_markers = [
            Line(UP*1 + LEFT*2, UP*1 + RIGHT*2, color=YELLOW, stroke_width=8),
            Line(UP*1 + RIGHT*2, DOWN*1 + RIGHT*2, color=YELLOW, stroke_width=8),
            Line(DOWN*1 + RIGHT*2, DOWN*1 + LEFT*2, color=YELLOW, stroke_width=8),
            Line(DOWN*1 + LEFT*2, UP*1 + LEFT*2, color=YELLOW, stroke_width=8),
        ]
        
        side_counts = VGroup()
        for i, sm in enumerate(side_markers):
            lbl = Text(str(i+1), font_size=36, color=YELLOW).move_to(sm.get_center() + sm.get_unit_vector()*0.4)
            side_counts.add(lbl)
            self.play(Create(sm), Write(lbl), run_time=0.5)
        
        ans_sides = MathTex(r"\text{Sides: } 4", color=YELLOW).shift(DOWN*2 + LEFT*2)
        self.play(Write(ans_sides))
        self.play(FadeOut(VGroup(*side_markers)), FadeOut(side_counts))

        # Counting Vertices
        vertices = [UP*1+LEFT*2, UP*1+RIGHT*2, DOWN*1+RIGHT*2, DOWN*1+LEFT*2]
        vertex_counts = VGroup()
        for i, v in enumerate(vertices):
            dot = Dot(v, color=RED, radius=0.15)
            lbl = Text(str(i+1), font_size=36, color=RED).next_to(dot, UR*0.5)
            vertex_counts.add(dot, lbl)
            self.play(Create(dot), Write(lbl), run_time=0.5)

        ans_vertices = MathTex(r"\text{Vertices: } 4", color=RED).shift(DOWN*2 + RIGHT*2)
        self.play(Write(ans_vertices))
        self.wait(2)

        self.play(FadeOut(rect), FadeOut(rect_text), FadeOut(ans_sides), FadeOut(ans_vertices), FadeOut(vertex_counts), FadeOut(example_title))

        # 6. Summary Slide
        summary_title = Text("Summary", font_size=44, color=BLUE).to_edge(UP)
        self.play(Write(summary_title))

        summary_points = VGroup(
            Text("• Point: A single position", font_size=32),
            Text("• Line: Goes on forever both ways", font_size=32),
            Text("• Ray: One endpoint, goes on forever", font_size=32),
            Text("• Angles: Right, Acute, and Obtuse", font_size=32),
            Text("• Shapes: Defined by sides and vertices", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT).shift(DOWN*0.5)

        for point in summary_points:
            self.play(FadeIn(point, shift=RIGHT*0.5))
            self.wait(0.8)

        self.wait(3)
        self.play(FadeOut(summary_points), FadeOut(summary_title))
        
        thanks = Text("Keep Exploring Geometry!", color=GOLD, font_size=48)
        self.play(Write(thanks))
        self.wait(2)