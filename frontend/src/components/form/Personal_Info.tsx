import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";

interface FormData {
	first_name: string;
	last_name: string;
	email: string;
	phone: string;
}

interface Props {
	formData: FormData;
	handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
	handleNext: () => void;
}

export default function Personal_Info({
	formData,
	handleChange,
	handleNext,
}: Props) {
	const [touched, setTouched] = useState({
		first_name: false,
		last_name: false,
		email: false,
		phone: false,
		form: false,
	});

	const [errors, setErrors] = useState({
		first_name: "",
		last_name: "",
		email: "",
		phone: "",
	});

	function isValidEmail(email: string): boolean {
		if (!email) return false;
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		return emailRegex.test(email);
	}

	function isValidPhone(phone: string): boolean {
		if (!phone) return false;

		const phoneRegex = /^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$/;
		return phoneRegex.test(phone);
	}

	const safeTrim = (str: string | null | undefined): string => {
		return str ? str.trim() : "";
	};

	const validateField = (
		name: string,
		value: string | null | undefined
	): string => {
		const trimmedValue = safeTrim(value);

		switch (name) {
			case "first_name":
				return trimmedValue === "" ? "First name is required" : "";
			case "last_name":
				return trimmedValue === "" ? "Last name is required" : "";
			case "email":
				return trimmedValue === ""
					? "Email is required"
					: !isValidEmail(trimmedValue)
					? "Invalid email format"
					: "";
			case "phone":
				return trimmedValue === ""
					? "Phone number is required"
					: !isValidPhone(trimmedValue)
					? "Invalid phone format"
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

	const hasErrors = () => {
		if (
			!touched.form &&
			!touched.first_name &&
			!touched.last_name &&
			!touched.email &&
			!touched.phone
		) {
			return false;
		}

		const hasFirstNameError =
			validateField("first_name", formData.first_name) !== "";
		const hasLastNameError =
			validateField("last_name", formData.last_name) !== "";
		const hasEmailError = validateField("email", formData.email) !== "";
		const hasPhoneError = validateField("phone", formData.phone) !== "";

		return (
			hasFirstNameError || hasLastNameError || hasEmailError || hasPhoneError
		);
	};

	const validateAndProceed = () => {
		setTouched((prev) => ({
			...prev,
			first_name: true,
			last_name: true,
			email: true,
			phone: true,
			form: true,
		}));

		const newErrors = {
			first_name: validateField("first_name", formData.first_name),
			last_name: validateField("last_name", formData.last_name),
			email: validateField("email", formData.email),
			phone: validateField("phone", formData.phone),
		};

		setErrors(newErrors);

		const hasValidationErrors = Object.values(newErrors).some(
			(error) => error !== ""
		);

		if (!hasValidationErrors) {
			handleNext();
		}
	};

	const shouldShowError = (fieldName: keyof typeof touched) => {
		return (
			(touched[fieldName] || touched.form) &&
			errors[fieldName as keyof typeof errors] !== ""
		);
	};

	return (
		<div className="space-y-4">
			<h2 className="text-xl font-semibold mb-4">Personal Information</h2>

			<div className="grid grid-cols-2 gap-4">
				<div className="flex flex-col gap-2">
					<Label htmlFor="first_name" className="flex items-center">
						First Name <span className="text-red-500 ml-1">*</span>
					</Label>
					<Input
						id="first_name"
						name="first_name"
						value={formData.first_name || ""}
						onChange={validateInput}
						onBlur={() => setTouched((prev) => ({ ...prev, first_name: true }))}
						required
						className={`bg-white ${
							shouldShowError("first_name")
								? "border-red-500"
								: "border-gray-300"
						}`}
					/>
					{shouldShowError("first_name") && (
						<p className="text-red-500 text-sm mt-1">{errors.first_name}</p>
					)}
				</div>

				<div className="flex flex-col gap-2">
					<Label htmlFor="last_name" className="flex items-center">
						Last Name <span className="text-red-500 ml-1">*</span>
					</Label>
					<Input
						id="last_name"
						name="last_name"
						value={formData.last_name || ""}
						onChange={validateInput}
						onBlur={() => setTouched((prev) => ({ ...prev, last_name: true }))}
						required
						className={`bg-white ${
							shouldShowError("last_name")
								? "border-red-500"
								: "border-gray-300"
						}`}
					/>
					{shouldShowError("last_name") && (
						<p className="text-red-500 text-sm mt-1">{errors.last_name}</p>
					)}
				</div>
			</div>

			<div className="flex flex-col gap-2">
				<Label htmlFor="email" className="flex items-center">
					Email <span className="text-red-500 ml-1">*</span>
				</Label>
				<Input
					id="email"
					name="email"
					type="email"
					value={formData.email || ""}
					onChange={validateInput}
					onBlur={() => setTouched((prev) => ({ ...prev, email: true }))}
					required
					className={`bg-white ${
						shouldShowError("email") ? "border-red-500" : "border-gray-300"
					}`}
				/>
				{shouldShowError("email") && (
					<p className="text-red-500 text-sm mt-1">{errors.email}</p>
				)}
			</div>

			<div className="flex flex-col gap-2">
				<Label htmlFor="phone" className="flex items-center">
					Phone <span className="text-red-500 ml-1">*</span>
				</Label>
				<Input
					id="phone"
					name="phone"
					value={formData.phone || ""}
					onChange={validateInput}
					onBlur={() => setTouched((prev) => ({ ...prev, phone: true }))}
					required
					className={`bg-white ${
						shouldShowError("phone") ? "border-red-500" : "border-gray-300"
					}`}
					placeholder="(123) 456-7890"
				/>
				{shouldShowError("phone") && (
					<p className="text-red-500 text-sm mt-1">{errors.phone}</p>
				)}
			</div>

			<div className="flex justify-end mt-6">
				<Button
					type="button"
					onClick={validateAndProceed}
					disabled={hasErrors()}
				>
					Next
				</Button>
			</div>
		</div>
	);
}
