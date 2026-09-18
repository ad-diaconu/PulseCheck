import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const GuestOnlyRoute = () => {
    const { isAuthenticated, isLoading } = useAuth();

    if (isLoading) return null;
    if (isAuthenticated) return <Navigate to="/dashboard" replace />;
    return <Outlet/>;
}

export default GuestOnlyRoute;  