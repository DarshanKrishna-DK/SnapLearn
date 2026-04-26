import React from 'react';
import { motion } from 'framer-motion';

const PositioningSection = () => {
  return (
    <section className="bg-[#faf3e9] py-24 px-10 border-y border-[#887272]/10">
      <div className="max-w-7xl mx-auto">
        {/* Main Statement */}
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <h2 className="font-['Space_Grotesk'] font-black text-6xl md:text-8xl text-[#1e0003] tracking-tightest">
            NOT A TUTORING APP.<br/>
            <span className="text-[#795900] italic">AN ENGINE.</span>
          </h2>
        </motion.div>
        
        {/* Quote Statement */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <blockquote className="font-['Space_Grotesk'] text-3xl md:text-4xl text-[#4A0010] max-w-4xl mx-auto leading-tight">
            "You are not competing with EdTech giants.<br/>
            You are supplying their AI tutoring layer."
          </blockquote>
        </motion.div>
        
        {/* Stat Boxes */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-5xl mx-auto"
        >
          <div className="bg-[#fff8f0] border border-[#887272]/15 p-8 flex flex-col items-center justify-center hover:border-[#795900] transition-colors">
            <div className="font-['JetBrains_Mono'] text-[#795900] text-2xl font-bold mb-2">[ 1 API CALL ]</div>
            <div className="text-[10px] uppercase tracking-widest text-[#554243] font-['Space_Grotesk']">Full Personalized Tutoring</div>
          </div>
          <div className="bg-[#fff8f0] border border-[#887272]/15 p-8 flex flex-col items-center justify-center hover:border-[#795900] transition-colors">
            <div className="font-['JetBrains_Mono'] text-[#795900] text-2xl font-bold mb-2">[ 0 TRAINING ]</div>
            <div className="text-[10px] uppercase tracking-widest text-[#554243] font-['Space_Grotesk']">Pure Prompt Engineering</div>
          </div>
          <div className="bg-[#fff8f0] border border-[#887272]/15 p-8 flex flex-col items-center justify-center hover:border-[#795900] transition-colors">
            <div className="font-['JetBrains_Mono'] text-[#795900] text-2xl font-bold mb-2">[ ∞ VIDEOS ]</div>
            <div className="text-[10px] uppercase tracking-widest text-[#554243] font-['Space_Grotesk']">No Generation Caps</div>
          </div>
          <div className="bg-[#fff8f0] border border-[#887272]/15 p-8 flex flex-col items-center justify-center hover:border-[#795900] transition-colors">
            <div className="font-['JetBrains_Mono'] text-[#795900] text-2xl font-bold mb-2">[ 3 STYLES ]</div>
            <div className="text-[10px] uppercase tracking-widest text-[#554243] font-['Space_Grotesk']">Auto-Switching on Confusion</div>
          </div>
        </motion.div>

        {/* Why This Positioning Wins */}
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          viewport={{ once: true }}
          className="mt-20"
        >
          <h3 className="font-['Space_Grotesk'] font-bold text-2xl text-center mb-12 text-[#1e0003]">
            WHY THIS POSITIONING WINS
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              "You are not competing with EdTech giants. You are potentially supplying their AI tutoring layer.",
              "Platforms spend months building what SnapLearn AI exposes in a single API call.",
              "The standalone app proves the engine works. The SDK demo proves it is embeddable.",
              "Switching costs compound as platforms build their student memory on your schema."
            ].map((point, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.1 * index }}
                viewport={{ once: true }}
                className="bg-[#fff8f0] border border-[#887272]/15 p-6 hover:border-[#795900] hover:shadow-[0_0_15px_rgba(121,89,0,0.1)] transition-all"
              >
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-[#795900] text-[#ffffff] flex items-center justify-center text-xs font-bold">
                    {index + 1}
                  </div>
                  <p className="text-[#554243] font-['Inter'] text-sm leading-relaxed">{point}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default PositioningSection;