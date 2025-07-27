// components/common/Input.tsx
import React from 'react';

interface InputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  type?: 'text' | 'textarea' | 'file';
  rows?: number;
  maxLength?: number;
  accept?: string; // for file input
  style?: React.CSSProperties;
}

export const Input: React.FC<InputProps> = ({
  value,
  onChange,
  placeholder,
  disabled = false,
  type = 'text',
  rows = 5,
  maxLength,
  accept,
  style = {}
}) => {
  const baseStyles = {
    width: '100%',
    padding: 'var(--spacing-md)',
    border: '2px solid #e9ecef',
    borderRadius: 'var(--radius-md)',
    fontSize: '16px',
    fontFamily: 'inherit',
    lineHeight: '1.5',
    ...style
  };

  if (type === 'textarea') {
    return (
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        maxLength={maxLength}
        rows={rows}
        style={{
          ...baseStyles,
          resize: 'vertical',
          minHeight: '150px'
        }}
      />
    );
  }

  if (type === 'file') {
    return (
      <input
        type="file"
        accept={accept}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onChange(file.name); // or handle file differently
        }}
        disabled={disabled}
        style={{
          ...baseStyles,
          cursor: 'pointer'
        }}
      />
    );
  }

  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      disabled={disabled}
      maxLength={maxLength}
      style={baseStyles}
    />
  );
};