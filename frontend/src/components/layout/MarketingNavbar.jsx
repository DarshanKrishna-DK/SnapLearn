import React, { useState } from 'react';
import { motion } from 'framer-motion';

const MarketingNavbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <nav className="bg-[#4A0010] sticky top-0 z-50 flex justify-between items-center w-full px-6 py-4 max-w-full shadow-[0_0_15px_rgba(121,89,0,0.15)] after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-full after:h-[2px] after:bg-[#795900]">
      <div className="text-2xl font-black italic tracking-tighter text-[#FFF8F0] font-['Space_Grotesk']">
        SNAPLEARN_AI
      </div>
      
      {/* Desktop Navigation */}
      <div className="hidden md:flex gap-8">
        <button 
          onClick={() => scrollToSection('features')}
          className="font-['Space_Grotesk'] font-bold uppercase tracking-[0.05em] text-sm text-[#795900] border-b-2 border-[#795900] pb-1"
        >
          FEATURES
        </button>
        <button 
          onClick={() => scrollToSection('tech-stack')}
          className="font-['Space_Grotesk'] font-bold uppercase tracking-[0.05em] text-sm text-[#FFF8F0]/70 hover:text-[#FFF8F0] transition-colors"
        >
          TECH_STACK
        </button>
        <button 
          onClick={() => scrollToSection('sdk')}
          className="font-['Space_Grotesk'] font-bold uppercase tracking-[0.05em] text-sm text-[#FFF8F0]/70 hover:text-[#FFF8F0] transition-colors"
        >
          SDK
        </button>
        <button 
          onClick={() => scrollToSection('docs')}
          className="font-['Space_Grotesk'] font-bold uppercase tracking-[0.05em] text-sm text-[#FFF8F0]/70 hover:text-[#FFF8F0] transition-colors"
        >
          DOCUMENTATION
        </button>
      </div>
      
      {/* CTA Button */}
      <div className="flex items-center gap-4">
        <button 
          onClick={() => scrollToSection('demo')}
          className="bg-[#795900] text-[#ffffff] px-4 py-2 font-['Space_Grotesk'] font-bold uppercase text-xs tracking-widest pixel-shadow transition-all hover:glow-secondary"
        >
          START_TERMINAL
        </button>
      </div>
      
      {/* Mobile Menu (if needed) */}
      <div className="md:hidden">
        <button
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="text-[#FFF8F0] p-2"
        >
          ☰
        </button>
      </div>
    </nav>
  );
};

export default MarketingNavbar;