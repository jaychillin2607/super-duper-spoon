import { Card } from "@/components/ui/card";
import { CheckCircle } from "lucide-react";

export default function SuccessMessage() {
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
