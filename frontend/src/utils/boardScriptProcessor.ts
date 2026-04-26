import { BoardScript, BoardStep } from '@/types';

/**
 * Process and improve board script content for better scientific presentation
 */
export const processBoardScript = (script: BoardScript): BoardScript => {
  const processedSteps: BoardStep[] = script.steps.map((step, index) => {
    let processedContent = step.content;
    let processedType = step.type;

    // Clean up excessive emojis and improve scientific content
    if (processedContent.includes('🌊') || processedContent.includes('water')) {
      processedContent = improveWaterCycleContent(processedContent, index);
    } else if (processedContent.includes('math') || processedContent.includes('equation')) {
      processedContent = improveMathContent(processedContent);
      processedType = 'equation';
    } else if (processedContent.includes('This is called') || processedContent.includes('✨')) {
      processedType = 'highlight';
      processedContent = processedContent.replace(/✨/g, '').trim();
    }

    // Determine appropriate step type based on content
    if (index === 0 || processedContent.includes('CYCLE') || processedContent.toUpperCase() === processedContent) {
      processedType = 'title';
    } else if (processedContent.includes('→') || processedContent.includes('H₂O') || processedContent.includes('PROCESS')) {
      processedType = 'diagram';
    } else if (processedContent.includes('EVAPORATION') || processedContent.includes('CONDENSATION') || 
               processedContent.includes('PRECIPITATION') || processedContent.includes('COLLECTION')) {
      processedType = 'highlight';
    }

    return {
      ...step,
      content: processedContent,
      type: processedType,
      draw_duration_ms: step.draw_duration_ms || 2500 // Slightly slower for better readability
    };
  });

  return {
    ...script,
    steps: processedSteps,
    total_duration_ms: processedSteps.length * 2500 + 2000 // Add buffer time
  };
};

/**
 * Improve water cycle specific content
 */
const improveWaterCycleContent = (content: string, stepIndex: number): string => {
  let improved = content;

  // Clean up emojis and replace with scientific notation
  improved = improved.replace(/🌊/g, 'H₂O(l)');
  improved = improved.replace(/☁️/g, 'Cloud Formation');
  improved = improved.replace(/🌧️/g, 'Precipitation');
  improved = improved.replace(/💧/g, 'H₂O');
  improved = improved.replace(/⬆️|UP!/g, '↑');
  improved = improved.replace(/🔄/g, '⟲');
  improved = improved.replace(/✨/g, '');

  // Replace casual language with scientific terms
  improved = improved.replace(/SUN heats/g, 'Solar radiation heats');
  improved = improved.replace(/water turns into vapor/gi, 'H₂O(l) → H₂O(g)');
  improved = improved.replace(/vapor gets cold/gi, 'H₂O(g) + ΔT ↓');
  improved = improved.replace(/forms clouds/gi, '→ Cloud nucleation');
  improved = improved.replace(/water falls back/gi, 'H₂O(l) precipitation');
  improved = improved.replace(/flows back/gi, 'Surface runoff →');

  // Create step-specific scientific diagrams
  if (stepIndex === 0) {
    return 'THE WATER CYCLE: A Continuous Process';
  } else if (improved.includes('EVAPORATION')) {
    return `EVAPORATION: H₂O(l) + Solar Energy → H₂O(g) ↑
    
• Solar radiation provides energy
• Liquid water becomes water vapor
• Occurs at surface of water bodies`;
  } else if (improved.includes('CONDENSATION')) {
    return `CONDENSATION: H₂O(g) + Cooling → H₂O(l) droplets
    
• Water vapor cools at higher altitudes
• Forms tiny droplets around nuclei
• Creates visible clouds`;
  } else if (improved.includes('PRECIPITATION')) {
    return `PRECIPITATION: Cloud droplets → Surface H₂O
    
• Droplets combine and grow heavy
• Gravity pulls water downward
• Rain, snow, sleet, or hail`;
  } else if (improved.includes('COLLECTION')) {
    return `COLLECTION: Surface flow → Water bodies
    
• Runoff flows to rivers and lakes
• Infiltration → Groundwater
• Cycle continues indefinitely ⟲`;
  }

  return improved.replace(/!/g, '.').replace(/\s+/g, ' ').trim();
};

/**
 * Improve mathematical content
 */
const improveMathContent = (content: string): string => {
  let improved = content;

  // Convert common math expressions
  improved = improved.replace(/\^2/g, '²');
  improved = improved.replace(/\^3/g, '³');
  improved = improved.replace(/sqrt/g, '√');
  improved = improved.replace(/pi/g, 'π');
  improved = improved.replace(/delta/g, 'Δ');
  improved = improved.replace(/theta/g, 'θ');
  improved = improved.replace(/alpha/g, 'α');
  improved = improved.replace(/beta/g, 'β');

  return improved;
};

/**
 * Create a fallback board script for cases where the original is poorly formatted
 */
export const createFallbackBoardScript = (topic: string, explanation: string): BoardScript => {
  const steps: BoardStep[] = [
    {
      step: 0,
      content: topic.toUpperCase(),
      type: 'title',
      draw_duration_ms: 2000
    }
  ];

  // Extract key sentences and create steps
  const sentences = explanation.split(/[.!?]+/).filter(s => s.trim().length > 20);
  
  sentences.slice(0, 6).forEach((sentence, index) => {
    let type: BoardStep['type'] = 'body';
    let content = sentence.trim();

    // Determine step type based on content
    if (content.includes('called') || content.includes('This is')) {
      type = 'highlight';
    } else if (content.includes('=') || content.includes('formula') || content.includes('equation')) {
      type = 'equation';
    } else if (content.includes('process') || content.includes('step') || content.includes('→')) {
      type = 'diagram';
    }

    steps.push({
      step: index + 1,
      content: content,
      type: type,
      draw_duration_ms: 2500
    });
  });

  return {
    steps,
    total_duration_ms: steps.length * 2500 + 1000,
    background_color: '#0a1a0a',
    text_color: '#ffffff'
  };
};