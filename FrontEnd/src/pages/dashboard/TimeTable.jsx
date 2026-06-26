import { fetchWithAuth } from "../../api";
import { useState, useEffect } from "react";
import Toast from "../../components/Toast";
import Sidebar from "../../components/Sidebar";
import StudentNav from "../../components/student_nav";
import styles from "../../styles/pages/timetable.module.css";

export default function TimeTable() {
  const [error, setError] = useState("");
  const [timetable, setTimetable] = useState([]);

  const userId = localStorage.getItem("id");

  useEffect(() => {
    const timeTable = async () => {
      try {
        const response = await fetchWithAuth(
          `http://127.0.0.1:8000/student/${userId}/time-table`,
          {
            method: "GET",
          },
        );

        if (!response.ok) {
          setError("Could not load timetable");
          return;
        }
        const data = await response.json();
        const parsed = JSON.parse(data.timetable);
        setTimetable(parsed.timetable);
      } catch (error) {
        console.error(error);
        setError("Could not load timetable");
      }
    };

    timeTable();
  }, [userId]);

  return (
    <>
      <Sidebar />
      <div className={styles["timeTable"]}>
        <StudentNav />
        {error && <Toast message={error} onClose={() => setError("")} />}

        <h1>Exam Timetable</h1>

        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Subject</th>
              <th>Task</th>
              <th>Hours</th>
            </tr>
          </thead>
          <tbody>
            {timetable.map((item, index) => (
              <tr key={index}>
                <td>{item.date}</td>
                <td>{item.subject}</td>
                <td>{item.task}</td>
                <td>{item.hours}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
