import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AdminDesk } from "./admin/AdminDesk";
import { AdminLogin } from "./admin/AdminLogin";
import { Shell } from "./components/Shell";
import { About } from "./pages/About";
import { Essay } from "./pages/Essay";
import { Essays } from "./pages/Essays";
import { Home } from "./pages/Home";
import { Lab } from "./pages/Lab";
import { Missing } from "./pages/Missing";
import { Work } from "./pages/Work";
import { Works } from "./pages/Works";
import { SiteProvider } from "./site";

export function App() {
  return (
    <SiteProvider>
      <BrowserRouter>
        <Routes>
          <Route path="admin" element={<AdminLogin />} />
          <Route path="admin/desk" element={<AdminDesk />} />
          <Route element={<Shell />}>
            <Route index element={<Home />} />
            <Route path="essays" element={<Essays />} />
            <Route path="essays/:slug" element={<Essay />} />
            <Route path="works" element={<Works />} />
            <Route path="works/:slug" element={<Work />} />
            <Route path="about" element={<About />} />
            <Route path="lab" element={<Lab />} />
            <Route path="*" element={<Missing />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </SiteProvider>
  );
}
