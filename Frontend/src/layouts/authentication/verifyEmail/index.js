import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const VerifyEmailPage = () => {
  const [isVerified, setIsVerified] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const url = window.location.href;
    const token = url.split("/").pop();
console.log("token: ", token)
    if (token) {
      axios
        .get(`http://127.0.0.1:8000/accounts/verify-email/${token}`)
        .then((response) => {
          localStorage.setItem("auth_token", token); // Save token for further use
          setIsVerified(true);
          navigate("/dashboard"); // Redirect to dashboard or login page
        })
        .catch((error) => {
          setError("Invalid or expired token.");
        });
    console.log("token: ", token)

    }
  }, [navigate]);

  return (
    <div>
      {isVerified ? (
        <p>Your email has been successfully verified!</p>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <p>Verifying your email...</p>
      )}
    </div>
  );
};

export default VerifyEmailPage;
