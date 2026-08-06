import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";

export default function MainLayout({
  children,
}) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(16,185,129,0.12),_transparent_28%),radial-gradient(circle_at_top_right,_rgba(250,204,21,0.12),_transparent_22%),linear-gradient(180deg,_#f8fafc_0%,_#eefbf3_100%)]">
      <Navbar />

      <div className="flex">
        <Sidebar />

        <main className="flex-1 p-4 md:p-6 xl:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
