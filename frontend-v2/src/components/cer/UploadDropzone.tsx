import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useCERStore } from '../../store/useCERStore';

export function UploadDropzone() {
  const { startUpload, updateProgress, completeUpload } = useCERStore();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    startUpload(file.name);

    // Simulate upload process with realistic stages
    const stages = [
      {
        stage: 'detecting' as const,
        progress: 15,
        message: 'Detecting file format...',
        details: ['✓ Detected format: GSE Portale SPC'],
        delay: 200,
      },
      {
        stage: 'reading' as const,
        progress: 35,
        message: 'Reading data...',
        details: ['✓ Found 720 hourly readings'],
        delay: 300,
      },
      {
        stage: 'matching' as const,
        progress: 65,
        message: 'Matching members...',
        details: ['✓ Matched 12 members by POD code'],
        delay: 400,
      },
      {
        stage: 'calculating' as const,
        progress: 87,
        message: 'Calculating shared energy...',
        details: ['→ Calculating shared energy...'],
        delay: 300,
      },
    ];

    for (const stage of stages) {
      await new Promise(resolve => setTimeout(resolve, stage.delay));
      updateProgress({
        stage: stage.stage,
        progress: stage.progress,
        message: stage.message,
        fileName: file.name,
        details: stage.details,
      });
    }

    // Complete upload with updated data
    await new Promise(resolve => setTimeout(resolve, 400));
    completeUpload(
      {
        id: 'cer_002',
        month: 'January',
        year: 2025,
        totalEarnings: 13156,
        changeAmount: 1512,
        changePercentage: 13.0,
        lastUpdated: new Date(),
        hourlyReadings: 720,
        membersProcessed: 12,
      },
      [
        {
          type: 'peak',
          icon: '🌞',
          title: 'Peak sharing improved: Now 10am-3pm',
          description: 'Was 11am-2pm - expanded by 2 hours',
        },
        {
          type: 'opportunity',
          icon: '📈',
          title: 'Weekend performance up 18%',
          description: 'Solar production optimization paying off',
        },
        {
          type: 'opportunity',
          icon: '💡',
          title: 'Shift EV charging to midday',
          description: 'Use excess solar production → +€124/month',
          impact: '+€124/month',
        },
      ]
    );
  }, [startUpload, updateProgress, completeUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    multiple: false,
  });

  return (
    <div
      {...getRootProps()}
      className={`
        relative border-2 border-dashed rounded-2xl p-16 text-center cursor-pointer
        transition-all duration-300 ease-out
        ${isDragActive
          ? 'border-green-500 bg-green-50 scale-[1.02] shadow-2xl'
          : 'border-gray-300 bg-white hover:border-green-400 hover:bg-gray-50 hover:scale-[1.01]'
        }
      `}
    >
      <input {...getInputProps()} />

      <div className="space-y-4">
        <div className="text-6xl">
          {isDragActive ? '✨' : '📁'}
        </div>

        <div>
          <p className="text-xl font-semibold text-gray-800 mb-2">
            {isDragActive
              ? 'Drop your file here'
              : 'Drop your GSE or e-distribuzione file here'
            }
          </p>
          <p className="text-sm text-gray-500">
            We support all formats automatically
          </p>
        </div>

        <button
          type="button"
          className="
            mt-4 px-6 py-3 bg-green-500 text-white rounded-lg font-medium
            hover:bg-green-600 transition-colors duration-200
            focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2
          "
        >
          Or click to browse
        </button>
      </div>
    </div>
  );
}
