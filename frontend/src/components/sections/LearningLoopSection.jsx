import React from 'react';
import { motion } from 'framer-motion';

const LearningLoopSection = () => {
  return (
    <section className="bg-[#fff8f0] py-32 px-10 overflow-hidden">
      <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-20 items-center">
        {/* Left: Text Content */}
        <div>
          <motion.h2 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="font-['Space_Grotesk'] font-black text-5xl mb-8 text-[#1e0003]"
          >
            THE ADAPTIVE FEEDBACK LOOP
          </motion.h2>
          
          <div className="space-y-6">
            <motion.div 
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              viewport={{ once: true }}
              className="flex items-start gap-4 group"
            >
              <div className="w-10 h-10 bg-[#4A0010] text-[#795900] flex items-center justify-center font-['JetBrains_Mono'] shrink-0 font-bold">01</div>
              <div>
                <h4 className="font-['Space_Grotesk'] font-bold text-xl text-[#1e0003]">STUDENT_ASKS</h4>
                <p className="text-[#554243] font-['Inter']">Natural language query captured by the interface. Student profile and learning history retrieved instantly.</p>
              </div>
            </motion.div>
            
            <motion.div 
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
              className="flex items-start gap-4 group"
            >
              <div className="w-10 h-10 bg-[#4A0010] text-[#795900] flex items-center justify-center font-['JetBrains_Mono'] shrink-0 font-bold">02</div>
              <div>
                <h4 className="font-['Space_Grotesk'] font-bold text-xl text-[#1e0003]">AI_CONSTRUCTS_PEDAGOGY</h4>
                <p className="text-[#554243] font-['Inter']">The AI logic layer maps the query to a pedagogical roadmap based on grade level, previous confusion patterns, and preferred learning styles.</p>
              </div>
            </motion.div>
            
            <motion.div 
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              viewport={{ once: true }}
              className="flex items-start gap-4 group"
            >
              <div className="w-10 h-10 bg-[#4A0010] text-[#795900] flex items-center justify-center font-['JetBrains_Mono'] shrink-0 font-bold">03</div>
              <div>
                <h4 className="font-['Space_Grotesk'] font-bold text-xl text-[#1e0003]">MANIM_RENDERS_VIDEO</h4>
                <p className="text-[#554243] font-['Inter']">Programmatic animation generation creates personalized visuals. Dynamic blackboard environments tailored to the student's cognitive model.</p>
              </div>
            </motion.div>
            
            <motion.div 
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              viewport={{ once: true }}
              className="flex items-start gap-4 group"
            >
              <div className="w-10 h-10 bg-[#4A0010] text-[#795900] flex items-center justify-center font-['JetBrains_Mono'] shrink-0 font-bold">04</div>
              <div>
                <h4 className="font-['Space_Grotesk'] font-bold text-xl text-[#1e0003]">CONFUSION_DETECTED</h4>
                <p className="text-[#554243] font-['Inter']">Student interaction patterns signal confusion. System automatically switches teaching style and re-explains using a different pedagogical approach.</p>
              </div>
            </motion.div>
          </div>
        </div>
        
        {/* Right: Flowchart Visualization */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          viewport={{ once: true }}
          className="relative"
        >
          <div className="w-full aspect-square border-4 border-dashed border-[#887272]/20 flex items-center justify-center bg-[#faf3e9]">
            {/* Symbolic Hexagon Flowchart */}
            <div className="grid grid-cols-3 grid-rows-3 gap-2 w-4/5 h-4/5">
              <div className="col-start-2 flex items-center justify-center bg-[#795900]/10 border border-[#795900] text-[#795900] p-4 text-center text-[10px] font-['JetBrains_Mono'] font-bold">
                STUDENT<br/>ASKS
              </div>
              
              <div className="col-start-3 row-start-2 flex items-center justify-center bg-[#1e0003] text-[#fff8f0] p-4 text-center text-[10px] font-['JetBrains_Mono'] font-bold">
                PROFILE<br/>FETCH
              </div>
              
              <div className="col-start-2 row-start-3 flex items-center justify-center border-2 border-[#1e0003] p-4 text-center text-[10px] font-['JetBrains_Mono'] font-bold text-[#1e0003]">
                MANIM<br/>RENDER
              </div>
              
              <div className="col-start-1 row-start-2 flex items-center justify-center bg-[#795900] text-[#ffffff] p-4 text-center text-[10px] font-['JetBrains_Mono'] font-bold">
                STYLE<br/>ADAPT
              </div>
              
              {/* Center: Loop Icon */}
              <div className="col-start-2 row-start-2 flex items-center justify-center">
                <span className="material-symbols-outlined text-6xl text-[#1e0003] opacity-20">autorenew</span>
              </div>
            </div>
          </div>
          
          {/* Floating Animation Dots */}
          {[...Array(8)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-2 h-2 bg-[#D4A843] rounded-full"
              style={{
                left: `${10 + (i * 10)}%`,
                top: `${20 + (i % 3) * 20}%`
              }}
              animate={{
                y: [-5, 5, -5],
                opacity: [0.3, 1, 0.3]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: i * 0.2
              }}
            />
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default LearningLoopSection;