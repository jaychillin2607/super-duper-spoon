import type React from "react";

import { enrichBusinessData, submitLeadData } from "@/api/api";
import { getSessionData, saveSessionData } from "@/api/session";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AlertCircle, CheckCircle, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import StepIndicator from "./Step_Indicator";

type FormData = {
  // Step 1
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  // Step 2
  business_name: string;
  tin: string;
  zip_code: string;
  // Step 3
  monthly_revenue: string;
  years_in_business: string;
  // Enrichment data
  business_start_date?: string;
  sos_status?: string;
};

const initialFormData: FormData = {
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
  business_name: "",
  tin: "",
  zip_code: "",
  monthly_revenue: "",
  years_in_business: "",
};

export default function MerchantForm() {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [loading, setLoading] = useState(false);
  const [enriching, setEnriching] = useState(false);
  const [enriched, setEnriched] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Load session data on mount
  useEffect(() => {
    const loadSession = async () => {
      const sessionId = localStorage.getItem("sessionId");
      if (sessionId) {
        const data = await getSessionData(sessionId);
        if (data) {
          setFormData(data);
          // Determine which step to show based on data
          if (data.years_in_business) {
            setCurrentStep(3);
          } else if (data.business_name) {
            setCurrentStep(2);
          }
          if (data.business_start_date) {
            setEnriched(true);
          }
        }
      }
    };

    loadSession();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const saveSession = async () => {
    const sessionId = localStorage.getItem("sessionId");
    if (sessionId) {
      await saveSessionData(sessionId, formData);
    }
  };

  const handleNext = async () => {
    // Validate current step
    if (currentStep === 1) {
      if (
        !formData.first_name ||
        !formData.last_name ||
        !formData.email ||
        !formData.phone
      ) {
        setError("Please fill out all fields");
        return;
      }
    } else if (currentStep === 2) {
      if (!formData.business_name || !formData.tin || !formData.zip_code) {
        setError("Please fill out all fields");
        return;
      }

      // If we haven't enriched yet, do it now
      if (!enriched && !enriching) {
        await enrichBusinessInfo();
      }
    }

    setError(null);
    await saveSession();
    setCurrentStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setCurrentStep((prev) => prev - 1);
  };

  const enrichBusinessInfo = async () => {
    if (!formData.business_name || !formData.zip_code) return;

    setEnriching(true);
    try {
      const data = await enrichBusinessData(
        formData.business_name,
        formData.zip_code
      );
      setFormData((prev) => ({
        ...prev,
        business_start_date: data.business_start_date,
        sos_status: data.sos_status,
      }));
      setEnriched(true);
      await saveSession();
    } catch (err) {
      console.error("Error enriching business data:", err);
      setError("Failed to enrich business data. Please try again.");
    } finally {
      setEnriching(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.monthly_revenue || !formData.years_in_business) {
      setError("Please fill out all fields");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Convert string values to numbers for the API
      const submitData = {
        ...formData,
        monthly_revenue: Number.parseFloat(formData.monthly_revenue),
        years_in_business: Number.parseFloat(formData.years_in_business),
      };

      await submitLeadData(submitData);
      setSuccess(true);
      // Clear session after successful submission
      localStorage.removeItem("sessionId");
    } catch (err) {
      console.error("Error submitting lead data:", err);
      setError("Failed to submit application. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Trigger enrichment when business name and zip code are both filled
  useEffect(() => {
    if (
      formData.business_name &&
      formData.zip_code &&
      !enriched &&
      !enriching &&
      currentStep === 2
    ) {
      enrichBusinessInfo();
    }
  }, [formData.business_name, formData.zip_code, currentStep]);

  if (success) {
    return (
      <Card className="text-center py-8">
        <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Application Submitted!
        </h2>
        <p className="text-gray-600">
          Thank you for your application. We'll be in touch soon.
        </p>
      </Card>
    );
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
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4">Personal Information</h2>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="first_name">First Name</Label>
                <Input
                  id="first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div>
                <Label htmlFor="last_name">Last Name</Label>
                <Input
                  id="last_name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            <div>
              <Label htmlFor="phone">Phone</Label>
              <Input
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                required
              />
            </div>

            <div className="flex justify-end mt-6">
              <Button type="button" onClick={handleNext}>
                Next
              </Button>
            </div>
          </div>
        )}

        {currentStep === 2 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4">Business Information</h2>

            <div>
              <Label htmlFor="business_name">Business Name</Label>
              <Input
                id="business_name"
                name="business_name"
                value={formData.business_name}
                onChange={handleChange}
                required
              />
            </div>

            <div>
              <Label htmlFor="tin">TIN (EIN or SSN)</Label>
              <Input
                id="tin"
                name="tin"
                value={formData.tin}
                onChange={handleChange}
                required
              />
            </div>

            <div>
              <Label htmlFor="zip_code">Zip Code</Label>
              <Input
                id="zip_code"
                name="zip_code"
                value={formData.zip_code}
                onChange={handleChange}
                required
              />
            </div>

            {enriching && (
              <div className="flex items-center space-x-2 text-blue-600">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Verifying business information...</span>
              </div>
            )}

            {enriched && (
              <Card className="p-4 bg-green-50 border-green-200">
                <h3 className="font-medium text-green-800 flex items-center">
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Business Verified
                </h3>
                <div className="mt-2 text-sm text-green-700">
                  <p>Business Start Date: {formData.business_start_date}</p>
                  <p>SOS Status: {formData.sos_status}</p>
                </div>
              </Card>
            )}

            <div className="flex justify-between mt-6">
              <Button type="button" onClick={handleBack}>
                Back
              </Button>
              <Button type="button" onClick={handleNext} disabled={enriching}>
                Next
              </Button>
            </div>
          </div>
        )}

        {currentStep === 3 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4">
              Financial Information
            </h2>

            <div>
              <Label htmlFor="monthly_revenue">Monthly Revenue ($)</Label>
              <Input
                id="monthly_revenue"
                name="monthly_revenue"
                type="number"
                value={formData.monthly_revenue}
                onChange={handleChange}
                required
              />
            </div>

            <div>
              <Label htmlFor="years_in_business">Years in Business</Label>
              <Input
                id="years_in_business"
                name="years_in_business"
                type="number"
                step="0.1"
                value={formData.years_in_business}
                onChange={handleChange}
                required
              />
            </div>

            <div className="flex justify-between mt-6">
              <Button type="button" variant="outline" onClick={handleBack}>
                Back
              </Button>
              <Button type="submit" disabled={loading}>
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
        )}
      </form>
    </Card>
  );
}
