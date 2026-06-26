import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import Student from "./pages/dashboard/Student";
import Subject from "./pages/dashboard/Subject";
import EditSubject from "./pages/dashboard/EditSubject";
import TimeTable from "./pages/dashboard/TimeTable";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/register" element={<Register />} />
      <Route path="/login" element={<Login />} />
      <Route path="/student/:id/time-table" element={<TimeTable />} />
      <Route path="/student/:id" element={<Student />} />
      <Route path="/student/:id/subjects" element={<Subject />} />
      <Route
        path="/student/:id/subjects/:subjectId/edit"
        element={<EditSubject />}
      />
    </Routes>
  );
}

export default App;
