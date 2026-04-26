import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';

type Props = { icon: LucideIcon; className?: string; label: string };

export function IconFrame3D({ icon: Icon, className = '', label }: Props) {
  return (
    <motion.div
      className={`sl-icon-cube ${className}`}
      whileHover={{ rotateX: 4, rotateY: -4, y: -2 }}
      transition={{ type: 'spring', stiffness: 320, damping: 22 }}
      title={label}
    >
      <Icon className="h-6 w-6 text-gold-400" aria-hidden />
    </motion.div>
  );
}
