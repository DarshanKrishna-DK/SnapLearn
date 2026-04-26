import { Link } from 'react-router-dom';
import { motion, type HTMLMotionProps } from 'framer-motion';
import { forwardRef, type ReactNode } from 'react';

type Variant = 'solid' | 'ghost';

const base =
  'inline-flex items-center justify-center gap-2 text-[0.55rem] sm:text-[0.62rem] leading-relaxed tracking-tight px-4 py-3 rounded-md text-center min-h-[3rem]';

type Props = {
  children: ReactNode;
  variant?: Variant;
  className?: string;
  to?: string;
  href?: string;
} & Omit<HTMLMotionProps<'button'>, 'children'>;

export const PixelButton = forwardRef<HTMLButtonElement, Props>(function PixelButton(
  { children, variant = 'solid', className = '', to, href, onClick, type = 'button', ...rest },
  ref
) {
  const cls = variant === 'solid' ? 'sl-3d-press' : 'sl-3d-ghost';
  if (to) {
    return (
      <Link to={to} onClick={onClick} className={`${base} ${cls} ${className}`}>
        {children}
      </Link>
    );
  }
  if (href) {
    return (
      <a href={href} className={`${base} ${cls} ${className}`} rel="noreferrer" target={href.startsWith('http') ? '_blank' : undefined}>
        {children}
      </a>
    );
  }
  return (
    <motion.button
      ref={ref}
      type={type}
      className={`${base} ${cls} ${className} disabled:opacity-40 disabled:pointer-events-none`}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      {...rest}
    >
      {children}
    </motion.button>
  );
});
