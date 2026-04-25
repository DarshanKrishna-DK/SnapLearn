from manim import *

class ExplanationScene(Scene):
    def construct(self):
        # Enhanced title with personalization
        title = Text("Multiplication basics", font_size=48, color=WHITE, weight=BOLD)
        subtitle = Text("Personalized Learning", font_size=24, color=LIGHT_BLUE)
        subtitle.next_to(title, DOWN, buff=0.5)
        
        # Grade-appropriate introduction
        self.play(Create(title), run_time=2)
        self.play(Create(subtitle), run_time=1.5)
        self.wait(2)
        
        # Clear and transition
        self.play(FadeOut(title), FadeOut(subtitle))
        
        # Main learning content adapted to style
        if "mixed" == "visual":
            content = Text("Let's visualize Multiplication basics!", font_size=40, color=WHITE)
            diagram = Circle(radius=2, color=LIGHT_BLUE)
            diagram.next_to(content, DOWN, buff=1)
            
            self.play(Create(content))
            self.play(Create(diagram))
            self.wait(3)
            
        elif "mixed" == "kinesthetic":
            content = Text("Let's explore Multiplication basics step by step!", font_size=40, color=WHITE)
            steps = VGroup()
            for i in range(3):
                step = Text(f"Step {i+1}: Learn about Multiplication basics", font_size=32, color=LIGHT_BLUE)
                step.move_to(UP * (1-i) * 0.8)
                steps.add(step)
            
            self.play(Create(content))
            self.wait(1)
            self.play(FadeOut(content))
            
            for step in steps:
                self.play(Create(step), run_time=1.5)
                self.wait(1)
        
        else:  # auditory or mixed
            content = Text("Understanding Multiplication basics is important\nfor Grade 4 students", 
                         font_size=36, color=WHITE)
            explanation = Text("This concept builds on what you already know\nand prepares you for future learning", 
                             font_size=32, color=LIGHT_BLUE)
            explanation.next_to(content, DOWN, buff=1)
            
            self.play(Create(content))
            self.wait(2)
            self.play(Create(explanation))
            self.wait(3)
        
        # Personalized encouragement
        encouragement = Text("Great job learning about Multiplication basics!\nYou're making excellent progress!", 
                           font_size=40, color=GREEN)
        
        self.play(FadeOut(*self.mobjects))
        self.play(Create(encouragement))
        self.wait(3)
        
        # Final fade
        self.play(FadeOut(encouragement))