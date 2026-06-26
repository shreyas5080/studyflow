import { Link } from "react-router-dom";
import style from "../styles/components/sidebar.module.css";
export default function Sidebar() {
  return (
    <aside className={style["sideBar"]}>
      <nav className={style["sideNav"]}>
        <div className={style["navTitle"]}>StudyFlow</div>
        <ul className={style["navList"]}>
          <li>
            <Link to="/dashboard">Dashboard</Link>
          </li>
          <li>
            <Link to="/study-plans">Study Plans</Link>
          </li>
          <li>
            <Link to="/progress">Progress</Link>
          </li>
          <li>
            <Link to="/settings">Settings</Link>
          </li>
        </ul>
      </nav>
    </aside>
  );
}
