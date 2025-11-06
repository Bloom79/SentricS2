import { motion } from 'framer-motion';
import { useCERStore } from '../../store/useCERStore';

export function ProcessingAnimation() {
  const uploadProgress = useCERStore((state) => state.uploadProgress);

  if (!uploadProgress) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl shadow-xl p-12 max-w-2xl mx-auto"
    >
      <div className="text-center space-y-8">
        {/* Title */}
        <motion.div
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            ✨ Processing Your File
          </h2>
          <p className="text-lg text-gray-600 font-mono">
            {uploadProgress.fileName}
          </p>
        </motion.div>

        {/* Progress Bar */}
        <div className="space-y-3">
          <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-green-500 to-green-600 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${uploadProgress.progress}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600 font-medium">{uploadProgress.message}</span>
            <span className="text-gray-900 font-bold tabular-nums">
              {uploadProgress.progress}%
            </span>
          </div>
        </div>

        {/* Status Messages */}
        <div className="bg-gray-50 rounded-xl p-6 text-left space-y-2">
          {uploadProgress.details.map((detail, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="text-gray-700"
            >
              {detail}
            </motion.div>
          ))}
        </div>

        {/* Elapsed Time */}
        <motion.p
          className="text-gray-500 text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          Processing...
        </motion.p>
      </div>
    </motion.div>
  );
}
