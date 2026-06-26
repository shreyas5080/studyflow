import { useState } from "react";
import styles from "../styles/pages/register.module.css";
import Toast from "../components/Toast";

function Register() {
  const [user, setUser] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  const handleChange = (e) => {
    setUser({ ...user, [e.target.name]: e.target.value });
  };

  const submit = async () => {
    setError("");
    setSuccessMessage("");

    const response = await fetch("http://127.0.0.1:8000/request-otp", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: user.email }),
    });

    if (response.ok) {
      const data = await response.json(); // Helping for debug
      console.log(data.message);
      setOtpSent(true);
    } else {
      const data = await response.json().catch(() => null);
      setError(
        data?.detail ||
          "We couldn't send the OTP. Please confirm your email address and try again.",
      );
    }
  };

  const verifyOtp = async () => {
    setError("");
    setSuccessMessage("");
    setIsVerifying(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: user.email, otp }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        setError(
          data?.detail ||
            "The OTP you entered is incorrect. Please check your email and try again.",
        );
        return;
      }

      const createResponse = await fetch("http://127.0.0.1:8000/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(user),
      });

      if (createResponse.ok) {
        setSuccessMessage("Registration complete. You may now log in.");
        setOtpSent(false);
        setUser({ username: "", email: "", password: "" });
        setOtp("");
      } else {
        const data = await createResponse.json().catch(() => null);
        setError(
          data?.detail ||
            "Registration could not be completed. Please review your details and try again.",
        );
      }
    } catch (err) {
      console.log(err);
      setError("Network error detected. Please wait a moment and try again.");
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <>
      <div className={styles["div-btn"]}>
        <div className={styles["form-btn"]}>
          <p>Register</p>
          {!otpSent ? (
            <>
              <div className={styles["page-set"]}>
                <input
                  type="text"
                  name="username"
                  value={user.username}
                  placeholder=" "
                  onChange={handleChange}
                  required
                />
                <label>Username</label>
              </div>
              <div className={styles["page-set"]}>
                <input
                  type="email"
                  name="email"
                  value={user.email}
                  placeholder=" "
                  onChange={handleChange}
                  required
                />
                <label>Email</label>
              </div>
              <div className={styles["page-set"]}>
                <input
                  type="password"
                  name="password"
                  value={user.password}
                  placeholder=" "
                  onChange={handleChange}
                  required
                />
                <label>Password</label>
              </div>
              <button onClick={submit}>Submit</button>
            </>
          ) : (
            <>
              <div className={styles["page-set"]}>
                <input
                  type="text"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  placeholder=" "
                />
                <label>Enter OTP</label>
              </div>
              <button onClick={verifyOtp} disabled={isVerifying}>
                {isVerifying ? "Verifying..." : "Verify OTP"}
              </button>
            </>
          )}
        </div>
      </div>
      {error && <Toast message={error} onClose={() => setError("")} />}
      {successMessage && (
        <Toast message={successMessage} onClose={() => setSuccessMessage("")} />
      )}
    </>
  );
}

export default Register;
