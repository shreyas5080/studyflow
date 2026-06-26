import { Link } from "react-router-dom";
import styles from "../styles/components/student_nav.module.css";

export default function StudentNav({ username = "Student" }) {
  const userId = localStorage.getItem("id");

  return (
    <nav className={styles.navbar}>
      <h1 className={styles["navbar-title"]}>Welcome Back, {username}!</h1>
      <ul className={styles["nav-list"]}>
        <li>
          <Link to={userId ? `/student/${userId}/time-table` : "/login"}>
            Study Table
          </Link>
        </li>
        <li>
          <Link to={userId ? `/student/${userId}/subjects` : "/login"}>
            Add Exam
          </Link>
        </li>
        <li>
          <Link to="/login">Help</Link>
        </li>
        <li>
          <Link to="/login">Logout</Link>
        </li>
      </ul>
    </nav>
  );
}
