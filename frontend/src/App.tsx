import { useEffect } from "react";
import { generateSessionId } from "./api/session";
import "./App.css";
import MerchantForm from "./components/Merchant_Form";
function App() {
  useEffect(() => {
    // Ensure we have a session ID
    if (!localStorage.getItem("sessionId")) {
      localStorage.setItem("sessionId", generateSessionId());
    }
  }, []);

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-gray-900">
          Merchant Application
        </h1>
        <p className="mt-2 text-gray-600">
          Complete the form below to apply for funding
        </p>
      </div>
      <MerchantForm />
    </div>
  );
}

export default App;
