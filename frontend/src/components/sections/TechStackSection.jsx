import React from 'react';
import { motion } from 'framer-motion';

const TechStackSection = () => {
  const techStack = [
    { name: 'FastAPI', icon: '⚡', category: 'Backend' },
    { name: 'React 19', icon: '⚛️', category: 'Frontend' },
    { name: 'Manim Engine', icon: '🎬', category: 'Animation' },
    { name: 'Supabase', icon: '🗄️', category: 'Database' },
    { name: 'Gemini API', icon: '🤖', category: 'AI/ML' },
    { name: 'Three.js', icon: '🎮', category: '3D Graphics' },
    { name: 'Framer Motion', icon: '🌀', category: 'Animation' },
    { name: 'Tailwind CSS', icon: '🎨', category: 'Styling' }
  ];

  return (
    <section id="tech-stack" className="bg-[#fff8f0] py-24 px-10">
      <div className="max-w-7xl mx-auto">
        <motion.h2 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="font-['Space_Grotesk'] font-black text-5xl text-center mb-16 text-[#1e0003]"
        >
          TECH STACK
        </motion.h2>
        
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          viewport={{ once: true }}
          className="text-center text-[#554243] font-['Inter'] text-lg max-w-3xl mx-auto mb-16"
        >
          Built with modern, production-ready technologies. 
          Every component chosen for performance, scalability, and developer experience.
        </motion.p>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {techStack.map((tech, index) => (
            <motion.div
              key={tech.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="flex flex-col items-center p-8 bg-[#f4ede3] border border-transparent hover:border-[#795900] hover:bg-[#fff8f0] transition-all group cursor-pointer"
            >
              <div className="text-5xl mb-4 group-hover:scale-110 transition-transform">
                {tech.icon}
              </div>
              <div className="font-['JetBrains_Mono'] font-bold text-xs uppercase tracking-wider text-[#1e0003] mb-1">
                {tech.name}
              </div>
              <div className="font-['Inter'] text-[10px] uppercase tracking-widest text-[#795900]">
                {tech.category}
              </div>
            </motion.div>
          ))}
        </div>
        
        {/* Architecture Highlight */}
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          viewport={{ once: true }}
          className="mt-20 text-center"
        >
          <div className="inline-flex items-center gap-4 bg-[#1e0003] text-[#fff8f0] px-8 py-4 font-['JetBrains_Mono'] text-sm">
            <span className="material-symbols-outlined text-[#795900]">architecture</span>
            MICROSERVICES • DOCKER • CI/CD • REAL-TIME STREAMING
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default TechStackSection;