import React from 'react';
import { motion } from 'framer-motion';

const DemoTimelineSection = () => {
  const roadmapItems = [
    {
      phase: "01",
      title: "Alpha Terminal",
      description: "Core rendering engine and LaTeX integration finalized. Public API access for early contributors.",
      status: "active",
      features: ["Manim Video Generation", "Grade-Level Adaptation", "Basic SDK"]
    },
    {
      phase: "02", 
      title: "Multi-Agent Orchestration",
      description: "Collaborative AI instructors that debate pedagogical approaches before rendering.",
      status: "locked",
      features: ["Agent Collaboration", "Style Debates", "Enhanced Accuracy"]
    },
    {
      phase: "03",
      title: "Spatial VR Dashboard", 
      description: "Transitioning from 2D blackboards to full 3D interactive mathematical landscapes.",
      status: "locked",
      features: ["VR Integration", "3D Math Spaces", "Hand Tracking"]
    }
  ];

  return (
    <section className="bg-[#1e0003] text-[#fff8f0] py-32 px-10 relative overflow-hidden">
      <div className="absolute inset-0 scanline-overlay opacity-10"></div>
      
      <div className="max-w-7xl mx-auto relative z-10">
        <motion.h2 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="font-['Space_Grotesk'] font-black text-5xl mb-20 text-center"
        >
          DEVELOPMENT ROADMAP
        </motion.h2>
        
        <div className="space-y-12">
          {roadmapItems.map((item, index) => (
            <motion.div
              key={item.phase}
              initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: index * 0.2 }}
              viewport={{ once: true }}
              className={`flex flex-col md:flex-row gap-8 items-center p-8 border-l-8 transition-all ${
                item.status === 'active' 
                  ? 'bg-[#fff8f0]/5 border-[#795900] hover:bg-[#fff8f0]/10' 
                  : 'bg-[#fff8f0]/5 border-[#887272]/30 opacity-60'
              }`}
            >
              {/* Phase Number */}
              <div className={`font-['Space_Grotesk'] font-black text-6xl leading-none ${
                item.status === 'active' 
                  ? 'text-[#D4A843]/80' 
                  : 'text-[#fff8f0]/10'
              }`}>
                {item.phase}
              </div>
              
              {/* Content */}
              <div className="flex-grow">
                <div className="flex items-center gap-4 mb-4">
                  <h4 className="font-['Space_Grotesk'] font-bold text-2xl uppercase tracking-widest">
                    {item.title}
                  </h4>
                  {item.status === 'active' && (
                    <span className="bg-[#795900] text-[#ffffff] px-2 py-1 text-xs font-['JetBrains_Mono'] font-bold">
                      ACTIVE
                    </span>
                  )}
                </div>
                
                <p className="text-[#fff8f0]/80 font-light max-w-2xl mb-4 font-['Inter']">
                  {item.description}
                </p>
                
                {/* Features */}
                <div className="flex flex-wrap gap-2">
                  {item.features.map((feature, featureIndex) => (
                    <span 
                      key={featureIndex}
                      className={`px-3 py-1 text-xs font-['JetBrains_Mono'] border ${
                        item.status === 'active'
                          ? 'border-[#795900] text-[#795900]'
                          : 'border-[#fff8f0]/20 text-[#fff8f0]/40'
                      }`}
                    >
                      {feature}
                    </span>
                  ))}
                </div>
              </div>
              
              {/* Status */}
              <div className={`font-['JetBrains_Mono'] text-sm ${
                item.status === 'active' 
                  ? 'text-[#795900]' 
                  : 'text-[#fff8f0]/30'
              }`}>
                {item.status === 'active' ? 'PRESS START >>' : 'LOCKED'}
              </div>
            </motion.div>
          ))}
        </div>
        
        {/* Demo Access */}
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          viewport={{ once: true }}
          className="mt-20 text-center"
        >
          <div className="bg-[#4A0010] border-2 border-[#795900] p-8 max-w-2xl mx-auto">
            <h3 className="font-['Space_Grotesk'] font-bold text-xl mb-4">
              🎯 LIVE ALPHA DEMO AVAILABLE NOW
            </h3>
            <p className="text-[#fff8f0]/80 font-['Inter'] mb-6">
              Experience Phase 01 features in action. Generate personalized math videos and see grade-level adaptation in real time.
            </p>
            <button 
              onClick={() => window.location.href = '/tutor'}
              className="bg-[#795900] text-[#ffffff] px-8 py-4 font-['Space_Grotesk'] font-bold text-lg pixel-shadow flex items-center gap-3 mx-auto hover:glow-secondary transition-all"
            >
              <span className="material-symbols-outlined">play_circle</span>
              LAUNCH DEMO
            </button>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default DemoTimelineSection;