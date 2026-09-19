import { createBrowserRouter, createRoutesFromElements, Route, RouterProvider, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import {Toaster} from "sonner";
import AuthLayout from "./layouts/AuthLayout";
import NotFoundPage from './pages/NotFoundPage';
import MainPage from './pages/MainPage';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';
import GuestOnlyRoute from "./components/GuestOnlyRoute";
import Dashboard from "./pages/Dashboard";
import ProtectedRoute from "./components/ProtectedRoute";

const router = createBrowserRouter(
  createRoutesFromElements(
    <>
      <Route path="/" element={<MainPage />} />

      <Route element={<GuestOnlyRoute/>}>
        <Route path="auth" element={<AuthLayout />}>
          <Route index element={<Navigate to="login" replace />} />
          <Route path="signup" element={<RegisterPage />} />
          <Route path="login" element={<LoginPage />} />
        </Route>
      </Route>
      
      <Route element={<ProtectedRoute/>}>
        <Route path="dashboard" element={<Dashboard/>} />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </>
  )
);

const App = () => {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
      <Toaster position="bottom-right" richColors/>
    </AuthProvider>
  );
}

export default App;