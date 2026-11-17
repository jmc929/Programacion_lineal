import React from 'react';

export function Button({
  children,
  type = 'button',
  variant = 'primary', // 'primary' | 'secondary' | 'danger' | 'outline'
  onClick,
  disabled = false,
  className = '',
  ...props
}) {
  return (
    <button
      type={type}
      className={`btn btn-${variant} ${className}`}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
