import styles from "../styles/components/toast.module.css";

export default function Toast({ message, onClose, type = "error" }) {
  if (!message) return null;

  const title = type === "success" ? "Success" : "Oops!";
  const toastClass =
    type === "success" ? styles.toastSuccess : styles.toastError;

  return (
    <div className={`${styles.toast} ${toastClass}`} role="alert">
      <div className={styles.toastContent}>
        <strong>{title}</strong>
        <span className={styles.toastMessage}>{message}</span>
      </div>
      <button onClick={onClose} className={styles.toastClose}>
        Dismiss
      </button>
    </div>
  );
}
