import { useEffect, useState } from "react";
import "./App.css";
import MerchantForm from "./components/Merchant_Form";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Loader2 } from "lucide-react";
import { checkBackendHealth } from "./api/api";

function App() {
	const [loading, setLoading] = useState(true);
	const [backendError, setBackendError] = useState(false);

	// Check backend connectivity on load
	useEffect(() => {
		const verifyBackend = async () => {
			try {
				const isHealthy = await checkBackendHealth();
				setBackendError(!isHealthy);
			} catch (error) {
				console.error("Backend connectivity error:", error);
				setBackendError(true);
			} finally {
				setLoading(false);
			}
		};

		verifyBackend();
	}, []);

	if (loading) {
		return (
			<div className="flex flex-col items-center justify-center min-h-screen">
				<Loader2 className="h-12 w-12 animate-spin text-blue-500 mb-4" />
				<p className="text-gray-600">Loading application...</p>
			</div>
		);
	}

	return (
		<div className="max-w-3xl mx-auto p-4">
			<div className="text-center mb-10">
				<h1 className="text-3xl font-bold text-gray-900">
					Merchant Application
				</h1>
				<p className="mt-2 text-gray-600">
					Complete the form below to apply for funding
				</p>
			</div>

			{backendError && (
				<Alert variant="destructive" className="mb-6">
					<AlertCircle className="h-4 w-4" />
					<AlertDescription>
						Unable to connect to the application server. Please try again later
						or contact support.
					</AlertDescription>
				</Alert>
			)}

			{!backendError && <MerchantForm />}
		</div>
	);
}

export default App;
