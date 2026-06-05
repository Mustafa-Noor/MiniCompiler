import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Footer from '../components/Footer';
import ToastContainer from '../components/Toast';
import LoadingOverlay from '../components/LoadingOverlay';

export default function DashboardLayout() {
  return (
    <div className="h-full flex flex-col">
      <LoadingOverlay />
      <ToastContainer />
      <div className="flex flex-1 overflow-hidden">
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
