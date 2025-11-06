import { motion } from 'framer-motion';
import { useCERStore } from '../../store/useCERStore';
import { UploadDropzone } from './UploadDropzone';
import { ProcessingAnimation } from './ProcessingAnimation';
import { InsightCard } from './InsightCard';

export function CERDashboard() {
  const { data, insights, isUploading } = useCERStore();

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('it-IT', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Format date
  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('it-IT', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  if (isUploading) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8">
        <ProcessingAnimation />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Hero Section - The Number */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-xl p-12 text-center"
        >
          <h1 className="text-2xl font-semibold text-gray-700 mb-4 tracking-tight">
            YOUR CER EARNINGS
          </h1>

          {data && (
            <>
              {/* The Hero Number */}
              <motion.div
                key={data.totalEarnings}
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="mb-4"
              >
                <div className="text-7xl font-bold text-gray-900 tabular-nums">
                  {formatCurrency(data.totalEarnings)}
                </div>
              </motion.div>

              {/* Change Indicator */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                className={`
                  inline-flex items-center gap-2 px-4 py-2 rounded-full
                  ${data.changeAmount >= 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}
                `}
              >
                <span className="text-2xl">
                  {data.changeAmount >= 0 ? '↑' : '↓'}
                </span>
                <span className="font-semibold text-xl tabular-nums">
                  {formatCurrency(Math.abs(data.changeAmount))}
                </span>
                <span className="text-lg">
                  ({data.changePercentage > 0 ? '+' : ''}{data.changePercentage.toFixed(1)}%)
                </span>
              </motion.div>

              {/* Context */}
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="text-gray-600 mt-4"
              >
                vs. last month
              </motion.p>

              {/* Last Updated */}
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="text-sm text-gray-500 mt-6"
              >
                Last updated: {formatDate(data.lastUpdated)}
              </motion.p>
            </>
          )}
        </motion.div>

        {/* Upload Dropzone */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <UploadDropzone />
        </motion.div>

        {/* Insights Section */}
        {insights.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-6"
          >
            <h2 className="text-2xl font-bold text-gray-900">
              📊 INSIGHTS THIS MONTH
            </h2>

            <div className="grid gap-4">
              {insights.map((insight, index) => (
                <InsightCard
                  key={index}
                  insight={insight}
                  index={index}
                />
              ))}
            </div>
          </motion.div>
        )}

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="flex gap-4 justify-center"
        >
          <button className="
            px-6 py-3 bg-green-500 text-white rounded-lg font-semibold
            hover:bg-green-600 transition-colors duration-200
            shadow-lg hover:shadow-xl
          ">
            Download Member Reports
          </button>
          <button className="
            px-6 py-3 bg-white text-gray-700 rounded-lg font-semibold
            border-2 border-gray-300 hover:border-gray-400
            transition-colors duration-200
          ">
            View Detailed Analytics
          </button>
        </motion.div>
      </div>
    </div>
  );
}
