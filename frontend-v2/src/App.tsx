import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CERDashboard } from './components/cer/CERDashboard';
import { MorningBriefing } from './components/trading/MorningBriefing';
import { PerformanceDashboard } from './components/bess/PerformanceDashboard';

type View = 'cer' | 'trading' | 'bess';

interface NavItem {
  id: View;
  label: string;
  icon: string;
  description: string;
}

const navItems: NavItem[] = [
  {
    id: 'cer',
    label: 'CER Billing',
    icon: '☀️',
    description: 'Know your number instantly',
  },
  {
    id: 'trading',
    label: '15-Min Trading',
    icon: '💰',
    description: 'Money on the table',
  },
  {
    id: 'bess',
    label: 'BESS Monitoring',
    icon: '🔋',
    description: 'Stop losing money',
  },
];

function App() {
  const [currentView, setCurrentView] = useState<View>('cer');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with Navigation */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-8 py-6">
          {/* Logo and Title */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                SentricS2
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Insanely Great Edition
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className="text-sm text-gray-600">Demo Mode</p>
                <p className="text-xs text-gray-500">All data is simulated</p>
              </div>
              <div className="text-4xl">✨</div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex gap-3">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id)}
                className={`
                  relative flex-1 px-6 py-4 rounded-xl font-semibold
                  transition-all duration-300
                  ${currentView === item.id
                    ? 'bg-gradient-to-br from-green-500 to-green-600 text-white shadow-lg scale-105'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }
                `}
              >
                <div className="flex flex-col items-center gap-2">
                  <span className="text-3xl">{item.icon}</span>
                  <span className="text-sm font-bold">{item.label}</span>
                  <span className={`
                    text-xs
                    ${currentView === item.id ? 'text-white/90' : 'text-gray-500'}
                  `}>
                    {item.description}
                  </span>
                </div>

                {/* Active Indicator */}
                {currentView === item.id && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute inset-0 bg-gradient-to-br from-green-500 to-green-600 rounded-xl -z-10"
                    transition={{ type: 'spring', duration: 0.5 }}
                  />
                )}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="relative">
        <AnimatePresence mode="wait">
          {currentView === 'cer' && (
            <motion.div
              key="cer"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <CERDashboard />
            </motion.div>
          )}

          {currentView === 'trading' && (
            <motion.div
              key="trading"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <MorningBriefing />
            </motion.div>
          )}

          {currentView === 'bess' && (
            <motion.div
              key="bess"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <PerformanceDashboard />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-8 py-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">
                © 2025 SentricS2 - Insanely Great Edition
              </p>
              <p className="text-xs text-gray-500 mt-1">
                "Design is not just what it looks like. Design is how it works." - Steve Jobs
              </p>
            </div>
            <div className="text-4xl opacity-50">
              🇮🇹
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
