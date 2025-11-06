import { motion } from 'framer-motion';
import { useBESSStore } from '../../store/useBESSStore';
import { IssueCard } from './IssueCard';

export function PerformanceDashboard() {
  const performance = useBESSStore((state) => state.performance);

  if (!performance) return null;

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('it-IT', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getScoreColor = (score: number) => {
    if (score >= 95) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 60) return 'text-amber-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 95) return 'EXCELLENT';
    if (score >= 80) return 'GOOD, BUT NOT GREAT';
    if (score >= 60) return 'NEEDS IMPROVEMENT';
    return 'CRITICAL';
  };

  const getStars = (score: number) => {
    const fullStars = Math.floor(score / 20);
    const emptyStars = 5 - fullStars;
    return '⭐'.repeat(fullStars) + '☆'.repeat(emptyStars);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Performance Score Card */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-xl p-12 text-center"
        >
          <h1 className="text-2xl font-semibold text-gray-700 mb-6 tracking-tight">
            YOUR BESS PERFORMANCE SCORE
          </h1>

          {/* The Score */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: 'spring', duration: 0.6 }}
            className="mb-4"
          >
            <div className={`text-8xl font-bold ${getScoreColor(performance.score)} tabular-nums`}>
              {performance.score}/100
            </div>
          </motion.div>

          {/* Stars */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-5xl mb-4"
          >
            {getStars(performance.score)}
          </motion.div>

          {/* Label */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className={`text-2xl font-bold ${getScoreColor(performance.score)}`}
          >
            {getScoreLabel(performance.score)}
          </motion.p>
        </motion.div>

        {/* Total Loss Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-red-500 to-red-600 rounded-2xl shadow-2xl p-10 text-center text-white"
        >
          <p className="text-xl mb-3 uppercase tracking-wide">
            💸 You're losing
          </p>
          <div className="text-7xl font-bold tabular-nums mb-3">
            {formatCurrency(performance.totalLoss)}
          </div>
          <p className="text-2xl opacity-90">/year</p>
          <p className="mt-6 text-lg bg-white/20 backdrop-blur inline-block px-6 py-3 rounded-full">
            Here's exactly how to fix it ↓
          </p>
        </motion.div>

        {/* Issues List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="space-y-6"
        >
          {performance.issues.map((issue, index) => (
            <IssueCard key={issue.id} issue={issue} index={index} />
          ))}
        </motion.div>

        {/* Apply All Fixes Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="flex flex-col gap-4"
        >
          <button className="
            w-full px-8 py-6 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl font-bold text-xl
            hover:from-green-600 hover:to-green-700 transition-all duration-200
            shadow-2xl hover:shadow-3xl hover:scale-[1.02]
            flex items-center justify-center gap-4
          ">
            <span className="text-3xl">✓</span>
            <span>
              APPLY ALL FIXES → Save {formatCurrency(performance.totalLoss)}/year
            </span>
          </button>

          <div className="flex gap-4">
            <button className="
              flex-1 px-6 py-3 bg-white text-gray-700 rounded-lg font-semibold
              border-2 border-gray-300 hover:border-gray-400
              transition-colors duration-200
            ">
              Explain the Math
            </button>
            <button className="
              flex-1 px-6 py-3 bg-white text-gray-700 rounded-lg font-semibold
              border-2 border-gray-300 hover:border-gray-400
              transition-colors duration-200
            ">
              Customize Settings
            </button>
          </div>
        </motion.div>

        {/* Info Box */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="bg-blue-50 border-2 border-blue-200 rounded-xl p-6"
        >
          <div className="flex items-start gap-4">
            <div className="text-3xl">ℹ️</div>
            <div>
              <h3 className="font-bold text-gray-900 mb-2">
                How we calculate your score
              </h3>
              <p className="text-gray-700 text-sm leading-relaxed">
                Your BESS Performance Score is based on how effectively you're capturing revenue opportunities.
                We compare your actual operations against optimal dispatch strategy considering: real-time prices,
                battery constraints, degradation costs, and market conditions. A score of 100 means perfect optimization.
                87 means you're doing well, but leaving {formatCurrency(performance.totalLoss)} on the table annually.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
