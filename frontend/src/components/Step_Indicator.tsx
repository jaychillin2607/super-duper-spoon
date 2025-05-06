import { CheckCircle } from "lucide-react";
interface StepIndicatorProps {
  currentStep: number;
  totalSteps: number;
}

export default function StepIndicator({
  currentStep,
  totalSteps,
}: StepIndicatorProps) {
  const steps = [
    { number: 1, title: "Personal Information" },
    { number: 2, title: "Business Information" },
    { number: 3, title: "Financial Information" },
  ];
  return (
    <div className="w-full">
      <div className="flex items-center justify-between">
        {steps.map((step) => (
          <div key={step.number} className="flex flex-col items-center">
            <div
              className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                step.number < currentStep
                  ? "bg-green-500 border-green-500 text-white"
                  : step.number === currentStep
                  ? "border-blue-500 text-blue-500"
                  : "border-gray-300 text-gray-300"
              }`}
            >
              {step.number < currentStep ? (
                <CheckCircle className="w-6 h-6" />
              ) : (
                <span>{step.number}</span>
              )}
            </div>
            <span
              className={`mt-2 text-sm ${
                step.number <= currentStep ? "text-gray-900" : "text-gray-400"
              }`}
            >
              {step.title}
            </span>
          </div>
        ))}
      </div>

      <div className="relative mt-4">
        <div className="absolute top-0 left-0 h-1 bg-gray-200 w-full"></div>
        <div
          className="absolute top-0 left-0 h-1 bg-blue-500 transition-all duration-300"
          style={{ width: `${((currentStep - 1) / (totalSteps - 1)) * 100}%` }}
        ></div>
      </div>
    </div>
  );
}
