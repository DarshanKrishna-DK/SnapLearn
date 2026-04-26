import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const Feature2Blackboard = () => {
  const [activeDemo, setActiveDemo] = useState('grade2');
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);

  const demos = {
    grade2: {
      title: "GRADE 2: Addition",
      explanation: "🍎 + 🍎🍎 = 🍎🍎🍎",
      style: "Visual + Concrete Objects",
      complexity: "Simple"
    },
    grade7: {
      title: "GRADE 7: Addition", 
      explanation: "2 + 1 = 3 (Integer Properties)",
      style: "Abstract + Algebraic Rules",
      complexity: "Symbolic"
    },
    grade12: {
      title: "GRADE 12: Addition",
      explanation: "∀ a,b ∈ ℝ: a + b = b + a (Commutative Property)",
      style: "Formal + Mathematical Proof",
      complexity: "Rigorous"
    }
  };

  useEffect(() => {
    if (!isAutoPlaying) return;
    
    const interval = setInterval(() => {
      const keys = Object.keys(demos);
      const currentIndex = keys.indexOf(activeDemo);
      const nextIndex = (currentIndex + 1) % keys.length;
      setActiveDemo(keys[nextIndex]);
    }, 3000);

    return () => clearInterval(interval);
  }, [activeDemo, isAutoPlaying]);

  return (
    <section className="bg-[#fff8f0] py-32 px-10 relative">
      <div className="max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-12 gap-12 items-center">
          
          {/* Left: Interactive Demo */}
          <div className="lg:col-span-7">
            <motion.h3 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="font-['Space_Grotesk'] font-black text-4xl mb-8 text-[#1e0003]"
            >
              SAME CONCEPT, DIFFERENT STYLES
            </motion.h3>
            
            {/* Grade Level Selector */}
            <div className="flex gap-2 mb-8">
              {Object.entries(demos).map(([key, demo]) => (
                <button
                  key={key}
                  onClick={() => {
                    setActiveDemo(key);
                    setIsAutoPlaying(false);
                  }}
                  className={`px-4 py-2 font-['JetBrains_Mono'] text-xs font-bold transition-all ${
                    activeDemo === key 
                      ? 'bg-[#795900] text-[#ffffff] pixel-shadow' 
                      : 'bg-[#f4ede3] text-[#1e0003] hover:bg-[#eee7dd]'
                  }`}
                >
                  {key.toUpperCase()}
                </button>
              ))}
              
              <button
                onClick={() => setIsAutoPlaying(!isAutoPlaying)}
                className={`ml-4 px-3 py-2 font-['JetBrains_Mono'] text-xs ${
                  isAutoPlaying ? 'bg-[#1e0003] text-[#fff8f0]' : 'bg-[#f4ede3] text-[#1e0003]'
                } transition-all`}
              >
                {isAutoPlaying ? '⏸' : '▶'}
              </button>
            </div>
            
            {/* Blackboard Demo */}
            <motion.div 
              key={activeDemo}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.6 }}
              className="bg-gradient-to-br from-[#1A2E1A] to-[#0F1F0F] border-4 border-[#4A0010] aspect-video relative overflow-hidden"
            >
              {/* Chalk Texture Overlay */}
              <div className="absolute inset-0 opacity-30" style={{
                backgroundImage: 'url("data:image/svg+xml,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'100\' height=\'100\' viewBox=\'0 0 100 100\'><defs><filter id=\'noiseFilter\'><feTurbulence type=\'fractalNoise\' baseFrequency=\'0.85\' numOctaves=\'4\' stitchTiles=\'stitch\'/></filter></defs><rect width=\'100%\' height=\'100%\' filter=\'url(%23noiseFilter)\' opacity=\'0.05\'/></svg>")'
              }}></div>
              
              {/* Main Content */}
              <div className="relative z-10 flex flex-col items-center justify-center h-full p-8">
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ duration: 0.8 }}
                >
                  <h4 className="text-[#D4A843] font-['Space_Grotesk'] font-bold text-xl mb-6 text-center">
                    {demos[activeDemo].title}
                  </h4>
                  
                  <div className="text-[#fff8f0] text-3xl md:text-5xl font-['JetBrains_Mono'] text-center mb-8">
                    {demos[activeDemo].explanation}
                  </div>
                  
                  <div className="text-[#D4A843]/60 font-['Inter'] text-sm text-center">
                    Teaching Style: {demos[activeDemo].style}<br/>
                    Complexity: {demos[activeDemo].complexity}
                  </div>
                </motion.div>
              </div>
              
              {/* Chalk Dust Animation */}
              {[...Array(15)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-1 h-1 bg-[#fff8f0] rounded-full opacity-40"
                  style={{
                    left: `${Math.random() * 80 + 10}%`,
                    top: `${Math.random() * 80 + 10}%`
                  }}
                  animate={{
                    y: [0, -20, 0],
                    opacity: [0.4, 1, 0.4]
                  }}
                  transition={{
                    duration: 3 + Math.random() * 2,
                    repeat: Infinity,
                    delay: Math.random() * 2
                  }}
                />
              ))}
            </motion.div>
            
            <div className="mt-4 text-[#554243] text-sm font-['Inter']">
              💡 Same concept, automatically adapted for cognitive development level
            </div>
          </div>
          
          {/* Right: Technical Details */}
          <div className="lg:col-span-5">
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <h3 className="font-['Space_Grotesk'] font-black text-3xl mb-6 text-[#1e0003]">
                AUTOMATIC PEDAGOGY SWITCHING
              </h3>
              
              <div className="space-y-6">
                <div className="border-l-4 border-[#795900] pl-6">
                  <h4 className="font-['Space_Grotesk'] font-bold text-lg mb-2 text-[#1e0003]">Grade Detection</h4>
                  <p className="text-[#554243] font-['Inter'] text-sm">
                    System instantly identifies cognitive level from student profile and adjusts explanation complexity automatically.
                  </p>
                </div>
                
                <div className="border-l-4 border-[#795900] pl-6">
                  <h4 className="font-['Space_Grotesk'] font-bold text-lg mb-2 text-[#1e0003]">Style Adaptation</h4>
                  <p className="text-[#554243] font-['Inter'] text-sm">
                    Different visual languages: concrete objects for elementary, symbolic notation for middle school, formal proofs for advanced.
                  </p>
                </div>
                
                <div className="border-l-4 border-[#795900] pl-6">
                  <h4 className="font-['Space_Grotesk'] font-bold text-lg mb-2 text-[#1e0003]">Confusion Recovery</h4>
                  <p className="text-[#554243] font-['Inter'] text-sm">
                    If student shows confusion signals, system automatically downgrades to a simpler pedagogical approach and re-explains.
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Feature2Blackboard;