import { Link } from "react-router-dom";
import { useTitle } from "../site";

export function Missing() {
  useTitle("不在航线上");
  return (
    <section className="boot">
      <p className="eyebrow">404</p>
      <h1>这页不在航线上</h1>
      <Link className="btn" to="/">
        回到驾驶舱
      </Link>
    </section>
  );
}
