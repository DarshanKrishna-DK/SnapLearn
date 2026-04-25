import React, { useState, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';

interface QuestionInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isLoading?: boolean;
  placeholder?: string;
  className?: string;
  maxLength?: number;
}

const QuestionInput: React.FC<QuestionInputProps> = ({
  value,
  onChange,
  onSubmit,
  isLoading = false,
  placeholder = "Type your question here...",
  className = "",
  maxLength = 500
}) => {
  const [isFocused, setIsFocused] = useState(false);

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading && value.trim()) {
        onSubmit();
      }
    }
  };

  const handleSubmit = () => {
    if (!isLoading && value.trim()) {
      onSubmit();
    }
  };

  const remainingChars = maxLength - value.length;
  const isNearLimit = remainingChars <= 50;

  return (
    <div className={className}>
      <div 
        className={`relative border rounded-lg transition-all duration-200 ${
          isFocused 
            ? 'border-primary-500 ring-2 ring-primary-200' 
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={handleKeyPress}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          maxLength={maxLength}
          disabled={isLoading}
          className={`w-full px-4 py-3 pr-12 bg-transparent resize-none focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed ${
            value.length > 0 ? 'min-h-[100px]' : 'min-h-[60px]'
          }`}
          rows={1}
          style={{
            height: 'auto',
            minHeight: value.length > 0 ? '100px' : '60px',
          }}
        />
        
        {/* Submit button */}
        <button
          onClick={handleSubmit}
          disabled={isLoading || !value.trim()}
          className={`absolute right-2 bottom-2 p-2 rounded-lg transition-all duration-200 ${
            !isLoading && value.trim()
              ? 'bg-primary-600 text-white hover:bg-primary-700 active:scale-95'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          }`}
          title="Send question (Enter)"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>

      {/* Character counter and help text */}
      <div className="flex items-center justify-between mt-2 text-sm">
        <div className="text-gray-500">
          {value.length === 0 ? (
            "Press Enter to submit, Shift+Enter for new line"
          ) : (
            "Make your question as specific as possible for better explanations"
          )}
        </div>
        
        <div className={`${isNearLimit ? 'text-orange-600' : 'text-gray-500'}`}>
          {remainingChars} characters remaining
        </div>
      </div>

      {/* Length warning */}
      {isNearLimit && (
        <div className="mt-2 text-sm text-orange-600 bg-orange-50 border border-orange-200 rounded-lg p-2">
          You're approaching the character limit. Consider breaking your question into smaller parts.
        </div>
      )}
    </div>
  );
};

export default QuestionInput;