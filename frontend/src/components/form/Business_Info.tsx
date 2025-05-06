import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { FormData } from "@/types/formType";
import { CheckCircle, Loader2 } from "lucide-react";
import { useState } from "react";

interface Props {
	formData: FormData;
	handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
	handleBlur: (e: React.FocusEvent<HTMLInputElement>) => void; // Add the blur handler
	handleNext: () => void;
	handleBack: () => void;
	enriching: boolean;
	enriched: boolean;
}

export default function Business_Info({
	formData,
	handleChange,
	handleBlur,
	handleNext,
	handleBack,
	enriching,
	enriched,
}: Props) {
	// Track whether form has been interacted with
	const [touched, setTouched] = useState({
		business_name: false,
		tin: false,
		zip_code: false,
		form: false, // tracks if form has been submitted
	});

	// Initialize errors state - start with no errors
	const [errors, setErrors] = useState({
		business_name: "",
		tin: "",
		zip_code: "",
	});

	// Safely trim a string, handling null or undefined
	const safeTrim = (str: string | null | undefined): string => {
		return str ? str.trim() : "";
	};

	// Validate field and return error message if invalid
	const validateField = (
		name: string,
		value: string | null | undefined
	): string => {
		const trimmedValue = safeTrim(value);

		switch (name) {
			case "business_name":
				return trimmedValue === "" ? "Business name is required" : "";
			case "tin":
				return trimmedValue === ""
					? "TIN is required"
					: !/^\d+$/.test(trimmedValue)
					? "TIN must contain only numbers"
					: trimmedValue.length < 9 || trimmedValue.length > 11
					? "TIN must be 9-11 digits"
					: "";
			case "zip_code":
				return trimmedValue === ""
					? "Zip code is required"
					: !/^\d+$/.test(trimmedValue)
					? "Zip code must contain only numbers"
					: trimmedValue.length < 5
					? "Zip code must be at least 5 digits"
					: "";
			default:
				return "";
		}
	};

	// Custom input handler for validation
	const validateInput = (e: React.ChangeEvent<HTMLInputElement>) => {
		const { name, value } = e.target;

		// Mark this field as touched
		setTouched((prev) => ({
			...prev,
			[name]: true,
		}));

		// Validate this field
		setErrors((prev) => ({
			...prev,
			[name]: validateField(name, value),
		}));

		// Process the change through the parent handler
		handleChange(e);
	};

	// Handle input blur for enrichment
	const handleInputBlur = (e: React.FocusEvent<HTMLInputElement>) => {
		// Mark as touched
		const { name } = e.target;
		setTouched((prev) => ({
			...prev,
			[name]: true,
		}));

		// Validate on blur
		setErrors((prev) => ({
			...prev,
			[name]: validateField(name, e.target.value),
		}));

		// Call the parent blur handler for enrichment logic
		handleBlur(e);
	};

	// Check if form has any errors - for disabling the Next button
	const hasErrors = () => {
		// Only check for errors if form submitted or fields have been touched
		if (
			!touched.form &&
			!touched.business_name &&
			!touched.tin &&
			!touched.zip_code
		) {
			return false;
		}

		// Validate all fields
		const hasBusinessNameError =
			validateField("business_name", formData.business_name) !== "";
		const hasTinError = validateField("tin", formData.tin) !== "";
		const hasZipCodeError = validateField("zip_code", formData.zip_code) !== "";

		return hasBusinessNameError || hasTinError || hasZipCodeError;
	};

	// Validation before proceeding to next step
	const validateAndProceed = () => {
		// Mark form as submitted
		setTouched({
			business_name: true,
			tin: true,
			zip_code: true,
			form: true,
		});

		// Validate all fields
		const newErrors = {
			business_name: validateField("business_name", formData.business_name),
			tin: validateField("tin", formData.tin),
			zip_code: validateField("zip_code", formData.zip_code),
		};

		setErrors(newErrors);

		// Check if there are any errors
		const hasValidationErrors = Object.values(newErrors).some(
			(error) => error !== ""
		);

		// Only proceed if all validations pass
		if (!hasValidationErrors) {
			handleNext();
		}
	};

	// Show error only if the field has been touched or form submitted
	const shouldShowError = (fieldName: keyof typeof touched) => {
		return (
			(touched[fieldName] || touched.form) &&
			errors[fieldName as keyof typeof errors] !== ""
		);
	};

	// Show enrichment data from the response
	const renderEnrichmentData = () => {
		if (!enriched || !formData.enrichment_data) {
			return null;
		}

		const data = formData.enrichment_data;

		return (
			<Card className="p-4 bg-green-50 border-green-200">
				<h3 className="font-medium text-green-800 flex items-center">
					<CheckCircle className="h-4 w-4 mr-2" />
					Business Verified
				</h3>
				<div className="mt-2 text-sm text-green-700">
					{data.business_start_date && (
						<p>Business Start Date: {data.business_start_date}</p>
					)}
					{data.sos_status && <p>Status: {data.sos_status}</p>}
					{data.industry_code && <p>Industry Code: {data.industry_code}</p>}
					{data.naics_code && <p>NAICS Code: {data.naics_code}</p>}
				</div>
			</Card>
		);
	};

	return (
		<div className="space-y-4">
			<h2 className="text-xl font-semibold mb-4">Business Information</h2>

			<div className="flex flex-col gap-2">
				<Label htmlFor="business_name" className="flex items-center">
					Business Name <span className="text-red-500 ml-1">*</span>
				</Label>
				<Input
					id="business_name"
					name="business_name"
					value={formData.business_name || ""}
					onChange={validateInput}
					onBlur={handleInputBlur} // Use our new blur handler
					required
					className={`bg-white ${
						shouldShowError("business_name")
							? "border-red-500"
							: "border-gray-300"
					}`}
				/>
				{shouldShowError("business_name") && (
					<p className="text-red-500 text-sm mt-1">{errors.business_name}</p>
				)}
			</div>

			<div className="flex flex-col gap-2">
				<Label htmlFor="tin" className="flex items-center">
					TIN (EIN or SSN) <span className="text-red-500 ml-1">*</span>
				</Label>
				<Input
					id="tin"
					name="tin"
					value={formData.tin || ""}
					onChange={validateInput}
					onBlur={handleInputBlur} // Use our new blur handler
					required
					className={`bg-white ${
						shouldShowError("tin") ? "border-red-500" : "border-gray-300"
					}`}
					placeholder="Enter 9-11 digits without hyphens"
				/>
				{shouldShowError("tin") && (
					<p className="text-red-500 text-sm mt-1">{errors.tin}</p>
				)}
			</div>

			<div className="flex flex-col gap-2">
				<Label htmlFor="zip_code" className="flex items-center">
					Zip Code <span className="text-red-500 ml-1">*</span>
				</Label>
				<Input
					id="zip_code"
					name="zip_code"
					value={formData.zip_code || ""}
					onChange={validateInput}
					onBlur={handleInputBlur}
					required
					className={`bg-white ${
						shouldShowError("zip_code") ? "border-red-500" : "border-gray-300"
					}`}
				/>
				{shouldShowError("zip_code") && (
					<p className="text-red-500 text-sm mt-1">{errors.zip_code}</p>
				)}
				<p className="text-xs text-gray-500">Enter your 5-digit ZIP code</p>
			</div>

			{enriching && (
				<div className="flex items-center space-x-2 text-blue-600">
					<Loader2 className="h-4 w-4 animate-spin" />
					<span>Verifying business information...</span>
				</div>
			)}

			{enriched && renderEnrichmentData()}

			<div className="flex justify-between mt-6">
				<Button type="button" onClick={handleBack}>
					Back
				</Button>
				<Button
					type="button"
					onClick={validateAndProceed}
					disabled={
						enriching ||
						hasErrors() ||
						!formData.business_name ||
						!formData.tin ||
						!formData.zip_code
					}
				>
					Next
				</Button>
			</div>
		</div>
	);
}
