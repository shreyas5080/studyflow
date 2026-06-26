import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import StudentNav from "../../components/student_nav";
import Sidebar from "../../components/Sidebar";
import Toast from "../../components/Toast";
import { fetchWithAuth } from "../../api";
import style from "../../styles/pages/studentDash.module.css";

export default function Student() {
  const { id: routeId } = useParams();
  const id = localStorage.getItem("id");
  const name = localStorage.getItem("username");
  const [student, setStudent] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!id || !token) {
      navigate("/login");
      return;
    }

    if (routeId !== id) {
      navigate(`/student/${id}`);
      return;
    }

    const fetchStudent = async () => {
      try {
        const response = await fetchWithAuth(
          `http://127.0.0.1:8000/student/${id}`,
        );

        if (!response.ok) {
          if (response.status === 401 || response.status === 403) {
            navigate("/login");
            return;
          }
          const data = await response.json().catch(() => null);
          setError(
            data?.detail ||
              "Unable to load your dashboard. Please refresh or log in again.",
          );
          return;
        }

        const data = await response.json();
        setStudent(data);
      } catch (err) {
        console.error(err);
        setError(
          "Unable to load your dashboard. Please refresh or try again later.",
        );
      }
    };

    fetchStudent();
  }, [id, routeId, navigate]);

  return (
    <>
      <Sidebar />
      <div className={style["studentDash"]}>
        <StudentNav username={student?.username || name} />
        <h1>Student Dashboard</h1>
        {error && <Toast message={error} onClose={() => setError("")} />}
        <p>Student ID: {student?.id || id}</p>
        <p>Hello, {student?.username || name}!</p>
        <div className={style["welcome"]}>
          <h1 className={style["cardTitle"]}>Student Progress</h1>
          <div className={style["cards"]}>
            <div className={style["card"]}>
              <h2>progess</h2>
              <p>45% complete</p>
            </div>
            <div className={style["card"]}>
              <h2>Next Exam</h2>
              <p>Mathematics - Midterm Exam</p>
            </div>
            <div className={style["card"]}>
              <h2>Total exam left</h2>
              <p>2</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
