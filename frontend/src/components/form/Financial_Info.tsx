import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { FormData } from "@/types/formType";
import { Loader2 } from "lucide-react";
import { useState } from "react";

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
	const [touched, setTouched] = useState({
		monthly_revenue: false,
		years_in_business: false,
		form: false,
	});

	const [errors, setErrors] = useState({
		monthly_revenue: "",
		years_in_business: "",
	});

	const validateField = (name: string, value: string): string => {
		switch (name) {
			case "monthly_revenue":
				return !value
					? "Monthly revenue is required"
					: Number(value) <= 0
					? "Monthly revenue must be greater than zero"
					: "";
			case "years_in_business":
				return !value
					? "Years in business is required"
					: Number(value) < 0
					? "Years in business cannot be negative"
					: "";
			default:
				return "";
		}
	};

	const validateInput = (e: React.ChangeEvent<HTMLInputElement>) => {
		const { name, value } = e.target;

		setTouched((prev) => ({
			...prev,
			[name]: true,
		}));

		setErrors((prev) => ({
			...prev,
			[name]: validateField(name, value),
		}));

		handleChange(e);
	};

	const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
		const { name } = e.target;

		setTouched((prev) => ({
			...prev,
			[name]: true,
		}));

		setErrors((prev) => ({
			...prev,
			[name]: validateField(name, e.target.value),
		}));
	};

	const hasErrors = () => {
		const hasMonthlyRevenueError =
			validateField("monthly_revenue", formData.monthly_revenue as string) !==
			"";
		const hasYearsInBusinessError =
			validateField(
				"years_in_business",
				formData.years_in_business as string
			) !== "";

		return hasMonthlyRevenueError || hasYearsInBusinessError;
	};

	const shouldShowError = (fieldName: keyof typeof touched) => {
		return (
			(touched[fieldName] || touched.form) &&
			errors[fieldName as keyof typeof errors] !== ""
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
					value={formData.monthly_revenue || ""}
					onChange={validateInput}
					onBlur={handleBlur}
					required
					className={`bg-white ${
						shouldShowError("monthly_revenue")
							? "border-red-500"
							: "border-gray-300"
					}`}
				/>
				{shouldShowError("monthly_revenue") && (
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
					step="0.1"
					value={formData.years_in_business || ""}
					onChange={validateInput}
					onBlur={handleBlur}
					required
					className={`bg-white ${
						shouldShowError("years_in_business")
							? "border-red-500"
							: "border-gray-300"
					}`}
				/>
				{shouldShowError("years_in_business") && (
					<p className="text-red-500 text-sm mt-1">
						{errors.years_in_business}
					</p>
				)}
			</div>

			<div className="flex justify-between mt-6">
				<Button type="button" onClick={handleBack}>
					Back
				</Button>
				<Button
					type="submit"
					disabled={
						loading ||
						hasErrors() ||
						!formData.monthly_revenue ||
						!formData.years_in_business
					}
				>
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
