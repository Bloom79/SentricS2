import { motion } from 'framer-motion';
import { CERInsight } from '../../types';

interface InsightCardProps {
  insight: CERInsight;
  index: number;
}

export function InsightCard({ insight, index }: InsightCardProps) {
  const colors = {
    peak: 'bg-green-50 border-green-200',
    low: 'bg-amber-50 border-amber-200',
    opportunity: 'bg-blue-50 border-blue-200',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
      className={`
        ${colors[insight.type]}
        border-2 rounded-xl p-5
        hover:shadow-lg transition-shadow duration-200
      `}
    >
      <div className="flex items-start gap-4">
        <div className="text-3xl flex-shrink-0">
          {insight.icon}
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 mb-1">
            {insight.title}
          </h3>
          <p className="text-gray-700 text-sm">
            {insight.description}
          </p>
          {insight.impact && (
            <p className="mt-2 text-green-700 font-bold text-sm">
              {insight.impact}
            </p>
          )}
        </div>
      </div>
    </motion.div>
  );
}
