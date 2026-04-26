import React from 'react';
import { motion } from 'framer-motion';

const CTASection = () => {
  return (
    <section className="relative bg-[#4A0010] py-40 px-10 overflow-hidden text-center">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-[#795900]/20 via-transparent to-transparent"></div>
      <div className="absolute inset-0 scanline-overlay opacity-20"></div>
      
      {/* Floating Elements */}
      {[...Array(12)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-2 h-2 bg-[#D4A843] rounded-full opacity-20"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0.2, 0.8, 0.2]
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 2
          }}
        />
      ))}
      
      <div className="relative z-10 max-w-4xl mx-auto">
        <motion.h2 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="font-['Space_Grotesk'] font-black text-6xl md:text-8xl text-[#fff8f0] mb-8 tracking-tightest"
        >
          READY TO BUILD?
        </motion.h2>
        
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          viewport={{ once: true }}
          className="text-[#fff8f0]/60 text-xl mb-12 font-['JetBrains_Mono'] uppercase tracking-[0.2em]"
        >
          Deployment is just one command away.
        </motion.p>
        
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          viewport={{ once: true }}
          className="flex flex-wrap justify-center gap-6 mb-16"
        >
          <button 
            onClick={() => window.open('https://github.com/your-repo/snaplearn-ai', '_blank')}
            className="bg-[#795900] text-[#ffffff] px-10 py-5 font-['Space_Grotesk'] font-black text-2xl pixel-shadow flex items-center gap-4 hover:glow-secondary transition-all"
          >
            <span className="material-symbols-outlined">code</span> 
            VIEW ON GITHUB
          </button>
          
          <button 
            onClick={() => window.location.href = '/tutor'}
            className="bg-[#fff8f0] text-[#1e0003] px-10 py-5 font-['Space_Grotesk'] font-black text-2xl pixel-shadow hover:bg-[#f4ede3] transition-all"
          >
            TRY LIVE DEMO
          </button>
        </motion.div>
        
        {/* Terminal Command */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          viewport={{ once: true }}
          className="bg-[#1e0003] border border-[#795900] p-6 max-w-2xl mx-auto mb-16"
        >
          <div className="font-['JetBrains_Mono'] text-[#795900] text-xs mb-2">SNAPLEARN_AI_SETUP.sh</div>
          <div className="font-['JetBrains_Mono'] text-[#fff8f0] text-sm">
            <span className="text-[#D4A843]">$</span> git clone https://github.com/your-repo/snaplearn-ai<br/>
            <span className="text-[#D4A843]">$</span> cd snaplearn-ai && npm install<br/>
            <span className="text-[#D4A843]">$</span> npm run dev<br/>
            <span className="text-[#795900] animate-pulse">// SYSTEM_READY</span>
          </div>
        </motion.div>
        
        <motion.div 
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          viewport={{ once: true }}
          className="font-['JetBrains_Mono'] text-[#D4A843]/40 text-xs animate-pulse"
        >
          SYS_READY // SESSION_ID: {Math.random().toString(36).substr(2, 9).toUpperCase()}-SNAP-LEARN-001
        </motion.div>
      </div>
    </section>
  );
};

export default CTASection;