import React from 'react';
import { motion } from 'framer-motion';

const MarketingFooter = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-[#1E0003] w-full flex flex-col md:flex-row justify-between items-center gap-4 px-10 py-12 border-t-0">
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        whileInView={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
        className="font-['JetBrains_Mono'] text-[10px] tracking-widest uppercase text-[#795900]"
      >
        SYSTEM_STAT: OPERATIONAL // © {currentYear} SNAPLEARN_AI
      </motion.div>
      
      <motion.div 
        initial={{ opacity: 0, x: 20 }}
        whileInView={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        viewport={{ once: true }}
        className="flex gap-8"
      >
        <a 
          href="#" 
          className="font-['JetBrains_Mono'] text-[10px] tracking-widest uppercase text-[#fff8f0]/40 hover:text-[#795900] hover:tracking-[0.2em] transition-all duration-300"
        >
          GITHUB
        </a>
        <a 
          href="#" 
          className="font-['JetBrains_Mono'] text-[10px] tracking-widest uppercase text-[#fff8f0]/40 hover:text-[#795900] hover:tracking-[0.2em] transition-all duration-300"
        >
          DISCORD
        </a>
        <a 
          href="#" 
          className="font-['JetBrains_Mono'] text-[10px] tracking-widest uppercase text-[#fff8f0]/40 hover:text-[#795900] hover:tracking-[0.2em] transition-all duration-300"
        >
          API_LOGS
        </a>
        <a 
          href="#" 
          className="font-['JetBrains_Mono'] text-[10px] tracking-widest uppercase text-[#795900] underline underline-offset-4"
        >
          LEGAL
        </a>
      </motion.div>
    </footer>
  );
};

export default MarketingFooter;