import React, { useRef, useEffect } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';

const HeroSection = () => {
  const sectionRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end start"]
  });

  const y = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <motion.header 
      ref={sectionRef}
      id="hero"
      className="relative bg-[#4A0010] min-h-screen flex flex-col justify-center px-10 overflow-hidden"
      style={{ y }}
    >
      {/* Scanline Overlay */}
      <div className="absolute inset-0 scanline-overlay opacity-20"></div>
      
      {/* Main Content Grid */}
      <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        {/* Left Content */}
        <div className="lg:col-span-7">
          <motion.div 
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="inline-block bg-[#795900] text-[#ffffff] font-['JetBrains_Mono'] px-3 py-1 mb-6 text-xs font-bold"
          >
            [ STATUS: SYSTEM_ACTIVE // BUILD WITH AI HACKATHON • GDG BENGALURU • REVA UNIVERSITY ]
          </motion.div>
          
          <motion.h1 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.4 }}
            className="text-7xl md:text-9xl font-black italic leading-[0.85] tracking-tighter text-[#fff8f0] mb-8 font-['Space_Grotesk']"
          >
            SNAP<br/>LEARN<br/>AI
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="text-[#fff8f0]/80 text-xl max-w-xl mb-10 font-light border-l-4 border-[#795900] pl-6"
          >
            The Adaptive Tutoring Engine That Thinks Like a Teacher. 
            Generates personalized animated video explanations, detects student confusion in real time, 
            switches teaching styles automatically, and exposes everything as an embeddable SDK.
          </motion.p>
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            className="flex flex-wrap gap-6"
          >
            <button 
              onClick={() => window.location.href = '/tutor'}
              className="bg-[#795900] text-[#ffffff] px-8 py-4 font-['Space_Grotesk'] font-black text-xl pixel-shadow flex items-center gap-3 hover:glow-secondary transition-all"
            >
              <span className="material-symbols-outlined">play_arrow</span> 
              LAUNCH DEMO
            </button>
            <button 
              onClick={() => scrollToSection('sdk')}
              className="border-2 border-[#fff8f0] text-[#fff8f0] px-8 py-4 font-['Space_Grotesk'] font-black text-xl hover:bg-[#fff8f0] hover:text-[#4A0010] transition-all"
            >
              EXPLORE SDK
            </button>
          </motion.div>
        </div>
        
        {/* Right 3D Visualization Space */}
        <div className="lg:col-span-5 relative">
          <motion.div 
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 1 }}
            className="aspect-square bg-[#4A0010] border-2 border-[#795900]/30 relative group"
          >
            {/* Mock 3D Blackboard */}
            <div className="absolute inset-0 bg-gradient-to-br from-[#1A2E1A] to-[#0F1F0F] border-8 border-[#4A0010] m-4">
              {/* Floating Equations */}
              <div className="absolute top-1/4 left-1/4 text-[#D4A843] text-2xl font-['JetBrains_Mono'] animate-pulse">
                ∫f(x)dx
              </div>
              <div className="absolute top-1/2 right-1/4 text-[#fff8f0] text-xl font-['JetBrains_Mono'] animate-pulse" style={{ animationDelay: '0.5s' }}>
                E=mc²
              </div>
              <div className="absolute bottom-1/3 left-1/3 text-[#D4A843] text-lg font-['JetBrains_Mono'] animate-pulse" style={{ animationDelay: '1s' }}>
                a²+b²=c²
              </div>
              
              {/* Chalk Dust Particles */}
              {[...Array(20)].map((_, i) => (
                <div 
                  key={i}
                  className="absolute w-1 h-1 bg-[#fff8f0] rounded-full opacity-60 animate-bounce"
                  style={{
                    left: `${Math.random() * 80 + 10}%`,
                    top: `${Math.random() * 80 + 10}%`,
                    animationDelay: `${Math.random() * 2}s`,
                    animationDuration: `${2 + Math.random() * 2}s`
                  }}
                />
              ))}
            </div>
            
            {/* Terminal Overlay */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="bg-[#1E0003]/80 backdrop-blur-sm p-8 border border-[#795900] text-[#795900] font-['JetBrains_Mono'] text-sm leading-relaxed">
                <span className="block mb-2 text-[#fff8f0] opacity-50">// INITIALIZING_RENDER...</span>
                <span className="text-[#D4A843]">&gt;&gt; Blackboard.draw(Equation_01)</span><br/>
                <span className="text-[#D4A843]">&gt;&gt; Manim.render_sequence(30fps)</span><br/>
                <span className="text-[#D4A843]">&gt;&gt; Gemini.construct_pedagogy()</span><br/>
                <span className="animate-pulse">_</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
      
      {/* Scroll Indicator */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 1.5 }}
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="text-[#795900] text-2xl cursor-pointer"
          onClick={() => document.getElementById('problem').scrollIntoView({ behavior: 'smooth' })}
        >
          ↓
        </motion.div>
      </motion.div>
    </motion.header>
  );
};

export default HeroSection;