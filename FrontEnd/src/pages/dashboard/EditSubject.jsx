import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Toast from "../../components/Toast";
import { fetchWithAuth } from "../../api";
import style from "../../styles/pages/editSubject.module.css";

export default function EditSubject() {
  const { id: userId, subjectId } = useParams();
  const navigate = useNavigate();
  const [subject, setSubject] = useState({
    subject_name: "",
    exam_date: "",
    difficulty: "",
  });
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchSubject = async () => {
      const token = localStorage.getItem("token");

      if (!userId || !subjectId || !token) {
        setError("Unable to load the subject. Please sign in and try again.");
        return;
      }

      const response = await fetchWithAuth(
        `http://127.0.0.1:8000/student/${userId}/subjects/${subjectId}`,
      );

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        setError(data?.detail || "Unable to load the subject.");
        return;
      }

      setSubject(
        data.subject || {
          subject_name: "",
          exam_date: "",
          difficulty: "",
        },
      );
    };

    fetchSubject();
  }, [userId, subjectId]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const token = localStorage.getItem("token");

    if (!token) {
      setError("You must be logged in to update the subject.");
      return;
    }

    const response = await fetchWithAuth(
      `http://127.0.0.1:8000/student/${userId}/subjects/${subjectId}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(subject),
      },
    );

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      setError(data?.detail || "Failed to update the subject.");
      return;
    }

    navigate(`/student/${userId}/subjects`);
  };

  return (
    <div className={style["editSubject"]}>
      {error && <Toast message={error} onClose={() => setError("")} />}
      <form onSubmit={handleSubmit}>
        <h1>Edit Subject</h1>
        <input
          type="text"
          value={subject.subject_name}
          onChange={(e) =>
            setSubject({
              ...subject,
              subject_name: e.target.value,
            })
          }
        />
        <input
          type="date"
          value={subject.exam_date}
          onChange={(e) =>
            setSubject({
              ...subject,
              exam_date: e.target.value,
            })
          }
        />
        <select
          value={subject.difficulty}
          onChange={(e) =>
            setSubject({
              ...subject,
              difficulty: e.target.value,
            })
          }
        >
          <option value="">Select difficulty</option>
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
        <button type="submit">Save</button>
      </form>
    </div>
  );
}
