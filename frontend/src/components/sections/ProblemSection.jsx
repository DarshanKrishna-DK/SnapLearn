import React from 'react';
import { motion } from 'framer-motion';

const ProblemSection = () => {
  const problems = [
    {
      id: "ERR_01",
      icon: "🎬",
      title: "AI VIDEO TOOLS HAVE CAPS",
      description: "Synthesia, HeyGen, Runway all impose generation limits, watermarks on free tiers, and time caps. Every video is identical regardless of grade or student history."
    },
    {
      id: "ERR_02", 
      icon: "🔄",
      title: "NO TEACHING LOOP IN AI",
      description: "Every AI tool stops at the explanation. None of them check if the student understood, switch approach when confused, or remember what happened last session. SnapLearn AI closes that loop."
    },
    {
      id: "ERR_03",
      icon: "🧊", 
      title: "STATELESS AI = NO ADAPTATION",
      description: "General AI tools restart every session cold. No student profile, no weak topic tracking, no style preference memory. Every interaction treated as if the student is new."
    },
    {
      id: "ERR_04",
      icon: "📐",
      title: "ONE STYLE DOES NOT FIT ALL", 
      description: "A Grade 2 student and a Grade 7 student asking the same question need fundamentally different explanations. Existing tools give everyone the same output."
    },
    {
      id: "ERR_05",
      icon: "🔌",
      title: "NO EMBEDDABLE TUTORING ENGINE",
      description: "EdTech platforms that want adaptive AI tutoring have to build everything from scratch. No SDK exists that gives a platform instant access to a persistent, personalised tutoring engine."
    }
  ];

  return (
    <section id="problem" className="bg-[#fff8f0] py-32 px-10 relative">
      {/* Diagonal Top Edge */}
      <div className="absolute top-0 left-0 w-full h-24 bg-[#4A0010] -translate-y-1/2 diagonal-clip"></div>
      
      <div className="max-w-7xl mx-auto">
        <motion.h2 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="font-['Space_Grotesk'] font-black text-5xl uppercase mb-16 flex items-center gap-4 text-[#1e0003]"
        >
          <span className="text-[#795900]">&gt;</span> WHAT'S BROKEN IN EdTech TODAY
        </motion.h2>
        
        {/* Asymmetric Problem Grid */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-0 border border-[#887272]/15">
          {/* Cards 1 and 2: side by side */}
          <motion.div 
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            viewport={{ once: true }}
            className="md:col-span-2 p-10 bg-[#f4ede3] border-r border-[#887272]/15 hover:bg-[#eee7dd] transition-colors cursor-pointer group"
          >
            <div className="text-[#795900] font-['JetBrains_Mono'] mb-4 text-xs">{problems[0].id}</div>
            <div className="text-4xl mb-4">{problems[0].icon}</div>
            <h3 className="font-['Space_Grotesk'] font-bold text-2xl mb-4 text-[#1e0003]">{problems[0].title}</h3>
            <p className="text-[#554243] font-['Inter']">{problems[0].description}</p>
            <div className="w-1 h-8 bg-[#D4A843] mt-4 group-hover:h-12 transition-all"></div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            viewport={{ once: true }}
            className="p-10 bg-[#faf3e9] border-r border-[#887272]/15 hover:bg-[#eee7dd] transition-colors cursor-pointer group"
          >
            <div className="text-[#795900] font-['JetBrains_Mono'] mb-4 text-xs">{problems[1].id}</div>
            <div className="text-4xl mb-4">{problems[1].icon}</div>
            <h3 className="font-['Space_Grotesk'] font-bold text-2xl mb-4 text-[#1e0003]">{problems[1].title}</h3>
            <p className="text-[#554243] text-sm font-['Inter']">{problems[1].description}</p>
            <div className="w-1 h-8 bg-[#D4A843] mt-4 group-hover:h-12 transition-all"></div>
          </motion.div>

          {/* Card 3: full width, larger */}
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            viewport={{ once: true }}
            className="md:col-span-5 p-10 bg-[#1e0003] text-[#fff8f0] flex flex-col md:flex-row justify-between items-center gap-8 hover:bg-[#4A0010] transition-colors cursor-pointer"
          >
            <div>
              <div className="text-[#795900] font-['JetBrains_Mono'] mb-2 text-xs">CRITICAL_SYSTEM_FAILURE</div>
              <h3 className="font-['Space_Grotesk'] font-black text-3xl mb-2">{problems[4].title}</h3>
              <p className="text-[#fff8f0]/60 font-['Inter']">{problems[4].description}</p>
            </div>
            <button className="bg-[#795900] text-[#ffffff] px-8 py-3 font-['Space_Grotesk'] font-bold tracking-widest pixel-shadow whitespace-nowrap">
              VIEW_SOURCE
            </button>
          </motion.div>

          {/* Cards 4 and 5: side by side */}
          <motion.div 
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            viewport={{ once: true }}
            className="p-10 bg-[#f4ede3] border-r border-[#887272]/15 hover:bg-[#eee7dd] transition-colors cursor-pointer group"
          >
            <div className="text-[#795900] font-['JetBrains_Mono'] mb-4 text-xs">{problems[2].id}</div>
            <div className="text-4xl mb-4">{problems[2].icon}</div>
            <h3 className="font-['Space_Grotesk'] font-bold text-2xl mb-4 text-[#1e0003]">{problems[2].title}</h3>
            <p className="text-[#554243] text-sm font-['Inter']">{problems[2].description}</p>
            <div className="w-1 h-8 bg-[#D4A843] mt-4 group-hover:h-12 transition-all"></div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            viewport={{ once: true }}
            className="p-10 bg-[#faf3e9] hover:bg-[#eee7dd] transition-colors cursor-pointer group"
          >
            <div className="text-[#795900] font-['JetBrains_Mono'] mb-4 text-xs">{problems[3].id}</div>
            <div className="text-4xl mb-4">{problems[3].icon}</div>
            <h3 className="font-['Space_Grotesk'] font-bold text-2xl mb-4 text-[#1e0003]">{problems[3].title}</h3>
            <p className="text-[#554243] text-sm font-['Inter']">{problems[3].description}</p>
            <div className="w-1 h-8 bg-[#D4A843] mt-4 group-hover:h-12 transition-all"></div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default ProblemSection;