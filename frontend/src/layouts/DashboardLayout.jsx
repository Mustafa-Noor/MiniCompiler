import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Footer from '../components/Footer';
import ToastContainer from '../components/Toast';
import LoadingOverlay from '../components/LoadingOverlay';

export default function DashboardLayout() {
  return (
    <div className="h-full flex flex-col relative overflow-hidden bg-[#07080c] text-slate-200">
      {/* Premium background radial glow spots */}
      <div className="absolute top-[-10%] left-[-5%] w-[45%] h-[45%] rounded-full bg-sky-500/5 blur-[120px] pointer-events-none z-0" />
      <div className="absolute bottom-[-10%] right-[-5%] w-[50%] h-[50%] rounded-full bg-indigo-500/4 blur-[140px] pointer-events-none z-0" />

      <LoadingOverlay />
      <ToastContainer />
      <div className="flex flex-1 overflow-hidden relative z-10">
        <Sidebar />
        <main className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto p-6 scrollbar-thin">
            <Outlet />
          </div>
          <Footer />
        </main>
      </div>
    </div>
  );
}

