export type FormData = {
	first_name: string;
	last_name: string;
	email: string;
	phone: string;

	business_name: string;
	tin: string;
	zip_code: string;

	monthly_revenue: string;
	years_in_business: string;

	business_start_date?: string;
	sos_status?: string;
	industry_code?: string;
	naics_code?: string;
	enrichment_data?: any;

	completed_steps?: {
		step1: boolean;
		step2: boolean;
		step3: boolean;
	};
	current_step?: number;
};
