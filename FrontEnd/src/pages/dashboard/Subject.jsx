import { useEffect, useState } from "react";
import StudentNav from "../../components/student_nav";
import Sidebar from "../../components/Sidebar";
import Toast from "../../components/Toast";
import styles from "../../styles/pages/subject.module.css";
import { useNavigate } from "react-router-dom";
import { fetchWithAuth } from "../../api";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

export default function Subject() {
  let [subject, setSubjectName] = useState({
    subject_name: "",
    exam_date: "",
    difficulty: "",
  });
  let [subjects, setSubjects] = useState([]);
  let [error, setError] = useState("");

  const navigate = useNavigate();
  let userId = localStorage.getItem("id");
  let username = localStorage.getItem("username");

  useEffect(() => {
    const fetchSubjects = async () => {
      try {
        const response = await fetchWithAuth(
          `http://127.0.0.1:8000/student/${userId}/subjects`,
        );

        if (!response.ok) {
          if (response.status === 401 || response.status === 403) {
            setError(
              "You are not authorized to view subjects. Please sign in again.",
            );
            return;
          }
          setError(
            "Unable to load your subjects right now. Please refresh the page.",
          );
          return;
        }

        const data = await response.json();
        setSubjects(data.subjects || []);
      } catch (err) {
        console.error("Error fetching subjects:", err);
        setError(
          "Unable to load your subjects. Please refresh or try again later.",
        );
      }
    };

    if (userId) {
      fetchSubjects();
    }
  }, [userId]);

  const onSubmit = async (e) => {
    e.preventDefault();
    const today = new Date().toISOString().split("T")[0];

    if (subject.exam_date < today) {
      setError("Exam date cannot be in the past.");
      return;
    }
    try {
      const response = await fetchWithAuth(
        `http://127.0.0.1:8000/student/${userId}/subjects`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(subject),
        },
      );

      const data = await response.json();
      if (!response.ok) {
        setError("You can't add subject.");
        return;
      }
      setSubjectName({ subject_name: "", exam_date: "", difficulty: "" });
      setSubjects([...subjects, data.subject]);
    } catch (error) {
      console.error("Error adding subject:", error);
      setError(
        "Could not add the subject. Please check the details and try again.",
      );
    }
  };

  const toDelete = async (subjId) => {
    try {
      const response = await fetchWithAuth(
        `http://127.0.0.1:8000/student/${userId}/subjects/${subjId}`,
        {
          method: "DELETE",
        },
      );
      if (!response.ok) {
        setError("Could not delete the subject, pls Try Again.");
        return;
      }
      setSubjects(subjects.filter((subj) => subj.id !== subjId));
    } catch (error) {
      console.log("Error: ", error);
      setError("Could not Delete the subject, pls Try Again");
    }
  };

  const onGen = async () => {
    try {
      const response = await fetchWithAuth(
        `http://127.0.0.1:8000/student/${userId}/subjects/generate-table`,
        { method: "POST" },
      );

      if (!response.ok) {
        setError("Could not generate exam timetable now");
        return;
      }
    } catch (error) {
      console.log("Error:", error);
      setError("Could not generate exam timetable now");
    }
  };
  return (
    <div className={styles["subjectContainer"]}>
      <StudentNav username={username} />
      <Sidebar />
      <h1 className={styles["title"]}>Subject Page</h1>
      {error && <Toast message={error} onClose={() => setError("")} />}

      <form className={styles["addSubject"]} onSubmit={onSubmit}>
        <h2>Add Exam</h2>
        <input
          type="text"
          placeholder="Subject Name"
          value={subject.subject_name}
          onChange={(e) =>
            setSubjectName({ ...subject, subject_name: e.target.value })
          }
        />
        <DatePicker
          selected={subject.exam_date ? new Date(subject.exam_date) : null}
          onChange={(date) =>
            setSubjectName({
              ...subject,
              exam_date: date.toLocaleDateString("en-CA"),
            })
          }
          minDate={new Date()}
          dateFormat="dd-MM-yyyy"
          placeholderText="Select Exam Date"
          className={styles.dateInput}
        />
        <div className={styles["difficultyGroup"]}>
          <label>
            <input
              type="radio"
              name="difficulty"
              value="easy"
              checked={subject.difficulty === "easy"}
              onChange={(e) =>
                setSubjectName({ ...subject, difficulty: e.target.value })
              }
              required
            />
            Easy
          </label>

          <label>
            <input
              type="radio"
              name="difficulty"
              value="medium"
              checked={subject.difficulty === "medium"}
              onChange={(e) =>
                setSubjectName({ ...subject, difficulty: e.target.value })
              }
            />
            Medium
          </label>

          <label>
            <input
              type="radio"
              name="difficulty"
              value="hard"
              checked={subject.difficulty === "hard"}
              onChange={(e) =>
                setSubjectName({ ...subject, difficulty: e.target.value })
              }
            />
            Hard
          </label>
        </div>
        <button type="submit">Add Subject</button>
      </form>

      <div className={styles["subjectTable"]}>
        <h2>Your Upcoming Exam</h2>
        {subjects.length === 0 ? (
          <p>No subjects added yet.</p>
        ) : (
          <table border="1" style={{ marginTop: "20px", width: "100%" }}>
            <thead>
              <tr>
                <th>Subject ID</th>
                <th>Subject Name</th>
                <th>Exam Date</th>
                <th>Difficulty</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {subjects.map((subj) => (
                <tr key={subj.id}>
                  <td>{subj.id}</td>
                  <td>{subj.subject_name}</td>
                  <td>
                    {new Date(subj.exam_date).toLocaleDateString("en-GB", {
                      day: "numeric",
                      month: "short",
                      year: "numeric",
                    })}
                  </td>
                  <td>
                    <span className={styles[subj.difficulty]}>
                      {subj.difficulty}
                    </span>
                  </td>
                  <td>
                    <button
                      onClick={() =>
                        navigate(`/student/${userId}/subjects/${subj.id}/edit`)
                      }
                      className={styles["edit"]}
                    >
                      ✏️ Edit
                    </button>
                    <button
                      onClick={() => toDelete(subj.id)}
                      className={styles["delete"]}
                    >
                      Delete{" "}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <td colSpan="5" style={{ textAlign: "right" }}>
                  <button onClick={onGen} className={styles["genTable"]}>
                    Generate Table
                  </button>
                </td>
              </tr>
            </tfoot>
          </table>
        )}
      </div>
    </div>
  );
}
