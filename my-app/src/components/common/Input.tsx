import React from 'react';
import styled from 'styled-components';

type InputType = 'textarea' | 'text' | 'file' | 'email' | 'password' | 'number' | 'search';

interface InputProps {
  type?: InputType;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  maxLength?: number;
  style?: React.CSSProperties;
  id?: string;
  onKeyDown?: (e: React.KeyboardEvent) => void;

  min?: number;
  max?: number;
  step?: number;
  inputMode?: React.HTMLAttributes<HTMLInputElement>['inputMode'];
  pattern?: string;
}

const StyledInput = styled.input`
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
`;

const StyledTextarea = styled.textarea`
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
  resize: vertical;
`;

export const Input: React.FC<InputProps> = ({
  type = 'text',
  value,
  onChange,
  placeholder,
  disabled = false,
  maxLength,
  style,
  id,
  onKeyDown,
  min,
  max,
  step,
  inputMode,
  pattern,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    onChange(e.target.value);
  };

  if (type === 'textarea') {
    return (
      <StyledTextarea
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        disabled={disabled}
        maxLength={maxLength}
        style={style}
        id={id}
        onKeyDown={onKeyDown}
      />
    );
  }

  return (
    <StyledInput
      type={type}
      value={value}
      onChange={handleChange}
      placeholder={placeholder}
      disabled={disabled}
      maxLength={maxLength}
      style={style}
      id={id}
      onKeyDown={onKeyDown}

      min={type === 'number' ? min : undefined}
      max={type === 'number' ? max : undefined}
      step={type === 'number' ? step : undefined}
      inputMode={inputMode}
      pattern={pattern}
    />
  );
};
