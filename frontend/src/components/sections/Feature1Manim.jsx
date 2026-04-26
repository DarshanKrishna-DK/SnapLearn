import React, { useState } from 'react';
import { motion } from 'framer-motion';

const Feature1Manim = () => {
  const [isPlaying, setIsPlaying] = useState(false);

  return (
    <section id="features" className="bg-[#4A0010] py-32 px-10 relative">
      <div className="absolute inset-0 scanline-overlay opacity-30"></div>
      <div className="max-w-7xl mx-auto relative z-10">
        <div className="grid lg:grid-cols-12 gap-12">
          {/* Left: Video/Demo Space */}
          <div className="lg:col-span-8">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="bg-[#1e0003] border-4 border-[#795900]/50 p-1 shadow-[0_0_50px_rgba(121,89,0,0.2)]"
            >
              <div className="bg-black aspect-video relative overflow-hidden group cursor-pointer" onClick={() => setIsPlaying(!isPlaying)}>
                {/* Mock Terminal/Blackboard */}
                <div className="w-full h-full bg-gradient-to-br from-[#0A0F0A] to-[#1A1F1A] flex flex-col justify-center items-center relative">
                  
                  {/* Terminal Header */}
                  <div className="absolute top-4 left-4 font-['JetBrains_Mono'] text-[10px] text-[#795900]">
                    [ RENDERING SEQUENCE: MANIM_OFFLINE_V2 ]<br/>
                    [ STATUS: {isPlaying ? 'COMPILING_SHADERS...' : 'READY_TO_RENDER'} ]
                  </div>
                  
                  {/* Play Button Overlay */}
                  {!isPlaying && (
                    <motion.div 
                      whileHover={{ scale: 1.1 }}
                      className="absolute inset-0 flex items-center justify-center bg-black/30 group-hover:bg-black/50 transition-colors"
                    >
                      <div className="w-20 h-20 bg-[#795900] rounded-full flex items-center justify-center">
                        <span className="material-symbols-outlined text-4xl text-white">play_arrow</span>
                      </div>
                    </motion.div>
                  )}
                  
                  {/* Animated Mathematical Content */}
                  {isPlaying ? (
                    <div className="space-y-6">
                      <motion.div 
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 1 }}
                        className="text-[#D4A843] text-6xl font-['JetBrains_Mono'] text-center"
                      >
                        ∫f(x)dx
                      </motion.div>
                      
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: '100%' }}
                        transition={{ duration: 2, delay: 1 }}
                        className="h-1 bg-[#D4A843] mx-auto"
                      />
                      
                      <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 1, delay: 2 }}
                        className="text-[#fff8f0] text-2xl font-['JetBrains_Mono'] text-center"
                      >
                        = F(x) + C
                      </motion.div>
                    </div>
                  ) : (
                    <div className="text-[#D4A843]/30 text-4xl font-['JetBrains_Mono'] text-center">
                      Click to see Manim in action
                    </div>
                  )}
                  
                  {/* Progress Bar */}
                  <div className="absolute inset-x-0 bottom-0 h-1 bg-[#795900] w-2/3" 
                       style={{ width: isPlaying ? '66%' : '0%', transition: 'width 3s linear' }} />
                </div>
              </div>
            </motion.div>
          </div>
          
          {/* Right: Feature Details */}
          <div className="lg:col-span-4 flex flex-col justify-center">
            <motion.h3 
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="text-[#fff8f0] font-['Space_Grotesk'] font-black text-4xl mb-6"
            >
              MATH IN MOTION
            </motion.h3>
            
            <motion.ul 
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              viewport={{ once: true }}
              className="space-y-4"
            >
              {[
                "DYNAMIC SVG RENDERING",
                "OFFLINE MP4 GENERATOR", 
                "LATEX INTEGRATION",
                "CUSTOM ANIMATION TIMING",
                "ZERO WATERMARKS"
              ].map((feature, index) => (
                <li key={index} className="flex items-center gap-3 text-[#fff8f0]/80 font-['JetBrains_Mono'] text-sm">
                  <span className="material-symbols-outlined text-[#795900]" style={{"font-variation-settings": "'FILL' 1"}}>
                    check_box
                  </span>
                  {feature}
                </li>
              ))}
            </motion.ul>
            
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              viewport={{ once: true }}
              className="mt-8"
            >
              <button className="bg-[#795900] text-[#ffffff] px-6 py-3 font-['Space_Grotesk'] font-bold text-sm tracking-widest pixel-shadow flex items-center gap-2 hover:glow-secondary transition-all">
                <span className="material-symbols-outlined">code</span>
                VIEW CODE SAMPLE
              </button>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Feature1Manim;