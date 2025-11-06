import { motion } from 'framer-motion';
import { BESSIssue } from '../../types';

interface IssueCardProps {
  issue: BESSIssue;
  index: number;
}

export function IssueCard({ issue, index }: IssueCardProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('it-IT', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
      className="border-2 border-amber-200 bg-amber-50 rounded-xl p-6 hover:shadow-xl transition-shadow duration-200"
    >
      {/* Header */}
      <div className="flex items-start gap-4 mb-4">
        <div className="text-4xl">⚠️</div>
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-900 mb-1">
            ISSUE #{index + 1}: {issue.title}
          </h3>
        </div>
      </div>

      {/* Description */}
      <div className="mb-4 pl-16">
        <p className="text-gray-700 mb-4">{issue.description}</p>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 bg-white rounded-lg p-4">
          <div>
            <p className="text-sm text-gray-600 mb-1">Last 30 days</p>
            <p className="text-lg font-semibold text-gray-900">
              47 hours of negative prices
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Missed opportunity</p>
            <p className="text-lg font-semibold text-gray-900">
              2,115 kWh
            </p>
          </div>
        </div>

        {/* Annual Loss - Big and Bold */}
        <div className="mt-4 bg-red-50 border-2 border-red-200 rounded-lg p-4 text-center">
          <p className="text-sm text-red-700 font-semibold mb-1">Annual Loss</p>
          <p className="text-4xl font-bold text-red-600 tabular-nums">
            {formatCurrency(issue.annualLoss)}
          </p>
        </div>
      </div>

      {/* Fix Section */}
      <div className="pl-16 space-y-3">
        <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4">
          <p className="text-sm font-semibold text-green-800 mb-2">FIX:</p>
          <p className="text-lg font-bold text-green-900 mb-2">{issue.fix}</p>
          <p className="text-gray-700">{issue.fixDetails}</p>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button className="
            flex-1 px-6 py-3 bg-green-500 text-white rounded-lg font-bold
            hover:bg-green-600 transition-colors duration-200
            shadow-md hover:shadow-lg
          ">
            {issue.id === 'issue_1' && 'Enable Auto-Trading'}
            {issue.id === 'issue_2' && 'Optimize Discharge'}
            {issue.id === 'issue_3' && 'Increase DOD'}
          </button>
          <button className="
            px-6 py-3 bg-white text-gray-700 rounded-lg font-semibold
            border-2 border-gray-300 hover:border-gray-400
            transition-colors duration-200
          ">
            Learn More
          </button>
        </div>
      </div>
    </motion.div>
  );
}
