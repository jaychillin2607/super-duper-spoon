import { Alert, AlertDescription } from "@/components/ui/alert";
import { Card } from "@/components/ui/card";
import { useMerchantForm } from "@/hooks/useMerchantForm";
import { AlertCircle } from "lucide-react";
import Business_Info from "./form/Business_Info";
import Financial_Info from "./form/Financial_Info";
import Personal_Info from "./form/Personal_Info";
import SuccessMessage from "./form/SuccessMessage";
import StepIndicator from "./Step_Indicator";

export default function MerchantForm() {
	const {
		formData,
		handleChange,
		handleBlur, // Include the handleBlur function from the hook
		currentStep,
		handleNext,
		handleBack,
		handleSubmit,
		loading,
		enriching,
		enriched,
		error,
		success,
	} = useMerchantForm();

	if (success) {
		return <SuccessMessage />;
	}

	return (
		<Card className="p-6 max-w-2xl mx-auto mt-8">
			<StepIndicator currentStep={currentStep} totalSteps={3} />

			{error && (
				<Alert variant="destructive" className="mb-4">
					<AlertCircle className="h-4 w-4" />
					<AlertDescription>{error}</AlertDescription>
				</Alert>
			)}

			<form onSubmit={handleSubmit}>
				{currentStep === 1 && (
					<Personal_Info
						formData={formData}
						handleChange={handleChange}
						handleNext={handleNext}
					/>
				)}
				{currentStep === 2 && (
					<Business_Info
						formData={formData}
						handleChange={handleChange}
						handleBlur={handleBlur}
						handleNext={handleNext}
						handleBack={handleBack}
						enriching={enriching}
						enriched={enriched}
					/>
				)}
				{currentStep === 3 && (
					<Financial_Info
						formData={formData}
						handleChange={handleChange}
						handleBack={handleBack}
						loading={loading}
					/>
				)}
			</form>
		</Card>
	);
}
