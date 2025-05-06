import { enrichBusinessData, submitLeadFromSession } from "@/api/api";
import { initializeSession, updateSession } from "@/api/session";
import type { FormData } from "@/types/formType";
import { useEffect, useRef, useState } from "react";

export function useMerchantForm() {
	const [sessionId, setSessionId] = useState<string | null>(null);
	const [formData, setFormData] = useState<FormData>({
		first_name: "",
		last_name: "",
		email: "",
		phone: "",
		business_name: "",
		tin: "",
		zip_code: "",
		monthly_revenue: "",
		years_in_business: "",
	});

	const [currentStep, setCurrentStep] = useState(1);
	const [loading, setLoading] = useState(false);
	const [enriching, setEnriching] = useState(false);
	const [enriched, setEnriched] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [success, setSuccess] = useState(false);

	const isInitialLoad = useRef(true);

	const zipCodeBlurred = useRef(false);
	const businessNameBlurred = useRef(false);

	useEffect(() => {
		const loadSession = async () => {
			try {
				setLoading(true);
				const { sessionId, sessionData } = await initializeSession();

				setSessionId(sessionId);

				if (sessionData && sessionData.form_data) {
					const formData = sessionData.form_data;
					setFormData(formData);

					const completedSteps = formData.completed_steps || {};

					if (completedSteps.step3) {
						setCurrentStep(3);
					} else if (completedSteps.step2) {
						setCurrentStep(2);
					} else if (completedSteps.step1) {
						setCurrentStep(1);
					}

					if (formData.enrichment_data) {
						setEnriched(true);
					}
				}
			} catch (err) {
				console.error("Error initializing session:", err);
				setError("Failed to initialize session. Please refresh the page.");
			} finally {
				setLoading(false);
				isInitialLoad.current = false;
			}
		};

		loadSession();
	}, []);

	const saveSession = async (
		updatedData: Partial<FormData> = {},
		step: number = currentStep
	) => {
		if (!sessionId) return;

		try {
			const newFormData = { ...formData, ...updatedData };

			const completedSteps = newFormData.completed_steps || {
				step1: false,
				step2: false,
				step3: false,
			};

			if (
				step === 1 &&
				newFormData.first_name &&
				newFormData.last_name &&
				newFormData.email &&
				newFormData.phone
			) {
				completedSteps.step1 = true;
			} else if (
				step === 2 &&
				newFormData.business_name &&
				newFormData.tin &&
				newFormData.zip_code
			) {
				completedSteps.step2 = true;
			} else if (
				step === 3 &&
				newFormData.monthly_revenue &&
				newFormData.years_in_business
			) {
				completedSteps.step3 = true;
			}

			const dataToSave = {
				...newFormData,
				completed_steps: completedSteps,
				current_step: step,
			};

			await updateSession(sessionId, dataToSave);

			setFormData(dataToSave);
		} catch (err) {
			console.error("Error saving session:", err);
		}
	};

	const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		const { name, value } = e.target;

		if (error) setError(null);

		if (name === "zip_code") {
			setEnriched(false);
		}

		setFormData((prev) => ({ ...prev, [name]: value }));
	};

	const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
		const { name } = e.target;

		if (name === "zip_code") {
			zipCodeBlurred.current = true;
		} else if (name === "business_name") {
			businessNameBlurred.current = true;
		}

		if (
			currentStep === 2 &&
			formData.business_name &&
			formData.zip_code &&
			formData.zip_code.length >= 5 &&
			!enriched &&
			!enriching
		) {
			if (
				(name === "zip_code" && businessNameBlurred.current) ||
				(name === "business_name" && zipCodeBlurred.current)
			) {
				enrichBusinessInfo();
			}
		}
	};

	const handleNext = async () => {
		if (currentStep === 1) {
			if (
				!formData.first_name ||
				!formData.last_name ||
				!formData.email ||
				!formData.phone
			) {
				setError("Please fill out all required fields");
				return;
			}
		} else if (currentStep === 2) {
			if (!formData.business_name || !formData.tin || !formData.zip_code) {
				setError("Please fill out all required fields");
				return;
			}

			if (!enriched && !enriching) {
				await enrichBusinessInfo();
			}
		}

		await saveSession(formData, currentStep);
		setCurrentStep((prev) => prev + 1);
	};

	const handleBack = () => {
		setCurrentStep((prev) => prev - 1);
	};

	const enrichBusinessInfo = async () => {
		if (
			!sessionId ||
			!formData.business_name ||
			!formData.zip_code ||
			formData.zip_code.length < 5
		)
			return;

		setEnriching(true);
		setError(null);

		try {
			const enrichmentData = await enrichBusinessData(
				formData.business_name,
				formData.zip_code,
				sessionId
			);

			const updatedData = {
				...formData,
				business_start_date: enrichmentData.business_start_date,
				sos_status: enrichmentData.sos_status,
				enrichment_data: enrichmentData,
			};

			setFormData(updatedData);
			setEnriched(true);

			await saveSession(updatedData);
		} catch (err) {
			console.error("Error enriching business data:", err);
			setError(
				"Failed to verify business information. You may continue with your application."
			);
		} finally {
			setEnriching(false);
		}
	};

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();

		if (!sessionId) {
			setError("Session not found. Please refresh the page.");
			return;
		}

		if (!formData.monthly_revenue || !formData.years_in_business) {
			setError("Please fill out all required fields");
			return;
		}

		setLoading(true);
		setError(null);

		try {
			await saveSession(
				{
					...formData,
					completed_steps: {
						step1: true,
						step2: true,
						step3: true,
					},
				},
				3
			);

			await submitLeadFromSession(sessionId);

			localStorage.removeItem("sessionId");

			setSuccess(true);
		} catch (err: any) {
			console.error("Error submitting application:", err);
			setError(
				err.response?.data?.error ||
					"Failed to submit application. Please try again."
			);
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		if (currentStep !== 2) return;

		if (enriching) return;

		const shouldEnrich =
			sessionId &&
			formData.business_name &&
			formData.business_name.trim().length > 1 &&
			formData.zip_code &&
			formData.zip_code.length === 5 &&
			!enriched;

		if (shouldEnrich) {
			enrichBusinessInfo();
		}
	}, [
		formData.zip_code,
		formData.business_name,
		currentStep,
		sessionId,
		enriched,
		enriching,
	]);

	return {
		formData,
		handleChange,
		handleBlur,
		currentStep,
		handleNext,
		handleBack,
		handleSubmit,
		loading,
		enriching,
		enriched,
		error,
		success,
	};
}
