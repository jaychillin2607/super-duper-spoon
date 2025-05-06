import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { FormData } from "@/types/formType";
import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

interface Props {
	formData: FormData;
	handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
	handleBack: () => void;
	loading: boolean;
}

export default function Financial_Info({
	formData,
	handleChange,
	handleBack,
	loading,
}: Props) {
	// Initialize errors state
	const [errors, setErrors] = useState({
		monthly_revenue: formData.monthly_revenue
			? ""
			: "Monthly revenue is required",
		years_in_business: formData.years_in_business
			? Number(formData.years_in_business) < 0
				? "Years in business cannot be negative"
				: ""
			: "Years in business is required",
	});

	// Use useEffect to update validation on formData changes
	useEffect(() => {
		setErrors({
			monthly_revenue: !formData.monthly_revenue
				? "Monthly revenue is required"
				: "",
			years_in_business: !formData.years_in_business
				? "Years in business is required"
				: Number(formData.years_in_business) < 0
				? "Years in business cannot be negative"
				: "",
		});
	}, [formData]);

	// Custom input handler for validation
	const validateInput = (e: React.ChangeEvent<HTMLInputElement>) => {
		const { name, value } = e.target;
		let newErrors = { ...errors };

		// Validate based on field name
		switch (name) {
			case "monthly_revenue":
				newErrors.monthly_revenue = !value ? "Monthly revenue is required" : "";
				break;
			case "years_in_business":
				newErrors.years_in_business = !value
					? "Years in business is required"
					: Number(value) < 0
					? "Years in business cannot be negative"
					: "";
				break;
		}

		setErrors(newErrors);

		// Process the change through the parent handler
		handleChange(e);
	};

	// Check if form has any errors
	const hasErrors = () => {
		return (
			errors.monthly_revenue !== "" ||
			errors.years_in_business !== "" ||
			!formData.monthly_revenue ||
			!formData.years_in_business ||
			Number(formData.years_in_business) < 0
		);
	};

	return (
		<div className="space-y-4">
			<h2 className="text-xl font-semibold mb-4">Financial Information</h2>

			<div className="flex flex-col gap-2">
				<Label htmlFor="monthly_revenue" className="flex items-center">
					Monthly Revenue ($) <span className="text-red-500 ml-1">*</span>
				</Label>
				<Input
					id="monthly_revenue"
					name="monthly_revenue"
					type="number"
					min="0"
					step="1"
					value={formData.monthly_revenue}
					onChange={validateInput}
					required
					className={errors.monthly_revenue ? "border-red-500" : ""}
				/>
				{errors.monthly_revenue && (
					<p className="text-red-500 text-sm mt-1">{errors.monthly_revenue}</p>
				)}
			</div>

			<div className="flex flex-col gap-2">
				<Label htmlFor="years_in_business" className="flex items-center">
					Years in Business <span className="text-red-500 ml-1">*</span>
				</Label>
				<Input
					id="years_in_business"
					name="years_in_business"
					type="number"
					min="0"
					step="1"
					value={formData.years_in_business}
					onChange={validateInput}
					required
					className={errors.years_in_business ? "border-red-500" : ""}
				/>
				{errors.years_in_business && (
					<p className="text-red-500 text-sm mt-1">
						{errors.years_in_business}
					</p>
				)}
			</div>

			<div className="flex justify-between mt-6">
				<Button type="button" onClick={handleBack}>
					Back
				</Button>
				<Button type="submit" disabled={loading || hasErrors()}>
					{loading ? (
						<>
							<Loader2 className="mr-2 h-4 w-4 animate-spin" />
							Submitting...
						</>
					) : (
						"Submit Application"
					)}
				</Button>
			</div>
		</div>
	);
}
