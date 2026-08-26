import { createBrowserRouter, createRoutesFromElements, Route, Router, RouterProvider, Navigate } from "react-router-dom";
import AuthLayout from "./layouts/AuthLayout";
import NotFoundPage from './pages/NotFoundPage';
import MainPage from './pages/MainPage';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';

const router = createBrowserRouter(
  createRoutesFromElements(
    <>
      <Route path="/" element={<MainPage />} />

      <Route path="auth" element={<AuthLayout />}>
        <Route index element={<Navigate to="login" replace />} />
        <Route path="signup" element={<RegisterPage />} />
        <Route path="login" element={<LoginPage />} />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </>
  )
);

const App = () => {
  return <RouterProvider router={router} />
}

export default App;