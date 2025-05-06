// types/formTypes.ts

export type FormData = {
	// Step 1: Personal Information
	first_name: string;
	last_name: string;
	email: string;
	phone: string;

	// Step 2: Business Information
	business_name: string;
	tin: string;
	zip_code: string;

	// Step 3: Financial Information
	monthly_revenue: string;
	years_in_business: string;

	// Enrichment data
	business_start_date?: string;
	sos_status?: string;
	industry_code?: string;
	naics_code?: string;
	enrichment_data?: any;

	// Form state tracking
	completed_steps?: {
		step1: boolean;
		step2: boolean;
		step3: boolean;
	};
	current_step?: number;
};
