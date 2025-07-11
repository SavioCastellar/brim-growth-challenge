interface ProgressIndicatorProps {
    currentStep: number;
}

const ProgressIndicator = ({ currentStep }: ProgressIndicatorProps) => {
    const steps = [
        { number: 1, label: "Upload File" },
        { number: 2, label: "AI Analysis" },
        { number: 3, label: "View Results" },
        { number: 4, label: "Share & Restart" }
    ];

    return (
        <div className="flex justify-center items-center mb-8">
            <div className="flex items-center space-x-4">
                {steps.map((step, index) => (
                    <div key={step.number} className="flex items-center">
                        <div className="flex flex-col items-center">
                            <div
                                className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-white transition-all duration-300 ${step.number <= currentStep
                                    ? 'bg-[#153333] shadow-lg'
                                    : 'bg-gray-300'
                                    }`}
                            >
                                {step.number}
                            </div>
                            <span className={`text-sm mt-2 font-medium ${step.number <= currentStep
                                ? 'text-[#153333]'
                                : 'text-gray-500'
                                }`}>
                                {step.label}
                            </span>
                        </div>
                        {index < steps.length - 1 && (
                            <div
                                className={`h-0.5 w-16 mx-4 transition-all duration-300 ${step.number < currentStep
                                    ? 'bg-[#153333]'
                                    : 'bg-gray-300'
                                    }`}
                            />
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ProgressIndicator;