import { useAuth } from "../context/AuthContext"
import { Outlet, Navigate } from "react-router-dom";



const ProtectedRoute = () => {

    const {isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
        return null;
    }

    if (!isAuthenticated){
        return <Navigate to="/auth/login" replace/>
    }

    return <Outlet />


}

export default ProtectedRoute;