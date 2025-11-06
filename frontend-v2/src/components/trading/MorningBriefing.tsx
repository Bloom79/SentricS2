import { motion } from 'framer-motion';
import { useTradingStore } from '../../store/useTradingStore';

export function MorningBriefing() {
  const briefing = useTradingStore((state) => state.briefing);

  if (!briefing) return null;

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('it-IT', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      weekday: 'long',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    }).format(date);
  };

  const opportunityGain = briefing.potentialRevenue - briefing.currentRevenue;
  const opportunityPercent = ((opportunityGain / briefing.currentRevenue) * 100).toFixed(0);

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 to-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Morning Greeting */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <div className="text-6xl mb-4">🌅</div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            GOOD MORNING
          </h1>
          <p className="text-xl text-gray-600">
            {formatDate(briefing.date)}
          </p>
        </motion.div>

        {/* Current Revenue Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl shadow-xl p-10 text-center"
        >
          <p className="text-lg text-gray-600 mb-3 uppercase tracking-wide">
            Your 6 plants will make
          </p>
          <div className="text-6xl font-bold text-gray-900 tabular-nums mb-2">
            {formatCurrency(briefing.currentRevenue)}
          </div>
          <p className="text-gray-500">today</p>
        </motion.div>

        {/* Potential Revenue Card - The Hook */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl shadow-2xl p-10 text-center text-white"
        >
          <p className="text-xl mb-4 uppercase tracking-wide">
            But you could make
          </p>
          <div className="text-7xl font-bold tabular-nums mb-3">
            {formatCurrency(briefing.potentialRevenue)}
          </div>
          <div className="inline-flex items-center gap-3 bg-white/20 backdrop-blur px-6 py-3 rounded-full">
            <span className="text-3xl font-bold">
              +{formatCurrency(opportunityGain)}
            </span>
            <span className="text-2xl">
              (+{opportunityPercent}%)
            </span>
          </div>
        </motion.div>

        {/* Opportunities List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-2xl shadow-xl p-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <span>💰</span>
            HERE'S HOW TO GET IT
          </h2>

          <div className="space-y-6">
            {briefing.opportunities.map((opp, index) => (
              <motion.div
                key={opp.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + index * 0.1 }}
                className="border-l-4 border-green-500 pl-6 py-4 bg-gray-50 rounded-r-xl"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl font-bold text-gray-900 tabular-nums">
                        {index + 1}.
                      </span>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {opp.action}
                      </h3>
                      <span className="text-sm text-gray-600 bg-gray-200 px-3 py-1 rounded-full">
                        {opp.time}
                      </span>
                    </div>
                    <p className="text-gray-700 ml-8">
                      {opp.description}
                    </p>
                  </div>
                  <div className="text-right ml-6">
                    <div className="text-2xl font-bold text-green-600 tabular-nums">
                      +{formatCurrency(opp.impact)}
                    </div>
                    <div className={`
                      text-xs font-semibold px-2 py-1 rounded mt-1
                      ${opp.price < 0 ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}
                    `}>
                      {opp.price < 0 ? 'NEGATIVE' : `€${opp.price}/MWh`}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="flex flex-col gap-4"
        >
          <button className="
            w-full px-8 py-5 bg-green-500 text-white rounded-xl font-bold text-lg
            hover:bg-green-600 transition-all duration-200
            shadow-lg hover:shadow-2xl hover:scale-[1.02]
            flex items-center justify-center gap-3
          ">
            <span className="text-2xl">✓</span>
            Apply All Optimizations
          </button>

          <button className="
            w-full px-8 py-5 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-xl font-bold text-lg
            hover:from-green-700 hover:to-green-800 transition-all duration-200
            shadow-lg hover:shadow-2xl
            flex items-center justify-center gap-3
          ">
            <span className="text-2xl">🤖</span>
            Auto-Optimize Going Forward
          </button>

          <div className="flex gap-4 mt-2">
            <button className="
              flex-1 px-6 py-3 bg-white text-gray-700 rounded-lg font-semibold
              border-2 border-gray-300 hover:border-gray-400
              transition-colors duration-200
            ">
              Show Me The Math
            </button>
            <button className="
              flex-1 px-6 py-3 bg-white text-gray-700 rounded-lg font-semibold
              border-2 border-gray-300 hover:border-gray-400
              transition-colors duration-200
            ">
              Customize Preferences
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
