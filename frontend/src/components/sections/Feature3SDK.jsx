import React, { useState } from 'react';
import { motion } from 'framer-motion';

const Feature3SDK = () => {
  const [activeTab, setActiveTab] = useState('embed');

  const codeExamples = {
    embed: `// Embed SnapLearn AI in your app
import { SnapLearnSDK } from '@snaplearn/sdk';

const tutorConfig = {
  apiKey: 'your_api_key',
  studentId: 'student_123',
  gradeLevel: 7,
  theme: 'dark-terminal'
};

function MyApp() {
  return (
    <div>
      <SnapLearnSDK 
        config={tutorConfig}
        onExplanationComplete={(result) => {
          console.log('Video generated:', result.videoUrl);
        }}
      />
    </div>
  );
}`,
    
    api: `// Direct API Usage
const response = await fetch('/api/explain', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: "Explain quadratic equations",
    student_id: "student_123", 
    grade_level: 9,
    language: "english"
  })
});

const explanation = await response.json();
// Returns: personalized video + text explanation`,

    webhook: `// Real-time Confusion Detection
const snaplearn = new SnapLearnClient({
  apiKey: 'your_key',
  onConfusionDetected: (student, topic) => {
    // Student is confused - auto-switch teaching style
    snaplearn.switchTeachingStyle('visual');
  },
  onMasteryAchieved: (student, skill) => {
    // Update your platform's skill tree
    updateStudentProgress(student, skill);
  }
});`
  };

  return (
    <section id="sdk" className="bg-[#faf3e9] py-32 px-10">
      <div className="max-w-7xl mx-auto">
        <motion.h2 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="font-['Space_Grotesk'] font-black text-5xl text-center mb-16 text-[#1e0003]"
        >
          EMBEDDABLE EVERYWHERE
        </motion.h2>
        
        <div className="grid lg:grid-cols-12 gap-12">
          {/* Left: SDK Description */}
          <div className="lg:col-span-5">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <h3 className="font-['Space_Grotesk'] font-bold text-3xl mb-6 text-[#1e0003]">
                ONE SDK, INFINITE INTEGRATIONS
              </h3>
              
              <div className="space-y-6 mb-8">
                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 bg-[#795900] text-[#ffffff] flex items-center justify-center text-sm font-bold">✓</div>
                  <div>
                    <h4 className="font-['Space_Grotesk'] font-bold text-lg text-[#1e0003]">React Component</h4>
                    <p className="text-[#554243] font-['Inter'] text-sm">Drop-in component for instant tutoring</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 bg-[#795900] text-[#ffffff] flex items-center justify-center text-sm font-bold">✓</div>
                  <div>
                    <h4 className="font-['Space_Grotesk'] font-bold text-lg text-[#1e0003]">REST API</h4>
                    <p className="text-[#554243] font-['Inter'] text-sm">Language-agnostic HTTP endpoints</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 bg-[#795900] text-[#ffffff] flex items-center justify-center text-sm font-bold">✓</div>
                  <div>
                    <h4 className="font-['Space_Grotesk'] font-bold text-lg text-[#1e0003]">WebSocket Streaming</h4>
                    <p className="text-[#554243] font-['Inter'] text-sm">Real-time confusion detection & adaptation</p>
                  </div>
                </div>
              </div>
              
              <button className="bg-[#1e0003] text-[#fff8f0] px-6 py-3 font-['Space_Grotesk'] font-bold text-sm tracking-widest pixel-shadow hover:bg-[#4A0010] transition-all">
                DOWNLOAD SDK
              </button>
            </motion.div>
          </div>
          
          {/* Right: Code Examples */}
          <div className="lg:col-span-7">
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              viewport={{ once: true }}
            >
              {/* Tab Navigation */}
              <div className="flex gap-2 mb-4">
                {Object.keys(codeExamples).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-4 py-2 font-['JetBrains_Mono'] text-xs font-bold transition-all ${
                      activeTab === tab 
                        ? 'bg-[#1e0003] text-[#fff8f0]' 
                        : 'bg-[#eee7dd] text-[#1e0003] hover:bg-[#e8e2d8]'
                    }`}
                  >
                    {tab.toUpperCase()}
                  </button>
                ))}
              </div>
              
              {/* Code Block */}
              <motion.div 
                key={activeTab}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
                className="bg-[#1e0003] border border-[#795900]/20 p-6 overflow-x-auto"
              >
                <div className="font-['JetBrains_Mono'] text-[10px] text-[#795900] mb-4">
                  SNAPLEARN_SDK_{activeTab.toUpperCase()}.js
                </div>
                <pre className="font-['JetBrains_Mono'] text-sm text-[#fff8f0] leading-relaxed">
                  <code>{codeExamples[activeTab]}</code>
                </pre>
              </motion.div>
              
              <div className="mt-4 flex items-center gap-2 text-[#554243] text-xs font-['Inter']">
                <span className="material-symbols-outlined text-[#795900]">info</span>
                Full documentation available at docs.snaplearn.ai
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Feature3SDK;