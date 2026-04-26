import React from 'react';

interface FormattedExplanationProps {
  explanation: string;
  className?: string;
}

const FormattedExplanation: React.FC<FormattedExplanationProps> = ({ 
  explanation, 
  className = "" 
}) => {
  // Process the text to make it more readable and presentable
  const processText = (text: string) => {
    // Split into sentences
    const sentences = text.split('. ').filter(s => s.trim().length > 0);
    
    // Group sentences into logical paragraphs
    const paragraphs: string[] = [];
    let currentParagraph = '';
    
    sentences.forEach((sentence, index) => {
      // Add period back if it was removed by split
      const processedSentence = sentence.endsWith('.') ? sentence : sentence + '.';
      
      // Check if this sentence should start a new paragraph
      const shouldStartNewParagraph = 
        sentence.toLowerCase().includes('first,') ||
        sentence.toLowerCase().includes('next,') ||
        sentence.toLowerCase().includes('then,') ||
        sentence.toLowerCase().includes('finally,') ||
        sentence.toLowerCase().includes('as the') ||
        sentence.toLowerCase().includes('when the') ||
        sentence.toLowerCase().includes('once the') ||
        sentence.toLowerCase().includes('this is called') ||
        (currentParagraph.length > 200 && index < sentences.length - 1);
      
      if (shouldStartNewParagraph && currentParagraph) {
        paragraphs.push(currentParagraph.trim());
        currentParagraph = processedSentence;
      } else {
        currentParagraph += (currentParagraph ? ' ' : '') + processedSentence;
      }
    });
    
    // Add the last paragraph
    if (currentParagraph) {
      paragraphs.push(currentParagraph.trim());
    }
    
    return paragraphs;
  };

  // Extract key terms and definitions
  const extractKeyTerms = (text: string) => {
    const keyTerms: { term: string; definition: string }[] = [];
    
    // Look for bold terms (marked with **)
    const boldMatches = text.match(/\*\*(.*?)\*\*/g);
    if (boldMatches) {
      boldMatches.forEach(match => {
        const term = match.replace(/\*\*/g, '');
        const termIndex = text.indexOf(match);
        // Get the sentence containing this term
        const sentences = text.split('. ');
        const containingSentence = sentences.find(s => s.includes(term));
        if (containingSentence) {
          keyTerms.push({
            term,
            definition: containingSentence
          });
        }
      });
    }
    
    // Look for "This is called..." patterns
    const definitionMatches = text.match(/This (?:part )?is called \*\*(.*?)\*\*/g);
    if (definitionMatches) {
      definitionMatches.forEach(match => {
        const term = match.match(/\*\*(.*?)\*\*/)?.[1];
        if (term) {
          const termIndex = text.indexOf(match);
          const beforeText = text.substring(Math.max(0, termIndex - 100), termIndex);
          const sentences = beforeText.split('. ');
          const contextSentence = sentences[sentences.length - 1] || '';
          
          keyTerms.push({
            term,
            definition: contextSentence + ' This is called ' + term + '.'
          });
        }
      });
    }
    
    return keyTerms;
  };

  const paragraphs = processText(explanation);
  const keyTerms = extractKeyTerms(explanation);

  // Format text with proper highlighting
  const formatTextWithHighlights = (text: string) => {
    // Convert **text** to bold
    return text.replace(/\*\*(.*?)\*\*/g, '<strong class="text-blue-600 font-semibold">$1</strong>');
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Main explanation */}
      <div className="space-y-4">
        {paragraphs.map((paragraph, index) => (
          <p 
            key={index} 
            className="text-gray-700 leading-relaxed text-base"
            dangerouslySetInnerHTML={{ 
              __html: formatTextWithHighlights(paragraph) 
            }}
          />
        ))}
      </div>

      {/* Key terms section (if any found) */}
      {keyTerms.length > 0 && (
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg">
          <h4 className="font-semibold text-blue-800 mb-3 text-sm uppercase tracking-wider">
            Key Terms
          </h4>
          <div className="space-y-2">
            {keyTerms.map((item, index) => (
              <div key={index} className="text-sm">
                <span className="font-semibold text-blue-700">{item.term}:</span>
                <span className="text-blue-600 ml-2">{item.definition.replace(/\*\*/g, '')}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FormattedExplanation;